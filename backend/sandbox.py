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

def run_docker(user_code, input_val):
    if not client:
        return "Error: Docker client not initialized"

    # 1. Write the student's code to a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_script:
        temp_script.write(user_code)
        temp_path = temp_script.name

    try:
        try:
            client.images.get("python:3.9-slim")
        except docker.errors.ImageNotFound:
            print("Downloading Python image... this may take a moment.")
            client.images.pull("python:3.9-slim")
            
        # 2. Prepare the input (Add newline so input() doesn't hang!)
        input_str = (str(input_val) + "\n").encode('utf-8')

        # 3. Create the container (Don't start it yet)
        container = client.containers.create(
            image="python:3.9-slim",
            command="python /app/script.py",
            volumes={temp_path: {'bind': '/app/script.py', 'mode': 'ro'}},
            mem_limit="128m",
            network_disabled=True,
            stdin_open=True, # Allow sending input
            auto_remove=False
        )

        # 4. Start and Send Input
        container.start()
        
        # This sends the number + Enter key to the running script
        socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
        socket.send(input_str)
        socket.close()

        # 5. Wait for finish and grab logs
        container.wait(timeout=3) # Wait max 3 seconds
        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        container.remove()
        return output.strip()

    except Exception as e:
        # Print the REAL error to your server terminal
        print(f"🛑 DOCKER FAILURE: {e}")
        
        # Cleanup container if it got stuck
        try: container.remove(force=True)
        except: pass
        
        return f"Error: {str(e)}"
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)