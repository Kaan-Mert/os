# memory/tlb.py

class TLBEntry:
    def __init__(self, pid, page_number, frame_number):
        self.pid = pid
        self.page_number = page_number
        self.frame_number = frame_number

class TLBCache:
    """Simulates a Translation Lookaside Buffer (TLB) (Module 6) for fast page translation."""
    
    def __init__(self, max_entries=8):
        self.max_entries = max_entries
        self.entries = []  # List of TLBEntry objects (FIFO list)
        self.hits = 0
        self.misses = 0
        
    def lookup(self, pid, page_number):
        """Looks up a translation. Moves entry to the end to simulate LRU update, 
        returns the frame number on hit, or None on miss.
        """
        for i, entry in enumerate(self.entries):
            if entry.pid == pid and entry.page_number == page_number:
                self.hits += 1
                # Move to end (LRU update)
                tlb_entry = self.entries.pop(i)
                self.entries.append(tlb_entry)
                return tlb_entry.frame_number
                
        self.misses += 1
        return None
        
    def insert(self, pid, page_number, frame_number):
        """Inserts a new page translation into the TLB. Evicts using FIFO/LRU if full."""
        # Check if entry already exists (update it)
        for i, entry in enumerate(self.entries):
            if entry.pid == pid and entry.page_number == page_number:
                self.entries[i].frame_number = frame_number
                return
                
        if len(self.entries) >= self.max_entries:
            # Evict first element (FIFO/LRU replacement)
            evicted = self.entries.pop(0)
            
        self.entries.append(TLBEntry(pid, page_number, frame_number))
        
    def invalidate_all(self):
        """Invalidates all TLB entries (on context switches or flush operations)."""
        self.entries.clear()

    def invalidate_process(self, pid):
        """Flushes TLB entries corresponding to a specific process ID."""
        self.entries = [entry for entry in self.entries if entry.pid != pid]

    @property
    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset_stats(self):
        self.hits = 0
        self.misses = 0
