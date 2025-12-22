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
        
        # Update counts
        progress.probes_used += 1
        
        # --- NEW: Save to History Log ---
        new_log = ProbeLog(
            user_id=user_id,
            question_id=question_id,
            input_val=str(val),
            output_val=str(expected_output)
        )
        db.session.add(new_log)
        # --------------------------------

        db.session.commit()

        return jsonify({
            "input": val,
            "output": expected_output,
            "probes_left": config['max_probes'] - progress.probes_used
        })
    except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- NEW: SUBMIT ROUTE (Runs User Code in Docker) ---
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    user_code = data.get('code')
    language = data.get('language', 'python')

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
        actual = run_docker(user_code, test_val, language)

        if str(actual).strip() == str(expected).strip():
            passed_count += 1
            logs.append({"input": test_val, "status": "Pass"})
        else:
            logs.append({"input": test_val, "status": "Fail", "got": actual, "expected": "Hidden"})

    # 3. Database & Scoring Logic
    user = User.query.get(user_id)
    progress = UserProgress.query.filter_by(user_id=user_id, question_id=question_id).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id, 
            question_id=question_id, 
            probes_used=0, 
            tests_passed=0,
            is_solved=False
        )
        db.session.add(progress)

    score_change = 0
    
    # CHECK: Did they improve their previous best?
    # We update 'solved_at' ONLY if they improve their score.
    # This acts as the tie-breaker: "Who reached this score FIRST?"
    if passed_count > progress.tests_passed:
        # Partial Scoring: 10 pts per new test passed
        new_tests = passed_count - progress.tests_passed
        points_per_test = 10 
        
        score_change += (new_tests * points_per_test)
        
        # Update Record
        progress.tests_passed = passed_count
        progress.solved_at = datetime.utcnow() # Tie-breaker timestamp

    # CHECK: Did they solve ALL tests? (Completion Bonus)
    is_complete = (passed_count == len(test_cases))
    
    if is_complete and not progress.is_solved:
        progress.is_solved = True
        
        # --- BONUS SCORING (Updated) ---
        # 1. Base Points (Difficulty)
        score_change += config['base_points']

        # 2. Probe Bonus (Reward for efficiency)
        # 50 points per unused probe
        probes_left = max(0, config['max_probes'] - progress.probes_used)
        probe_bonus = probes_left * 50
        
        # 3. Time Bonus -> REMOVED per your request
        # We rely on 'solved_at' for tie-breaking instead.
        
        score_change += probe_bonus
        
        logs.append({
            "status": "Bonus", 
            "msg": f"Base: {config['base_points']}, Probe Bonus: {probe_bonus}"
        })

    # Commit Score Updates
    if score_change > 0:
        user.total_score += score_change
    
    db.session.commit()

    return jsonify({
        "solved": is_complete,
        "score_added": score_change,
        "tests_passed": passed_count,
        "total_tests": len(test_cases),
        "details": logs
    })

@app.route('/get_progress', methods=['POST'])
def get_progress():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    
    # 1. Get attempts count
    progress = UserProgress.query.filter_by(user_id=user_id, question_id=question_id).first()
    probes_used = progress.probes_used if progress else 0
    
    # 2. Get Probe History (Newest first)
    logs = ProbeLog.query.filter_by(user_id=user_id, question_id=question_id).order_by(ProbeLog.timestamp.desc()).all()
    
    history = [{"in": log.input_val, "out": log.output_val} for log in logs]
    
    return jsonify({
        "probes_used": probes_used,
        "history": history
    })


# Global State for Event Status
EVENT_ENDED = False
TOP_5_WINNERS = []

@app.route('/admin/end_event', methods=['POST'])
def end_event():
    global EVENT_ENDED, TOP_5_WINNERS
    
    # 1. Get all users ordered by total score (descending)
    users = User.query.order_by(User.total_score.desc()).all()
    
    # 2. Prepare Leaderboard Data
    leaderboard = []
    for u in users:
        leaderboard.append({
            "id": u.id,
            "username": u.username,
            "total_score": u.total_score
        })
    
    # 3. Get Top 3
    top3 = leaderboard[:3]
    
    # 4. Set Global State
    EVENT_ENDED = True
    TOP_5_WINNERS = leaderboard[:5] # Store Top 5 for the modal
    
    return jsonify({
        "leaderboard": leaderboard,
        "top3": top3
    })

@app.route('/event/status', methods=['GET'])
def event_status():
    return jsonify({
        "ended": EVENT_ENDED,
        "top5": TOP_5_WINNERS
    })
