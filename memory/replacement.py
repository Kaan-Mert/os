# memory/replacement.py

class PageReplacementSimulator:
    """Simulates Page Replacement Algorithms (FIFO and LRU) for Module 7."""
    
    @staticmethod
    def simulate_fifo(page_references, capacity):
        """Simulates FIFO (First-In, First-Out) Page Replacement.
        Returns:
            faults (int), history (list of lists representing memory slots at each step)
        """
        memory_slots = []
        faults = 0
        history = []
        
        for page in page_references:
            if page not in memory_slots:
                faults += 1
                if len(memory_slots) < capacity:
                    memory_slots.append(page)
                else:
                    memory_slots.pop(0)  # Remove the oldest (first inserted) page
                    memory_slots.append(page)
            # Record state
            history.append(list(memory_slots))
            
        return faults, history

    @staticmethod
    def simulate_lru(page_references, capacity):
        """Simulates LRU (Least Recently Used) Page Replacement.
        Returns:
            faults (int), history (list of lists representing memory slots at each step)
        """
        memory_slots = []  # Elements are unique pages in memory
        page_recent_use = []  # Keeps track of recently used order (most recent at the end)
        faults = 0
        history = []
        
        for page in page_references:
            if page not in memory_slots:
                faults += 1
                if len(memory_slots) < capacity:
                    memory_slots.append(page)
                    page_recent_use.append(page)
                else:
                    # Find LRU page (the page that appears earliest in the recent use tracking)
                    lru_page = page_recent_use.pop(0)
                    memory_slots.remove(lru_page)
                    memory_slots.append(page)
                    page_recent_use.append(page)
            else:
                # Update recent usage (move page to end of recent use list)
                page_recent_use.remove(page)
                page_recent_use.append(page)
                
            history.append(list(memory_slots))
            
        return faults, history

    @classmethod
    def compare_algorithms(cls, page_references, capacities=[2, 3, 4, 5]):
        """Runs comparisons across multiple physical capacity sizes.
        Returns a dictionary containing faults counts for FIFO and LRU.
        """
        results = {"capacities": capacities, "fifo": [], "lru": []}
        
        for cap in capacities:
            fifo_faults, _ = cls.simulate_fifo(page_references, cap)
            lru_faults, _ = cls.simulate_lru(page_references, cap)
            results["fifo"].append(fifo_faults)
            results["lru"].append(lru_faults)
            
        return results
