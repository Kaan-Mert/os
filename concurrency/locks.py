# concurrency/locks.py

from collections import deque

class Resource:
    """Represents a shared hardware lock (e.g., Disk Lock, GPU Lock) in the simulator.
    Supports Priority Inheritance Protocol (PIP) to prevent priority inversion.
    """
    def __init__(self, name):
        self.name = name # Kaynağın adı (Örn: Disk Kilidi)
        self.owner = None # Kaynağı şu anda elinde tutan süreç (Process)
        self.waiting_queue = deque() # Kaynak meşgulken bekleyen süreçlerin kuyruğu
        
    def acquire(self, process, current_time, log_callback):
        """Attempts to lock the resource. Returns True if successful, False if blocked."""
        # Eğer kaynak boşsa, talep eden sürece kaynağı tahsis ediyoruz
        if self.owner is None:
            self.owner = process
            log_callback(f"[OS LOG] [KAYNAK] {process.name} (PID: {process.pid}), '{self.name}' kaynağını kilitledi.")
            return True
        else:
            # Kaynak meşgulse, süreci bekleyenler kuyruğuna alıp BLOCKED durumuna geçiriyoruz
            self.waiting_queue.append(process)
            process.transition_to("BLOCKED", self.name)
            log_callback(f"[OS LOG] [KAYNAK BİRLEŞİMİ] {process.name} (PID: {process.pid}), '{self.name}' kaynağı meşgul olduğu için BLOCKED durumuna geçti. (Mevcut Sahibi: {self.owner.name})")
            return False
            
    def release(self, current_time, log_callback):
        """Releases the lock. Returns the next process to acquire it, or None."""
        if self.owner is None:
            return None
        old_owner = self.owner
        log_callback(f"[OS LOG] [KAYNAK] {old_owner.name} (PID: {old_owner.pid}), '{self.name}' kaynağını serbest bıraktı.")
        self.owner = None
        
        # Bekleyen bir süreç varsa, kaynağı doğrudan ona devredip READY durumuna geçiriyoruz
        if self.waiting_queue:
            next_proc = self.waiting_queue.popleft()
            next_proc.transition_to("READY")
            self.owner = next_proc
            log_callback(f"[OS LOG] [KAYNAK DEVİR] '{self.name}' kaynağı bekleyen {next_proc.name} (PID: {next_proc.pid}) sürecine devredildi, durum: READY.")
            return next_proc
        return None


class Mutex:
    """A standard thread-safe mutual exclusion lock (Mutex) for Module 9."""
    def __init__(self, name="Generic Mutex"):
        self.name = name # Kilidin adı
        self.locked = False # Kilidin kilitli olup olmadığı bayrağı
        self.owner_thread = None # Kilidi elinde tutan iş parçacığı (Thread ID)
        self.waiting_threads = deque() # Kilit açılana kadar bekleyen iş parçacıklarının kuyruğu

    def lock(self, thread_id, log_callback):
        """Acquires the lock for a thread."""
        # Kilit boşta ise, talep eden thread için kilidi kapatıyoruz (Atomic kilit edinimi)
        if not self.locked:
            self.locked = True
            self.owner_thread = thread_id
            log_callback(f"[OS LOG] [LOCK] Thread {thread_id} acquired Mutex '{self.name}'.")
            return True
        else:
            # Kilit doluysa, thread'i bekleyenler kuyruğuna alıp bloke ediyoruz
            self.waiting_threads.append(thread_id)
            log_callback(f"[OS LOG] [LOCK] Thread {thread_id} blocked waiting for Mutex '{self.name}'.")
            return False

    def unlock(self, log_callback):
        """Releases the lock and wakes up the next waiting thread."""
        if not self.locked:
            return None
        log_callback(f"[OS LOG] [LOCK] Mutex '{self.name}' released.")
        self.locked = False
        self.owner_thread = None
        # Kuyrukta bekleyen başka bir thread varsa, kilidi doğrudan ona devrediyoruz
        if self.waiting_threads:
            next_thread = self.waiting_threads.popleft()
            self.locked = True
            self.owner_thread = next_thread
            log_callback(f"[OS LOG] [LOCK] Mutex '{self.name}' handed over to Thread {next_thread}.")
            return next_thread
        return None
