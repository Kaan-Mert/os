# concurrency/semaphores.py

import threading
import time
import random

class ProducerConsumerSimulation:
    """Solves the Producer-Consumer problem using Semaphores (Module 10).
    Theme: Gamepad Input Events (Producer) -> Game Engine Processing (Consumer).
    """
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.buffer = []
        self.buffer_lock = threading.Lock() # Buffer listesine erişimi senkronize etmek için Mutex
        
        # Semaforlar (Semaphores)
        self.empty = threading.Semaphore(capacity)  # Boş slot sayısını takip eden semafor (başlangıçta tamamı boş)
        self.full = threading.Semaphore(0)          # Dolu slot sayısını takip eden semafor (başlangıçta hiç dolu yok)
        
        self.running = False
        self.log_messages = []

    def log(self, message, log_callback):
        self.log_messages.append(message)
        log_callback(message)

    def producer_thread(self, log_callback):
        """Generates gamepad inputs (e.g., button presses)."""
        input_buttons = ["A_BUTTON", "B_BUTTON", "X_BUTTON", "Y_BUTTON", "JOYSTICK_MOVE", "TRIGGER_PRESS"]
        event_id = 1
        
        while self.running:
            # Boş slot sayısını 1 azaltıyoruz (Eğer boş yer yoksa üretici thread burada BLOKE olur)
            self.empty.acquire()
            
            # Kritik bölgeye girmeden önce Mutex kilidini alıyoruz
            self.buffer_lock.acquire()
            event = f"{random.choice(input_buttons)}#{event_id}"
            self.buffer.append(event)
            self.log(f"[OS LOG] [SEMAFOR] [Gamepad] Buton giriş olayı üretildi: {event}. Buffer: {len(self.buffer)}/{self.capacity}", log_callback)
            event_id += 1
            # Kritik bölgeden çıkarken Mutex kilidini bırakıyoruz
            self.buffer_lock.release()
                
            # Dolu slot sayısını 1 artırıyoruz (Bekleyen tüketici varsa onu uyandırır)
            self.full.release()
            
            # Rastgele bir gecikme ekliyoruz
            time.sleep(random.uniform(0.1, 0.4))

    def consumer_thread(self, log_callback):
        """Game Engine consumes gamepad inputs and renders corresponding frames."""
        while self.running:
            # Dolu slot sayısını 1 azaltıyoruz (Eğer dolu yer yoksa tüketici thread burada BLOKE olur)
            self.full.acquire()
            if not self.running:
                break
                
            # Kritik bölgeye girmeden önce Mutex kilidini alıyoruz
            self.buffer_lock.acquire()
            event = self.buffer.pop(0)
            self.log(f"[OS LOG] [SEMAFOR] [Oyun Motoru] Giriş olayı işleniyor: {event}. Buffer: {len(self.buffer)}/{self.capacity}", log_callback)
            # Kritik bölgeden çıkarken Mutex kilidini bırakıyoruz
            self.buffer_lock.release()
            
            # Boş slot sayısını 1 artırıyoruz (Bekleyen üretici varsa onu uyandırır)
            self.empty.release()
            
            # İşleme süresi
            time.sleep(random.uniform(0.2, 0.5))

    def run(self, duration=3.0, log_callback=print):
        self.running = True
        self.buffer.clear()
        
        # Semaforları başlangıç durumuna sıfırlıyoruz
        self.empty = threading.Semaphore(self.capacity)
        self.full = threading.Semaphore(0)
        
        p = threading.Thread(target=self.producer_thread, args=(log_callback,))
        c = threading.Thread(target=self.consumer_thread, args=(log_callback,))
        
        self.log(f"[OS LOG] [SEMAFOR] Üretici-Tüketici (Producer-Consumer) simülasyonu başlatıldı (Süre: {duration}sn)...", log_callback)
        p.start()
        c.start()
        
        time.sleep(duration)
        
        # Kapatma sinyali
        self.running = False
        # Blokede kalmış threadler varsa uyansınlar diye semaforları serbest bırakıyoruz
        self.full.release()
        self.empty.release()
        
        p.join()
        c.join()
        
        self.log("[OS LOG] [SEMAFOR] Simülasyon başarıyla tamamlandı.", log_callback)
