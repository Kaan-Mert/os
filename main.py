# main.py
"""
Mini Operating System Simulator (Game Console OS Theme)
Central Orchestrator & Interactive CLI Dashboard
"""

import sys
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Package Imports
from core.process import Process
from core.scheduler import (
    run_fcfs, 
    run_round_robin, 
    run_mlfq, 
    simulate_priority_inversion_scenario
)
from memory.translation import MemoryManager
from memory.segmentation import SegmentationSystem
from memory.paging import PagingSystem
from memory.tlb import TLBCache
from memory.replacement import PageReplacementSimulator
from concurrency.locks import Mutex
from concurrency.semaphores import ProducerConsumerSimulation
from concurrency.multithreading import RaceConditionDemo
from storage.disk_scheduler import DiskScheduler
from storage.raid import RAIDSystem
from storage.filesystem import VirtualFileSystem
from storage.journaling import JournaledFileSystem
from analysis.ssd_hdd import SSDvsHDDAnalysis
from analysis.performance import PerformancePlotter

console = Console()

def get_fresh_workload():
    """Generates a fresh test workload of console processes."""
    return [
        Process(1, "Gamepad Input Handler", 0, 3, 1, 16),
        Process(2, "Game Engine Render", 1, 8, 1, 128),
        Process(3, "Audio Processing", 2, 5, 2, 64),
        Process(4, "Network Download", 3, 10, 3, 32),
        Process(5, "Background Game Save", 4, 4, 3, 64)
    ]

def show_menu():
    menu_text = (
        "[bold cyan]Modüller ve Simülasyon Seçenekleri:[/bold cyan]\n"
        "  [bold green]1.[/bold green] CPU Zamanlama & Gantt Şeması (FCFS vs RR vs MLFQ) - [yellow]Modül 1, 2[/yellow]\n"
        "  [bold green]2.[/bold green] Priority Inversion & PIP (Öncelik Mirası Deneyi) - [yellow]Modül 9, Zorluk[/yellow]\n"
        "  [bold green]3.[/bold green] Adres Çevirisi, Sayfalama (Paging) & TLB Simülasyonu - [yellow]Modül 3, 5, 6[/yellow]\n"
        "  [bold green]4.[/bold green] Segmentasyon & Sınır Güvenliği Aşım Kontrolü - [yellow]Modül 4[/yellow]\n"
        "  [bold green]5.[/bold green] Sayfa Değiştirme (FIFO vs LRU Page Fault Analizi) - [yellow]Modül 7[/yellow]\n"
        "  [bold green]6.[/bold green] Concurrency: Yarış Durumu (Race Condition) & Semafor (Producer-Consumer) - [yellow]Modül 8, 10, 11[/yellow]\n"
        "  [bold green]7.[/bold green] Depolama: Disk Schedulers, RAID 0/1 & Journaled FS (Crash Consistency) - [yellow]Modül 12, 13, 14, 15[/yellow]\n"
        "  [bold green]8.[/bold green] SSD vs HDD Performans Karşılaştırma Analizi - [yellow]Modül 16[/yellow]\n"
        "  [bold green]9.[/bold green] TÜM Grafiksel PNG Raporlarını Yeniden Oluştur (Generate Plots)\n"
        "  [bold red]Q.[/bold red] Çıkış (Exit)"
    )
    console.print(Panel(menu_text, border_style="cyan", title="[bold white]=== Game Console OS Simulator Dashboard ===[/bold white]", box=box.ROUNDED))

