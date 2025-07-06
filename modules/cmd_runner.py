# -*- coding: utf-8 -*-
# author    : mefamex
# Created   : 2025-07-03-23:30
# file_name : cmd_runner.py
# version   : 0.5
#

""" updates :

- 2025-07-03-23:41:00 -v0.0 : Hata mesajları için daha iyi bir çıktı formatı eklendi.
- 2025-07-03-23:45:00 -v0.1 : CodeExecutor sınıfı ile yeniden yazıldı. Güvenli çalışma alanı,
                                farklı dil desteği, dosya işlemleri ve gelişmiş hata yönetimi eklendi.
                                Testler Windows ortamına uygun hale getirildi.
- 2025-07-03-23:49:00 -v0.2 : Çalışma alanı (work_dir) artık kullanıcının ev dizini yerine,
                                projenin mevcut dizini içinde oluşturuluyor.
- 2025-07-03-23:55:00 -v0.3 : Boş çıktı veren komutlar için özel mesaj düzeltildi.
                                Unicode karakter sorunları için encoding 'cp65001' olarak denendi.
                                Temizleme sırasında log dosyası hatası (WinError 32) giderildi.
- 2025-07-03-23:59:00 -v0.4 : Temizleme hatası için daha güçlü bir çözüm uygulandı (logging handlers).
                                Unicode kodlama 'utf-8'e geri döndürüldü, Windows konsol sınırlaması not edildi.
                                Boş çıktı testindeki sorun için mantık kontrol edildi.
- 2025-07-06-18:10:00 -v0.5 : Workspace oluşturma kaldırıldı. Mevcut dizin kullanılacak.
                                Log dosyaları "logs/cmd_runner_logs/" altında timestamp ile oluşturulacak.

"""
import subprocess, shutil, time, logging, os
from pathlib import Path
from typing import Dict, Any

FILE_ENCODING : str = 'utf-8'  # Windows konsol sınırlamaları nedeniyle 'cp65001' yerine 'utf-8' kullanıldı

