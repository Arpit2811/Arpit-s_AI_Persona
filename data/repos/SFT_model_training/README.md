SFT Model Training Pipeline
Overview

This repository provides a pipeline for Supervised Fine-Tuning (SFT) of large language models using Hugging Face Transformers, Datasets, and PyTorch. It supports loading datasets from Parquet or JSON formats, processing conversational data, tokenizing inputs, and training models efficiently on GPU-enabled systems.

The project is designed for scalability and can be adapted for large datasets and multi-GPU environments.

Features
Support for chat-based datasets with role and content structure
Efficient dataset loading from Parquet and Hugging Face datasets
Batch tokenization pipeline
Configurable training parameters
Logging for monitoring training and debugging
Compatible with large-scale training setups
Project Structure
SFT_MODEL_TRAINING/

├── data/                  # Input datasets
├── tokenizer/             # Saved tokenizer files
├── logs/                  # Log files

├── train.py               # Main training script
├── preprocess.py          # Data preprocessing logic
├── utils.py               # Utility functions
├── config.py              # Configuration settings

├── requirements.txt
└── README.md
Installation
Clone the repository
git clone https://github.com/Arpit2811/SFT_MODEL_TRAINING.git
cd SFT_MODEL_TRAINING
Create a virtual environment
python -m venv env
source env/bin/activate

On Windows:

env\Scripts\activate
Install dependencies
pip install -r requirements.txt
Dataset Format

The pipeline expects conversational data in the following format:

[
  {"role": "user", "content": "Question"},
  {"role": "assistant", "content": "Answer"}
]

If using Parquet files, the data should typically be stored under a column such as messages containing the same structure.

Data Processing

The preprocessing pipeline performs the following steps:

Loads dataset from Parquet or JSON files
Extracts role and content fields
Formats conversations into a training-ready structure
Applies tokenization using a Hugging Face tokenizer
Training

Run the training script:

python train.py

Training parameters can be configured in the configuration file or directly in the script. Typical parameters include:

BATCH_SIZE = 8
LEARNING_RATE = 2e-5
EPOCHS = 3
MAX_LENGTH = 2048
Logging

Logs are stored in the logs/ directory. These include:

Dataset processing progress
Training status
Error and debug information
Output

After training, the following outputs are generated:

Model checkpoints in the output directory
Tokenizer files in the tokenizer directory
Performance Considerations
Use mixed precision (fp16 or bfloat16) for faster training
Adjust batch size based on available GPU memory
Use gradient accumulation for large models
Prefer Parquet format for handling large datasets
Future Enhancements
Integration with parameter-efficient fine-tuning methods such as LoRA
Support for distributed training frameworks such as DeepSpeed
Evaluation and benchmarking pipeline
Inference utilities
License

This project is licensed under the MIT License.

Author

Arpit Kumble