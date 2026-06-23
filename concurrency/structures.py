# concurrency/structures.py

import threading
import time

class ThreadSafeQueue:
    """A thread-safe FIFO queue (Module 11) protected by a Mutex."""
    
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.queue = []
        self.lock = threading.Lock() # Kuyruk işlemlerini atomik kılmak için Mutex kilidi
        self.not_full = threading.Condition(self.lock) # Kuyruk doluyken bekleten koşul değişkeni
        self.not_empty = threading.Condition(self.lock) # Kuyruk boşken bekleten koşul değişkeni

    def enqueue(self, item, log_callback=None):
        """Adds an item to the queue. Blocks if full."""
        # Kuyruğa ekleme yaparken kilidi alıyoruz
        self.lock.acquire()
        
        # Kuyruk kapasitesi dolu olduğu sürece bekliyoruz (Spurious wakeup durumlarına karşı while kullanılır)
        while len(self.queue) >= self.capacity:
            if log_callback:
                log_callback(f"[OS LOG] [KUYRUK] Üretici (Producer) kuyruk dolu olduğu için bekliyor...")
            self.not_full.wait() # not_full koşulu üzerinde bloke olur, bu esnada geçici olarak kilidi bırakır
            
        self.queue.append(item)
        if log_callback:
            log_callback(f"[OS LOG] [KUYRUK] Kuyruğa eklendi: {item}. Boyut: {len(self.queue)}/{self.capacity}")
            
        # Kuyruğun artık boş olmadığını (en az 1 eleman olduğunu) tüketiciye bildiriyoruz
        self.not_empty.notify()
        # İşimiz bittiğinde kilidi bırakıyoruz
        self.lock.release()

    def dequeue(self, log_callback=None):
        """Removes and returns an item. Blocks if empty."""
        # Kuyruktan veri çekerken kilidi alıyoruz
        self.lock.acquire()
        
        # Kuyruk boş olduğu sürece bekliyoruz
        while len(self.queue) == 0:
            if log_callback:
                log_callback(f"[OS LOG] [KUYRUK] Tüketici (Consumer) kuyruk boş olduğu için bekliyor...")
            self.not_empty.wait() # not_empty koşulu üzerinde bloke olur, kilidi geçici olarak bırakır
            
        item = self.queue.pop(0)
        if log_callback:
            log_callback(f"[OS LOG] [KUYRUK] Kuyruktan alındı: {item}. Boyut: {len(self.queue)}/{self.capacity}")
            
        # Kuyrukta yer açıldığını üreticiye bildiriyoruz
        self.not_full.notify()
        # Kilidi bırakıyoruz
        self.lock.release()
        return item

    def qsize(self):
        """Returns the size of the queue safely."""
        self.lock.acquire()
        size = len(self.queue)
        self.lock.release()
        return size
