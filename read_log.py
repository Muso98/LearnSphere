import os

log_file = r'm:\LearnSphere\error_log.txt'
if os.path.exists(log_file):
    try:
        with open(log_file, 'r', encoding='utf-16') as f:
            content = f.read()
            print("--- BEGIN ERROR LOG ---")
            print(content[-2000:]) # Print last 2000 chars
            print("--- END ERROR LOG ---")
    except Exception as e:
        print(f"Error reading utf-16: {e}")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("--- BEGIN ERROR LOG (UTF-8) ---")
                print(content[-2000:])
                print("--- END ERROR LOG ---")
        except Exception as e2:
             print(f"Error reading utf-8: {e2}")
else:
    print("Log file not found")
