
def easy1(n):
    return n * 2

def easy2(n):
    if n%2 == 0:
        return True
    else:
        return False

def med1(n):
    a, b = 0, 1
    lis = []
    for i in range(n):
        lis.append(a)
        a, b = b, a + b
    return lis

def med2(n):
    lis = []
    for i in range(2, n):
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                break
        else:
            lis.append(i)
    return lis

def hard1(n):
    lis = []
    for i in range(n):
        if i % 2 == 0:
            lis.append(i **2 )
        else:
            lis.append(i ** 3)
    return lis


QUESTIONS = {
    1: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "The machine responds predictably. Discover the pattern.",
        "func": easy1,
        # HIDDEN TESTS: The user code must pass ALL of these to win
        "test_cases": [10, 69, -5, 100, 79],
        "templates": {
            "python": "def solve(n):\n    # Write your logic here\n    return n",
            "c": "int solve(int n) {\n    // Write your logic here\n    return n;\n}"
        }
    },
    2: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "The output belongs to one of two possible categories.",
        "func": easy2,
        "test_cases": [-5, 12, 20, 35, 101],
        "templates": {
            "python": "def solve(n):\n    # Write your logic here\n    return value",
            "c": "int solve(int n) {\n    // Write your logic here\n    return value;\n}"
        }
    },
    3: {
        "difficulty": "Medium",
        "base_points": 200,
        "max_probes": 7,
        "description": "The system reveals a growing sequence.",
        "func": med1,
        "test_cases": [5, 10, 15, 20, 25],
        "templates": {
            "python": "def solve(n):\n    # Return a list OR print the sequence\n    return []",
            "c": "void solve(int n) {\n    // Print the sequence separated by spaces\n    // e.g. printf(\"%d \", val);\n}"
        }
    },
    4: {
        "difficulty": "Medium",
        "base_points": 200,
        "max_probes": 7,
        "description": "Only certain numbers are accepted by the system.",
        "func": med2,
        "test_cases": [10, 20, 30, 50, 100],
        "templates": {
            "python": "def solve(n):\n    # Return a list OR print the sequence\n    return []",
            "c": "void solve(int n) {\n    // Print the sequence separated by spaces\n    // e.g. printf(\"%d \", val);\n}"
        }   
    },
    5: {
        "difficulty": "Hard",
        "base_points": 300,
        "max_probes": 10,
        "description": "Position matters. Rules change as the sequence grows.",
        "func": hard1,
        "test_cases": [5, 10, 20, 25, 30],
        "templates": {
            "python": "def solve(n):\n    # Return a list OR print the sequence\n    return []",
            "c": "void solve(int n) {\n    // Print the sequence separated by spaces\n    // e.g. printf(\"%d \", val);\n}"
        }
    }
}

def get_question_config(q_id):
    return QUESTIONS.get(q_id)

def run_host_logic(q_id, user_input):
    config = QUESTIONS.get(q_id)
    if not config:
        return None
    return config["func"](user_input)