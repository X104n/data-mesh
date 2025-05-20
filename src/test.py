import time

def _read_last_n_lines(f, n=1):
    size = f.tell()
    if size == 0:
        return []

    position = size - 1
    newlines_found = 0
    
    while position >= 0:
        f.seek(position)
        char = f.read(1)
        if char.decode() == '\n':
            newlines_found += 1
            if newlines_found == n and position > 0:
                position += 1
                break
        position -= 1
        
    if position < 0:
        position = 0

    f.seek(position)
    last_chunk = f.read()
    text = last_chunk.decode()
    last_lines = text.splitlines()

    if len(last_lines) > n:
        return last_lines[-n:]
    return last_lines

file = open("test_log.csv", "a+b")
start = time.time()
# Example usage
last_2_lines = _read_last_n_lines(file, 2)
print("Last 2 lines:", last_2_lines)

last_3_lines = _read_last_n_lines(file, 3)
print("Last 3 lines:", last_3_lines)

last_lines = _read_last_n_lines(file, 10)
print(f"Last lines read: {len(last_lines)}")
last_lines = [line.strip().split(";") for line in last_lines if line.strip()]
valid_address = False        
for line in last_lines:
    if len(line) >= 3 and line[1] == "addr_to_check":
        if line[2] == "Hello":
            valid_address = True

print(f"Valid address: {valid_address}")

end = time.time()
print(f"Elapsed time: {end - start} seconds")
file.close()