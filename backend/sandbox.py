
import docker
import os
import tempfile

try:
    client = docker.from_env()
except Exception as e:
    print(f"WARNING: Docker not found! {e}")
    client = None

# --- HARNESSES ---
PYTHON_HARNESS = """
import sys
if __name__ == "__main__":
    try:
        # Just read from standard in (which we will pipe from a file)
        input_str = sys.stdin.read().strip()
        if not input_str: exit()
        n = int(input_str)
        if 'solve' in globals(): 
            ret = solve(n)
            if ret is not None: print(ret)
        elif 'solution' in globals(): 
            ret = solution(n)
            if ret is not None: print(ret)
    except Exception as e: print(f"Runtime Error: {e}")
"""

C_HARNESS_INT = """
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    printf("%d", solve(n));
    return 0;
}
"""

C_HARNESS_VOID = """
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    solve(n);
    return 0;
}
"""

def run_docker(user_code, input_val, language='python', c_mode='int'):
    if not client: return "Error: Docker client not initialized"

    # 1. SETUP COMMANDS & CODE
    if language == 'python':
        image = "python:3.9-slim"
        filename = "script.py"
        # We use 'sh -c' to pipe the input file into the script
        run_cmd = "sh -c 'python /app/script.py < /app/input.txt'"
        full_code = user_code + "\n\n" + PYTHON_HARNESS
    
    elif language == 'c':
        image = "gcc:latest" 
        filename = "script.c"
        # Compile, then run with input piping
        run_cmd = "sh -c 'gcc /app/script.c -o /app/run -lm && /app/run < /app/input.txt'"
        
        # Add common defines for compatibility
        header = "#include <stdio.h>\n#include <math.h>\n#include <stdbool.h>\n#define TRUE 1\n#define FALSE 0\n#define True 1\n#define False 0\n"

        if c_mode == 'void':
            full_code = header + user_code + "\n\n" + C_HARNESS_VOID
        else:
            full_code = header + user_code + "\n\n" + C_HARNESS_INT

    else:
        return "Error: Unsupported Language"

    # 2. CREATE TEMP FILES (Code AND Input)
    # File A: The Code
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=filename) as temp_script:
        temp_script.write(full_code)
        script_path = temp_script.name

    # File B: The Input
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_input:
        temp_input.write(str(input_val) + "\n") # Ensure newline!
        input_path = temp_input.name

    # 3. FIX PERMISSIONS (Crucial for Ubuntu)
    os.chmod(script_path, 0o644)
    os.chmod(input_path, 0o644)

    try:
        # Pull image if missing
        try:
            client.images.get(image)
        except docker.errors.ImageNotFound:
            print(f"Downloading {image}...")
            client.images.pull(image)

        # 4. RUN CONTAINER
        # We mount BOTH the script and the input file
        container = client.containers.run(
            image=image,
            command=run_cmd,
            volumes={
                script_path: {'bind': f'/app/{filename}', 'mode': 'ro'},
                input_path:  {'bind': '/app/input.txt',  'mode': 'ro'}
            },
            mem_limit="128m",
            network_disabled=True,
            remove=True,     # Auto-delete container when done
            stdout=True, 
            stderr=True
        )

        return container.decode('utf-8').strip()

    except Exception as e:
        print(f"🛑 DOCKER FAILURE: {e}")
        return f"Error: {str(e)}"
    
    finally:
        # Cleanup both temp files
        if os.path.exists(script_path): os.remove(script_path)
        if os.path.exists(input_path):  os.remove(input_path)