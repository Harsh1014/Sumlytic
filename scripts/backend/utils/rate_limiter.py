import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    def allow_request(self, client_id):
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the time window
        while client_requests and client_requests[0] <= now - self.time_window:
            client_requests.popleft()
        
        # Check if client has exceeded the limit
        if len(client_requests) >= self.max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_id):
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        while client_requests and client_requests[0] <= now - self.time_window:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))
    
    def get_reset_time(self, client_id):
        client_requests = self.requests[client_id]
        if not client_requests:
            return 0
        
        return client_requests[0] + self.time_window
