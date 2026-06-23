# storage/filesystem.py

class VirtualFile:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content
        self.size = len(content)

class VirtualDirectory:
    def __init__(self, name):
        self.name = name
        self.files = {} # Klasör içindeki dosyalar (dosya_adı -> VirtualFile)
        self.subdirs = {} # Alt klasörler (klasör_adı -> VirtualDirectory)


class VirtualFileSystem:
    """Simulates a Hierarchical File System (Module 14)."""
    
    def __init__(self):
        self.root = VirtualDirectory("/") # Kök dizin (Root Directory) oluşturuluyor
        
    def _parse_path(self, path):
        """Splits path into components. Returns list of directory names."""
        # Dosya yolunu parçalara ayırıyoruz (Örn: "/user/saves" -> ["user", "saves"])
        # Liste üreteci (list comprehension) yerine standart bir döngü kullanılmıştır
        parts = []
        for p in path.split("/"):
            if p:
                parts.append(p)
        return parts

    def _resolve_dir(self, path_parts):
        """Walks directory tree. Returns VirtualDirectory if valid, or None."""
        # Verilen dizin yolunu kök dizinden başlayarak adım adım geziyoruz (Tree Walk)
        current = self.root
        for part in path_parts:
            if part in current.subdirs:
                current = current.subdirs[part]
            else:
                return None # Alt dizin bulunamazsa None döner
        return current

    def mkdir(self, path):
        """Creates a directory path.
        Example: mkdir("/user/saves")
        """
        parts = self._parse_path(path)
        if not parts:
            return False, "HATA: Geçersiz dizin adı."
            
        parent_parts = parts[:-1]
        dir_name = parts[-1]
        
        parent_dir = self._resolve_dir(parent_parts)
        if parent_dir is None:
            # Üst dizinler mevcut değilse onları sırasıyla özyinelemeli/otomatik oluşturuyoruz
            current = self.root
            for part in parent_parts:
                if part not in current.subdirs:
                    current.subdirs[part] = VirtualDirectory(part)
                current = current.subdirs[part]
            parent_dir = current
            
        if dir_name in parent_dir.subdirs:
            return False, f"HATA: Dizin zaten mevcut: '{dir_name}'"
            
        parent_dir.subdirs[dir_name] = VirtualDirectory(dir_name)
        return True, f"Dizin oluşturuldu: {path}"

    def create_file(self, file_path, content=""):
        """Creates or overwrites a file in the VFS."""
        parts = self._parse_path(file_path)
        if not parts:
            return False, "HATA: Geçersiz dosya adı."
            
        parent_parts = parts[:-1]
        file_name = parts[-1]
        
        parent_dir = self._resolve_dir(parent_parts)
        if parent_dir is None:
            # Üst klasör yoksa önce onu oluşturuyoruz
            self.mkdir("/" + "/".join(parent_parts))
            parent_dir = self._resolve_dir(parent_parts)
            
        # Dosyayı ilgili klasörün dosyalar sözlüğüne kaydediyoruz
        parent_dir.files[file_name] = VirtualFile(file_name, content)
        return True, f"Dosya oluşturuldu: {file_path} ({len(content)} byte)"

    def lookup(self, file_path):
        """Looks up a file. Returns contents if found, or None."""
        parts = self._parse_path(file_path)
        if not parts:
            return None
            
        parent_parts = parts[:-1]
        file_name = parts[-1]
        
        # Dosyanın bulunduğu klasörü çözümleyip dosyayı arıyoruz
        parent_dir = self._resolve_dir(parent_parts)
        if parent_dir is not None and file_name in parent_dir.files:
            return parent_dir.files[file_name].content
        return None

    def delete_file(self, file_path):
        """Removes a file from the VFS."""
        parts = self._parse_path(file_path)
        if not parts:
            return False, "HATA: Geçersiz yol."
            
        parent_parts = parts[:-1]
        file_name = parts[-1]
        
        parent_dir = self._resolve_dir(parent_parts)
        if parent_dir is not None and file_name in parent_dir.files:
            del parent_dir.files[file_name]
            return True, f"Dosya silindi: {file_path}"
        return False, f"HATA: Dosya bulunamadı: {file_path}"

    def get_structure(self):
        """Returns a string listing the entire directory structure (recursively)."""
        # Tüm dizin ağacını derinlik öncelikli arama (DFS) mantığıyla gezerek ekrana basılacak formatta metin üretiyoruz
        lines = []
        def _walk(directory, depth=0):
            indent = "  " * depth
            lines.append(f"{indent}[DIR] {directory.name}/")
            for subdir in directory.subdirs.values():
                _walk(subdir, depth + 1)
            for f in directory.files.values():
                lines.append(f"{indent}  [FILE] {f.name} ({f.size} bytes)")
        _walk(self.root)
        return "\n".join(lines)
