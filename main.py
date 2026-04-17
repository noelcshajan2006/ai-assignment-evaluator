from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import re
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# =========================
# ✅ CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 📦 MODEL
# =========================
class Assignment(BaseModel):
    content: str


# =========================
# 🗄️ DATABASE
# =========================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    score INTEGER,
    result TEXT
)
""")
conn.commit()


# =========================
# 🧹 CLEAN OUTPUT
# =========================
def clean_output(text):
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    text = text.replace('\r', '')
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()


# =========================
# 🤖 RUN AI
# =========================
def run_agent(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return clean_output(result.stdout)

    except Exception as e:
        return f"Exception occurred: {str(e)}"


# =========================
# 📊 SCORE EXTRACTION (FIXED)
# =========================
def extract_score(text):
    match = re.search(r"SCORE[:\s]*([0-9]{1,3})", text, re.IGNORECASE)

    if match:
        score = int(match.group(1))
        return min(score, 100)  # clamp max to 100

    return 0


# =========================
# 🤖 AGENTS
# =========================
def input_agent(content):
    return content


def validation_agent(content):
    if not content or not content.strip():
        return False
    return True


def analysis_agent(content):
    prompt = f"Analyze this assignment:\n{content}"
    return run_agent(prompt)


def scoring_agent(content):
    prompt = f"""
Evaluate this assignment strictly.

Return ONLY in this format:
SCORE: <number>

Rules:
- Poor content → below 40
- Average → 40–70
- Good → above 70

Assignment:
{content}
"""
    result = run_agent(prompt)
    return extract_score(result)


def feedback_agent(content):
    prompt = f"Give 3 to 5 feedback points:\n{content}"
    return run_agent(prompt)


def grammar_agent(content):
    prompt = f"Check grammar mistakes:\n{content}"
    return run_agent(prompt)


# =========================
# 🧠 SUPER AGENT (ORCHESTRATION)
# =========================
def super_agent(content):

    # Step 1: Input
    content = input_agent(content)

    # Step 2: Validation
    if not validation_agent(content):
        return 0, "Validation Failed: No content provided"

    # Step 3: Analysis
    analysis = analysis_agent(content)

    # Step 4: Score
    score = scoring_agent(content)

    # =========================
    # 🔥 ORCHESTRATION LOGIC
    # =========================
    if score < 40 or len(content.split()) < 10:
        feedback = "Poor assignment. Needs major improvement."
    else:
        feedback = feedback_agent(content)

    # Step 5: Grammar
    grammar = grammar_agent(content)

    # Final Output
    final_output = f"""
ANALYSIS:
{analysis}

SCORE:
{score}

FEEDBACK:
{feedback}

GRAMMAR:
{grammar}
"""

    return score, final_output


# =========================
# 🌐 MAIN PIPELINE
# =========================
def evaluate_assignment(content):
    return super_agent(content)


# =========================
# ⏱️ SCHEDULER
# =========================
def scheduled_task():
    print("🔄 Scheduler running: system check...")


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, "interval", seconds=60)
scheduler.start()


# =========================
# 🌐 API
# =========================
@app.post("/evaluate")
def evaluate(data: Assignment):
    score, output = evaluate_assignment(data.content)

    cursor.execute(
        "INSERT INTO history (content, score, result) VALUES (?, ?, ?)",
        (data.content, score, output)
    )
    conn.commit()

    return {
        "score": score,
        "result": output
    }


@app.get("/history")
def get_history():
    cursor.execute("SELECT content, score, result FROM history")
    rows = cursor.fetchall()

    return [
        {"content": r[0], "score": r[1], "result": r[2]}
        for r in rows
    ]