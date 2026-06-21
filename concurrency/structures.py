# concurrency/structures.py

import threading
import time

class ThreadSafeQueue:
    """A thread-safe FIFO queue (Module 11) protected by a Mutex."""
    
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.queue = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def enqueue(self, item, log_callback=None):
        """Adds an item to the queue. Blocks if full."""
        with self.lock:
            while len(self.queue) >= self.capacity:
                if log_callback:
                    log_callback(f"[OS LOG] [KUYRUK] Üretici (Producer) kuyruk dolu olduğu için bekliyor...")
                self.not_full.wait()
            self.queue.append(item)
            if log_callback:
                log_callback(f"[OS LOG] [KUYRUK] Kuyruğa eklendi: {item}. Boyut: {len(self.queue)}/{self.capacity}")
            self.not_empty.notify()

    def dequeue(self, log_callback=None):
        """Removes and returns an item. Blocks if empty."""
        with self.lock:
            while len(self.queue) == 0:
                if log_callback:
                    log_callback(f"[OS LOG] [KUYRUK] Tüketici (Consumer) kuyruk boş olduğu için bekliyor...")
                self.not_empty.wait()
            item = self.queue.pop(0)
            if log_callback:
                log_callback(f"[OS LOG] [KUYRUK] Kuyruktan alındı: {item}. Boyut: {len(self.queue)}/{self.capacity}")
            self.not_full.notify()
            return item

    def qsize(self):
        """Returns the size of the queue safely."""
        with self.lock:
            return len(self.queue)
