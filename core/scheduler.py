# core/scheduler.py

from core.process import Process
from concurrency.locks import Resource
from memory.translation import MemoryManager

def run_fcfs(processes, log_callback):
    """First-Come First-Served Scheduling (Baseline Design)."""
    # Süreçlerin durumlarını sıfırlıyoruz
    for p in processes:
        p.reset()
    mem_manager = MemoryManager(512)
    ready_queue = []
    completed_processes = []
    current_time = 0
    active_process = None
    prev_active_pid = None
    context_switches = 0
    
    total_processes = len(processes)
    log_callback("\n[OS LOG] === FCFS PLANLAMA BAŞLATILDI ===")
    
    while len(completed_processes) < total_processes:
        # 1. Yeni gelen süreçleri bellek durumuna göre READY kuyruğuna alıyoruz
        for p in processes:
            if p.arrival_time == current_time and p.state == "READY" and p not in ready_queue and p not in completed_processes:
                if mem_manager.allocate(p, log_callback):
                    ready_queue.append(p)
                    log_callback(f"[OS LOG] [KUYRUK] {p.name} (PID: {p.pid}) sisteme ulaştı, READY kuyruğuna girdi.")
                else:
                    log_callback(f"[OS LOG] [BELLEK REDDİ] {p.name} sisteme kabul edilemedi.")
                    
        # 2. CPU boştaysa ve hazırda bekleyen süreç varsa en eskiden başlayarak (FCFS) çalıştırıyoruz
        if active_process is None:
            if ready_queue:
                active_process = ready_queue.pop(0)
                active_process.transition_to("RUNNING")
                if active_process.start_time is None:
                    active_process.start_time = current_time
                    
        # Bağlam Değişimi (Context Switch) durumunu kontrol ediyoruz
        current_pid = active_process.pid if active_process else None
        if current_pid != prev_active_pid:
            if prev_active_pid is not None or current_pid is not None:
                context_switches += 1
                if active_process:
                    log_callback(f"[OS LOG] [BAĞLAM DEĞİŞİMİ] CPU'ya yeni proses yüklendi: {active_process.name} (PID: {active_process.pid})")
            prev_active_pid = current_pid
            
        # 3. CPU üzerindeki süreci bir zaman birimi (tick) boyunca çalıştırıyoruz
        if active_process is not None:
            active_process.add_execution_interval(current_time, current_time + 1)
            active_process.remaining_time -= 1
            log_callback(f"[OS LOG] [CPU] {active_process.name} çalışıyor (Kalan Süre: {active_process.remaining_time})")
            
            # Sürecin çalışması bittiyse bellekten temizliyoruz
            if active_process.remaining_time == 0:
                active_process.transition_to("COMPLETED")
                active_process.end_time = current_time + 1
                active_process.turnaround_time = active_process.end_time - active_process.arrival_time
                active_process.waiting_time = active_process.turnaround_time - active_process.burst_time
                mem_manager.deallocate(active_process, log_callback)
                completed_processes.append(active_process)
                log_callback(f"[OS LOG] [PROSES TAMAMLANDI] {active_process.name} sona erdi. Gecikme: {active_process.waiting_time}, Yaşam Süresi: {active_process.turnaround_time}")
                active_process = None
        else:
            log_callback("[OS LOG] [CPU] CPU Boşta (Idle)")
            
        # Hazır kuyruğundaki tüm süreçlerin bekleme süresini artırıyoruz
        for p in ready_queue:
            p.waiting_time += 1
            
        current_time += 1
        
    return completed_processes, context_switches


