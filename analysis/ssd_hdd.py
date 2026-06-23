# analysis/ssd_hdd.py

class SSDvsHDDAnalysis:
    """Simulates performance differences between SSD and HDD (Module 16).
    Models rotational and seek latencies of mechanical hard drives vs flash memory.
    """
    
    def simulate_hdd_time(requests, scheduling_algorithm="FCFS", head_start=50):
        """Simulates HDD timing using:
        - 7200 RPM Rotational Latency: ~4.17 ms (average)
        - Seek time: proportional to track distance (e.g., 0.1 ms per track)
        - Data transfer time: 0.1 ms
        """
        current_head = head_start
        total_time_ms = 0.0
        pending = list(requests)
        
        # Disk kafasının hareket sırasını belirliyoruz
        if scheduling_algorithm == "FCFS":
            path = pending
        elif scheduling_algorithm == "SSTF":
            path = []
            while pending:
                # Lambda yerine standart döngü ile en yakın disk isteğini arıyoruz
                closest = pending[0]
                min_dist = abs(closest - current_head)
                for r in pending:
                    dist = abs(r - current_head)
                    if dist < min_dist:
                        min_dist = dist
                        closest = r
                        
                path.append(closest)
                pending.remove(closest)
                current_head = closest
        else:
            path = pending
            
        current_head = head_start
        for req in path:
            # 1. Arama Süresi (Seek Time): Okuyucu kafanın silindirler arasındaki fiziksel hareketi
            distance = abs(req - current_head)
            seek_time = distance * 0.08  # Silindir başına 0.08 milisaniye gecikme
            
            # 2. Dönme Gecikmesi (Rotational Latency): Diskin dönerek ilgili sektörü kafanın altına getirme süresi
            rotational_latency = 4.17  # 7200 RPM disk için ortalama dönme süresi
            
            # 3. Transfer Süresi (Transfer Time): Verinin disk plakasından okunup gönderilme süresi
            transfer_time = 0.1
            
            # Toplam I/O süresini biriktiriyoruz
            total_time_ms += (seek_time + rotational_latency + transfer_time)
            current_head = req
            
        return total_time_ms

    def simulate_ssd_time(requests):
        """Simulates SSD timing (Flash memory, near-zero seek latency, no rotation).
        - Latency is near constant: ~0.1 ms access delay per request.
        """
        # SSD mekanik kafa barındırmadığı için arama ve dönme gecikmesi 0'dır, rasgele erişim süresi sabittir
        access_latency_ms = 0.1 # Sabit elektronik erişim süresi
        transfer_time = 0.02
        return len(requests) * (access_latency_ms + transfer_time)

    def get_comparison_discussion():
        return (
            "[bold white]HDD vs SSD Karşılaştırma Raporu (Game Console OS Context):[/bold white]\n\n"
            "1. [bold yellow]Disk Schedulers (Disk Planlama):[/bold yellow]\n"
            "   - [bold cyan]HDD[/bold cyan], mekanik okuyucu kafaya (actuator arm) ve dönen plakalara (platter) sahip olduğu için disk kafasının hareketi "
            "aşırı yavaştır. Bu yüzden FCFS yerine SSTF kullanımı HDD'de seek süresini dramatik biçimde azaltır.\n"
            "   - [bold cyan]SSD[/bold cyan], tamamen entegre devrelerden oluştuğu için mekanik kafa hareketi yoktur. FCFS veya SSTF kullanılması "
            "erişim süresini değiştirmez. SSD'ler için planlama önemsizleşirken, I/O paralelliği (NCQ/NVMe) önem kazanır.\n\n"
            "2. [bold yellow]Oyun Konsolu Performansı (Texture & Asset Loading):[/bold yellow]\n"
            "   - Konsollarda açık dünya oyunları yüklenirken HDD'ler disk kafasının sürekli farklı sektörlere zıplamasıyla kilitlenir. "
            "Bu durum 'texture pop-in' (kaplamaların geç gelmesi) sorununa yol açar.\n"
            "   - SSD kullanan modern konsollar (örn: PS5/Xbox Series X) 100x daha yüksek I/O bant genişliği sunduğu için bekleme ekranlarını kaldırır "
            "ve oyun motoruna doğrudan asset yayını yapabilir."
        )