class CodeExecutor:
    def __init__(self, work_dir: str = "", timeout: int = 30):
        """
        CMD kodlarını ve komutlarını güvenli şekilde çalıştıran executor
        
        Args:
            work_dir: Çalışma dizini (None ise mevcut dizin kullanılır)
            timeout: Maksimum çalışma süresi (saniye)
        """
        self.timeout      : int = timeout
        self.work_dir     : str = work_dir or os.getcwd()
        self.log_filepath : Path
        self.log_filename : str
        self.log_dir      : Path
        self.cmd_runner_logs_dir : Path
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Logging ayarları - logs/cmd_runner_logs/ altında timestamp ile dosya oluşturur"""
        # Ana logs klasörü
        self.log_dir = Path(self.work_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # cmd_runner_logs alt klasörü
        self.cmd_runner_logs_dir = self.log_dir / "cmd_runner_logs"
        self.cmd_runner_logs_dir.mkdir(exist_ok=True)
        
        # Timestamp ile log dosyası adı
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"cmd_runner_logs_{timestamp}.log"
        self.log_filepath = self.cmd_runner_logs_dir / self.log_filename
        
        # Mevcut handler'ları temizle
        logger = logging.getLogger(__name__)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

        # Yeni logging yapılandırması
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_filepath, encoding=FILE_ENCODING),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"CodeExecutor başlatıldı - Log dosyası: {self.log_filepath}")
    
    def execute_cmd(self, command: str) -> Dict[str, Any]:
        """
        CMD komutunu çalıştır
        
        Args:
            command: Çalıştırılacak komut
            
        Returns:
            Dict: Çalıştırma sonuçları
        """
        try:
            while command.startswith('\n') or command.startswith('\r'):command = command[1:]
            while command.endswith('\n') or command.endswith('\r'):command = command[:-1]
            with open(self.log_filepath, 'w', encoding=FILE_ENCODING) as f: f.write("#\n#\n#\n#\n#\n")
            self.logger.info(f"COMMAND: {command}")
            ## komuttaki metine kadar olan ilk satır atlamaların hepsini temizle
            
            newfile = False
            # if command more than 1 line write it to bat file and run there
            if "\n" in command:
                bat_file_path = Path(self.work_dir) / "tempCodeRunner.bat"
                txt_output_path = Path(self.work_dir) / "tempCodeRunner.txt"
                with open(bat_file_path, 'w', encoding=FILE_ENCODING) as f: f.write(f"{command}\n")
                with open(txt_output_path, 'w', encoding=FILE_ENCODING) as f: f.write("\n")
                command = f"call {bat_file_path} >> {txt_output_path} 2>&1"
                newfile = True

            result = subprocess.run(
                command,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding=FILE_ENCODING,
                errors='replace' 
            )
            if newfile:
                if txt_output_path.exists():
                    file_output = txt_output_path.read_text(encoding=FILE_ENCODING)
                    result.stdout = file_output
                    result.stderr = ""
                else:
                    result.stdout = ""
                    result.stderr = "Çıktı dosyası bulunamadı."
            stdout_output = result.stdout.strip()
            stderr_output = result.stderr.strip()

            # Boş çıktı durumunda özel mesaj
            if not stdout_output and not stderr_output and result.returncode == 0:
                stdout_output = "COMMAND EXECUTED BUT PRODUCED NO OUTPUT."
            
            # Sonucu logla
            if stdout_output: self.logger.info(f"STDOUT : {stdout_output}")
            if stderr_output: self.logger.warning(f"STDERR : {stderr_output}")

            return {
                "success": True,
                "exit_code": result.returncode,
                "stdout": stdout_output,
                "stderr": stderr_output,
                "command": command,
                "execution_time": time.time()
            }
            
        except subprocess.TimeoutExpired:
            error_msg = f"Komut {self.timeout} saniye içinde tamamlanamadı"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "exit_code": -1,
                "stdout": "",
                "stderr": "TimeoutExpired"
            }
        except Exception as e:
            error_msg = f"Komut hatası: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def cleanup(self) -> None:
        """Logging handler'larını temizle"""
        try:
            logger = logging.getLogger(__name__)
            for handler in list(logger.handlers): 
                handler.close()
                logger.removeHandler(handler)
            self.logger.info("CodeExecutor temizlendi")
        except Exception as e:
            print(f"Temizleme hatası: {e}")
    
    def test(self) -> None:
        """Basit test fonksiyonu: echo, hatalı komut ve boş çıktı testleri"""
        test_cases = [
            {"name": "echo testi", "command": "echo Merhaba Test!", "expect": "Merhaba Test!"},
            {"name": "hatalı komut", "command": "bu_komut_yok", "expect": ["not found", "bulunamadı", "tanınmıyor"]},
            {"name": "boş çıktı", "command": ": > emptyfile && rm emptyfile", "expect": "KOMUT ÇALIŞTI AMA EKRANA BİR ÇIKTI ÜRETMEDİ."}
        ]
        passed = 0
        for i, t in enumerate(test_cases):
            print(f"\n--- TEST {i+1}: {t['name']} ---")
            result = self.execute_cmd(t["command"])
            output = (result.get("stdout") or "") + (result.get("stderr") or "")
            print(f"ÇIKTI:\n{output}")
            if isinstance(t["expect"], list):
                if any(e.lower() in output.lower() for e in t["expect"]):
                    print("BAŞARILI!"); passed += 1
                else:
                    print("BAŞARISIZ!")
            else:
                if t["expect"].lower() in output.lower():
                    print("BAŞARILI!"); passed += 1
                else:
                    print("BAŞARISIZ!")
        print(f"\n{passed}/{len(test_cases)} test başarılı.")

# Test
def run_tests():
    """Test fonksiyonunu çalıştır"""
    executor = CodeExecutor()
    print("Testler başlatılıyor...")
    executor.test()
    print("Testler tamamlandı.")
    executor.cleanup()


# --- Ana Program Döngüsü ---
if __name__ == "__main__":
    main_executor = CodeExecutor() 
    print("Mefamex-AI Otonom Agent Köprüsü v0.4 - CMD Komut Yürütücü Aktif")
    print(f"Çalışma dizini: {main_executor.work_dir}")
    print("Çıkmak için 'exit' veya 'quit' yazın. 'test' yazarak testleri çalıştırabilirsiniz.")
    while True:
        user_command = input("\nMefamex> ")
        if user_command.lower() == "test":
            main_executor.test()
            continue
        if user_command.lower() in ["exit", "quit"]:
            print("Köprü sonlandırılıyor. Hoşça kal!")
            main_executor.cleanup() 
            break
        command_output_result = main_executor.execute_cmd(user_command)
        output_str = ""
        if command_output_result.get("stdout"):
            output_str += f"SONUÇ:\n{command_output_result['stdout']}\n"
        if command_output_result.get("stderr"):
            output_str += f"HATA:\n{command_output_result['stderr']}\n"
        if not output_str.strip() and command_output_result.get("success"):
            output_str = "KOMUT ÇALIŞTI AMA EKRANA BİR ÇIKTI ÜRETMEDİ."
        elif command_output_result.get("error") and not output_str.strip():
            output_str = f"İŞLEM HATASI: {command_output_result['error']}"
        print(output_str)