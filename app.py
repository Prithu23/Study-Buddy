import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"  # or "llama-3.1-8b-instant" for faster/cheaper

app = Flask(__name__)
CORS(app)

with open("faq.json", encoding="utf-8") as f:
    FAQS = json.load(f)

# ---------- Role prompt ----------
ROLE_PROMPT = (
    "You are StudyBuddy, a patient and encouraging study tutor for "
    "engineering undergraduates. Explain concepts step by step in simple "
    "language, give one short example, and end with a one-line summary. "
    "Keep answers under 150 words."
)

# ---------- Few-shot examples ----------
FEW_SHOT_EXAMPLES = [
    ("What is a stack?",
     "Definition: A stack is a linear data structure that follows LIFO "
     "(Last In, First Out).\n"
     "Example: A pile of plates - you remove the top one first.\n"
     "Key point: Main operations are push and pop."),
    ("What is normalization?",
     "Definition: Normalization organizes database tables to reduce redundancy.\n"
     "Example: Splitting a table with repeated customer details into "
     "Customer and Orders tables.\n"
     "Key point: It improves consistency and saves storage."),
]

# ---------- Simple FAQ retrieval (keyword overlap) ----------
def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def retrieve(query, k=2, min_overlap=2):
    q = tokens(query)
    scored = []
    for item in FAQS:
        score = len(q & tokens(item["question"] + " " + item["answer"]))
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:k] if score >= min_overlap]

# ---------- Prompt builders ----------
def build_messages(mode, user_msg):
    if mode == "zero_shot":
        return [{"role": "user", "content": user_msg}]

    if mode == "few_shot":
        msgs = []
        for q, a in FEW_SHOT_EXAMPLES:
            msgs.append({"role": "user", "content": q})
            msgs.append({"role": "assistant", "content": a})
        msgs.append({"role": "user", "content": user_msg})
        return msgs

    if mode == "role":
        return [
            {"role": "system", "content": ROLE_PROMPT},
            {"role": "user", "content": user_msg},
        ]

    if mode == "faq":
        hits = retrieve(user_msg)
        if hits:
            context = "\n".join(
                f"Q: {h['question']}\nA: {h['answer']}" for h in hits
            )
        else:
            context = "(no relevant FAQ entries found)"
        system = (
            ROLE_PROMPT
            + "\n\nAnswer ONLY using the FAQ context below. If the answer is "
              "not in the context, reply exactly: \"I couldn't find that in "
              "the FAQ. Please ask your faculty or coordinator.\"\n\n"
              "FAQ context:\n" + context
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]

    raise ValueError("Unknown mode")

# ---------- API route ----------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    mode = data.get("mode", "zero_shot")
    if not message:
        return jsonify({"error": "Empty message"}), 400
    try:
        messages = build_messages(mode, message)
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            reasoning_effort="low",
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply, "mode": mode, "prompt_used": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)