def run_round_robin(processes, quantum, log_callback):
    """Round Robin Scheduling (Time Shared Design)."""
    # Süreçlerin durumlarını sıfırlıyoruz
    for p in processes:
        p.reset()
    mem_manager = MemoryManager(512)
    ready_queue = []
    completed_processes = []
    current_time = 0
    active_process = None
    quantum_spent = 0
    prev_active_pid = None
    context_switches = 0
    
    total_processes = len(processes)
    log_callback(f"\n[OS LOG] === ROUND ROBIN PLANLAMA BAŞLATILDI (Quantum: {quantum}) ===")
    
    while len(completed_processes) < total_processes:
        # 1. Yeni gelen süreçleri bellek durumuna göre READY kuyruğuna alıyoruz
        for p in processes:
            if p.arrival_time == current_time and p.state == "READY" and p not in ready_queue and p not in completed_processes:
                if mem_manager.allocate(p, log_callback):
                    ready_queue.append(p)
                    log_callback(f"[OS LOG] [KUYRUK] {p.name} (PID: {p.pid}) sisteme ulaştı, READY kuyruğuna girdi.")
                else:
                    log_callback(f"[OS LOG] [BELLEK REDDİ] {p.name} sisteme kabul edilemedi.")
                    
        # 2. Sürecin zaman dilimi (quantum) dolduysa, CPU'dan çekip (preempt) kuyruğun sonuna alıyoruz
        if active_process is not None:
            if quantum_spent >= quantum and active_process.remaining_time > 0:
                log_callback(f"[OS LOG] [ZAMAN AŞIMI] {active_process.name} zaman dilimini doldurdu ({quantum} tick). Kuyruk sonuna alınıyor.")
                active_process.transition_to("READY")
                ready_queue.append(active_process)
                active_process = None
                quantum_spent = 0
                
        # 3. CPU boşsa, kuyruğun başındaki süreci (Round Robin sırasına göre) seçiyoruz
        if active_process is None:
            if ready_queue:
                active_process = ready_queue.pop(0)
                active_process.transition_to("RUNNING")
                quantum_spent = 0
                if active_process.start_time is None:
                    active_process.start_time = current_time
                    
        # Bağlam değişimi kontrolü
        current_pid = active_process.pid if active_process else None
        if current_pid != prev_active_pid:
            if prev_active_pid is not None or current_pid is not None:
                context_switches += 1
                if active_process:
                    log_callback(f"[OS LOG] [BAĞLAM DEĞİŞİMİ] CPU'ya yeni proses yüklendi: {active_process.name} (PID: {active_process.pid})")
            prev_active_pid = current_pid
            
        # 4. Süreci bir zaman dilimi çalıştırıp kalan süreyi ve harcanan kuantumu güncelliyoruz
        if active_process is not None:
            active_process.add_execution_interval(current_time, current_time + 1)
            active_process.remaining_time -= 1
            quantum_spent += 1
            log_callback(f"[OS LOG] [CPU] {active_process.name} çalışıyor (Kalan: {active_process.remaining_time}, Quantum: {quantum_spent}/{quantum})")
            
            # Süreç bittiyse kaynakları serbest bırakıyoruz
            if active_process.remaining_time == 0:
                active_process.transition_to("COMPLETED")
                active_process.end_time = current_time + 1
                active_process.turnaround_time = active_process.end_time - active_process.arrival_time
                active_process.waiting_time = active_process.turnaround_time - active_process.burst_time
                mem_manager.deallocate(active_process, log_callback)
                completed_processes.append(active_process)
                log_callback(f"[OS LOG] [PROSES TAMAMLANDI] {active_process.name} sona erdi. Gecikme: {active_process.waiting_time}, Yaşam Süresi: {active_process.turnaround_time}")
                active_process = None
                quantum_spent = 0
        else:
            log_callback("[OS LOG] [CPU] CPU Boşta (Idle)")
            
        # Bekleme sürelerini güncelliyoruz
        for p in ready_queue:
            p.waiting_time += 1
            
        current_time += 1
        
    return completed_processes, context_switches


