@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ########################################
echo #####                              #####
echo #####   REMOTE DEVICE ASSISTANT    #####
echo #####        PROJECT SETUP         #####
echo #####          @MEFAMEX            #####
echo #####                              #####
echo ########################################
echo.

:: Renkli çıktı için
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

:: Python sürümünü kontrol et
echo %YELLOW%[INFO]%RESET% Python sürümü kontrol ediliyor...
python --version 2>nul
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Python bulunamadı! Lütfen Python 3.13.5 yükleyin.
    pause
    exit /b 1
)

:: Python sürümünü al
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[OK]%RESET% Python sürümü: %PYTHON_VERSION%

:: Proje dizinini oluştur
set PROJECT_NAME=remote-device-assistant
set PROJECT_DIR=%cd%\%PROJECT_NAME%

if exist "%PROJECT_DIR%" (
    echo %YELLOW%[WARNING]%RESET% Proje dizini zaten mevcut: %PROJECT_DIR%
    set /p "OVERWRITE=Üzerine yazmak istiyor musunuz? (y/N): "
    if /i "!OVERWRITE!" neq "y" (
        echo %RED%[ABORT]%RESET% Kurulum iptal edildi.
        pause
        exit /b 1
    )
    echo %YELLOW%[INFO]%RESET% Mevcut dizin temizleniyor...
    rmdir /s /q "%PROJECT_DIR%" 2>nul
)

echo %GREEN%[INFO]%RESET% Proje dizini oluşturuluyor: %PROJECT_DIR%
mkdir "%PROJECT_DIR%" 2>nul

:: Ana proje yapısını oluştur
echo %GREEN%[INFO]%RESET% Proje yapısı oluşturuluyor...
cd "%PROJECT_DIR%"

:: Dizin yapısını oluştur
mkdir src\rda\core
mkdir src\rda\modules\c2
mkdir src\rda\modules\cmd
mkdir src\rda\modules\ai
mkdir src\rda\modules\updater
mkdir src\rda\utils
mkdir src\rda\security
mkdir config
mkdir logs
mkdir tests\unit
mkdir tests\integration
mkdir docs
mkdir scripts\windows
mkdir scripts\linux
mkdir scripts\macos
mkdir data\keys
mkdir data\cache

:: Virtual environment oluştur
echo %GREEN%[INFO]%RESET% Virtual environment oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Virtual environment oluşturulamadı!
    pause
    exit /b 1
)

:: Virtual environment'ı aktifleştir
echo %GREEN%[INFO]%RESET% Virtual environment aktifleştiriliyor...
call venv\Scripts\activate.bat

:: Gerekli paketleri yükle
echo %GREEN%[INFO]%RESET% Gerekli Python paketleri yükleniyor...
python -m pip install --upgrade pip

:: Requirements.txt oluştur ve yükle
echo aiohttp>=3.9.0> requirements.txt
echo cryptography>=41.0.0>> requirements.txt
echo python-telegram-bot>=20.7>> requirements.txt
echo pydantic>=2.5.0>> requirements.txt
echo google-generativeai>=0.3.0>> requirements.txt
echo openai>=1.6.0>> requirements.txt
echo pillow>=10.1.0>> requirements.txt
echo psutil>=5.9.0>> requirements.txt
echo pyjwt>=2.8.0>> requirements.txt
echo python-dotenv>=1.0.0>> requirements.txt
echo watchdog>=3.0.0>> requirements.txt
echo pywin32>=306;sys_platform=="win32">> requirements.txt
echo pycryptodomex>=3.19.0>> requirements.txt
echo schedule>=1.2.0>> requirements.txt
echo click>=8.1.0>> requirements.txt
echo rich>=13.7.0>> requirements.txt
echo pytest>=7.4.0>> requirements.txt
echo pytest-asyncio>=0.21.0>> requirements.txt
echo black>=23.12.0>> requirements.txt
echo flake8>=6.1.0>> requirements.txt
echo mypy>=1.8.0>> requirements.txt

pip install -r requirements.txt

:: Development requirements
echo pytest-cov>=4.1.0> requirements-dev.txt
echo bandit>=1.7.5>> requirements-dev.txt
echo safety>=2.3.0>> requirements-dev.txt
echo pre-commit>=3.6.0>> requirements-dev.txt

pip install -r requirements-dev.txt

echo %GREEN%[SUCCESS]%RESET% Python paketleri başarıyla yüklendi!

:: Proje dosyalarını oluştur
echo %GREEN%[INFO]%RESET% Proje dosyaları oluşturuluyor...

