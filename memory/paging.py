# memory/paging.py

class PagingSystem:
    """Simulates a Paging memory system (Module 5) with page lookup and translation."""
    
    def __init__(self, page_size_kb=4):
        self.page_size = page_size_kb * 1024  # Bayt cinsinden sayfa boyutu (Varsayılan: 4096 bayt)
        
    def initialize_page_table(self, process):
        """Initializes an empty page table mapping for a process."""
        # Sürecin boş sayfa tablosunu (Page Table) ilklendiriyoruz
        process.page_table = {}  # sanal_sayfa_numarası -> fiziksel_çerçeve_numarası

    def map_page(self, process, page_number, frame_number):
        """Maps a process's virtual page number to a physical frame number."""
        # Sanal sayfa numarasını fiziksel çerçeve numarasına eşliyoruz
        process.page_table[page_number] = frame_number

    def lookup(self, process, page_number):
        """Checks if a page number is currently present in the process's page table.
        Returns the frame number if found (Hit), or None (Page Fault/Miss).
        """
        # Sayfanın bellekte (sayfa tablosunda) olup olmadığını sorguluyoruz
        if page_number in process.page_table:
            return process.page_table[page_number]
        return None

    def translate(self, process, logical_address):
        """Translates a logical address into page number, offset, and looks up the frame."""
        # Sanal adresi sayfa boyutuna bölerek sanal sayfa numarasını buluyoruz
        page_number = logical_address // self.page_size
        # Sanal adresin sayfa boyutuyla modunu alarak sayfa içindeki ofseti buluyoruz
        offset = logical_address % self.page_size
        
        # Sayfa tablosundan bu sayfanın yüklendiği çerçeveyi arıyoruz
        frame_number = self.lookup(process, page_number)
        
        # Sayfa bellekte varsa fiziksel adresi hesaplıyoruz (Sayfa İsabeti - Page Hit)
        if frame_number is not None:
            physical_address = (frame_number * self.page_size) + offset
            return {
                "success": True,
                "page_number": page_number,
                "frame_number": frame_number,
                "offset": offset,
                "physical_address": physical_address
            }
        else:
            # Sayfa bellekte değilse Sayfa Hatası (Page Fault) oluşur ve diskten getirilmesi gerekir
            return {
                "success": False,
                "page_number": page_number,
                "offset": offset,
                "reason": "PAGE FAULT (Page not in memory)"
            }
