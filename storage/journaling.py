# storage/journaling.py

class JournalTransaction:
    def __init__(self, tx_id, filepath, content, state="START"):
        self.tx_id = tx_id
        self.filepath = filepath
        self.content = content
        self.state = state  # START or COMMIT

class JournaledFileSystem:
    """Simulates Crash Consistency via Journaling (Module 15) for a filesystem."""
    
    def __init__(self, vfs):
        self.vfs = vfs
        self.journal = []  # List of JournalTransaction objects
        self.next_tx_id = 1
        
    def write_file(self, filepath, content, simulate_crash_after_journal_start=False, log_callback=print):
        """Simulates writing a file using Metadata Journaling.
        Can inject a simulated crash immediately after the journal 'START' is written.
        """
        tx_id = self.next_tx_id
        self.next_tx_id += 1
        
        # 1. Write 'START' to Journal
        log_callback(f"[OS LOG] [JOURNAL] [Tx {tx_id}] Journal yazılıyor: START | Dosya: {filepath}")
        tx = JournalTransaction(tx_id, filepath, content, state="START")
        self.journal.append(tx)
        
        # Simulated fault injection
        if simulate_crash_after_journal_start:
            log_callback(f"[OS LOG] [CRASH] !!! SİSTEM ÇÖKTÜ (Simulated Crash) !!! Yazım tamamlanmadan elektrik kesintisi oluştu.")
            return False, "CRASHED"
            
        # 2. Write to actual File System
        log_callback(f"[OS LOG] [FS] [Tx {tx_id}] Veri disk bloklarına yazılıyor...")
        self.vfs.create_file(filepath, content)
        
        # 3. Write 'COMMIT' to Journal
        tx.state = "COMMIT"
        log_callback(f"[OS LOG] [JOURNAL] [Tx {tx_id}] Journal güncelleniyor: COMMIT")
        return True, "SUCCESS"

    def recover(self, log_callback=print):
        """Scans the journal to restore filesystem consistency after a crash.
        Redoes transactions with COMMIT, and discards (rolls back) transactions with only START.
        """
        log_callback("\n[OS LOG] [JOURNAL RECOVERY] Kurtarma mekanizması başlatılıyor...")
        
        if not self.journal:
            log_callback("[OS LOG] [JOURNAL RECOVERY] Temiz kapanış saptandı. Journal boş.")
            return
            
        for tx in list(self.journal):
            if tx.state == "COMMIT":
                # Redo/Replay: Ensure the file is written
                log_callback(f"[OS LOG] [JOURNAL RECOVERY] [Tx {tx.tx_id}] Bulundu: COMMIT. Redo/Replay yapılıyor: {tx.filepath}")
                self.vfs.create_file(tx.filepath, tx.content)
            elif tx.state == "START":
                # Rollback: Discard changes
                log_callback(f"[OS LOG] [JOURNAL RECOVERY] [Tx {tx.tx_id}] Bulundu: START (COMMIT yok). Yarım kalan işlem geri alınıyor (Rollback): {tx.filepath}")
                # Remove from disk if it was partially written
                self.vfs.delete_file(tx.filepath)
                
        # Flush/Checkpoint the journal
        self.journal.clear()
        log_callback("[OS LOG] [JOURNAL RECOVERY] Kurtarma tamamlandı. Sistem kararlı duruma getirildi. Journal sıfırlandı.")
