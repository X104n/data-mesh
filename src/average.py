def calculate_average_basic():
    total = 0
    count = 0
    
    with open("src/domain_app.csv", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("//"):  # Skip comments and empty lines
                try:
                    total += float(line)
                    count += 1
                except ValueError:
                    # Skip non-numeric lines
                    continue
    
    if count > 0:
        average = total / count
        print(f"Average: {average:.6f} seconds")
    else:
        print("No valid data found")

if __name__ == "__main__":
    calculate_average_basic()