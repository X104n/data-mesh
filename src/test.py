def read_last_n_lines(f, n=1):
        f.seek(0, 2)  # Go to the end of the file
        size = f.tell()
        
        if size == 0:  # Empty file
            return []
            
        # Start from the end
        position = size - 1
        newlines_found = 0
        
        # Find the start of the nth-to-last line
        while position >= 0:
            f.seek(position)
            char = f.read(1)
            if char == b'\n':
                newlines_found += 1
                if newlines_found == n and position > 0:
                    # Found the nth newline from the end
                    position += 1
                    break
            position -= 1
            
        # If we went all the way to the beginning, start from there
        if position < 0:
            position = 0
            
        # Read the last n lines
        f.seek(position)
        last_chunk = f.read().decode('utf-8')
        last_lines = last_chunk.splitlines()
        
        # If we have more lines than requested, return only the last n
        if len(last_lines) > n:
            return last_lines[-n:]
        return last_lines


file = open("test_log.csv", "rb")
# Example usage
last_2_lines = read_last_n_lines(file, 2)
print("Last 2 lines:", last_2_lines)

last_3_lines = read_last_n_lines(file, 3)
print("Last 3 lines:", last_3_lines)

last_lines = read_last_n_lines(file, 10)
print(f"Last lines read: {len(last_lines)}")
last_lines = [line.strip().split(";") for line in last_lines if line.strip()]
ip = "ip"
valid_address = False

for line in last_lines:
    # Printing what number of lines we are checking
    print(f"Checking line: {line}")
    if line[2] == ip:
        if line[3] == "bruh":
            valid_address = True

print(f"Valid address: {valid_address}")