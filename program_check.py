import subprocess

def program_check(path, input_data):
    try:
        result = subprocess.run(['python3', path], input=input_data, text=True, capture_output=True, timeout=5)
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Timeout"
    except subprocess.CalledProcessError as e:
        return e.stderr
