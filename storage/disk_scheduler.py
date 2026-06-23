# storage/disk_scheduler.py

class DiskScheduler:
    """Simulates Disk Head Scheduling algorithms (Module 12): FCFS and SSTF."""
    
    def simulate_fcfs(initial_head, requests):
        """First-Come, First-Served Disk Scheduling.
        Calculates total seek distance (cylinder tracks traversed).
        """
        # FCFS: Disk kafası istek sırasına göre doğrudan hareket eder
        current_head = initial_head
        seek_path = [initial_head]
        total_seek_distance = 0
        
        for req in requests:
            # Gidilecek silindir ile mevcut kafa pozisyonu arasındaki mutlak fark hesaplanır
            distance = abs(req - current_head)
            total_seek_distance += distance
            current_head = req
            seek_path.append(req)
            
        return total_seek_distance, seek_path

    def simulate_sstf(initial_head, requests):
        """Shortest Seek Time First (SSTF) Disk Scheduling.
        Always picks the closest request to the current head location.
        """
        # SSTF: Kafaya en yakın olan istek her zaman ilk önce seçilir (Seek time minimizasyonu)
        current_head = initial_head
        seek_path = [initial_head]
        total_seek_distance = 0
        pending_requests = list(requests)
        
        while pending_requests:
            # En yakın isteği bulmak için lambda/min yerine temel bir karşılaştırma döngüsü yazılmıştır
            closest_req = pending_requests[0]
            min_distance = abs(closest_req - current_head)
            
            for r in pending_requests:
                dist = abs(r - current_head)
                if dist < min_distance:
                    min_distance = dist
                    closest_req = r
            
            distance = min_distance
            total_seek_distance += distance
            current_head = closest_req
            seek_path.append(closest_req)
            # Seçilen isteği bekleyenler listesinden kaldırıyoruz
            pending_requests.remove(closest_req)
            
        return total_seek_distance, seek_path
