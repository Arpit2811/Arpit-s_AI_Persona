"""
ingestion.py
------------
Unified Ingestion Pipeline — Resume (.docx) + GitHub READMEs (.md)
Parses all sources → structured chunks with metadata → BGE embeddings → FAISS index

Sources supported:
  - Resume      : single .docx file
  - GitHub READMEs : one or more .md files (one per repo)

Output (index/ directory):
  - resume.index   : FAISS flat IP index
  - chunks.json    : all chunks with text + metadata

Usage:
    from ingestion import run_ingestion

    run_ingestion(
        resume_path="Resume_Arpit_v2026.docx",
        readme_paths=[
            "repos/minhash_dedup/README.md",
            "repos/arxiv_downloader/README.md",
        ],
        out_dir="index"
    )

Dependencies:
    pip install python-docx sentence-transformers faiss-cpu numpy
"""

import os
import re
import json
import numpy as np
import faiss
from docx import Document
from sentence_transformers import SentenceTransformer


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # 768-dim, no prefix needed at index time

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — RESUME PARSING (.docx)
# ─────────────────────────────────────────────────────────────────────────────

RESUME_SECTION_HEADERS = {
    "summary":        ["summary", "profile", "about"],
    "experience":     ["experience", "work experience", "employment"],
    "projects":       ["projects", "academic projects", "project"],
    "skills":         ["skills", "technology skills", "technical skills"],
    "certifications": ["certifications", "licenses", "licenses & certifications"],
    "education":      ["education", "academic background"],
    "interests":      ["interests", "hobbies", "avocations"],
}

def _detect_resume_section(text: str) -> str | None:
    clean = text.strip().lower().rstrip(":")
    for section, keywords in RESUME_SECTION_HEADERS.items():
        if clean in keywords:
            return section
    return None


def _parse_docx(path: str) -> dict[str, list[str]]:
    doc = Document(path)
    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        section = _detect_resume_section(text)
        if section:
            current = section
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(text)
    return sections


def _build_resume_chunks(sections: dict[str, list[str]], chunks: list[dict], chunk_id_ref: list):
    """Append resume chunks into shared chunks list."""

    def add(section, text, metadata=None):
        cid = chunk_id_ref[0]
        chunks.append({
            "id":       f"chunk_{cid:04d}",
            "source":   "resume",
            "section":  section,
            "text":     text.strip(),
            "metadata": metadata or {},
        })
        chunk_id_ref[0] += 1

    if sections.get("header"):
        add("header", "\n".join(sections["header"]), {"type": "contact"})

    if sections.get("summary"):
        add("summary", " ".join(sections["summary"]), {"type": "summary"})

    # Experience — one chunk per role block
    exp_lines = sections.get("experience", [])
    current_role, current_company = [], None
    for line in exp_lines:
        is_company = bool(re.search(r'\b(20\d{2})\b', line)) and len(line) < 80
        if is_company and current_role:
            add("experience", "\n".join(current_role), {"type": "role", "company": current_company or ""})
            current_role = []
        if is_company:
            current_company = line.split("|")[0].strip()
        current_role.append(line)
    if current_role:
        add("experience", "\n".join(current_role), {"type": "role", "company": current_company or ""})

    # Projects — one chunk per project
    proj_lines = sections.get("projects", [])
    current_proj = []
    for line in proj_lines:
        is_new = line.startswith("Project") or ("|" in line and re.search(r'\b(20\d{2})\b', line))
        if is_new and current_proj:
            add("projects", "\n".join(current_proj), {"type": "project"})
            current_proj = []
        current_proj.append(line)
    if current_proj:
        add("projects", "\n".join(current_proj), {"type": "project"})

    # Skills — one chunk per category
    for line in sections.get("skills", []):
        if ":" in line:
            cat, _, items = line.partition(":")
            add("skills", f"{cat.strip()}: {items.strip()}", {"type": "skill_category", "category": cat.strip()})
        else:
            add("skills", line, {"type": "skill_misc"})

    if sections.get("certifications"):
        add("certifications", "\n".join(sections["certifications"]), {"type": "certifications"})

    if sections.get("education"):
        add("education", "\n".join(sections["education"]), {"type": "education"})

    if sections.get("interests"):
        add("interests", " ".join(sections["interests"]), {"type": "interests"})


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — GITHUB README PARSING (.md)
# ─────────────────────────────────────────────────────────────────────────────

def _infer_repo_name(path: str) -> str:
    """Derive a clean repo name from the file path."""
    parts = os.path.normpath(path).split(os.sep)
    # prefer parent directory name over filename
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").replace("_", " ").title()
    return os.path.splitext(parts[-1])[0].replace("-", " ").replace("_", " ").title()


