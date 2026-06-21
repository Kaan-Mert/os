# analysis/performance.py

import matplotlib.pyplot as plt

class PerformancePlotter:
    """Generates and saves performance visualization plots (Matplotlib) directly to disk."""
    
    @staticmethod
    def plot_scheduler_gantt(fcfs_procs, rr_procs, mlfq_procs, filename="gantt_chart.png"):
        """Saves comparison Gantt Chart for FCFS, RR, and MLFQ algorithms."""
        fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
        fig.suptitle("Mini OS Scheduler Gantt Chart Karşılaştırması\n(Game Console OS Theme)", fontsize=16, fontweight='bold', color='#1a1a1a')
        
        # Consistent color palette for console workloads
        colors = {
            "Gamepad Input Handler": "#2ca02c",
            "Game Engine Render": "#1f77b4",
            "Audio Processing": "#ff7f0e",
            "Network Download": "#9467bd",
            "Background Game Save": "#d62728"
        }
        
        def draw_gantt_on_axis(ax, procs, title):
            ax.set_title(title, fontsize=12, fontweight='bold', loc='left', color='#333333')
            ax.grid(True, linestyle="--", alpha=0.5, zorder=0)
            
            sorted_procs = sorted(procs, key=lambda x: x.pid)
            y_labels = [p.name for p in sorted_procs]
            ax.set_yticks(range(len(y_labels)))
            ax.set_yticklabels(y_labels, fontsize=9, fontweight='semibold')
            
            for idx, p in enumerate(sorted_procs):
                for interval in p.execution_intervals:
                    start, end = interval
                    duration = end - start
                    color = colors.get(p.name, "#7f7f7f")
                    ax.barh(idx, duration, left=start, align='center', color=color, alpha=0.85, edgecolor='black', linewidth=0.8, zorder=3)
                    if duration >= 1:
                        ax.text(start + duration/2, idx, f"{duration}", ha='center', va='center', color='white', fontweight='bold', fontsize=8, zorder=4)
                        
            ax.set_ylim(-0.5, len(y_labels) - 0.5)
            
        draw_gantt_on_axis(axes[0], fcfs_procs, "1. First-Come, First-Served (FCFS) - [Baseline]")
        draw_gantt_on_axis(axes[1], rr_procs, "2. Round Robin (RR, Quantum=4) - [Time Shared]")
        draw_gantt_on_axis(axes[2], mlfq_procs, "3. Multi-Level Feedback Queue (MLFQ, Q=[2,4,8], Boost=20) - [Enhanced]")
        
        axes[2].set_xlabel("Sanal Zaman Birimi (Tick)", fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        fig.subplots_adjust(top=0.90)
        plt.savefig(filename, dpi=300)
        plt.close()

    @staticmethod
    def plot_page_replacement(capacities, fifo_faults, lru_faults, filename="page_faults.png"):
        """Plots line chart comparing Page Fault rates of FIFO and LRU algorithms."""
        plt.figure(figsize=(9, 5))
        plt.plot(capacities, fifo_faults, marker='o', color='#d62728', linestyle='-', linewidth=2, label='FIFO (Baseline)')
        plt.plot(capacities, lru_faults, marker='s', color='#1f77b4', linestyle='--', linewidth=2, label='LRU (Enhanced)')
        
        plt.title("Sayfa Değiştirme Algoritmaları Hata Oranı Karşılaştırması\n(FIFO vs LRU Page Fault Comparison)", fontsize=12, fontweight='bold')
        plt.xlabel("Fiziksel Bellek Sayfa Çerçevesi Kapasitesi (Physical Frame Capacity)", fontsize=10, fontweight='semibold')
        plt.ylabel("Toplam Page Fault (Sayfa Hatası) Sayısı", fontsize=10, fontweight='semibold')
        plt.xticks(capacities)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(frameon=True, facecolor='white', edgecolor='gray')
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()

    @staticmethod
    def plot_disk_scheduling(initial_head, requests, fcfs_path, sstf_path, filename="disk_scheduling.png"):
        """Plots track-path line chart for FCFS vs SSTF head movements."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        fig.suptitle("Disk Kafası Planlama Yolu Karşılaştırması (FCFS vs SSTF)", fontsize=14, fontweight='bold')
        
        # FCFS Plot
        ax1.plot(range(len(fcfs_path)), fcfs_path, marker='o', color='#ff7f0e', linewidth=2, label='Kafa Hareket Yolu')
        ax1.set_title("First-Come, First-Served (FCFS)", fontsize=11, fontweight='semibold')
        ax1.set_ylabel("Disk Silindir İz Numarası (Cylinder Track)", fontsize=10)
        ax1.set_xlabel("İşlem Sırası (Request Index)", fontsize=10)
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()
        
        # Annotate order
        for i, val in enumerate(fcfs_path):
            ax1.annotate(f"#{i}", (i, val), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, fontweight='bold')
            
        # SSTF Plot
        ax2.plot(range(len(sstf_path)), sstf_path, marker='s', color='#2ca02c', linewidth=2, label='Kafa Hareket Yolu')
        ax2.set_title("Shortest Seek Time First (SSTF)", fontsize=11, fontweight='semibold')
        ax2.set_xlabel("İşlem Sırası (Request Index)", fontsize=10)
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend()
        
        # Annotate order
        for i, val in enumerate(sstf_path):
            ax2.annotate(f"#{i}", (i, val), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, fontweight='bold')

        plt.tight_layout()
        fig.subplots_adjust(top=0.88)
        plt.savefig(filename, dpi=300)
        plt.close()

    @staticmethod
    def plot_ssd_hdd_comparison(hdd_fcfs_time, hdd_sstf_time, ssd_time, filename="ssd_hdd.png"):
        """Plots bar chart comparing simulated total access time in milliseconds."""
        plt.figure(figsize=(9, 5))
        labels = ['HDD (FCFS)', 'HDD (SSTF)', 'SSD (Any)']
        times_ms = [hdd_fcfs_time, hdd_sstf_time, ssd_time]
        colors = ['#ff7f0e', '#2ca02c', '#1f77b4']
        
        bars = plt.bar(labels, times_ms, color=colors, edgecolor='black', width=0.5, zorder=3)
        plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
        
        plt.title("SSD vs HDD Veri Erişim Süresi Performans Karşılaştırması\n(Simüle Edilmiş I/O Gecikmesi)", fontsize=12, fontweight='bold')
        plt.ylabel("Toplam Erişim Gecikmesi (Milisaniye - ms)", fontsize=10, fontweight='semibold')
        
        # Add labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.5, f"{height:.2f} ms", ha='center', va='bottom', fontweight='bold', fontsize=9)
            
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
