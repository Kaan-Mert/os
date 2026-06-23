from core.process import Process
from memory.translation import MemoryManager

def simulate_io_blocking_scenario(log_callback=print):
    """Slayt 4: Çapraz Bileşen Etkileşimi (Disk I/O Blocking) Simülasyonu"""
    log_callback("\n[OS LOG] === ÇAPRAZ BİLEŞEN ETKİLEŞİMİ (DISK I/O) DENEYİ ===")
    
    p_engine = Process(101, "Game Engine Render", arrival_time=0, burst_time=5, priority=1, memory_required=128)
    p_input = Process(102, "Gamepad Input", arrival_time=0, burst_time=3, priority=1, memory_required=16)
    
    # Oyun Motoru CPU üzerinde çalıştırılmaya başlanıyor
    p_engine.transition_to("RUNNING")
    log_callback(f"[OS LOG] [CPU] '{p_engine.name}' (PID: {p_engine.pid}) çalışıyor. Yeni harita kaplamasına (texture) ihtiyaç duydu.")
    
    # Oyun Motoru diskten veri beklediği için BLOCKED durumuna geçiriliyor ve CPU boşa çıkarılıyor
    p_engine.transition_to("BLOCKED", reason="Disk I/O")
    log_callback(f"[OS LOG] [I/O İSTEĞİ] '{p_engine.name}' diskten veri beklediği için RUNNING durumundan BLOCKED durumuna geçirildi ve CPU'dan çekildi.")
    
    # CPU boşta kalmasın diye hazır bekleyen Gamepad Input süreci CPU'ya yükleniyor (Bağlam Değişimi)
    p_input.transition_to("RUNNING")
    log_callback(f"[OS LOG] [BAĞLAM DEĞİŞİMİ] CPU boş kalmamak için anında '{p_input.name}' sürecine tahsis edildi. Oyuncu tepkiselliği (stutter olmadan) korundu.")
    
    # Disk veriyi getirdiğinde (kesme/interrupt alındığında) bloke süreç hazır durumuna geri dönüyor
    p_engine.transition_to("READY")
    p_input.transition_to("READY")
    log_callback(f"[OS LOG] [I/O TAMAMLANDI] Disk donanımı veriyi getirdi (Kesme/Interrupt). '{p_engine.name}' tekrar READY kuyruğuna alındı ve çalışmaya hazır.")
    log_callback("[OS LOG] DENEY BAŞARILI: I/O işlemi sırasında CPU %100 verimle kullanıldı.\n")

def simulate_oom_killer_scenario(log_callback=print):
    """Slayt 6: Hata Senaryosu (OOM - Out of Memory Killer) Simülasyonu"""
    log_callback("\n[OS LOG] === HATA SENARYOSU: OOM (OUT OF MEMORY) KILLER DENEYİ ===")
    
    mem_manager = MemoryManager(total_memory=512)
    
    p_game = Process(201, "AAA Game Main Process", 0, 10, priority=1, memory_required=300)
    p_audio = Process(202, "Audio System", 0, 10, priority=2, memory_required=100)
    p_bg = Process(203, "Background Download", 0, 10, priority=3, memory_required=112)
    
    mem_manager.allocate(p_game, log_callback)
    mem_manager.allocate(p_audio, log_callback)
    mem_manager.allocate(p_bg, log_callback)
    
    log_callback(f"[OS LOG] [BELLEK] Sistem belleği (512 MB) tamamen doldu. Boş alan: {mem_manager.get_free_memory()} MB")
    
    p_critical = Process(204, "Critical System Update", 1, 5, priority=1, memory_required=64)
    log_callback(f"[OS LOG] [SİSTEM UYARISI] Yüksek öncelikli '{p_critical.name}' (Gereken: {p_critical.memory_required} MB) sisteme girmeye çalışıyor!")
    
    success = mem_manager.allocate(p_critical, log_callback)
    if not success:
        log_callback("[OS LOG] [OOM DURUMU] Yeterli bellek yok! Sistem çöküşünü (Crash) engellemek için OOM Killer devreye giriyor...")
        
        processes = [p_game, p_audio, p_bg]
        # Öncelik değeri en büyük (sayısal olarak en büyük olan, en önemsiz süreçtir) kurban süreci seçiyoruz.
        # Lambda yerine standart bir for döngüsü ile en yüksek öncelik değerine sahip süreci buluyoruz.
        sacrificial_p = processes[0]
        for p in processes:
            if p.priority > sacrificial_p.priority:
                sacrificial_p = p
        
        log_callback(f"[OS LOG] [OOM KILLER] Kurban süreç seçildi: '{sacrificial_p.name}' (Öncelik: {sacrificial_p.priority}). Süreç zorla sonlandırılıyor (KILLED).")
        mem_manager.deallocate(sacrificial_p, log_callback)
        
        log_callback(f"[OS LOG] [KURTARMA] Bellek açıldı. Yeni boş alan: {mem_manager.get_free_memory()} MB. Kritik süreç tekrar tahsis ediliyor.")
        mem_manager.allocate(p_critical, log_callback)
        log_callback("[OS LOG] DENEY BAŞARILI: Sistem çökmek yerine düşük öncelikli süreci feda ederek hayatta kaldı.\n")
