# storage/raid.py

class VirtualDisk:
    """Represents a physical hard drive block array in a RAID setup."""
    def __init__(self, size_blocks=64):
        self.blocks = [None] * size_blocks
        self.status = "ONLINE"  # ONLINE, FAILED

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
        # Initialize two physical disks
        self.disk0 = VirtualDisk(size_blocks)
        self.disk1 = VirtualDisk(size_blocks)
        
    def reset_disks(self):
        self.disk0 = VirtualDisk(self.size_blocks)
        self.disk1 = VirtualDisk(self.size_blocks)

    def write_raid_0(self, filename, content):
        """RAID 0 Striping: Splits content into odd/even character blocks."""
        # Convert string to list of character blocks
        blocks = [content[i:i+2] for i in range(0, len(content), 2)]
        
        # If too large, truncate
        if len(blocks) > self.size_blocks * 2:
            blocks = blocks[:self.size_blocks * 2]
            
        try:
            for idx, blk in enumerate(blocks):
                disk_idx = idx % 2
                block_offset = idx // 2
                if disk_idx == 0:
                    self.disk0.write_block(block_offset, (filename, blk))
                else:
                    self.disk1.write_block(block_offset, (filename, blk))
            return True, f"RAID 0 Yazımı Başarılı: {len(blocks)} blok 2 diske dağıtıldı."
        except IOError:
            return False, "HATA: Disklerden biri arızalı olduğu için RAID 0 yazımı başarısız oldu!"

    def read_raid_0(self, filename):
        """Reads and reassembles striped blocks under RAID 0."""
        reconstructed = []
        try:
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
                    # End of file data blocks
                    break
            return "".join(reconstructed)
        except IOError:
            return None  # Total data loss under RAID 0 if a drive is down

    def write_raid_1(self, filename, content):
        """RAID 1 Mirroring: Writes identical data blocks to both disks."""
        blocks = [content[i:i+2] for i in range(0, len(content), 2)]
        if len(blocks) > self.size_blocks:
            blocks = blocks[:self.size_blocks]
            
        disk0_ok, disk1_ok = False, False
        
        # Write to Disk 0 if active
        try:
            for idx, blk in enumerate(blocks):
                self.disk0.write_block(idx, (filename, blk))
            disk0_ok = True
        except IOError:
            pass

        # Write to Disk 1 if active
        try:
            for idx, blk in enumerate(blocks):
                self.disk1.write_block(idx, (filename, blk))
            disk1_ok = True
        except IOError:
            pass
            
        if disk0_ok or disk1_ok:
            status = "Çift disk aynalandı" if (disk0_ok and disk1_ok) else "Tek diske yazıldı (Yedeklilik Kaybı)"
            return True, f"RAID 1 Yazımı Başarılı ({status})."
        return False, "HATA: Disklerin tamamı arızalı!"

    def read_raid_1(self, filename):
        """Reads data from any online mirrored drive."""
        # Try Disk 0
        try:
            reconstructed = []
            for idx in range(self.size_blocks):
                entry = self.disk0.read_block(idx)
                if entry is not None and entry[0] == filename:
                    reconstructed.append(entry[1])
            return "".join(reconstructed)
        except IOError:
            # Fallback to Disk 1
            try:
                reconstructed = []
                for idx in range(self.size_blocks):
                    entry = self.disk1.read_block(idx)
                    if entry is not None and entry[0] == filename:
                        reconstructed.append(entry[1])
                return "".join(reconstructed)
            except IOError:
                return None  # Both failed

    def fail_disk(self, disk_num):
        if disk_num == 0:
            self.disk0.status = "FAILED"
        else:
            self.disk1.status = "FAILED"

    def recover_raid_1(self):
        """Rebuilds failed drive mirroring in RAID 1 by copying blocks from the active drive."""
        if self.disk0.status == "FAILED" and self.disk1.status == "ONLINE":
            # Rebuild Disk 0 from Disk 1
            self.disk0.status = "ONLINE"
            self.disk0.blocks = list(self.disk1.blocks)
            return True, "Disk 0, Disk 1 üzerinden başarıyla senkronize edildi (RAID 1 Kurtarıldı)."
        elif self.disk1.status == "FAILED" and self.disk0.status == "ONLINE":
            # Rebuild Disk 1 from Disk 0
            self.disk1.status = "ONLINE"
            self.disk1.blocks = list(self.disk0.blocks)
            return True, "Disk 1, Disk 0 üzerinden başarıyla senkronize edildi (RAID 1 Kurtarıldı)."
        return False, "Kurtarma başarısız. Her iki disk de zaten çevrimiçi veya her ikisi de çökmüş!"