def handle_scheduling():
    console.print("\n[bold yellow]>>> Hız Testi: CPU Planlama Algoritmaları Karşılaştırma Deneyi...[/bold yellow]")
    
    log_messages = []
    def dummy_log(msg):
        log_messages.append(msg)
    
    # Run FCFS
    fcfs_procs = get_fresh_workload()
    fcfs_completed, fcfs_cs = run_fcfs(fcfs_procs, dummy_log)
    
    # Run RR
    rr_procs = get_fresh_workload()
    rr_completed, rr_cs = run_round_robin(rr_procs, 4, dummy_log)
    
    # Run MLFQ
    mlfq_procs = get_fresh_workload()
    mlfq_completed, mlfq_cs = run_mlfq(mlfq_procs, [2, 4, 8], 20, dummy_log)
    
    # Plot Gantt charts
    PerformancePlotter.plot_scheduler_gantt(fcfs_procs, rr_procs, mlfq_procs, "gantt_chart.png")
    
    # Stats table
    table = Table(title="CPU Planlama Algoritmaları İstatistik Raporu (FCFS vs RR vs MLFQ)", box=box.DOUBLE)
    table.add_column("Algoritma (Scheduler)", style="cyan", no_wrap=True)
    table.add_column("Ort. Bekleme (Waiting)", style="magenta")
    table.add_column("Ort. Yanıt (Turnaround)", style="green")
    table.add_column("Bağlam Değişimi (CS)", style="yellow")
    table.add_column("Tasarım Rolü ve Trade-off", style="white")
    
    def get_stats(procs):
        avg_w = sum(p.waiting_time for p in procs) / len(procs)
        avg_t = sum(p.turnaround_time for p in procs) / len(procs)
        return f"{avg_w:.2f} tick", f"{avg_t:.2f} tick"
        
    fcfs_w, fcfs_t = get_stats(fcfs_procs)
    rr_w, rr_t = get_stats(rr_procs)
    mlfq_w, mlfq_t = get_stats(mlfq_procs)
    
    table.add_row("FCFS (Baseline)", fcfs_w, fcfs_t, str(fcfs_cs), "Basit, adil ama interaktif gecikme yüksek")
    table.add_row("Round Robin (RR)", rr_w, rr_t, str(rr_cs), "Zaman paylaşımlı, bağlam değişimi orta düzey")
    table.add_row("MLFQ (Enhanced)", mlfq_w, mlfq_t, str(mlfq_cs), "En iyi interaktivite; GPU/Input korur, karmaşık")
    
    console.print(table)
    console.print("[bold green][OS LOG] Başarı: Gantt Şeması 'gantt_chart.png' olarak kaydedildi.[/bold green]")

def handle_priority_inversion():
    console.print("\n[bold yellow]>>> Öncelik Terslenmesi (Priority Inversion) ve Öncelik Mirası (PIP) Simülasyonu...[/bold yellow]")
    
    log_messages = []
    def console_log(msg):
        log_messages.append(msg)
        console.print(msg)
        
    # Unsync scenario (without PIP)
    inv_no_pip, dur_no_pip = simulate_priority_inversion_scenario(use_inheritance=False, log_callback=console_log)
    
    # Sync scenario (with PIP)
    inv_pip, dur_pip = simulate_priority_inversion_scenario(use_inheritance=True, log_callback=console_log)
    
    # Display comparison
    table = Table(title="Priority Inversion ve Priority Inheritance Deney Raporu", box=box.ROUNDED)
    table.add_column("Senaryo", style="cyan")
    table.add_column("Yüksek Öncelikli H Bitiş Zamanı", style="red")
    table.add_column("Toplam Süre (Ticks)", style="yellow")
    table.add_column("Diagnostic Durum", style="white")
    
    h_end_no_pip = next((p.end_time for p in inv_no_pip if p.pid == 12), "Kilitlendi / Starved")
    h_end_pip = next((p.end_time for p in inv_pip if p.pid == 12), "N/A")
    
    table.add_row("PIP Olmadan (Tasarım Açığı)", str(h_end_no_pip), f"{dur_no_pip} tick", "[bold red]Kilitlenme (Gamepad/Engine Kilitli)[/bold red]")
    table.add_row("PIP İle (Öncelik Mirası Aktif)", f"{h_end_pip} (Kurtarıldı)", f"{dur_pip} tick", "[bold green]Sorun Çözüldü (Normal Akış)[/bold green]")
    
    console.print(table)

