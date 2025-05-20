import os
import logging
import torch
import re
from textstat import flesch_reading_ease
from transformers import AutoTokenizer, BartForConditionalGeneration

# === Logging setup ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/compare_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Load BART model ===
model_id = "facebook/bart-large-cnn"
# model_id = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = BartForConditionalGeneration.from_pretrained(model_id)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# === Utility: Truncate text ===
def truncate_text(text, max_words=100):
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

# === Simple tokenizer without NLTK ===
def count_tokens(text):
    return len(re.findall(r'\b\w+\b', text))

def count_sentences(text):
    return len(re.findall(r'[.!?]+', text))

# === Main Function: Compare Papers ===
def compare_papers(paper1, paper2, max_words=100, max_tokens=256):
    abstract1 = truncate_text(paper1['abstract'], max_words)
    abstract2 = truncate_text(paper2['abstract'], max_words)

    comparison_input = f"""
Paper 1:
Title: {paper1['title']}
Abstract: {abstract1}

Paper 2:
Title: {paper2['title']}
Abstract: {abstract2}

Compare these two research papers in terms of goals, methods, contributions, strengths & weaknesses, and similarities.
"""

    logging.info("Prompt :\n%s", comparison_input.strip())

    inputs = tokenizer(
        comparison_input.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(device)

    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_tokens,
        num_beams=4,
        early_stopping=True
    )

    result = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    logging.info("Model output:\n%s", result)

    # === Evaluation (native Python) ===
    token_count = count_tokens(result)
    sentence_count = count_sentences(result)
    reading_score = flesch_reading_ease(result)
    input_length = inputs["input_ids"].shape[1]
    compression_ratio = round(input_length / max(1, token_count), 2)

    logging.info("Evaluation Metrics:")
    logging.info(f"- Output Token Count       : {token_count}")
    logging.info(f"- Sentence Count           : {sentence_count}")
    logging.info(f"- Flesch Reading Ease      : {reading_score:.2f}")
    logging.info(f"- Input Length (tokens)    : {input_length}")
    logging.info(f"- Compression Ratio (I/O)  : {compression_ratio}")

    return f"### Prompt:\n{comparison_input.strip()}\n\n### Response:\n{result.strip()}"
