import subprocess

def start_app():
    try:
        subprocess.Popen(['python3.9', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        print("app.py is running.")
    except Exception as e:
        print("Error starting app.py:", e)

def start_bob():
    try:
        subprocess.Popen(['python3.9', 'Bob.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        print("Bob.py is running.")
    except Exception as e:
        print("Error starting Bob.py:", e)

if __name__ == "__main__":
    try:
        start_app()  # Start app.py without waiting
        start_bob()  # Start Bob.py without waiting

        # Keep run.py running indefinitely
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        # Handle Ctrl+C for graceful shutdown
        pass