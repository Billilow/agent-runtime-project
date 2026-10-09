import time

class CircuitBreaker:
    def __init__(self, failure_threshold=3, cooldown_seconds=300):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = {} #{tool_name: how many times it failed consecutively}
        self.opend_until = {} #{tool_name: 차단이 풀리는 시각}

    def is_open(self, tool_name):
        if self.opend_until.get(tool_name, 0) > time.time():
            return True
        return False

    def record_failure(self, tool_name):
        self.failures[tool_name] = self.failures.get(tool_name, 0) + 1
        if self.failures.get(tool_name) >= self.failure_threshold:
            self.opend_until[tool_name] = time.time() + self.cooldown_seconds

    def record_success(self, tool_name):
        self.failures[tool_name] = 0