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
        self.buffer_lock = threading.Lock()
        
        # Semaphores
        self.empty = threading.Semaphore(capacity)  # Tracks empty slots
        self.full = threading.Semaphore(0)          # Tracks filled slots
        
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
            # Wait for an empty slot in buffer
            self.empty.acquire()
            
            # Lock the buffer to add item
            with self.buffer_lock:
                event = f"{random.choice(input_buttons)}#{event_id}"
                self.buffer.append(event)
                self.log(f"[OS LOG] [SEMAFOR] [Gamepad] Buton giriş olayı üretildi: {event}. Buffer: {len(self.buffer)}/{self.capacity}", log_callback)
                event_id += 1
                
            # Signal that buffer has a new item
            self.full.release()
            
            # Simulate random delay between gamepad events
            time.sleep(random.uniform(0.1, 0.4))

    def consumer_thread(self, log_callback):
        """Game Engine consumes gamepad inputs and renders corresponding frames."""
        while self.running:
            # Wait for a filled slot in buffer
            self.full.acquire()
            if not self.running:
                break
                
            # Lock the buffer to remove item
            with self.buffer_lock:
                event = self.buffer.pop(0)
                self.log(f"[OS LOG] [SEMAFOR] [Oyun Motoru] Giriş olayı işleniyor: {event}. Buffer: {len(self.buffer)}/{self.capacity}", log_callback)
                
            # Signal that buffer has an empty slot
            self.empty.release()
            
            # Simulate rendering / logic update time
            time.sleep(random.uniform(0.2, 0.5))

    def run(self, duration=3.0, log_callback=print):
        self.running = True
        self.buffer.clear()
        
        # Re-initialize semaphores to reset states
        self.empty = threading.Semaphore(self.capacity)
        self.full = threading.Semaphore(0)
        
        p = threading.Thread(target=self.producer_thread, args=(log_callback,))
        c = threading.Thread(target=self.consumer_thread, args=(log_callback,))
        
        self.log(f"[OS LOG] [SEMAFOR] Üretici-Tüketici (Producer-Consumer) simülasyonu başlatıldı (Süre: {duration}sn)...", log_callback)
        p.start()
        c.start()
        
        time.sleep(duration)
        
        # Shutdown
        self.running = False
        # Release semaphore to wake up waiting consumer if it's blocked
        self.full.release()
        self.empty.release()
        
        p.join()
        c.join()
        
        self.log("[OS LOG] [SEMAFOR] Simülasyon başarıyla tamamlandı.", log_callback)
