
def func1(n):
    return n * 2

def func2(n):
    # Example: (n * last digit)
    # 12 -> 12 * 2 = 24
    return n * (abs(n) % 10)

QUESTIONS = {
    1: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 3,
        "description": "A simple linear warmup.",
        "func": func1,
        # HIDDEN TESTS: The user code must pass ALL of these to win
        "test_cases": [10, 0, -5, 100, 9999] 
    },
    2: {
        "difficulty": "Medium",
        "base_points": 200,
        "max_probes": 3,
        "description": "The tail dictates the magnitude.",
        "func": func2,
        "test_cases": [5, 12, 20, 123, -15]
    }
}

def get_question_config(q_id):
    return QUESTIONS.get(q_id)

def run_host_logic(q_id, user_input):
    config = QUESTIONS.get(q_id)
    if not config:
        return None
    return config["func"](user_input)