import os
from datetime import datetime


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "chat.log")
os.makedirs(LOG_DIR, exist_ok=True)

def log_interaction(source: str, question: str, answer: str):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{time}] [{source}]\n"
        f"Q: {question}\n"
        f"A: {answer}\n"
        f"{'-'*30}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
