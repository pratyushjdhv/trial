# sandbox.py (Optimized)
# import docker
# import os
# import tempfile

# try:
#     client = docker.from_env()
# except:
#     print("WARNING: Docker not found! Submissions will fail.")
#     client = None

# def run_docker(user_code, input_val):
#     if not client:
#         return "Error: Docker not available"

#     # Create the temp file with their code
#     with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_script:
#         temp_script.write(user_code)
#         temp_path = temp_script.name

#     try:
#         # FIX: Append a newline character (\n)
#         # Python's input() waits for a newline, otherwise it hangs forever!
#         input_str = (str(input_val) + "\n").encode('utf-8') 

#         container = client.containers.create(
#             image="python:3.9-slim",
#             command="python /app/script.py", 
#             volumes={temp_path: {'bind': '/app/script.py', 'mode': 'ro'}},
#             mem_limit="128m",
#             nano_cpus=500000000,
#             network_disabled=True,
#             stdin_open=True, 
#             auto_remove=False 
#         )

#         # Start container
#         container.start()

#         # Send the input (Safe from injection!)
#         # This simulates typing the number and hitting Enter
#         socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
#         socket.send(input_str)
#         socket.close()

#         # Wait for it to finish
#         container.wait(timeout=2) 
        
#         # Get Output
#         output = container.logs(stdout=True, stderr=True).decode('utf-8')
#         container.remove()
        
#         return output.strip()

#     except Exception as e:
#         # Clean up if it crashes
#         try: container.remove(force=True)
#         except: pass
#         return "Error: Runtime Error or Timeout"
    
#     finally:
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

# ----------------------------------------------------------

import docker
import os
import tempfile

try:
    client = docker.from_env()
except:
    print("WARNING: Docker not found!")
    client = None

# --- NEW: The Wrapper Script ---
# This code is appended to the student's code inside the container.
# It reads input, calls their 'solve' function, and prints the result.
EXECUTION_HARNESS = """
import sys

if __name__ == "__main__":
    try:
        # Read input from Stdin (piped from Docker)
        input_str = sys.stdin.read().strip()
        if not input_str: exit()
        
        # Parse Input (Assume integer for now)
        n = int(input_str)
        
        # Check if they defined 'solve' or 'solution'
        if 'solve' in globals():
            print(solve(n))
        elif 'solution' in globals():
            print(solution(n))
        else:
            # Fallback: Maybe they wrote a script that just prints?
            pass 
            
    except Exception as e:
        print(f"Runtime Error: {e}")
"""

def run_docker(user_code, input_val):
    if not client: return "Error: Docker client not initialized"

    # 1. Combine User Code + Harness
    # We add the harness at the end so it can access the user's functions
    full_script = user_code + "\n\n" + EXECUTION_HARNESS

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_script:
        temp_script.write(full_script)
        temp_path = temp_script.name

    try:
        # Ensure image exists
        try:
            client.images.get("python:3.9-slim")
        except docker.errors.ImageNotFound:
            print("Downloading Python image...")
            client.images.pull("python:3.9-slim")
            
        # 2. Prepare Input
        input_str = (str(input_val) + "\n").encode('utf-8')

        # 3. Create Container
        container = client.containers.create(
            image="python:3.9-slim",
            command="python /app/script.py",
            volumes={temp_path: {'bind': '/app/script.py', 'mode': 'ro'}},
            mem_limit="128m",
            network_disabled=True,
            stdin_open=True,
            auto_remove=False
        )

        container.start()
        
        # Send Input
        socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
        socket.send(input_str)
        socket.close()

        container.wait(timeout=2)
        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        container.remove()
        
        return output.strip()

    except Exception as e:
        print(f"🛑 DOCKER FAILURE: {e}")
        try: container.remove(force=True)
        except: pass
        return f"Error: {str(e)}"
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)