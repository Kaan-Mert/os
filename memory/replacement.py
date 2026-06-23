# memory/replacement.py

def simulate_fifo(page_references, capacity):
    """Simulates FIFO (First-In, First-Out) Page Replacement.
    Returns:
        faults (int), history (list of lists representing memory slots at each step)
    """
    memory_slots = [] # Fiziksel bellekteki sayfa çerçevelerini temsil eden liste
    faults = 0 # Sayfa hatası (page fault) sayacı
    history = [] # Her adımda belleğin durumunu kaydeden tarihçe
    
    for page in page_references:
        # Eğer sayfa bellekte yoksa sayfa hatası (Page Fault) oluşur
        if page not in memory_slots:
            faults += 1
            # Bellekte boş yer varsa sayfayı doğrudan ekliyoruz
            if len(memory_slots) < capacity:
                memory_slots.append(page)
            else:
                # Bellek doluysa en eski giren sayfayı (listenin başındaki eleman, pop(0)) çıkarıp yeni sayfayı ekliyoruz
                memory_slots.pop(0)  
                memory_slots.append(page)
        # Bellek durumunun bir kopyasını geçmişe kaydediyoruz
        history.append(list(memory_slots))
        
    return faults, history


def simulate_lru(page_references, capacity):
    """Simulates LRU (Least Recently Used) Page Replacement.
    Returns:
        faults (int), history (list of lists representing memory slots at each step)
    """
    memory_slots = []  # Bellekteki benzersiz sayfalar
    page_recent_use = []  # Sayfaların son kullanılma sırası (en son kullanılan en sonda yer alır)
    faults = 0 # Sayfa hatası (page fault) sayacı
    history = []
    
    for page in page_references:
        # Sayfa bellekte yoksa sayfa hatası (Page Fault) oluşur
        if page not in memory_slots:
            faults += 1
            if len(memory_slots) < capacity:
                memory_slots.append(page)
                page_recent_use.append(page)
            else:
                # En uzun süredir kullanılmayan sayfayı (listenin başındaki eleman, pop(0)) bulup bellekten çıkarıyoruz
                lru_page = page_recent_use.pop(0)
                memory_slots.remove(lru_page)
                memory_slots.append(page)
                page_recent_use.append(page)
        else:
            # Sayfa zaten bellekteyse, kullanım sırasını güncellemek için listeden çıkarıp en sona (en güncel) ekliyoruz
            page_recent_use.remove(page)
            page_recent_use.append(page)
            
        history.append(list(memory_slots))
        
    return faults, history


def compare_algorithms(page_references, capacities=[2, 3, 4, 5]):
    """Runs comparisons across multiple physical capacity sizes.
    Returns a dictionary containing faults counts for FIFO and LRU.
    """
    results = {"capacities": capacities, "fifo": [], "lru": []}
    
    for cap in capacities:
        # FIFO ve LRU algoritmalarını verilen kapasitelerle çalıştırıp hataları karşılaştırıyoruz
        fifo_faults, _ = simulate_fifo(page_references, cap)
        lru_faults, _ = simulate_lru(page_references, cap)
        results["fifo"].append(fifo_faults)
        results["lru"].append(lru_faults)
        
    return results
