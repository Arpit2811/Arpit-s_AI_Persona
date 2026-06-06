**ArXiv Complete PDF Downloader — Distributed, Fault-Tolerant, Resume-Safe
This project is a high-performance, distributed ArXiv PDF scraper designed for large-scale archival of all papers on ArXiv from 1991 to today.
It supports:

1. Distributed scraping across multiple machines

2. Resume capability — never loses progress

3. Complete fault-tolerance

4. Adaptive rate limiting

5. Concurrent API calls + PDF downloads

6. Metadata storage

7. Auto category selection per year

8. Duplicate detection using a BloomFilter

9. Failure tracker

10. PDF integrity verification

11. Asynchronous downloads (aiohttp + asyncio)

Used properly, this system can download millions of PDFs safely.

**Features**
✔ Distributed Downloading

Split year ranges across machines so no machine downloads the same month twice.

✔ Auto Resume

If the downloader stops, it restarts from where it left.

✔ Month-wise Progress Tracking

Each month (e.g. 20150701_20150731) is marked completed after downloading papers.

✔ Metadata Management

Every downloaded paper is stored in metadata_all.json.

✔ Duplicate Avoidance

Using BloomFilter + memory checks to avoid reprocessing paper IDs.

✔ Intelligent Category Selection

ArXiv categories changed over the years — your script automatically picks correct ones.

✔ Fault-Tolerant PDF Downloading

PDFs are downloaded with retries and fallback HTTP download.

✔ PDF Verification

Ensures:

file exists

size > threshold

%PDF- header

%%EOF marker

✔ Fully Async
******
**Uses:

aiohttp
asyncio.Semaphore
concurrent tasks
for efficient parallel downloading**.