def handle_paging_tlb():
    console.print("\n[bold yellow]>>> Sanal Adres Çevirisi, Sayfalama (Paging) ve TLB Erişim Simülasyonu...[/bold yellow]")
    
    mem_manager = MemoryManager(512, frame_size_kb=4)
    paging_sys = PagingSystem(page_size_kb=4)
    tlb_cache = TLBCache(max_entries=4)
    
    p = Process(1, "Game Level Loader", 0, 10, 1, 64)
    paging_sys.initialize_page_table(p)
    
    # Reference some virtual memory addresses (each offset 4096 bytes)
    # Addresses map to virtual pages:
    # 0x1005 (Page 1), 0x205A (Page 2), 0x1005 (Page 1), 0x30AC (Page 3), 0x205A (Page 2), 0x51AF (Page 5)
    virtual_addresses = [0x1005, 0x205A, 0x1005, 0x30AC, 0x205A, 0x51AF]
    
    table = Table(title=f"Sanal Adres Çeviri Tablosu (Page Size: 4KB, TLB Entries: {tlb_cache.max_entries})", box=box.ROUNDED)
    table.add_column("Sanal Adres (VA)", style="cyan")
    table.add_column("Sanal Sayfa No", style="magenta")
    table.add_column("TLB Durumu", style="yellow")
    table.add_column("Sayfa Tablosu / Fault Durumu", style="orange3")
    table.add_column("Fiziksel Çerçeve No (PFN)", style="green")
    table.add_column("Fiziksel Adres (PA)", style="green")
    
    for va in virtual_addresses:
        page_num = va // (4 * 1024)
        offset = va % (4 * 1024)
        
        # 1. TLB Lookup
        frame_num = tlb_cache.lookup(p.pid, page_num)
        tlb_status = "[bold green]HIT[/bold green]" if frame_num is not None else "[bold red]MISS[/bold red]"
        
        pt_status = "N/A (TLB Hit)"
        pa_str = "N/A"
        frame_str = "N/A"
        
        if frame_num is None:
            # 2. Page Table Lookup
            frame_num = paging_sys.lookup(p, page_num)
            
            if frame_num is not None:
                pt_status = "[bold green]Page Table HIT[/bold green]"
                # Insert translation to TLB
                tlb_cache.insert(p.pid, page_num, frame_num)
            else:
                pt_status = "[bold red]PAGE FAULT[/bold red]"
                # Simulate loading page from disk to free memory frame
                frame_num = mem_manager.allocate_frame(p.pid, page_num)
                if frame_num != -1:
                    paging_sys.map_page(p, page_num, frame_num)
                    tlb_cache.insert(p.pid, page_num, frame_num)
                    pt_status += " -> Frame Tahsis Edildi"
                else:
                    pt_status += " -> Bellek Dolu (OOM)!"
                    
        if frame_num is not None and frame_num != -1:
            frame_str = str(frame_num)
            pa = (frame_num * 4096) + offset
            pa_str = hex(pa)
            
        table.add_row(hex(va), str(page_num), tlb_status, pt_status, frame_str, pa_str)
        
    console.print(table)
    console.print(f"[OS LOG] [TLB İSTATİSTİK] Toplam Hit: {tlb_cache.hits} | Miss: {tlb_cache.misses} | [bold yellow]TLB Hit Oranı: {tlb_cache.hit_ratio*100:.1f}%[/bold yellow]")

def handle_segmentation():
    console.print("\n[bold yellow]>>> Segmentasyon ve Segment Sınır Aşım (Segmentation Fault) Güvenlik Simülasyonu...[/bold yellow]")
    
    seg_sys = SegmentationSystem(512)
    p = Process(2, "FPS Player Entity", 0, 10, 1, 64)
    
    seg_sys.initialize_segments(p)
    
    # Display Segment Table
    table = Table(title=f"Proses '{p.name}' Segment Tablosu", box=box.ROUNDED)
    table.add_column("Segment Adı", style="cyan")
    table.add_column("Fiziksel Başlangıç Adresi (Base)", style="green")
    table.add_column("Boyut Limiti (Limit)", style="yellow")
    table.add_column("İzin", style="magenta")
    
    for name, seg in p.segment_table.items():
        perms = "R/W (Yazılabilir)" if seg.is_writable else "R (Sadece Okunabilir)"
        table.add_row(name, hex(seg.base), f"{seg.limit} byte", perms)
    console.print(table)
    
    # Translation 1: Valid access to Stack
    offset_valid = 1024
    res_valid = seg_sys.translate(p, "Stack", offset_valid)
    console.print(f"[OS LOG] [SEGMENTATION] İstek: Stack, Offset: {offset_valid} $\\rightarrow$ Sonuç: [bold green]BAŞARILI[/bold green]. Fiziksel Adres: {res_valid.get('physical_address')}")
    
    # Translation 2: Out of bounds access to Stack (Limit is 16KB = 16384 bytes)
    offset_invalid = 20000
    res_invalid = seg_sys.translate(p, "Stack", offset_invalid)
    console.print(f"[OS LOG] [SEGMENTATION FAULT] İstek: Stack, Offset: {offset_invalid} $\\rightarrow$ Sonuç: [bold red]{res_invalid.get('reason')}[/bold red]")

