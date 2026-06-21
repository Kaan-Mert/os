# memory/translation.py

class MemoryManager:
    """Manages physical memory allocation (at MB level for simple simulation, 
    and at Frame level for Paging/Segmentation).
    """
    def __init__(self, total_capacity_mb=512, frame_size_kb=4):
        self.total_capacity = total_capacity_mb
        self.allocated_memory = 0
        self.allocations = {}  # pid -> memory_mb
        
        # Frame-level Paging fields
        self.frame_size_kb = frame_size_kb
        self.total_frames = (total_capacity_mb * 1024) // frame_size_kb
        self.free_frames = list(range(self.total_frames))
        self.frame_map = {}   # frame_number -> (pid, page_number)
        
    def allocate(self, process, log_callback):
        """Simple process-level allocation (used by standard schedulers)."""
        if self.allocated_memory + process.memory_required <= self.total_capacity:
            self.allocated_memory += process.memory_required
            self.allocations[process.pid] = process.memory_required
            log_callback(f"[OS LOG] [BELLEK] {process.name} (PID: {process.pid}) için {process.memory_required} MB bellek ayrıldı. Toplam Kullanım: {self.allocated_memory}/{self.total_capacity} MB.")
            return True
        else:
            log_callback(f"[OS LOG] [BELLEK HATASI] {process.name} (PID: {process.pid}) için {process.memory_required} MB ayrılamadı! Boş alan: {self.total_capacity - self.allocated_memory} MB.")
            return False
            
    def deallocate(self, process, log_callback):
        """Simple process-level deallocation."""
        if process.pid in self.allocations:
            allocated = self.allocations.pop(process.pid)
            self.allocated_memory -= allocated
            log_callback(f"[OS LOG] [BELLEK] {process.name} tamamlandı, {allocated} MB bellek geri kazanıldı. Kalan Kullanım: {self.allocated_memory}/{self.total_capacity} MB.")
            
        # Free page frames if allocated
        allocated_frames = [f for f, val in self.frame_map.items() if val[0] == process.pid]
        for f in allocated_frames:
            del self.frame_map[f]
            self.free_frames.append(f)
        self.free_frames.sort()
            
    def allocate_frame(self, pid, page_number):
        """Allocates a single physical frame. Returns frame number, or -1 if full."""
        if self.free_frames:
            frame = self.free_frames.pop(0)
            self.frame_map[frame] = (pid, page_number)
            return frame
        return -1

    def deallocate_frame(self, frame_number):
        """Frees a specific frame."""
        if frame_number in self.frame_map:
            del self.frame_map[frame_number]
            self.free_frames.append(frame_number)
            self.free_frames.sort()
            
    def translate_address(self, process, virtual_address, offset_bits=12):
        """Translates a virtual address to physical using paging.
        Virtual address format: [ Page Number | Offset ]
        """
        page_size = 1 << offset_bits
        page_num = virtual_address // page_size
        offset = virtual_address % page_size
        
        if page_num in process.page_table:
            frame_num = process.page_table[page_num]
            physical_address = (frame_num << offset_bits) + offset
            return {
                "success": True,
                "page_number": page_num,
                "frame_number": frame_num,
                "offset": offset,
                "physical_address": physical_address
            }
        return {
            "success": False,
            "page_number": page_num,
            "offset": offset,
            "reason": "Page fault"
        }

    def reset(self):
        self.allocated_memory = 0
        self.allocations = {}
        self.free_frames = list(range(self.total_frames))
        self.frame_map = {}
