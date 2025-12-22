
def func1(n):
    return n * 2

def func2(n):
    return n * n

def func3(n):
    a, b = 0, 1
    lis = []
    for i in range(n):
        lis.append(a)
        a, b = b, a + b
    return a
    


QUESTIONS = {
    1: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "A simple linear warmup.",
        "func": func1,
        # HIDDEN TESTS: The user code must pass ALL of these to win
        "test_cases": [10, 0, -5, 100, 79] 
    },
    2: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "A single variable quadratic function.",
        "func": func2,
        "test_cases": [-5, 12, 20, 0, 101]
    },
    3: {
        "difficulty": "Medium",
        "base_points": 200,
        "max_probes": 7,
        "description": "Fibonacci sequence calculation.",
        "func": func3,
        "test_cases": [5, 10, 15, 20, 25]
    }
}

def get_question_config(q_id):
    return QUESTIONS.get(q_id)

def run_host_logic(q_id, user_input):
    config = QUESTIONS.get(q_id)
    if not config:
        return None
    return config["func"](user_input)