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

    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        return jsonify({
            "message": f"Welcome back, {username}!", 
            "id": existing_user.id,
            "username": existing_user.username
        })

    # Create new user if they don't exist
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": f"Welcome, {username}!", 
        "id": new_user.id,
        "username": new_user.username
    })


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
# backend/routes.py

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    user_code = data.get('code')

    if not user_code:
        return jsonify({"error": "No code provided"}), 400

    # 1. Get Config
    config = QUESTIONS.get(question_id)
    if not config:
        return jsonify({"error": "Invalid Question"}), 404

    # 2. Run Hidden Test Cases
    test_cases = config.get('test_cases', [])
    passed_count = 0
    logs = []

    for test_val in test_cases:
        expected = config['func'](test_val)
        actual = run_docker(user_code, test_val) # Run in Docker

        if str(actual).strip() == str(expected).strip():
            passed_count += 1
            logs.append({"input": test_val, "status": "Pass"})
        else:
            logs.append({"input": test_val, "status": "Fail", "got": actual, "expected": "Hidden"})

    # 3. Database & Scoring Logic
    user = User.query.get(user_id)
    progress = UserProgress.query.filter_by(user_id=user_id, question_id=question_id).first()

    # Initialize progress if it doesn't exist (Crucial for first submit)
    if not progress:
        progress = UserProgress(
            user_id=user_id, 
            question_id=question_id, 
            probes_used=0, 
            tests_passed=0, # Default to 0
            is_solved=False
        )
        db.session.add(progress)

    score_change = 0
    
    # CHECK: Did they improve? (Passed more tests than before)
    if passed_count > progress.tests_passed:
        # 1. Award points for NEW tests passed (Partial Scoring)
        new_tests = passed_count - progress.tests_passed
        points_per_test = 10 # You can adjust this
        
        score_change += (new_tests * points_per_test)
        
        # 2. Update their record
        progress.tests_passed = passed_count
        progress.solved_at = datetime.utcnow() # Updates timestamp on improvement!

    # CHECK: Did they solve ALL tests?
    is_complete = (passed_count == len(test_cases))
    
    if is_complete and not progress.is_solved:
        progress.is_solved = True
        
        # --- BONUS SCORING ---
        # A. Base Difficulty Points
        score_change += config['base_points']

        # B. Probes Bonus (50 pts per unused probe)
        # We assume max_probes is 3. If they used 1, they get 2 * 50 = 100 bonus.
        probes_left = max(0, config['max_probes'] - progress.probes_used)
        probe_bonus = probes_left * 50
        
        # C. Time Bonus (100 pts - minutes taken)
        # Calculates time since they registered/started
        time_taken = (datetime.utcnow() - user.event_start_time).total_seconds() / 60
        time_bonus = max(0, 100 - int(time_taken))
        
        total_bonus = probe_bonus + time_bonus
        score_change += total_bonus
        
        logs.append({"status": "Bonus", "msg": f"Base: {config['base_points']}, Speed Bonus: {time_bonus}, Probe Bonus: {probe_bonus}"})

    # Commit Score Updates
    if score_change > 0:
        user.total_score += score_change
    
    # Always commit to save progress (even if score didn't change)
    db.session.commit()

    return jsonify({
        "solved": is_complete,
        "score_added": score_change,
        "tests_passed": passed_count,
        "total_tests": len(test_cases),
        "details": logs
    })
