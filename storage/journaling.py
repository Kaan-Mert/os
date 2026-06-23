# storage/journaling.py

class JournalTransaction:
    def __init__(self, tx_id, filepath, content, state="START"):
        self.tx_id = tx_id # İşlem (Transaction) numarası
        self.filepath = filepath # Değişiklik yapılan dosya yolu
        self.content = content # Yazılacak yeni veri
        self.state = state  # İşlem durumu (START: Başladı, COMMIT: Başarıyla Günlüğe Yazıldı)

class JournaledFileSystem:
    """Simulates Crash Consistency via Journaling (Module 15) for a filesystem."""
    
    def __init__(self, vfs):
        self.vfs = vfs
        self.journal = []  # JournalTransaction nesnelerini tutan günlük listesi
        self.next_tx_id = 1
        
    def write_file(self, filepath, content, simulate_crash_after_journal_start=False, log_callback=print):
        """Simulates writing a file using Metadata Journaling.
        Can inject a simulated crash immediately after the journal 'START' is written.
        """
        tx_id = self.next_tx_id
        self.next_tx_id += 1
        
        # 1. Günlüğe 'START' kaydını yazıyoruz (İşlemin başladığını beyan ediyoruz)
        log_callback(f"[OS LOG] [JOURNAL] [Tx {tx_id}] Journal yazılıyor: START | Dosya: {filepath}")
        tx = JournalTransaction(tx_id, filepath, content, state="START")
        self.journal.append(tx)
        
        # Simüle edilmiş çöküş (crash) enjeksiyonu
        if simulate_crash_after_journal_start:
            log_callback(f"[OS LOG] [CRASH] !!! SİSTEM ÇÖKTÜ (Simulated Crash) !!! Yazım tamamlanmadan elektrik kesintisi oluştu.")
            return False, "CRASHED"
            
        # 2. Gerçek dosya sistemine (VFS) veriyi yazıyoruz
        log_callback(f"[OS LOG] [FS] [Tx {tx_id}] Veri disk bloklarına yazılıyor...")
        self.vfs.create_file(filepath, content)
        
        # 3. Günlüğe 'COMMIT' kaydını yazarak işlemin başarıyla bittiğini onaylıyoruz
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
            
        # Journal listesinin kopyası üzerinde dönüyoruz
        for tx in list(self.journal):
            # Durumu COMMIT olan işlemleri yeniden uyguluyoruz (Redo/Replay)
            if tx.state == "COMMIT":
                log_callback(f"[OS LOG] [JOURNAL RECOVERY] [Tx {tx.tx_id}] Bulundu: COMMIT. Redo/Replay yapılıyor: {tx.filepath}")
                self.vfs.create_file(tx.filepath, tx.content)
            # Durumu sadece START olan (yarım kalmış, çökmüş) işlemleri geri alıyoruz (Rollback)
            elif tx.state == "START":
                log_callback(f"[OS LOG] [JOURNAL RECOVERY] [Tx {tx.tx_id}] Bulundu: START (COMMIT yok). Yarım kalan işlem geri alınıyor (Rollback): {tx.filepath}")
                # Kısmen yazılmış olabilecek dosyayı diskten siliyoruz
                self.vfs.delete_file(tx.filepath)
                
        # Günlüğü temizliyoruz (Checkpoint / Flush)
        self.journal.clear()
        log_callback("[OS LOG] [JOURNAL RECOVERY] Kurtarma tamamlandı. Sistem kararlı duruma getirildi. Journal sıfırlandı.")
