# memory/tlb.py

class TLBEntry:
    def __init__(self, pid, page_number, frame_number):
        self.pid = pid # Hangi sürece ait olduğu (Process ID)
        self.page_number = page_number # Sanal Sayfa Numarası (Virtual Page Number)
        self.frame_number = frame_number # Karşılık gelen Fiziksel Çerçeve Numarası (Physical Frame Number)

class TLBCache:
    """Simulates a Translation Lookaside Buffer (TLB) (Module 6) for fast page translation."""
    
    def __init__(self, max_entries=8):
        self.max_entries = max_entries
        self.entries = []  # TLB girdilerini tutan FIFO/LRU listesi
        self.hits = 0 # Önbellek isabet sayısı
        self.misses = 0 # Önbellek ıskalama sayısı
        
    def lookup(self, pid, page_number):
        """Looks up a translation. Moves entry to the end to simulate LRU update, 
        returns the frame number on hit, or None on miss.
        """
        # TLB önbelleği taranarak aranan sayfa çevirisi var mı bakılıyor
        for i, entry in enumerate(self.entries):
            if entry.pid == pid and entry.page_number == page_number:
                self.hits += 1
                # Sayfa isabeti (TLB Hit): En son erişilen girdiyi listenin sonuna taşıyarak LRU güncellemesi yapıyoruz
                tlb_entry = self.entries.pop(i)
                self.entries.append(tlb_entry)
                return tlb_entry.frame_number
                
        self.misses += 1
        return None # Sayfa önbellekte bulunamadı (TLB Miss)
        
    def insert(self, pid, page_number, frame_number):
        """Inserts a new page translation into the TLB. Evicts using FIFO/LRU if full."""
        # Eğer girilmek istenen çeviri zaten varsa değerini güncelliyoruz
        for i, entry in enumerate(self.entries):
            if entry.pid == pid and entry.page_number == page_number:
                self.entries[i].frame_number = frame_number
                return
                
        # TLB dolduysa en eski girdiyi (listenin ilk elemanı, yani FIFO/LRU gereği pop(0)) çıkarıyoruz
        if len(self.entries) >= self.max_entries:
            evicted = self.entries.pop(0)
            
        # Yeni sayfa çevirisini TLB önbelleğine ekliyoruz
        self.entries.append(TLBEntry(pid, page_number, frame_number))
        
    def invalidate_all(self):
        """Invalidates all TLB entries (on context switches or flush operations)."""
        # Bağlam değişimi olduğunda (Context Switch) TLB önbelleğini tamamen temizliyoruz (Flush)
        self.entries.clear()

    def invalidate_process(self, pid):
        """Flushes TLB entries corresponding to a specific process ID."""
        # Belirli bir sürece ait tüm TLB girdilerini temizliyoruz
        # Liste üreteci (list comprehension) yerine standart bir döngü kullanılmıştır
        new_entries = []
        for entry in self.entries:
            if entry.pid != pid:
                new_entries.append(entry)
        self.entries = new_entries

    def get_hit_ratio(self):
        # TLB isabet oranını (hit ratio) hesaplıyoruz
        total = self.hits + self.misses
        if total > 0:
            return self.hits / total
        return 0.0

    def reset_stats(self):
        # İstatistik sayaçlarını sıfırlıyoruz
        self.hits = 0
        self.misses = 0
