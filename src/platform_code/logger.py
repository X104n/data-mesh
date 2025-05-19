import datetime

def reset_log_file():
    try:
        with open("src/platform_code/log.csv", 'w') as log_file:
            log_file.write("")
    except Exception as e:
        print(f"Error resetting log file: {e}")

def log(message, domain):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        with open("src/platform_code/log.csv", 'a') as log_file:
            log_file.write(f"{timestamp};{domain};{message}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")