def run_mlfq(processes, quantums=[2, 4, 8], boost_interval=20, log_callback=print):
    """Multi-Level Feedback Queue (Enhanced Game Console Design)."""
    for p in processes:
        p.reset()
        p.queue_level = 0
    mem_manager = MemoryManager(512)
    # 3 seviyeli kuyruğu liste üreteci olmadan basitçe oluşturuyoruz
    queues = [[], [], []]
    completed_processes = []
    current_time = 0
    active_process = None
    quantum_spent = 0
    prev_active_pid = None
    context_switches = 0
    
    total_processes = len(processes)
    log_callback(f"\n[OS LOG] === MLFQ PLANLAMA BAŞLATILDI (Quantumlar: {quantums}, Boost Süresi: {boost_interval}) ===")
    
    while len(completed_processes) < total_processes:
        # 1. Starvasyonu (açlığı) önlemek için tüm süreçleri periyodik olarak en üst kuyruğa yükseltiyoruz (Priority Boosting)
        if current_time > 0 and current_time % boost_interval == 0:
            log_callback(f"[OS LOG] [PRIORITY BOOST] Starvasyonu önlemek için periyodik yükseltme tetiklendi. Tüm hazır süreçler Kuyruk 0'a çekiliyor.")
            for q_idx in [1, 2]:
                while queues[q_idx]:
                    p = queues[q_idx].pop(0)
                    p.queue_level = 0
                    queues[0].append(p)
                    log_callback(f"[OS LOG] [KUYRUK YÜKSELTME] {p.name} (PID: {p.pid}) -> Kuyruk 0'a terfi ettirildi.")
            if active_process is not None and active_process.queue_level > 0:
                log_callback(f"[OS LOG] [KUYRUK YÜKSELTME] Çalışan süreç {active_process.name} -> Kuyruk 0'a yükseltildi.")
                active_process.queue_level = 0
                quantum_spent = 0
                
        # 2. Yeni gelen süreçleri en öncelikli kuyruk olan Kuyruk 0'a alıyoruz
        for p in processes:
            if p.arrival_time == current_time and p.state == "READY" and p not in completed_processes:
                # p sürecinin herhangi bir kuyrukta olup olmadığını kontrol etmek için any() yerine for döngüsü kullanıyoruz
                in_queues = False
                for q in queues:
                    if p in q:
                        in_queues = True
                        break
                if not in_queues and p != active_process:
                    if mem_manager.allocate(p, log_callback):
                        p.queue_level = 0
                        queues[0].append(p)
                        log_callback(f"[OS LOG] [KUYRUK] {p.name} (PID: {p.pid}) sisteme ulaştı, Kuyruk 0'a yerleştirildi.")
                    else:
                        log_callback(f"[OS LOG] [BELLEK REDDİ] {p.name} sisteme kabul edilemedi.")
                        
        # 3. CPU'da çalışan süreçten daha üst bir kuyrukta süreç varsa, çalışan süreci CPU'dan indiriyoruz (Preemption)
        if active_process is not None:
            has_higher = False
            for j in range(active_process.queue_level):
                if queues[j]:
                    has_higher = True
                    break
            if has_higher:
                log_callback(f"[OS LOG] [ÖNCELİKLİ KESME] Üst kuyruklarda bekleyen süreç var. {active_process.name} durduruluyor ve Kuyruk {active_process.queue_level} sonuna ekleniyor.")
                active_process.transition_to("READY")
                queues[active_process.queue_level].append(active_process)
                active_process = None
                quantum_spent = 0
                
        # 4. Kuantum süresini aşan süreci bir alt öncelikli kuyruğa düşürüyoruz (Demotion)
        if active_process is not None:
            current_q_limit = quantums[active_process.queue_level]
            if quantum_spent >= current_q_limit and active_process.remaining_time > 0:
                old_lvl = active_process.queue_level
                new_lvl = old_lvl + 1
                if new_lvl > 2:
                    new_lvl = 2
                active_process.queue_level = new_lvl
                log_callback(f"[OS LOG] [KUYRUK DÜŞÜRME] {active_process.name} zaman limitini ({current_q_limit}) aştı. Kuyruk {old_lvl} -> Kuyruk {new_lvl} seviyesine düşürüldü.")
                active_process.transition_to("READY")
                queues[new_lvl].append(active_process)
                active_process = None
                quantum_spent = 0
                
        # 5. Boşalan CPU için en üst seviyedeki (dolu olan ilk kuyruk) süreci seçiyoruz
        if active_process is None:
            for j in range(3):
                if queues[j]:
                    active_process = queues[j].pop(0)
                    active_process.transition_to("RUNNING")
                    quantum_spent = 0
                    if active_process.start_time is None:
                        active_process.start_time = current_time
                    break
                    
        # Bağlam değişimi kontrolü
        current_pid = active_process.pid if active_process else None
        if current_pid != prev_active_pid:
            if prev_active_pid is not None or current_pid is not None:
                context_switches += 1
                if active_process:
                    log_callback(f"[OS LOG] [BAĞLAM DEĞİŞİMİ] CPU'ya yeni proses yüklendi: {active_process.name} (PID: {active_process.pid}, Kuyruk: {active_process.queue_level})")
            prev_active_pid = current_pid
            
        # 6. Süreci çalıştırıyoruz
        if active_process is not None:
            active_process.add_execution_interval(current_time, current_time + 1)
            active_process.remaining_time -= 1
            quantum_spent += 1
            log_callback(f"[OS LOG] [CPU] {active_process.name} çalışıyor (Kalan: {active_process.remaining_time}, Kuyruk: {active_process.queue_level}, Quantum: {quantum_spent}/{quantums[active_process.queue_level]})")
            
            # Süreç bittiyse temizliyoruz
            if active_process.remaining_time == 0:
                active_process.transition_to("COMPLETED")
                active_process.end_time = current_time + 1
                active_process.turnaround_time = active_process.end_time - active_process.arrival_time
                active_process.waiting_time = active_process.turnaround_time - active_process.burst_time
                mem_manager.deallocate(active_process, log_callback)
                completed_processes.append(active_process)
                log_callback(f"[OS LOG] [PROSES TAMAMLANDI] {active_process.name} sona erdi. Gecikme: {active_process.waiting_time}, Yaşam Süresi: {active_process.turnaround_time}")
                active_process = None
                quantum_spent = 0
        else:
            log_callback("[OS LOG] [CPU] CPU Boşta (Idle)")
            
        # Bekleyen tüm süreçlerin bekleme süresini artırıyoruz
        for q_idx in range(3):
            for p in queues[q_idx]:
                p.waiting_time += 1
                
        current_time += 1
        
    return completed_processes, context_switches


