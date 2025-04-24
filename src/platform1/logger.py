class Logger:

    def __init__(self, name: str):
        self.name = name
        self.domains = []

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def error(self, message: str):
        print(f"[{self.name} ERROR] {message}")

    def info(self, message: str):
        print(f"[{self.name} INFO] {message}")