def handle_page_replacement():
    console.print("\n[bold yellow]>>> Sayfa Değiştirme (Page Replacement) FIFO vs LRU Karşılaştırma Deneyi...[/bold yellow]")
    
    # Virtual page reference string
    ref_string = [1, 3, 0, 3, 5, 6, 3, 1, 3, 2, 1, 4, 5, 2]
    capacities = [2, 3, 4, 5]
    
    results = PageReplacementSimulator.compare_algorithms(ref_string, capacities)
    
    # Plot fault rates
    PerformancePlotter.plot_page_replacement(capacities, results["fifo"], results["lru"], "page_faults.png")
    
    table = Table(title="FIFO vs LRU Page Fault Sayısı Karşılaştırması", box=box.ROUNDED)
    table.add_column("Bellek Kapasitesi (Sayfa Çerçevesi)", style="cyan")
    table.add_column("FIFO Hataları (Page Faults)", style="red")
    table.add_column("LRU Hataları (Page Faults)", style="green")
    table.add_column("İyileşme Farkı", style="yellow")
    
    for idx, cap in enumerate(capacities):
        fifo_f = results["fifo"][idx]
        lru_f = results["lru"][idx]
        diff = fifo_f - lru_f
        diff_str = f"+{diff} FIFO Hatası" if diff > 0 else ("Aynı" if diff == 0 else f"{diff} LRU Hatası")
        table.add_row(str(cap), str(fifo_f), str(lru_f), diff_str)
        
    console.print(table)
    console.print("[bold green][OS LOG] Başarı: Sayfa Değiştirme grafiği 'page_faults.png' olarak kaydedildi.[/bold green]")

def handle_concurrency_semaphores():
    console.print("\n[bold yellow]>>> Concurrency: Çoklu Threading, Yarış Durumu (Race Condition) ve Semafor Simülasyonu...[/bold yellow]")
    
    # 1. Race Condition Demo
    demo = RaceConditionDemo()
    results = demo.run_demo(num_threads=4, iterations=1000, log_callback=console.print)
    
    # 2. Semaphore Producer Consumer Demo
    sim = ProducerConsumerSimulation(capacity=4)
    sim.run(duration=2.5, log_callback=console.print)

