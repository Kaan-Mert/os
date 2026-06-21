# storage/disk_scheduler.py

class DiskScheduler:
    """Simulates Disk Head Scheduling algorithms (Module 12): FCFS and SSTF."""
    
    @staticmethod
    def simulate_fcfs(initial_head, requests):
        """First-Come, First-Served Disk Scheduling.
        Calculates total seek distance (cylinder tracks traversed).
        """
        current_head = initial_head
        seek_path = [initial_head]
        total_seek_distance = 0
        
        for req in requests:
            distance = abs(req - current_head)
            total_seek_distance += distance
            current_head = req
            seek_path.append(req)
            
        return total_seek_distance, seek_path

    @staticmethod
    def simulate_sstf(initial_head, requests):
        """Shortest Seek Time First (SSTF) Disk Scheduling.
        Always picks the closest request to the current head location.
        """
        current_head = initial_head
        seek_path = [initial_head]
        total_seek_distance = 0
        pending_requests = list(requests)
        
        while pending_requests:
            # Find request with minimum seek distance
            closest_req = min(pending_requests, key=lambda r: abs(r - current_head))
            distance = abs(closest_req - current_head)
            total_seek_distance += distance
            current_head = closest_req
            seek_path.append(closest_req)
            pending_requests.remove(closest_req)
            
        return total_seek_distance, seek_path
