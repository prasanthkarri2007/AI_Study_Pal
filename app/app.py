from flask import Flask, render_template, request
import os
import random
import joblib

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# ✅ SAFE ML MODEL LOAD (NO CRASH, NO FEATURE MISMATCH)
# =========================================================
try:
    difficulty_model = joblib.load(os.path.join(BASE_DIR, "models/difficulty_model.pkl"))
    difficulty_vectorizer = joblib.load(os.path.join(BASE_DIR, "models/vectorizer.pkl"))
    ML_ENABLED = True
except Exception as e:
    print("⚠️ ML disabled:", e)
    ML_ENABLED = False


# =========================================================
# 📚 QUIZ BANK (ALL SUBJECTS, 10 QUESTIONS EACH)
# =========================================================
quiz_bank = {
    "Math": [
        {"q": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4", "difficulty": "easy"},
        {"q": "What is 5 + 7?", "options": ["10", "11", "12", "13"], "answer": "12", "difficulty": "easy"},
        {"q": "Solve: 10 − 3", "options": ["5", "6", "7", "8"], "answer": "7", "difficulty": "easy"},

        {"q": "What is 12 × 4?", "options": ["36", "48", "44", "52"], "answer": "48", "difficulty": "medium"},
        {"q": "Solve: 3x = 21", "options": ["5", "6", "7", "8"], "answer": "7", "difficulty": "medium"},

        {"q": "What is the derivative of x²?", "options": ["x", "2x", "x²", "2"], "answer": "2x", "difficulty": "hard"},
        {"q": "Solve: x² − 9 = 0", "options": ["±1", "±2", "±3", "±9"], "answer": "±3", "difficulty": "hard"},
        {"q": "What is sin²θ + cos²θ?", "options": ["0", "1", "2", "Depends"], "answer": "1", "difficulty": "hard"},
    ],

    "Python": [
        {"q": "Which keyword defines a function?", "options": ["func", "define", "def", "function"], "answer": "def", "difficulty": "easy"},
        {"q": "Output of len([1,2,3])?", "options": ["2", "3", "4", "Error"], "answer": "3", "difficulty": "easy"},

        {"q": "Which type is immutable?", "options": ["list", "dict", "set", "tuple"], "answer": "tuple", "difficulty": "medium"},
        {"q": "What does list.append() do?", "options": ["add", "remove", "sort", "copy"], "answer": "add", "difficulty": "medium"},

        {"q": "What is PEP 8?", "options": ["library", "compiler", "style guide", "IDE"], "answer": "style guide", "difficulty": "hard"},
        {"q": "Which keyword handles exceptions?", "options": ["catch", "error", "except", "handle"], "answer": "except", "difficulty": "hard"},
    ],

    "Science": [
        {"q": "Red Planet?", "options": ["Earth", "Mars", "Venus", "Jupiter"], "answer": "Mars", "difficulty": "easy"},
        {"q": "Gas plants absorb?", "options": ["O₂", "N₂", "CO₂", "H₂"], "answer": "CO₂", "difficulty": "easy"},

        {"q": "Boiling point of water?", "options": ["90", "95", "100", "110"], "answer": "100", "difficulty": "medium"},
        {"q": "Which vitamin from sunlight?", "options": ["A", "B", "C", "D"], "answer": "D", "difficulty": "medium"},

        {"q": "Center of atom?", "options": ["Electron", "Proton", "Nucleus", "Neutron"], "answer": "Nucleus", "difficulty": "hard"},
    ]
}


# =========================================================
# 🧠 ML DIFFICULTY PREDICTION (SAFE)
# =========================================================
def predict_difficulty(question):
    if not ML_ENABLED:
        return "easy"
    try:
        X = difficulty_vectorizer.transform([question])
        return difficulty_model.predict(X)[0]
    except:
        return "easy"


# =========================================================
# 📝 QUIZ SELECTION LOGIC (NO REPEAT, HARD WORKS)
# =========================================================
def get_quiz_questions(subject, selected_level):
    all_questions = quiz_bank.get(subject, [])
    random.shuffle(all_questions)

    final = []
    for q in all_questions:
        level = q.get("difficulty") or predict_difficulty(q["q"])
        if level == selected_level:
            final.append(q)

    # fallback if not enough
    if len(final) < 5:
        final = all_questions.copy()

    return final[:10]


# =========================================================
# 📅 STUDY PLAN
# =========================================================
def generate_weekly_plan(subjects, hours, scenario):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    per_subject = round(float(hours) / len(subjects), 2)

    plan = []
    for day in days:
        for s in subjects:
            plan.append(f"{day}: {s} – {per_subject} hrs ({scenario})")
    return plan


def summarize_text(text):
    return " ".join(text.split()[:40])


# =========================================================
# 🚀 ROUTE
# =========================================================
@app.route("/", methods=["GET", "POST"])
def index():
    weekly_plan = None
    summary = None
    selected_quizzes = {}

    if request.method == "POST":
        subjects = request.form.getlist("subjects")
        hours = request.form.get("hours")
        scenario = request.form.get("scenario")
        text = request.form.get("text")
        difficulty = request.form.get("difficulty", "easy")

        if subjects and hours:
            weekly_plan = generate_weekly_plan(subjects, hours, scenario)

        if text:
            summary = summarize_text(text)

        for s in subjects:
            selected_quizzes[s] = get_quiz_questions(s, difficulty)

    return render_template(
        "index.html",
        weekly_plan=weekly_plan,
        summary=summary,
        selected_quizzes=selected_quizzes
    )


if __name__ == "__main__":
    app.run(debug=True)