def handle_storage_journaling():
    console.print("\n[bold yellow]>>> Depolama: Disk Schedulers, RAID 0/1 & Journaled File System (Crash Consistency)...[/bold yellow]")
    
    # 1. Disk Head Scheduling
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    head_start = 53
    
    fcfs_seek, fcfs_path = DiskScheduler.simulate_fcfs(head_start, requests)
    sstf_seek, sstf_path = DiskScheduler.simulate_sstf(head_start, requests)
    
    PerformancePlotter.plot_disk_scheduling(head_start, requests, fcfs_path, sstf_path, "disk_scheduling.png")
    
    disk_table = Table(title="Disk Kafa Planlama Algoritmaları Karşılaştırma", box=box.ROUNDED)
    disk_table.add_column("Algoritma", style="cyan")
    disk_table.add_column("Kafa Hareket Sırası (Path)", style="white")
    disk_table.add_column("Toplam Silindir Atlama Sayısı (Seek)", style="yellow")
    disk_table.add_column("Verimlilik İyileşmesi", style="green")
    
    impr = f"{((fcfs_seek - sstf_seek) / fcfs_seek * 100):.1f}% Daha Az Kafa Hareketi"
    disk_table.add_row("FCFS (Baseline)", " -> ".join(map(str, fcfs_path)), f"{fcfs_seek} silindir", "Referans")
    disk_table.add_row("SSTF (Enhanced)", " -> ".join(map(str, sstf_path)), f"{sstf_seek} silindir", impr)
    console.print(disk_table)
    console.print("[bold green][OS LOG] Başarı: Disk kafası hareket şeması 'disk_scheduling.png' olarak kaydedildi.[/bold green]\n")
    
    # 2. RAID 0 & RAID 1 Simulation
    console.print("[bold yellow]--- RAID 0 vs RAID 1 Performans ve Güvenilirlik Testi ---[/bold yellow]")
    raid = RAIDSystem(size_blocks=16)
    
    texture_data = "4K_ULTRA_TEXTURE_MAP_DATA_XYZ"
    raid.write_raid_0("level1_tex", texture_data)
    raid.write_raid_1("level1_tex", texture_data)
    
    # Test read under healthy condition
    console.print(f"[OS LOG] [RAID 0] Sağlıklı Durum Okuma: {raid.read_raid_0('level1_tex')}")
    console.print(f"[OS LOG] [RAID 1] Sağlıklı Durum Okuma: {raid.read_raid_1('level1_tex')}")
    
    # Inject Disk 0 Failure
    console.print("[bold red][FAULT INJECTION] !!! Disk 0 Arızalandı (FAILED) !!![/bold red]")
    raid.fail_disk(0)
    
    # Read under degraded condition
    r0_data = raid.read_raid_0("level1_tex")
    r1_data = raid.read_raid_1("level1_tex")
    
    console.print(f"[OS LOG] [RAID 0] Disk Çöküşü Sonrası Okuma: [bold red]{r0_data if r0_data else 'HATA: VERİ KAYBI (None)'}[/bold red]")
    console.print(f"[OS LOG] [RAID 1] Disk Çöküşü Sonrası Okuma: [bold green]{r1_data if r1_data else 'HATA: VERİ KAYBI'}[/bold green] (Aynadan Başarıyla Kurtarıldı)")
    
    # RAID 1 Rebuild
    success, msg = raid.recover_raid_1()
    console.print(f"[OS LOG] [RAID 1] {msg}")
    console.print(f"[OS LOG] [RAID 1] Kurtarma Sonrası Okuma: {raid.read_raid_1('level1_tex')}\n")
    
    # 3. Journaling Filesystem
    console.print("[bold yellow]--- Journaled Filesystem ve Crash Consistency / Recovery ---[/bold yellow]")
    vfs = VirtualFileSystem()
    jfs = JournaledFileSystem(vfs)
    
    # Transaction 1: Successful write
    jfs.write_file("/user/saves/auto_save.dat", "LEVEL:5,HP:100", simulate_crash_after_journal_start=False, log_callback=console.print)
    
    # Transaction 2: Crash write
    jfs.write_file("/user/saves/cloud_save.dat", "COINS:50000,SKIN:GOLDEN", simulate_crash_after_journal_start=True, log_callback=console.print)
    
    console.print("\n[bold white]VFS Durumu (Çöküş Hemen Sonrası):[/bold white]")
    console.print(vfs.get_structure())
    
    # Reboot and Recovery
    jfs.recover(log_callback=console.print)
    
    console.print("\n[bold white]VFS Durumu (Kurtarma Sonrası Kararlı Durum):[/bold white]")
    console.print(vfs.get_structure())

def handle_ssd_hdd():
    console.print("\n[bold yellow]>>> SSD vs HDD Donanım ve Erişim Süresi Karşılaştırma Analizi...[/bold yellow]")
    
    requests = [12, 140, 85, 30, 195, 42, 10, 110, 64, 180]
    
    hdd_fcfs = SSDvsHDDAnalysis.simulate_hdd_time(requests, "FCFS", head_start=50)
    hdd_sstf = SSDvsHDDAnalysis.simulate_hdd_time(requests, "SSTF", head_start=50)
    ssd_time = SSDvsHDDAnalysis.simulate_ssd_time(requests)
    
    PerformancePlotter.plot_ssd_hdd_comparison(hdd_fcfs, hdd_sstf, ssd_time, "ssd_hdd.png")
    
    table = Table(title="HDD vs SSD Simüle Edilmiş I/O Gecikme Raporu (10 Disk İsteği)", box=box.ROUNDED)
    table.add_column("Sürücü Tipi & Planlayıcı", style="cyan")
    table.add_column("Toplam Erişim Süresi (Gecikme)", style="yellow")
    table.add_column("Mekanik Kafa Seek / Rotasyon Durumu", style="white")
    
    table.add_row("HDD (FCFS - Baseline)", f"{hdd_fcfs:.2f} ms", "Seek Süresi Yoğun, Dönme Gecikmesi Sabit")
    table.add_row("HDD (SSTF - Planlama)", f"{hdd_sstf:.2f} ms", "Seek Süresi Optimize, Dönme Gecikmesi Sabit")
    table.add_row("SSD (Gecikmesiz Katı Hâl)", f"{ssd_time:.2f} ms", "Seek Yok, Plaka Yok, Tamamen Flash Bellek (100x Hızlı)")
    
    console.print(table)
    console.print("[bold green][OS LOG] Başarı: SSD vs HDD karşılaştırma grafiği 'ssd_hdd.png' olarak kaydedildi.[/bold green]\n")
    
    console.print(Panel(SSDvsHDDAnalysis.get_comparison_discussion(), border_style="yellow", title="[bold yellow]SSD vs HDD Discussion & Architectural Insights[/bold yellow]"))

