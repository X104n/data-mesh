import csv
from collections import deque

with open("src/domain_app.csv", "r") as f:
        lines = deque(f, 1_000)
print(lines)
print("==================================")
last_lines = [line.strip().split(";") for line in lines]
print(last_lines)