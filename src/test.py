import csv
from collections import deque

with open("src/platform1/log.csv", "r") as f:
        lines = deque(f, 2)
print(lines)
print("==================================")
last_lines = [line.strip().split(";") for line in lines]
print(last_lines)