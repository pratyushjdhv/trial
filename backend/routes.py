from flask import Blueprint, request, jsonify
from model import db, User, UserProgress, ProbeLog
from logic import QUESTIONS
from datetime import datetime, timezone
from sandbox import run_docker

bp = Blueprint('main', __name__)


@bp.route('/register', methods=['POST'])
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


@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Convert the list of objects into a list of JSON dictionaries
    result = [{"id": u.id, "username": u.username,
               "score": u.total_score} for u in users]
    return jsonify(result)


@bp.route('/questions', methods=['GET'])
def get_questions():

    questions = []
    for q_id, config in QUESTIONS.items():
        questions.append({
            "id": q_id,
            "difficulty": config["difficulty"],
            "base_points": config["base_points"],
            "max_probes": config["max_probes"],
            "description": config.get("description", ""),
            "templates": config.get("templates", {})
        })
    return jsonify(questions)


# Probe Route: User tests inputs against logic
@bp.route('/probe', methods=['POST'])
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

    # Check if they have probes left
    if progress.probes_used >= config['max_probes']:
        return jsonify({"error": "No probes left! Try submitting code."}), 403

    # 3. Run YOUR Hidden Logic
    try:
        expected_output = config['func'](val)
        
        # Update counts
        progress.probes_used += 1
        
        # Save to History Log
        new_log = ProbeLog(
            user_id=user_id,
            question_id=question_id,
            input_val=str(val),
            output_val=str(expected_output)
        )
        db.session.add(new_log)

        db.session.commit()

        return jsonify({
            "input": val,
            "output": expected_output,
            "probes_left": config['max_probes'] - progress.probes_used
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Submit Route: Runs User Code in Docker
@bp.route('/submit', methods=['POST'])
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
        
        # Determine C Mode based on expected output type
        c_mode = 'int'
        if isinstance(expected, list):
            c_mode = 'void'
            
        actual = run_docker(user_code, test_val, language, c_mode=c_mode)

        # Normalize for comparison
        def normalize(val):
            s = str(val).strip()
            # Remove brackets if present (Python list string)
            if s.startswith('[') and s.endswith(']'):
                s = s[1:-1]
            # Replace commas with spaces
            s = s.replace(',', ' ')
            # Collapse whitespace
            return " ".join(s.split())

        if normalize(actual) == normalize(expected):
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
            is_solved=False,
            score_earned=0
        )
        db.session.add(progress)

    # Scoring Formula: (10 * tests_passed) + (probes_left * 0.5 * base_points)

    # 1. Calculate Probes Left
    probes_left = max(0, config['max_probes'] - progress.probes_used)
    
    # 2. Calculate Multiplier
    # Logic: Allow full points if 1 probe is used (probes_left = max - 1)
    question = progress.question_id
    probe_multiplier = 0.0
    
    if question in [1, 2]:
        probe_multiplier = probes_left * 0.25
    elif question in [3, 4]:
        probe_multiplier = probes_left * 0.167
    elif question == 5:
        probe_multiplier = probes_left * 0.12
        
    # Ensure it doesn't exceed 1.0 (base points)
    probe_multiplier = min(1.0, probe_multiplier)

    
    # 3. Calculate New Total Score for this Question
    # We use the BEST passed_count achieved so far (or current if better)
    best_passed = max(progress.tests_passed, passed_count)
    
    new_question_score = (10 * best_passed) + (probe_multiplier * config['base_points'])
    new_question_score = int(new_question_score) # Ensure integer
    
    # 4. Calculate Delta (Change in score)
    score_change = new_question_score - progress.score_earned
    
    # 5. Update Progress
    if passed_count > progress.tests_passed:
        progress.tests_passed = passed_count
        progress.solved_at = datetime.now(timezone.utc)
        
    is_complete = (passed_count == len(test_cases))
    if is_complete:
        progress.is_solved = True
        
    # 6. Update User Total Score
    if score_change != 0:
        user.total_score += score_change
        progress.score_earned = new_question_score
        
        logs.append({
            "status": "Bonus", 
            "msg": f"Score Update: {score_change:+d} pts (Total for Q: {new_question_score})"
        })

    db.session.commit()

    return jsonify({
        "solved": is_complete,
        "score_added": score_change,
        "tests_passed": passed_count,
        "total_tests": len(test_cases),
        "details": logs
    })

@bp.route('/get_progress', methods=['POST'])
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

@bp.route('/admin/end_event', methods=['POST'])
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

@bp.route('/admin/reset_event', methods=['POST'])
def reset_event():
    global EVENT_ENDED, TOP_5_WINNERS
    
    # 1. Reset Global State
    EVENT_ENDED = False
    TOP_5_WINNERS = []
    
    # 2. Clear Database
    try:
        db.session.query(ProbeLog).delete()
        db.session.query(UserProgress).delete()
        db.session.query(User).delete()
        db.session.commit()
        return jsonify({"message": "Event reset and database cleared successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/event/status', methods=['GET'])
def event_status():
    return jsonify({
        "ended": EVENT_ENDED,
        "top5": TOP_5_WINNERS
    })