def simulate_priority_inversion_scenario(use_inheritance, log_callback):
    """Priority Inversion and Inheritance simulation."""
    p_l = Process(10, "Background Game Save", 0, 5, 3, 64)
    p_m = Process(11, "Audio Processing", 2, 6, 2, 64)
    p_h = Process(12, "Game Engine Render", 4, 4, 1, 128)
    
    processes = [p_l, p_m, p_h]
    for p in processes:
        p.reset()
        
    disk_resource = Resource("Disk Kilidi (Disk Lock)")
    mem_manager = MemoryManager(512)
    
    ready_list = []
    completed_processes = []
    current_time = 0
    active_process = None
    
    mode_str = "MİRAS MEKANİZMASI (PIP) AKTİF" if use_inheritance else "MİRAS MEKANİZMASI PASİF (TASARIM AÇIĞI)"
    log_callback(f"\n[OS LOG] === PRIORITY INVERSION DENEYİ: {mode_str} ===")
    
    while len(completed_processes) < 3 and current_time < 30:
        # 1. Süreçlerin Varış Anlarını Yakalama
        for p in processes:
            if p.arrival_time == current_time and p.state == "READY" and p not in ready_list and p not in completed_processes:
                if mem_manager.allocate(p, log_callback):
                    ready_list.append(p)
                    log_callback(f"[OS LOG] [PLANLAYICI] {p.name} (PID: {p.pid}, Öncelik: {p.priority}) sisteme geldi.")
                    
        # 2. Düşük öncelikli sürecin disk kaynağını alması
        if active_process == p_l and current_time == 1:
            disk_resource.acquire(p_l, current_time, log_callback)
            
        # Yüksek öncelikli sürecin, düşük öncelikli süreç elindeki diski istemesi
        if active_process == p_h and current_time == 5:
            success = disk_resource.acquire(p_h, current_time, log_callback)
            if not success:
                if p_h in ready_list:
                    ready_list.remove(p_h)
                active_process = None
                
                # PIP (Öncelik Mirası Protokolü) Devreye Giriyor
                if use_inheritance:
                    # Kaynağı elinde tutan sürecin önceliğini, onu bekleyen yüksek öncelikli sürecin seviyesine çekiyoruz
                    if disk_resource.owner.priority > p_h.priority:
                        old_prio = disk_resource.owner.priority
                        disk_resource.owner.priority = p_h.priority
                        log_callback(f"[OS LOG] [PIP AKTİF] !!! Öncelik Terslenmesi Önleme: '{disk_resource.owner.name}' önceliği geçici olarak {old_prio}'den {p_h.priority}'ye yükseltildi.")
                        
        # 3. Çalıştırılacak bir sonraki süreci seçme
        # List comprehension yerine standart döngü ile READY süreçleri filtreliyoruz
        runnable = []
        for p in ready_list:
            if p.state == "READY":
                runnable.append(p)
        
        # CPU'da çalışan süreci daha yüksek öncelikli bir süreç kesebilir (Preemption)
        if active_process is not None:
            higher_prio = []
            for p in runnable:
                if p.priority < active_process.priority:
                    higher_prio.append(p)
            if higher_prio:
                log_callback(f"[OS LOG] [PREEMPTION] Daha yüksek öncelikli {higher_prio[0].name} (Öncelik: {higher_prio[0].priority}) geldi. {active_process.name} (Öncelik: {active_process.priority}) askıya alınıyor.")
                active_process.transition_to("READY")
                if active_process not in ready_list:
                    ready_list.append(active_process)
                active_process = None
                
        # CPU boşsa çalıştırılacak en yüksek öncelikli süreci (sayısal öncelik değeri en küçük olan) seçiyoruz
        if active_process is None:
            if runnable:
                # Lambda ile sort etmek yerine temel bir döngü ile minimum öncelik değerini buluyoruz
                highest_prio_p = runnable[0]
                for p in runnable:
                    if p.priority < highest_prio_p.priority:
                        highest_prio_p = p
                
                active_process = highest_prio_p
                ready_list.remove(active_process)
                active_process.transition_to("RUNNING")
                if active_process.start_time is None:
                    active_process.start_time = current_time
                log_callback(f"[OS LOG] [CONTEXT SWITCH] CPU '{active_process.name}' (PID: {active_process.pid}, Öncelik: {active_process.priority}) sürecine tahsis edildi.")
                
        # 4. Süreci çalıştırma adımı
        if active_process is not None:
            active_process.add_execution_interval(current_time, current_time + 1)
            active_process.remaining_time -= 1
            log_callback(f"[OS LOG] [CPU] {active_process.name} çalışıyor (Öncelik: {active_process.priority}, Kalan: {active_process.remaining_time})")
            
            # Düşük öncelikli süreç bittiğinde disk kilidini açıyor
            if active_process == p_l and active_process.remaining_time == 0:
                next_owner = disk_resource.release(current_time + 1, log_callback)
                # Orijinal önceliğine geri döndürüyoruz
                if p_l.priority != p_l.original_priority:
                    log_callback(f"[OS LOG] [PIP GERİ DÖNÜŞ] {p_l.name} işini bitirdi ve kaynağı bıraktı. Orijinal önceliğine geri döndürülüyor ({p_l.original_priority}).")
                    p_l.priority = p_l.original_priority
                
                # Yüksek öncelikli süreci uyandırıp kuyruğa ekliyoruz
                if p_h.state == "READY" and p_h not in ready_list:
                    ready_list.append(p_h)
                    
            if active_process.remaining_time == 0:
                active_process.transition_to("COMPLETED")
                active_process.end_time = current_time + 1
                active_process.turnaround_time = active_process.end_time - active_process.arrival_time
                active_process.waiting_time = active_process.turnaround_time - active_process.burst_time
                mem_manager.deallocate(active_process, log_callback)
                completed_processes.append(active_process)
                log_callback(f"[OS LOG] [PROSES TAMAMLANDI] {active_process.name} Sona Erdi.")
                active_process = None
        else:
            log_callback("[OS LOG] [CPU] CPU Boşta (Idle)")
            
        for p in ready_list:
            if p.state == "READY" and p != active_process:
                p.waiting_time += 1
                
        current_time += 1
        
    return completed_processes, current_time
