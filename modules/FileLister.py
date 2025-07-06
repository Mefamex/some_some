# -*- coding: utf-8 -*-
"""
Simple Directory Explorer
Basit Dizin Keşif Aracı

Bu araç, belirtilen dizin yapısını analiz eder ve detaylı bilgilerle sunar.
"""

import os
import datetime
import fnmatch


class DirectoryExplorer:
    """
    Dizin yapısını analiz eden ve görselleştiren basit sınıf.
    """
    
    def __init__(self, root_path="", 
                show_size=False, 
                show_date=False, 
                show_folder_count=False,
                skip_hidden=True,
                skip_patterns=None,
                skip_site_packages_details=True):
        """
        DirectoryExplorer sınıfını başlatır.
        
        Args:
            root_path (str): Analiz edilecek dizin yolu (boş ise mevcut dizin)
            show_size (bool): Dosya boyutlarını göster
            show_date (bool): Tarih bilgilerini göster
            show_folder_count (bool): Klasör içindeki öğe sayısını göster
            skip_hidden (bool): Gizli dosya/klasörleri atla
            skip_patterns (list): Atlanacak dosya/klasör desenleri
            skip_site_packages_details (bool): site-packages içeriğini basitleştir
        """
        # Ayarlar
        self.root_path = root_path or os.getcwd()
        self.show_size = show_size
        self.show_date = show_date
        self.show_folder_count = show_folder_count
        self.skip_hidden = skip_hidden
        self.skip_patterns = skip_patterns or []
        self.skip_site_packages_details = skip_site_packages_details
        
        # Çıktı ayarları
        self.tab_size = 4
        self.output_width = 50
        self.output_lines = []
        
        # Başlat
        self._print_header()
        self._explore_directory()
        self._save_output()
    
    def _print_header(self):
        """Başlık bilgilerini yazdırır."""
        header = f"""
{'='*80}
    DIRECTORY EXPLORER / DİZİN KEŞİF ARACI
{'='*80}
Analiz Edilen Dizin: {self.root_path}
Tarih: {self._format_timestamp(datetime.datetime.now().timestamp())}
{'='*80}"""
        
        # Sütun başlıkları
        if self.show_folder_count or self.show_size or self.show_date:
            column_header = f"{'NAME':<60}"
            if self.show_folder_count:
                column_header += f"{'COUNT':<12}"
            if self.show_size:
                column_header += f"{'SIZE':<10}"
            if self.show_date:
                column_header += f"{'MODIFIED':<20}"
            
            header += f"\n{column_header}\n{'-'*80}"
        
        print(header)
        self.output_lines.append(header)
    
    def _format_timestamp(self, timestamp):
        """Unix timestamp'i okunabilir formata çevirir."""
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def _should_skip(self, name, path, is_dir):
        """Dosya/klasörün atlanıp atlanmayacağını kontrol eder."""
        # Gizli dosyalar
        if self.skip_hidden and name.startswith('.'):
            return True
        
        # Özel desenler
        rel_path = os.path.relpath(path, self.root_path)
        for pattern in self.skip_patterns:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
        
        return False
    
    def _format_size(self, size_bytes):
        """Boyutu okunabilir formata çevirir."""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _get_item_info(self, path):
        """Dosya/klasör bilgilerini alır."""
        try:
            stat = os.stat(path)
            return {
                'size': stat.st_size,
                'modified': self._format_timestamp(stat.st_mtime),
                'is_dir': os.path.isdir(path)
            }
        except (OSError, IOError):
            return {
                'size': 0,
                'modified': 'N/A',
                'is_dir': os.path.isdir(path)
            }
    
    def _count_items(self, dir_path):
        """Klasördeki öğe sayısını hesaplar."""
        try:
            items = os.listdir(dir_path)
            return len([item for item in items if not self._should_skip(item, os.path.join(dir_path, item), os.path.isdir(os.path.join(dir_path, item)))])
        except (OSError, IOError):
            return 0
    
    def _format_output_line(self, name, depth, info, item_count=None):
        """Çıktı satırını formatlar."""
        # Indent
        indent = "│" + " " * (self.tab_size - 1)
        prefix = indent * depth
        
        # İsim
        if info['is_dir']:
            icon = ">"
            name_part = f"{icon} {name}/"
        else:
            icon = "-"
            name_part = f"{icon} {name}"
        
        # Sabit genişlikli sütunlar için hazırla
        full_name = prefix + name_part
        
        # Sütun genişlikleri
        name_width = 60
        count_width = 12
        size_width = 10
        date_width = 20
        
        # Sütun içerikleri
        count_str = ""
        size_str = ""
        date_str = ""
        
        if self.show_folder_count and info['is_dir'] and item_count is not None:
            count_str = f"({item_count})"
        
        if self.show_size and not info['is_dir']:
            size_str = self._format_size(info['size'])
        
        if self.show_date:
            date_str = info['modified']
        
        # Sütunları hizala
        formatted_line = f"{full_name:<{name_width}}"
        
        if self.show_folder_count:
            formatted_line += f"{count_str:<{count_width}}"
        
        if self.show_size:
            formatted_line += f"{size_str:<{size_width}}"
        
        if self.show_date:
            formatted_line += f"{date_str:<{date_width}}"
        
        return formatted_line.rstrip()
    
    def _explore_directory(self, current_path=None, depth=0):
        """Dizini rekürsif olarak keşfeder."""
        if current_path is None:
            current_path = self.root_path
        
        try:
            # Dizin içeriğini al
            items = os.listdir(current_path)
            
            # Dosya ve klasörleri ayır
            dirs = []
            files = []
            
            for item in items:
                item_path = os.path.join(current_path, item)
                
                if self._should_skip(item, item_path, os.path.isdir(item_path)):
                    continue
                
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            # Sırala
            dirs.sort()
            files.sort()
            
            # Önce klasörleri işle
            for dir_name in dirs:
                dir_path = os.path.join(current_path, dir_name)
                info = self._get_item_info(dir_path)
                item_count = self._count_items(dir_path)
                
                line = self._format_output_line(dir_name, depth, info, item_count)
                print(line)
                self.output_lines.append(line)
                
                # site-packages özel durumu
                rel_path = os.path.relpath(dir_path, self.root_path)
                if self.skip_site_packages_details and 'site-packages' in rel_path.lower():
                    # Sadece ilk seviye içeriği göster
                    try:
                        sub_items = os.listdir(dir_path)[:5]  # İlk 5 öğe
                        for sub_item in sub_items:
                            sub_path = os.path.join(dir_path, sub_item)
                            sub_info = self._get_item_info(sub_path)
                            sub_line = self._format_output_line(sub_item, depth + 1, sub_info)
                            print(sub_line)
                            self.output_lines.append(sub_line)
                        if len(os.listdir(dir_path)) > 5:
                            more_line = f"{'│' + ' ' * (self.tab_size - 1) * (depth + 1)}... ({len(os.listdir(dir_path)) - 5} more items)"
                            print(more_line)
                            self.output_lines.append(more_line)
                    except (OSError, IOError):
                        pass
                else:
                    # Normal rekürsif keşif
                    self._explore_directory(dir_path, depth + 1)
            
            # Sonra dosyaları işle
            for file_name in files:
                file_path = os.path.join(current_path, file_name)
                info = self._get_item_info(file_path)
                
                line = self._format_output_line(file_name, depth, info)
                print(line)
                self.output_lines.append(line)
                
        except (OSError, IOError) as e:
            error_line = f"{'│' + ' ' * (self.tab_size - 1) * depth}❌ Error accessing: {e}"
            print(error_line)
            self.output_lines.append(error_line)
    
    def _save_output(self):
        """Çıktıyı dosyaya kaydeder."""
        try:
            # Dosya adı oluştur
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"DirectoryExplorer_{timestamp}.txt"
            
            # Dosyayı kaydet
            with open(filename, 'w', encoding='utf-8') as f:
                self.output_lines.append("================================================================================\n")
                f.write('\n'.join(self.output_lines))

            print(f"\n{'='*80}")
            print(f"Çıktı kaydedildi: {os.path.join(os.getcwd(), filename)}")
            print(f"{'='*80}")
            
        except (OSError, IOError) as e:
            print(f"Dosya kaydedilirken hata: {e}")




def main():
    """Ana fonksiyon - örnek kullanım."""
    print("Directory Explorer başlatılıyor...")
    
    # Basit kullanım
    # explorer = DirectoryExplorer()
    
    # Detaylı kullanım örneği:
    explorer = DirectoryExplorer(
        root_path=os.getcwd(),  # Mevcut dizin
        show_size=True,
        show_date=True,
        show_folder_count=True,
        skip_hidden=True,
        skip_patterns=['*.tmp', '*.log', '__pycache__', 'node_modules'],
        skip_site_packages_details=True
    )


if __name__ == "__main__":
    main()