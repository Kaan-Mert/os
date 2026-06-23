# core/process.py

class Process:
    """Represents a Process Control Block (PCB) in the Game Console OS simulator."""
    
    def __init__(self, pid, name, arrival_time, burst_time, priority, memory_required):
        # Süreç bilgilerini tutan PCB (Process Control Block) nesnesi oluşturuluyor
        self.pid = pid # Sürecin benzersiz kimlik numarası (Process ID)
        self.name = name # Sürecin adı (Örn: Gamepad Input Handler)
        self.arrival_time = arrival_time # Sürecin hazır kuyruğuna ulaştığı zaman birimi
        self.burst_time = burst_time # Sürecin CPU üzerinde çalışması gereken toplam süre
        self.priority = priority             # Öncelik değeri (1: En yüksek öncelik, 3: En düşük öncelik)
        self.original_priority = priority    # PIP (Priority Inheritance) için orijinal öncelik saklanıyor
        self.memory_required = memory_required  # Sürecin ihtiyaç duyduğu bellek miktarı (MB cinsinden)
        
        # Adres Alanı (Address Space)
        self.page_table = {}                 # Sayfa tablosu (sanal sayfa numarasından fiziksel çerçeveye eşleme)
        self.segment_table = {}              # Segment tablosu (segment adı -> base, limit ve erişim izinleri)
        self.file_handles = []               # Sürecin açık tuttuğu dosyaların listesi
        
        self.reset()

    def reset(self):
        # Simülasyonun her çalıştırılışında süreci başlangıç durumuna getiren sıfırlama metodu
        self.remaining_time = self.burst_time # Sürecin tamamlanması için gereken kalan CPU süresi
        self.state = "READY"                 # Sürecin anlık durumu (READY: hazır, RUNNING: çalışıyor, BLOCKED: blokeli, COMPLETED: bitti)
        self.queue_level = 0                 # MLFQ (Çok Seviyeli Geri Beslemeli Kuyruk) planlaması için anlık kuyruk seviyesi
        self.waiting_time = 0 # Sürecin hazır kuyruğunda beklediği toplam süre
        self.turnaround_time = 0 # Sürecin varışından tamamlanmasına kadar geçen toplam süre (Yaşam Süresi)
        self.start_time = None # Sürecin CPU'da ilk kez çalışmaya başladığı an
        self.end_time = None # Sürecin tamamlandığı an
        self.execution_intervals = []        # Gantt şeması için sürecin hangi zaman aralıklarında çalıştığını tutan liste
        self.blocked_reason = None           # Sürecin hangi I/O veya kilit yüzünden bloke (BLOCKED) olduğunu tutan alan
        self.page_faults_count = 0 # Sürecin çalışırken ürettiği toplam sayfa hatası (Page Fault) sayısı

    def transition_to(self, new_state, reason=None):
        """Manages state transitions and sets blocked reason if applicable."""
        # Sürecin durum geçişlerini kontrol eder ve geçersiz bir duruma geçişi engeller
        valid_states = {"READY", "RUNNING", "BLOCKED", "COMPLETED"}
        if new_state not in valid_states:
            raise ValueError(f"Invalid process state: {new_state}")
        self.state = new_state
        self.blocked_reason = reason if new_state == "BLOCKED" else None

    def add_execution_interval(self, start, end):
        """Helper to append or update execution intervals for plotting."""
        # Gantt şemasını doğru çizebilmek için ardışık çalışma zaman aralıklarını birleştirir veya ekler
        if self.execution_intervals and self.execution_intervals[-1][1] == start:
            self.execution_intervals[-1][1] = end
        else:
            self.execution_intervals.append([start, end])

    def __repr__(self):
        return f"Process(PID={self.pid}, Name='{self.name}', State={self.state}, Prio={self.priority}, Remaining={self.remaining_time})"
