# memory/segmentation.py

class Segment:
    def __init__(self, name, base, limit, is_writable=True):
        self.name = name
        self.base = base
        self.limit = limit
        self.is_writable = is_writable

class SegmentationSystem:
    """Simulates Segmentation (Module 4) for a process's logical layout."""
    
    def __init__(self, physical_memory_size_mb=512):
        self.physical_memory_size = physical_memory_size_mb * 1024 * 1024  # In bytes
        self.next_free_physical_base = 0x100000  # Start segments above kernel space (1MB)

    def initialize_segments(self, process):
        """Initializes virtual memory segments for a console process (Code, Stack, Heap, Assets)."""
        # Distribute segment allocations in physical memory
        code_size = 64 * 1024        # 64 KB
        stack_size = 16 * 1024       # 16 KB
        heap_size = 128 * 1024       # 128 KB
        assets_size = 256 * 1024     # 256 KB
        
        process.segment_table = {
            "Code": Segment("Code", self.next_free_physical_base, code_size, is_writable=False),
            "Stack": Segment("Stack", self.next_free_physical_base + code_size, stack_size, is_writable=True),
            "Heap": Segment("Heap", self.next_free_physical_base + code_size + stack_size, heap_size, is_writable=True),
            "Assets": Segment("Assets", self.next_free_physical_base + code_size + stack_size + heap_size, assets_size, is_writable=False)
        }
        
        self.next_free_physical_base += (code_size + stack_size + heap_size + assets_size + 0x1000)  # Add alignment gap

    def translate(self, process, segment_name, offset):
        """Translates a logical address segment name and offset to physical address.
        Checks for Segment Limits to prevent out-of-bounds access.
        """
        if segment_name not in process.segment_table:
            return {"success": False, "reason": "BİLİNMEYEN SEGMENT (Unknown Segment)"}
            
        segment = process.segment_table[segment_name]
        
        if offset >= segment.limit:
            # Segment Limit Fault!
            return {
                "success": False,
                "reason": f"SEGMENT TAŞMA HATASI (Segmentation Fault): Offset {offset} >= Limit {segment.limit} in '{segment_name}'."
            }
            
        physical_address = segment.base + offset
        return {
            "success": True,
            "segment_name": segment_name,
            "base_address": hex(segment.base),
            "limit": segment.limit,
            "physical_address": hex(physical_address)
        }
