
def easy1(n):
    return n * 2

def easy2(n):
    if n%2 == 0:
        return True
    else:
        return False
    
def easy3(n):
    n = abs(n)
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total

def easy4(n):
    if n == 0:
        return 1

    n = abs(n)
    count = 0
    while n > 0:
        count += 1
        n //= 10
    return count



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

def med3(n):
    total = 0
    lis = []
    for i in range(1, n + 1):
        total += i
        lis.append(total)
    return lis


def hard1(n):
    lis = []
    for i in range(n):
        if i % 2 == 0:
            lis.append(i **2 )
        else:
            lis.append(i ** 3)
    return lis

def hard2(n):
    lis = [1]
    value = 1
    for i in range(1, n):
        if i % 2 == 1:
            value *= 2
        else:
            value += i
        lis.append(value)
    return lis

def hard3(n):
    lis = []
    for i in range(1, n + 1):
        temp = i
        has_five = False

        while temp > 0:
            if temp % 10 == 5:
                has_five = True
                break
            temp //= 10

        if has_five:
            lis.append(-i)
        else:
            lis.append(i)

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
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "The system reacts to the internal structure of the multi-digit numbers.(try number like 123)",
        "func": easy3,
        "test_cases": [-567, 123, 101, 69, 202],
        "templates": {
            "python": "def solve(n):\n    # Write your logic here\n    return value",
            "c": "int solve(int n) {\n    // Write your logic here\n    return value;\n}"
        }
    },
    4: {
        "difficulty": "Easy",
        "base_points": 100,
        "max_probes": 5,
        "description": "The system reacts to the internal structure of the multi-digit numbers.(try number like 12345)",
        "func": easy4,
        "test_cases": [-56789, 1009, 101, 69, 0000],
        "templates": {
            "python": "def solve(n):\n    # Write your logic here\n    return value",
            "c": "int solve(int n) {\n    // Write your logic here\n    return value;\n}"
        }
    },
    5: {
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
    6: {
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
    7: {
        "difficulty": "Medium",
        "base_points": 200,
        "max_probes": 7,
        "description": "Observe the output carefully; it keeps building up.",
        "func": med3,
        "test_cases": [10, 2, 6, 12, 8],
        "templates": {
            "python": "def solve(n):\n    # Return a list OR print the sequence\n    return []",
            "c": "void solve(int n) {\n    // Print the sequence separated by spaces\n    // e.g. printf(\"%d \", val);\n}"
        }   
    },

    8: {
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
    },
    9: {
        "difficulty": "Hard",
        "base_points": 300,
        "max_probes": 10,
        "description": "Past influences the future.",
        "func": hard2,
        "test_cases": [5, 10, 8, 3, 0],
        "templates": {
            "python": "def solve(n):\n    # Return a list OR print the sequence\n    return []",
            "c": "void solve(int n) {\n    // Print the sequence separated by spaces\n    // e.g. printf(\"%d \", val);\n}"
        }
    },
    10: {
        "difficulty": "Hard",
        "base_points": 300,
        "max_probes": 10,
        "description": "Certain inputs cause err in system behavior.",
        "func": hard3,
        "test_cases": [10, 15, 20, 55, 100],
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

def tie_breaker_logic(n):
    # Logic: Return the sum of even digits 
    # 1234 -> (2+4) = 6
    n = abs(n)
    total = 0
    while n > 0:
        digit = n % 10
        if digit % 2 == 0:
            total += digit
        n //= 10
    return total

TIE_BREAKER_QUESTIONS = {
    101: {
        "difficulty": "Tie Breaker",
        "base_points": 500,
        "max_probes": 5,
        "description": "Final Showdown: pay close attention to the input and outputs. (try numbers like 123456 or larger)",
        "func": tie_breaker_logic,
        "test_cases": [1234, 2468, 1357, 1020, 888],
        "templates": {
            "python": "def solve(n):\n    # Write your logic here\n    return 0",
            "c": "int solve(int n) {\n    // Write your logic here\n    return 0;\n}"
        }
    }
}
