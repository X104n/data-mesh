def calculate_average_basic():
    total = 0
    count_success = 0
    count_failure = 0
    
    with open("src/domain_app.csv", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("//"):
                if line == "No product found":
                    count_failure += 1
                else:
                    try:
                        total += float(line)
                        count_success += 1
                    except ValueError:
                        continue
    
    total_attempts = count_success + count_failure
    
    if count_success > 0:
        average = total / count_success
        failure_percentage = (count_failure / total_attempts) * 100 if total_attempts > 0 else 0
        
        print(f"Total attempts: {total_attempts}")
        print(f"Successful retrievals: {count_success}")
        print(f"Failed retrievals: {count_failure}")
        print(f"Failure percentage: {failure_percentage:.2f}%")
        print(f"Average success time: {average:.6f} seconds")
    else:
        print("No successful retrievals found")

if __name__ == "__main__":
    calculate_average_basic()