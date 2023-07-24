import threading

class IPTracker:
    def __init__(self):
        self.seen_ips = set()
        self.lock = threading.Lock()

    def add_ip(self, ip):
        with self.lock:
            self.seen_ips.add(ip)

    def has_seen_ip(self, ip):
        with self.lock:
            return ip in self.seen_ips