:: Ana setup.py
echo from setuptools import setup, find_packages> setup.py
echo.>> setup.py
echo setup(>> setup.py
echo     name="remote-device-assistant",>> setup.py
echo     version="1.0.0",>> setup.py
echo     description="Remote Device Assistant - Secure cross-platform device management",>> setup.py
echo     author="@MEFAMEX",>> setup.py
echo     packages=find_packages(where="src"^),>> setup.py
echo     package_dir={"": "src"},>> setup.py
echo     python_requires=">=3.13",>> setup.py
echo     install_requires=open("requirements.txt"^).read().splitlines(^),>> setup.py
echo     entry_points={>> setup.py
echo         "console_scripts": [>> setup.py
echo             "rda=rda.main:main",>> setup.py
echo         ],>> setup.py
echo     },>> setup.py
echo ^)>> setup.py

:: Geliştirme araçları
echo %GREEN%[INFO]%RESET% Geliştirme araçları yapılandırılıyor...

:: pytest.ini
echo [pytest]> pytest.ini
echo testpaths = tests>> pytest.ini
echo python_files = test_*.py>> pytest.ini
echo python_classes = Test*>> pytest.ini
echo python_functions = test_*>> pytest.ini
echo addopts = -v --tb=short --strict-markers>> pytest.ini
echo markers =>> pytest.ini
echo     slow: marks tests as slow>> pytest.ini
echo     integration: marks tests as integration tests>> pytest.ini
echo     security: marks tests as security tests>> pytest.ini