def _split_readme_into_sections(content: str) -> list[tuple[str, str]]:
    """
    Split a markdown README into (heading, body) pairs.
    Top-level (# / ##) headings become section boundaries.
    Returns list of (section_title, section_text).
    """
    lines = content.splitlines()
    sections = []
    current_heading = "overview"
    current_lines = []

    for line in lines:
        h_match = re.match(r'^#{1,2}\s+(.*)', line)
        if h_match:
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_heading, body))
            current_heading = h_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_heading, body))

    return sections


def _build_readme_chunks(readme_path: str, chunks: list[dict], chunk_id_ref: list):
    """Parse a README.md and append chunks into shared chunks list."""
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    repo_name = _infer_repo_name(readme_path)
    sections  = _split_readme_into_sections(content)

    def add(section_title, text, metadata=None):
        cid = chunk_id_ref[0]
        meta = {"type": "readme_section", "repo": repo_name, "heading": section_title}
        if metadata:
            meta.update(metadata)
        chunks.append({
            "id":       f"chunk_{cid:04d}",
            "source":   "github",
            "section":  "github_repo",
            "text":     f"[Repo: {repo_name}] [{section_title}]\n{text.strip()}",
            "metadata": meta,
        })
        chunk_id_ref[0] += 1

    for heading, body in sections:
        # Skip empty or pure-code sections (not useful for Q&A)
        non_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL).strip()
        if len(non_code) < 30:
            continue

        # Long sections (>800 chars) get split into sub-chunks by paragraph
        if len(non_code) > 800:
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', non_code) if len(p.strip()) > 40]
            for i, para in enumerate(paragraphs):
                add(heading, para, {"sub_chunk": i})
        else:
            add(heading, non_code)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — EMBEDDING
# ─────────────────────────────────────────────────────────────────────────────

def _embed(chunks: list[dict]) -> np.ndarray:
    model = SentenceTransformer(EMBED_MODEL)
    texts = [c["text"] for c in chunks]
    print(f"[ingestion] Embedding {len(texts)} chunks with '{EMBED_MODEL}'…")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-10)
    return embeddings.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — INDEX + PERSIST
# ─────────────────────────────────────────────────────────────────────────────

def _build_and_save(chunks: list[dict], embeddings: np.ndarray, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, os.path.join(out_dir, "resume.index"))
    with open(os.path.join(out_dir, "chunks.json"), "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"[ingestion] Saved {len(chunks)} chunks → {out_dir}/")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def run_ingestion(
    resume_path: str | None      = None,
    readme_paths: list[str]      = None,
    out_dir: str                 = "index",
):
    """
    Ingest resume and/or GitHub READMEs into a unified FAISS index.

    Args:
        resume_path  : path to .docx resume file (optional)
        readme_paths : list of paths to README.md files (optional)
        out_dir      : output directory for index + chunks.json
    """
    chunks       = []
    chunk_id_ref = [0]   # mutable int passed by reference

    if resume_path:
        print(f"[ingestion] Parsing resume: {resume_path}")
        sections = _parse_docx(resume_path)
        print(f"[ingestion] Resume sections: {list(sections.keys())}")
        _build_resume_chunks(sections, chunks, chunk_id_ref)
        print(f"[ingestion] Resume chunks built: {chunk_id_ref[0]}")

    for rp in (readme_paths or []):
        print(f"[ingestion] Parsing README: {rp}")
        before = chunk_id_ref[0]
        _build_readme_chunks(rp, chunks, chunk_id_ref)
        print(f"[ingestion] README chunks built: {chunk_id_ref[0] - before}  ({rp})")

    if not chunks:
        raise ValueError("No sources provided. Pass resume_path and/or readme_paths.")

    print(f"[ingestion] Total chunks: {len(chunks)}")
    for c in chunks:
        src = c['source']
        sec = c['section']
        preview = c['text'][:70].replace('\n', ' ')
        print(f"  [{src:8s}][{sec:15s}] {c['id']} → {preview}…")

    embeddings = _embed(chunks)
    _build_and_save(chunks, embeddings, out_dir)
    print("[ingestion] Done.")


# ─────────────────────────────────────────────────────────────────────────────
# QUICK RUN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_ingestion(
        resume_path  = r"C:\Users\Admin\Desktop\sclaer\data\Resume_Arpit_v2026.docx",
        readme_paths = [r"C:\Users\Admin\Desktop\sclaer\data\repos\Arxiv_scrapping\README.md",
                        r"C:\Users\Admin\Desktop\sclaer\data\repos\Minhash_lsh_dedup\README.md",
                        r"C:\Users\Admin\Desktop\sclaer\data\repos\ATS_Resume_Analyser\README.md",
                        r"C:\Users\Admin\Desktop\sclaer\data\repos\SFT_model_training\README.md",
                        r"C:\Users\Admin\Desktop\sclaer\data\repos\Zlib_Processing\README.md"],
        out_dir = "index",
    )