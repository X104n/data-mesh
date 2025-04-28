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

def count_domain_messages():
    """
    Analyze the logger file to count specific messages from each domain.
    Prints a summary of message counts grouped by domain.
    """
    # Dictionary to store domain -> message -> count
    domain_messages = {}
    
    try:
        with open("src/platform1/log.csv", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse CSV format with semicolons: date, time;domain;message
                parts = line.split(";")
                if len(parts) < 3:  # Need at least timestamp, domain, message
                    continue
                
                # Extract domain and message from semicolon-separated format
                domain = parts[1]
                message = parts[2]
                
                # Initialize domain dict if not exists
                if domain not in domain_messages:
                    domain_messages[domain] = {}
                
                # Count this message
                if message not in domain_messages[domain]:
                    domain_messages[domain][message] = 1
                else:
                    domain_messages[domain][message] += 1
        
        # Print results
        print("\n=== Domain Message Analysis ===")
        for domain, messages in domain_messages.items():
            print(f"\nDomain: {domain}")
            for message, count in sorted(messages.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {message}: {count} times")
        
        # Print totals per domain
        print("\n=== Total Messages by Domain ===")
        for domain, messages in sorted(domain_messages.items(), 
                                      key=lambda x: sum(x[1].values()), 
                                      reverse=True):
            total = sum(messages.values())
            print(f"{domain}: {total} total messages")
        print ("\n=====================")
    except FileNotFoundError:
        print("Logger file not found. Make sure the path is correct.")
    except Exception as e:
        print(f"Error analyzing log file: {e}")

if __name__ == "__main__":
    domain_server_bool = input("Domain or Plarform? (d/p): ").strip().lower()
    if domain_server_bool == "d":
        calculate_average_basic()
    elif domain_server_bool == "p":
        count_domain_messages()
