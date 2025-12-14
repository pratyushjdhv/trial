from app import app
from flask import request, jsonify
from model import *
from logic import *
from datetime import datetime
from sandbox import run_docker


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required!"}), 400

    # 2. Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username taken! please take another."}), 400

    new_user = User(username=username)

    db.session.add(new_user)  # Add to the "staging area"
    db.session.commit()      # Save changes permanently

    return jsonify({"message": f"Welcome, {username}!", "id": new_user.id})


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Convert the list of objects into a list of JSON dictionaries
    result = [{"id": u.id, "username": u.username,
               "score": u.total_score} for u in users]
    return jsonify(result)


@app.route('/questions', methods=['GET'])
def get_questions():

    questions = []
    for q_id, config in QUESTIONS.items():
        questions.append({
            "id": q_id,
            "difficulty": config["difficulty"],
            "base_points": config["base_points"],
            "max_probes": config["max_probes"],
            "description": config.get("description", "")
        })
    return jsonify(questions)


# --- NEW: PROBE ROUTE (User tests inputs against YOUR logic) ---
@app.route('/probe', methods=['POST'])
def probe():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    user_input = data.get('input')

    # 1. Validation
    try:
        val = int(user_input)
    except (ValueError, TypeError):
        return jsonify({"error": "Input must be a valid integer"}), 400

    config = QUESTIONS.get(question_id)
    if not config:
        return jsonify({"error": "Invalid Question ID"}), 404

    # 2. Track Usage in DB
    progress = UserProgress.query.filter_by(
        user_id=user_id, question_id=question_id).first()

    # --- FIX STARTS HERE ---
    # Create progress entry if it's their first time
    if not progress:
        # Explicitly set probes_used=0 so Python knows it's an integer immediately
        progress = UserProgress(
            user_id=user_id,
            question_id=question_id,
            probes_used=0
        )
        db.session.add(progress)
        # We don't commit yet because we might update it below
    # --- FIX ENDS HERE ---

    # Check if they have probes left
    if progress.probes_used >= config['max_probes']:
        return jsonify({"error": "No probes left! Try submitting code."}), 403

    # 3. Run YOUR Hidden Logic
    try:
        expected_output = config['func'](val)

        # Save progress
        progress.probes_used += 1
        db.session.commit()

        return jsonify({
            "input": val,
            "output": expected_output,
            "probes_left": config['max_probes'] - progress.probes_used
        })
    except Exception as e:
        return jsonify({"error": "Internal Logic Error"}), 500


# --- NEW: SUBMIT ROUTE (Runs User Code in Docker) ---
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    user_code = data.get('code')

    if not user_code:
        return jsonify({"error": "No code provided"}), 400

    # 1. Get Question Details
    config = QUESTIONS.get(question_id)
    if not config:
        return jsonify({"error": "Invalid Question"}), 404

    # 2. Run Hidden Test Cases
    # We define hidden cases in logic.py or hardcode them here
    # Example: default cases if none provided in config
    test_cases = config.get('test_cases', [0, 10, -5, 100])

    passed = 0
    logs = []

    for test_val in test_cases:
        # A. Get Expected Output (From your logic)
        expected = config['func'](test_val)

        # B. Get Actual Output (From Student Code via Docker)
        actual = run_docker(user_code, test_val)

        # C. Compare
        # We convert both to string and strip whitespace to be safe
        if str(actual).strip() == str(expected).strip():
            passed += 1
            logs.append({"input": test_val, "status": "Pass"})
        else:
            logs.append({"input": test_val, "status": "Fail",
                        "got": actual, "expected": "Hidden"})

    # 3. Calculate Score
    is_correct = (passed == len(test_cases))
    points_awarded = 0

    if is_correct:
        progress = UserProgress.query.filter_by(
            user_id=user_id, question_id=question_id).first()

        # FIX: Initialize with default values if it doesn't exist
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                question_id=question_id,
                probes_used=0,
                is_solved=False
            )
            db.session.add(progress)

        if not progress.is_solved:
            progress.is_solved = True

            # Simple Time Penalty Logic (Optional)
            # points = Base - (Minutes since event start)
            points_awarded = config['base_points']

            # Update Total User Score
            user = User.query.get(user_id)
            user.total_score += points_awarded

            db.session.commit()

    return jsonify({
        "solved": is_correct,
        "score_added": points_awarded,
        "tests_passed": passed,
        "total_tests": len(test_cases),
        "details": logs
    })
