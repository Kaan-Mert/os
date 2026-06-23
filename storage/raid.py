# storage/raid.py

class VirtualDisk:
    """Represents a physical hard drive block array in a RAID setup."""
    def __init__(self, size_blocks=64):
        self.blocks = [None] * size_blocks
        self.status = "ONLINE"  # ONLINE veya FAILED (Disk durumu)

    def read_block(self, idx):
        if self.status == "FAILED":
            raise IOError("Disk is offline!")
        return self.blocks[idx]

    def write_block(self, idx, data):
        if self.status == "FAILED":
            raise IOError("Disk is offline!")
        self.blocks[idx] = data


class RAIDSystem:
    """Simulates RAID 0 (Striping) and RAID 1 (Mirroring) operations (Module 13)."""
    
    def __init__(self, size_blocks=16):
        self.size_blocks = size_blocks
        # İki adet fiziksel disk nesnesi ilklendiriliyor
        self.disk0 = VirtualDisk(size_blocks)
        self.disk1 = VirtualDisk(size_blocks)
        
    def reset_disks(self):
        self.disk0 = VirtualDisk(self.size_blocks)
        self.disk1 = VirtualDisk(self.size_blocks)

    def write_raid_0(self, filename, content):
        """RAID 0 Striping: Splits content into odd/even character blocks."""
        # Veriyi 2'şer karakterlik bloklara ayırıyoruz (List comprehension yerine standart döngü)
        blocks = []
        for i in range(0, len(content), 2):
            blocks.append(content[i:i+2])
        
        # Disk kapasitesi aşılıyorsa kırpıyoruz
        if len(blocks) > self.size_blocks * 2:
            blocks = blocks[:self.size_blocks * 2]
            
        # RAID 0'da disklerden biri bile arızalıysa yazma yapılamaz
        if self.disk0.status == "FAILED" or self.disk1.status == "FAILED":
            return False, "HATA: Disklerden biri arızalı olduğu için RAID 0 yazımı başarısız oldu!"
            
        for idx in range(len(blocks)):
            blk = blocks[idx]
            disk_idx = idx % 2 # Çift indisli bloklar Disk 0'a, tek indisli bloklar Disk 1'a (Striping)
            block_offset = idx // 2
            if disk_idx == 0:
                self.disk0.write_block(block_offset, (filename, blk))
            else:
                self.disk1.write_block(block_offset, (filename, blk))
        return True, f"RAID 0 Yazımı Başarılı: {len(blocks)} blok 2 diske dağıtıldı."

    def read_raid_0(self, filename):
        """Reads and reassembles striped blocks under RAID 0."""
        # Disklerden biri bile arızalıysa veri bütünlüğü bozulur ve veri okunamaz (RAID 0 hataya dayanıklı değildir)
        if self.disk0.status == "FAILED" or self.disk1.status == "FAILED":
            return None
            
        reconstructed = []
        for idx in range(self.size_blocks * 2):
            disk_idx = idx % 2
            block_offset = idx // 2
            if disk_idx == 0:
                entry = self.disk0.read_block(block_offset)
            else:
                entry = self.disk1.read_block(block_offset)
                
            if entry is not None and entry[0] == filename:
                reconstructed.append(entry[1])
            elif entry is None:
                break
        return "".join(reconstructed)

    def write_raid_1(self, filename, content):
        """RAID 1 Mirroring: Writes identical data blocks to both disks."""
        # List comprehension yerine standart döngü
        blocks = []
        for i in range(0, len(content), 2):
            blocks.append(content[i:i+2])
            
        if len(blocks) > self.size_blocks:
            blocks = blocks[:self.size_blocks]
            
        # Her iki disk de arızalıysa yazma başarısız olur
        if self.disk0.status == "FAILED" and self.disk1.status == "FAILED":
            return False, "HATA: Disklerin tamamı arızalı!"
            
        # Diskler çalışıyorsa veriyi ikisine de aynalayıp yazıyoruz (Aynalama - Mirroring)
        if self.disk0.status == "ONLINE":
            for idx in range(len(blocks)):
                self.disk0.write_block(idx, (filename, blocks[idx]))
                
        if self.disk1.status == "ONLINE":
            for idx in range(len(blocks)):
                self.disk1.write_block(idx, (filename, blocks[idx]))
                
        status = "Çift disk aynalandı"
        if self.disk0.status == "FAILED" or self.disk1.status == "FAILED":
            status = "Tek diske yazıldı (Yedeklilik Kaybı)"
            
        return True, f"RAID 1 Yazımı Başarılı ({status})."

    def read_raid_1(self, filename):
        """Reads data from any online mirrored drive."""
        # Disklerden herhangi biri aktifse veriyi okuyabiliriz (RAID 1 hata toleransı sağlar)
        if self.disk0.status == "ONLINE":
            reconstructed = []
            for idx in range(self.size_blocks):
                entry = self.disk0.read_block(idx)
                if entry is not None and entry[0] == filename:
                    reconstructed.append(entry[1])
            return "".join(reconstructed)
        elif self.disk1.status == "ONLINE":
            reconstructed = []
            for idx in range(self.size_blocks):
                entry = self.disk1.read_block(idx)
                if entry is not None and entry[0] == filename:
                    reconstructed.append(entry[1])
            return "".join(reconstructed)
        else:
            return None  # İki disk de göçtüyse veri kaybı kaçınılmazdır

    def fail_disk(self, disk_num):
        # Simülasyonda arıza enjekte etmek için diski FAILED durumuna getiriyoruz
        if disk_num == 0:
            self.disk0.status = "FAILED"
        else:
            self.disk1.status = "FAILED"

    def recover_raid_1(self):
        """Rebuilds failed drive mirroring in RAID 1 by copying blocks from the active drive."""
        # Arızalanan diski değiştirip sağlam diskteki verileri yeni diske kopyalıyoruz (Rebuild)
        if self.disk0.status == "FAILED" and self.disk1.status == "ONLINE":
            self.disk0.status = "ONLINE"
            self.disk0.blocks = list(self.disk1.blocks)
            return True, "Disk 0, Disk 1 üzerinden başarıyla senkronize edildi (RAID 1 Kurtarıldı)."
        elif self.disk1.status == "FAILED" and self.disk0.status == "ONLINE":
            self.disk1.status = "ONLINE"
            self.disk1.blocks = list(self.disk0.blocks)
            return True, "Disk 1, Disk 0 üzerinden başarıyla senkronize edildi (RAID 1 Kurtarıldı)."
        return False, "Kurtarma başarısız. Her iki disk de zaten çevrimiçi veya her ikisi de çökmüş!"