def generate_all_plots():
    console.print("\n[bold yellow]>>> Tüm Grafiksel Raporlar (PNG Grafik Dosyaları) Oluşturuluyor...[/bold yellow]")
    
    # 1. Gantt Chart
    log_messages = []
    fcfs_procs = get_fresh_workload()
    run_fcfs(fcfs_procs, log_messages.append)
    rr_procs = get_fresh_workload()
    run_round_robin(rr_procs, 4, log_messages.append)
    mlfq_procs = get_fresh_workload()
    run_mlfq(mlfq_procs, [2, 4, 8], 20, log_messages.append)
    PerformancePlotter.plot_scheduler_gantt(fcfs_procs, rr_procs, mlfq_procs, "gantt_chart.png")
    
    # 2. Page Fault Chart
    ref_string = [1, 3, 0, 3, 5, 6, 3, 1, 3, 2, 1, 4, 5, 2]
    capacities = [2, 3, 4, 5]
    results = PageReplacementSimulator.compare_algorithms(ref_string, capacities)
    PerformancePlotter.plot_page_replacement(capacities, results["fifo"], results["lru"], "page_faults.png")
    
    # 3. Disk Scheduling Chart
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    head_start = 53
    _, fcfs_path = DiskScheduler.simulate_fcfs(head_start, requests)
    _, sstf_path = DiskScheduler.simulate_sstf(head_start, requests)
    PerformancePlotter.plot_disk_scheduling(head_start, requests, fcfs_path, sstf_path, "disk_scheduling.png")
    
    # 4. SSD vs HDD Chart
    hdd_fcfs = SSDvsHDDAnalysis.simulate_hdd_time(requests, "FCFS", head_start=head_start)
    hdd_sstf = SSDvsHDDAnalysis.simulate_hdd_time(requests, "SSTF", head_start=head_start)
    ssd_time = SSDvsHDDAnalysis.simulate_ssd_time(requests)
    PerformancePlotter.plot_ssd_hdd_comparison(hdd_fcfs, hdd_sstf, ssd_time, "ssd_hdd.png")
    
    console.print("[bold green][OS LOG] Başarı: Tüm şemalar başarıyla kaydedildi:[/bold green]")
    console.print("  - gantt_chart.png (Zamanlama Gantt Tabloları)")
    console.print("  - page_faults.png (FIFO vs LRU Page Fault Grafiği)")
    console.print("  - disk_scheduling.png (FCFS vs SSTF Kafa Yolu Şeması)")
    console.print("  - ssd_hdd.png (SSD vs HDD Erişim Süresi Karşılaştırma Grafiği)")

def main():
    while True:
        try:
            show_menu()
            choice = console.input("\n[bold yellow]Seçiminiz (1-9 veya Q): [/bold yellow]").strip().upper()
            
            if choice == "Q":
                console.print("\n[bold green]Simulator Kapatılıyor. İyi çalışmalar![/bold green]\n")
                break
            elif choice == "1":
                handle_scheduling()
            elif choice == "2":
                handle_priority_inversion()
            elif choice == "3":
                handle_paging_tlb()
            elif choice == "4":
                handle_segmentation()
            elif choice == "5":
                handle_page_replacement()
            elif choice == "6":
                handle_concurrency_semaphores()
            elif choice == "7":
                handle_storage_journaling()
            elif choice == "8":
                handle_ssd_hdd()
            elif choice == "9":
                generate_all_plots()
            else:
                console.print("\n[bold red]Geçersiz Seçim! Lütfen listeden bir rakam girin.[/bold red]")
                
            console.input("\n[dim]Menüye dönmek için ENTER tuşuna basın...[/dim]")
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
        except KeyboardInterrupt:
            console.print("\n\n[bold green]Simulator Kapatılıyor. İyi çalışmalar![/bold green]\n")
            break

if __name__ == "__main__":
    main()