:: .gitignore
echo # Python> .gitignore
echo __pycache__/>> .gitignore
echo *.py[cod]>> .gitignore
echo *$py.class>> .gitignore
echo *.so>> .gitignore
echo .Python>> .gitignore
echo build/>> .gitignore
echo develop-eggs/>> .gitignore
echo dist/>> .gitignore
echo downloads/>> .gitignore
echo eggs/>> .gitignore
echo .eggs/>> .gitignore
echo lib/>> .gitignore
echo lib64/>> .gitignore
echo parts/>> .gitignore
echo sdist/>> .gitignore
echo var/>> .gitignore
echo wheels/>> .gitignore
echo *.egg-info/>> .gitignore
echo .installed.cfg>> .gitignore
echo *.egg>> .gitignore
echo.>> .gitignore
echo # Virtual Environment>> .gitignore
echo venv/>> .gitignore
echo env/>> .gitignore
echo ENV/>> .gitignore
echo.>> .gitignore
echo # IDE>> .gitignore
echo .vscode/>> .gitignore
echo .idea/>> .gitignore
echo *.swp>> .gitignore
echo *.swo>> .gitignore
echo.>> .gitignore
echo # Project specific>> .gitignore
echo config/local_config.json>> .gitignore
echo logs/*.log>> .gitignore
echo data/cache/*>> .gitignore
echo data/keys/private_*>> .gitignore
echo .env>> .gitignore

:: Black configuration
echo [tool.black]> pyproject.toml
echo line-length = 88>> pyproject.toml
echo target-version = ["py313"]>> pyproject.toml
echo include = '\.pyi?$'>> pyproject.toml
echo.>> pyproject.toml
echo [tool.mypy]>> pyproject.toml
echo python_version = "3.13">> pyproject.toml
echo warn_return_any = true>> pyproject.toml
echo warn_unused_configs = true>> pyproject.toml
echo disallow_untyped_defs = true>> pyproject.toml
echo.>> pyproject.toml
echo [tool.pytest.ini_options]>> pyproject.toml
echo testpaths = ["tests"]>> pyproject.toml
echo python_files = "test_*.py">> pyproject.toml

:: Makefile (Windows için)
echo # RDA Project Makefile> Makefile
echo.>> Makefile
echo .PHONY: help install test lint format clean run>> Makefile
echo.>> Makefile
echo help:>> Makefile
echo 	@echo "Available commands:">> Makefile
echo 	@echo "  install    - Install dependencies">> Makefile
echo 	@echo "  test       - Run tests">> Makefile
echo 	@echo "  lint       - Run linting">> Makefile
echo 	@echo "  format     - Format code">> Makefile
echo 	@echo "  clean      - Clean build artifacts">> Makefile
echo 	@echo "  run        - Run the application">> Makefile
echo.>> Makefile
echo install:>> Makefile
echo 	pip install -r requirements.txt>> Makefile
echo 	pip install -r requirements-dev.txt>> Makefile
echo.>> Makefile
echo test:>> Makefile
echo 	pytest tests/ -v>> Makefile
echo.>> Makefile
echo lint:>> Makefile
echo 	flake8 src/ tests/>> Makefile
echo 	mypy src/>> Makefile
echo 	bandit -r src/>> Makefile
echo.>> Makefile
echo format:>> Makefile
echo 	black src/ tests/>> Makefile
echo.>> Makefile
echo clean:>> Makefile
echo 	find . -type f -name "*.pyc" -delete>> Makefile
echo 	find . -type d -name "__pycache__" -delete>> Makefile
echo 	rm -rf build/ dist/ *.egg-info/>> Makefile
echo.>> Makefile
echo run:>> Makefile
echo 	python -m rda.main>> Makefile

:: Başlangıç batch dosyaları
echo %GREEN%[INFO]%RESET% Batch dosyaları oluşturuluyor...

:: run.bat
echo @echo off> run.bat
echo call venv\Scripts\activate.bat>> run.bat
echo python -m rda.main %*>> run.bat
echo pause>> run.bat

:: test.bat
echo @echo off> test.bat
echo call venv\Scripts\activate.bat>> test.bat
echo pytest tests/ -v>> test.bat
echo pause>> test.bat

:: format.bat
echo @echo off> format.bat
echo call venv\Scripts\activate.bat>> format.bat
echo black src/ tests/>> format.bat
echo echo Code formatted successfully!>> format.bat
echo pause>> format.bat

:: lint.bat
echo @echo off> lint.bat
echo call venv\Scripts\activate.bat>> lint.bat
echo flake8 src/ tests/>> lint.bat
echo mypy src/>> lint.bat
echo bandit -r src/>> lint.bat
echo pause>> lint.bat

:: activate.bat
echo @echo off> activate.bat
echo call venv\Scripts\activate.bat>> activate.bat
echo cmd /k>> activate.bat

echo %GREEN%[SUCCESS]%RESET% Batch dosyaları oluşturuldu!

:: README.md
echo # Remote Device Assistant (RDA)> README.md
echo.>> README.md
echo ^> **Secure cross-platform device management with AI integration**>> README.md
echo.>> README.md
echo ## Features>> README.md
echo.>> README.md
echo - 🔐 **Security-First**: Zero-trust architecture with TLS encryption>> README.md
echo - 🤖 **AI Integration**: Natural language command processing>> README.md
echo - 🔧 **Modular Design**: Plugin-based architecture>> README.md
echo - 🌐 **Cross-Platform**: Windows, macOS, Linux support>> README.md
echo - 📱 **Telegram Integration**: Secure remote control via Telegram>> README.md
echo - 🔄 **Self-Evolution**: Secure auto-update mechanism>> README.md
echo.>> README.md
echo ## Quick Start>> README.md
echo.>> README.md
echo ```bash>> README.md
echo # Activate virtual environment>> README.md
echo ./activate.bat>> README.md
echo.>> README.md
echo # Run the application>> README.md
echo ./run.bat>> README.md
echo.>> README.md
echo # Run tests>> README.md
echo ./test.bat>> README.md
echo ```>> README.md
echo.>> README.md
echo ## Project Structure>> README.md
echo.>> README.md
echo ```>> README.md
echo src/rda/>> README.md
echo ├── core/           # Core agent functionality>> README.md
echo ├── modules/        # Modular components>> README.md
echo │   ├── c2/         # Command & Control>> README.md
echo │   ├── cmd/        # Command execution>> README.md
echo │   ├── ai/         # AI integration>> README.md
echo │   └── updater/    # Self-update mechanism>> README.md
echo ├── utils/          # Utility functions>> README.md
echo └── security/       # Security components>> README.md
echo ```>> README.md
echo.>> README.md
echo ## Configuration>> README.md
echo.>> README.md
echo Copy `config/config.template.json` to `config/local_config.json` and configure:>> README.md
echo.>> README.md
echo ```json>> README.md
echo {>> README.md
echo   "agent_id": "your-device-name",>> README.md
echo   "admin_chat_id": "YOUR_TELEGRAM_CHAT_ID",>> README.md
echo   "c2": {>> README.md
echo     "telegram_bot_token": "YOUR_BOT_TOKEN">> README.md
echo   }>> README.md
echo }>> README.md
echo ```>> README.md
echo.>> README.md
echo ## License>> README.md
echo.>> README.md
echo © @MEFAMEX - All rights reserved>> README.md

echo %GREEN%[SUCCESS]%RESET% README.md oluşturuldu!

echo.
echo %GREEN%[SUCCESS]%RESET% RDA Projesi başarıyla kuruldu!
echo.
echo %BLUE%Proje dizini:%RESET% %PROJECT_DIR%
echo %BLUE%Virtual environment:%RESET% %PROJECT_DIR%\venv
echo.
echo %YELLOW%Sonraki adımlar:%RESET%
echo 1. activate.bat ile virtual environment'ı aktifleştirin
echo 2. config/local_config.json dosyasını düzenleyin
echo 3. run.bat ile uygulamayı başlatın
echo.
echo %GREEN%Kullanılabilir komutlar:%RESET%
echo - activate.bat  : Virtual environment aktifleştir
echo - run.bat       : Uygulamayı çalıştır  
echo - test.bat      : Testleri çalıştır
echo - format.bat    : Kodu formatla
echo - lint.bat      : Kod kalitesi kontrolü
echo.
echo %GREEN%[INFO]%RESET% Kurulum tamamlandı! İyi çalışmalar!
echo.
pause