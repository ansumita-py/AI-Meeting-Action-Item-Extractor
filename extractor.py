import re
import json
from datetime import datetime

# Transformer-based extraction is enabled when the required packages/model are available.
# The fallback rules keep the project usable if the model cannot be downloaded.
USE_TRANSFORMER = True
MODEL_NAME = "google/flan-t5-small"

_transformer = None

def get_transformer():
    global _transformer
    if _transformer is not None:
        return _transformer
    try:
        from transformers import pipeline
        _transformer = pipeline(
            "text2text-generation",
            model=MODEL_NAME,
            max_new_tokens=180
        )
        return _transformer
    except Exception:
        return None

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

def split_sentences(transcript):
    parts = re.split(r'(?<=[.!?])\s+|\n+', transcript)
    return [clean_text(p) for p in parts if clean_text(p)]

def transformer_extract(sentence):
    model = get_transformer()
    if model is None:
        return None

    prompt = f"""Extract an action item from this meeting sentence.
Return only JSON with these keys: task, owner, deadline.
If the owner or deadline is not stated, use "Unassigned" or "Not specified".
Sentence: {sentence}"""

    try:
        output = model(prompt)[0]["generated_text"]
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(0))
        if not data.get("task"):
            return None
        return {
            "task": str(data.get("task", sentence)).strip(),
            "owner": str(data.get("owner", "Unassigned")).strip(),
            "deadline": str(data.get("deadline", "Not specified")).strip()
        }
    except Exception:
        return None

def find_owner(sentence):
    patterns = [
        r"Assigned to\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",
        r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s+(?:will|should|needs to|must|to)\b",
        r"\b(?:owner|responsible|handled by)\s*[:\-]?\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)"
    ]
    for pattern in patterns:
        m = re.search(pattern, sentence, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Unassigned"

def find_deadline(sentence):
    patterns = [
        r"\b(?:by|before|on)\s+((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:\s+\w+)?)",
        r"\b(?:by|before|on)\s+(\d{1,2}(?:st|nd|rd|th)?\s+\w+)",
        r"\b(?:by|before|on)\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?)",
        r"\b(?:by|before|on)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"\b(by\s+tomorrow|by\s+today|by\s+next week|by\s+Friday|by\s+Monday)\b"
    ]
    for pattern in patterns:
        m = re.search(pattern, sentence, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Not specified"

def is_action_sentence(sentence):
    action_words = [
        "will", "should", "need to", "needs to", "must", "action item",
        "todo", "to-do", "follow up", "prepare", "send", "create",
        "update", "review", "complete", "finish", "submit", "schedule",
        "contact", "check", "fix", "develop", "design", "implement"
    ]
    lower = sentence.lower()
    return any(word in lower for word in action_words)

def extract_task(sentence):
    s = re.sub(r"^[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?:\s*", "", sentence)
    return s.strip(" .")

def confidence(sentence, owner, deadline, used_transformer=False):
    score = 0.50
    if owner != "Unassigned":
        score += 0.20
    if deadline != "Not specified":
        score += 0.20
    if any(v in sentence.lower() for v in ["will", "must", "need to", "action item"]):
        score += 0.10
    if used_transformer:
        score += 0.05
    return min(score, 0.99)

def validate_items(items):
    validated = []
    seen = set()

    for item in items:
        task_key = re.sub(r"[^a-z0-9]", "", item["task"].lower())
        if not task_key or task_key in seen:
            continue
        seen.add(task_key)

        deadline = item["deadline"]
        if re.fullmatch(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", deadline):
            try:
                datetime.strptime(deadline.replace("-", "/"), "%d/%m/%Y")
            except ValueError:
                item["deadline"] += " (check date)"

        if item["owner"] == "Unassigned":
            item["status"] = "Needs owner"
        elif item["deadline"] == "Not specified":
            item["status"] = "Needs deadline"
        else:
            item["status"] = "Open"

        validated.append(item)

    return validated

def extract_action_items(transcript):
    items = []

    for sentence in split_sentences(transcript):
        if not is_action_sentence(sentence):
            continue

        ai_data = transformer_extract(sentence) if USE_TRANSFORMER else None
        used_transformer = ai_data is not None

        if ai_data:
            task = ai_data["task"]
            owner = ai_data["owner"]
            deadline = ai_data["deadline"]
        else:
            owner = find_owner(sentence)
            deadline = find_deadline(sentence)
            task = extract_task(sentence)

        if len(task.split()) < 3:
            continue

        items.append({
            "task": task,
            "owner": owner,
            "deadline": deadline,
            "confidence": f"{confidence(sentence, owner, deadline, used_transformer) * 100:.0f}%",
            "status": "Open"
        })

    return validate_items(items)

if __name__ == "__main__":
    sample = """Alice: Rahul will prepare the project report by Friday.
Priya: I will review the report on Monday.
Manager: John should send the client email by tomorrow.
Anita: We need to schedule the next meeting."""
    for item in extract_action_items(sample):
        print(item)
