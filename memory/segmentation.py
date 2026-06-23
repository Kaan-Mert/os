# memory/segmentation.py

class Segment:
    def __init__(self, name, base, limit, is_writable=True):
        self.name = name # Segmentin adı (Örn: Code, Stack, Heap, Assets)
        self.base = base # Segmentin fiziksel bellekteki başlangıç adresi
        self.limit = limit # Segmentin maksimum boyutu (limit değeri)
        self.is_writable = is_writable # Segmentin yazma izni olup olmadığı (Stack/Heap yazılabilir, Code/Assets sadece okunabilir)

class SegmentationSystem:
    """Simulates Segmentation (Module 4) for a process's logical layout."""
    
    def __init__(self, physical_memory_size_mb=512):
        self.physical_memory_size = physical_memory_size_mb * 1024 * 1024  # Bayt cinsinden toplam fiziksel bellek boyutu
        self.next_free_physical_base = 0x100000  # Segmentleri kernel alanının (ilk 1MB) üzerinde başlatıyoruz

    def initialize_segments(self, process):
        """Initializes virtual memory segments for a console process (Code, Stack, Heap, Assets)."""
        # Her bir segmentin boyutunu belirliyoruz
        code_size = 64 * 1024        # 64 KB
        stack_size = 16 * 1024       # 16 KB
        heap_size = 128 * 1024       # 128 KB
        assets_size = 256 * 1024     # 256 KB
        
        # Sürecin segment tablosunu (Segment Table) oluşturuyoruz
        # Her segment fiziksel belleğe ardışık olarak yerleştiriliyor (base ve limit değerleri atanıyor)
        process.segment_table = {
            "Code": Segment("Code", self.next_free_physical_base, code_size, is_writable=False),
            "Stack": Segment("Stack", self.next_free_physical_base + code_size, stack_size, is_writable=True),
            "Heap": Segment("Heap", self.next_free_physical_base + code_size + stack_size, heap_size, is_writable=True),
            "Assets": Segment("Assets", self.next_free_physical_base + code_size + stack_size + heap_size, assets_size, is_writable=False)
        }
        
        # Sonraki süreç segmentleri için boş alanı güncelliyoruz (Hizalama boşluğu bırakarak)
        self.next_free_physical_base += (code_size + stack_size + heap_size + assets_size + 0x1000)

    def translate(self, process, segment_name, offset):
        """Translates a logical address segment name and offset to physical address.
        Checks for Segment Limits to prevent out-of-bounds access.
        """
        # Segment tablosunda istenen segment yoksa hata döndürülüyor
        if segment_name not in process.segment_table:
            return {"success": False, "reason": "BİLİNMEYEN SEGMENT (Unknown Segment)"}
            
        segment = process.segment_table[segment_name]
        
        # Sınır Kontrolü (Bounds Check): Ofset değeri segment limitini aşarsa Segmentation Fault hatası verilir
        if offset >= segment.limit:
            # Segment Limit Hatası! (Erişim segment sınırlarının dışında)
            return {
                "success": False,
                "reason": f"SEGMENT TAŞMA HATASI (Segmentation Fault): Offset {offset} >= Limit {segment.limit} in '{segment_name}'."
            }
            
        # Fiziksel Adres = Başlangıç Adresi (Base) + Ofset (Offset)
        physical_address = segment.base + offset
        return {
            "success": True,
            "segment_name": segment_name,
            "base_address": hex(segment.base),
            "limit": segment.limit,
            "physical_address": hex(physical_address)
        }
