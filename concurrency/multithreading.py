# concurrency/multithreading.py

import threading
import time

class RaceConditionDemo:
    """Demonstrates Concurrency (Module 8) with Race Conditions vs Correct Synchronization."""
    
    def __init__(self):
        self.counter_unsync = 0
        self.counter_sync = 0
        self.sync_lock = threading.Lock()
        
    def worker_unsync(self, iterations):
        """Worker thread that increments shared counter without synchronization."""
        for _ in range(iterations):
            # Read, increment, write (non-atomic operation)
            temp = self.counter_unsync
            time.sleep(0.000001)  # Force context switch to increase probability of race
            self.counter_unsync = temp + 1

    def worker_sync(self, iterations):
        """Worker thread that increments shared counter with synchronization."""
        for _ in range(iterations):
            with self.sync_lock:
                temp = self.counter_sync
                # Simulating identical delay
                time.sleep(0.000001)
                self.counter_sync = temp + 1

    def run_demo(self, num_threads=4, iterations=500, log_callback=print):
        log_callback(f"[OS LOG] [MULTITHREAD] Yarış Durumu (Race Condition) Deneyi Başlatıldı.")
        log_callback(f"[OS LOG] [MULTITHREAD] Thread Sayısı: {num_threads}, Döngü Sayısı: {iterations}")
        
        # 1. Run Unsynchronized
        self.counter_unsync = 0
        threads_unsync = []
        for i in range(num_threads):
            t = threading.Thread(target=self.worker_unsync, args=(iterations,))
            threads_unsync.append(t)
            
        start_time = time.time()
        for t in threads_unsync:
            t.start()
        for t in threads_unsync:
            t.join()
        end_time_unsync = time.time() - start_time
        
        expected_val = num_threads * iterations
        actual_unsync = self.counter_unsync
        lost_updates = expected_val - actual_unsync
        
        log_callback(f"[OS LOG] [MULTITHREAD] --- SENKRONİZASYONSUZ (RACE CONDITION) ---")
        log_callback(f"[OS LOG] [MULTITHREAD] Beklenen Değer : {expected_val}")
        log_callback(f"[OS LOG] [MULTITHREAD] Gerçekleşen    : {actual_unsync}")
        log_callback(f"[OS LOG] [MULTITHREAD] Kayıp Güncelleme: {lost_updates} (Kayıp Oranı: {lost_updates/expected_val*100:.2f}%)")
        
        # 2. Run Synchronized
        self.counter_sync = 0
        threads_sync = []
        for i in range(num_threads):
            t = threading.Thread(target=self.worker_sync, args=(iterations,))
            threads_sync.append(t)
            
        start_time = time.time()
        for t in threads_sync:
            t.start()
        for t in threads_sync:
            t.join()
        end_time_sync = time.time() - start_time
        
        actual_sync = self.counter_sync
        
        log_callback(f"[OS LOG] [MULTITHREAD] --- SENKRONİZASYONLU (MUTEX LOKLU) ---")
        log_callback(f"[OS LOG] [MULTITHREAD] Beklenen Değer : {expected_val}")
        log_callback(f"[OS LOG] [MULTITHREAD] Gerçekleşen    : {actual_sync}")
        log_callback(f"[OS LOG] [MULTITHREAD] Kayıp Güncelleme: {expected_val - actual_sync} (0% Kayıp)")
        
        return {
            "expected": expected_val,
            "unsync_actual": actual_unsync,
            "unsync_time": end_time_unsync,
            "sync_actual": actual_sync,
            "sync_time": end_time_sync
        }
