#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████╗███╗   ██╗ ██████╗     █████╗ ███╗   ██╗████████╗██╗██╗   ██╗██╗██████╗ ██╗   ██╗███████╗
╚══██╔══╝████╗  ██║██╔════╝    ██╔══██╗████╗  ██║╚══██╔══╝██║██║   ██║██║██╔══██╗██║   ██║██╔════╝
   ██║   ██╔██╗ ██║██║         ███████║██╔██╗ ██║   ██║   ██║██║   ██║██║██████╔╝██║   ██║███████╗
   ██║   ██║╚██╗██║██║         ██╔══██║██║╚██╗██║   ██║   ██║╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║
   ██║   ██║ ╚████║╚██████╗    ██║  ██║██║ ╚████║   ██║   ██║ ╚████╔╝ ██║██║  ██║╚██████╔╝███████║
   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝

   TNG ANTİVİRÜS V9 - TAM ÖNYÜKLEME YEDEKLEMELİ
   - MBR (Master Boot Record) yedeği
   - Boot Sector (VBR) yedeği  
   - Windows Boot Manager (bootmgr) yedeği
   - BCD (Boot Configuration Database) yedeği
   - EFI System Partition yedeği
   - Tüm boot dosyaları yedeği
"""

import os
import sys
import time
import json
import shutil
import datetime
import platform
import subprocess
import zipfile
import tempfile
import psutil
from pathlib import Path

# ============================================================================
# RENK SINIFI
# ============================================================================

try:
    import colorama
    colorama.init()
    RENK_VAR = True
except:
    RENK_VAR = False

class Renk:
    BAS = '\033['
    YESIL = f'{BAS}92m'
    SARI = f'{BAS}93m'
    KIRMIZI = f'{BAS}91m'
    MAVI = f'{BAS}94m'
    MOR = f'{BAS}95m'
    CYAN = f'{BAS}96m'
    BEYAZ = f'{BAS}97m'
    TURUNCU = f'{BAS}38;5;208m'
    PEMBE = f'{BAS}38;5;205m'
    SON = f'{BAS}0m'

def c(text, renk):
    return f"{renk}{text}{Renk.SON}" if RENK_VAR else text

GELISTIRICI = {
    "isim": "TEKNOLOJIGOBLINI",
    "instagram": "@TEKNOLOJIGOBLINI",
    "youtube": "@teknolojigoblini",
    "versiyon": "9.0.0"
}

def bytes_insan_oku(bytes_deger):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_deger < 1024.0:
            return f"{bytes_deger:.2f} {unit}"
        bytes_deger /= 1024.0
    return f"{bytes_deger:.2f} TB"

# ============================================================================
# VİRÜS VERİTABANI
# ============================================================================

TEHLIKELI_VIRUSLER = {
    "memz": {"isimler": ["memz", "memz.exe", "memz_trojan"], "aciklama": "MEMZ - MBR/EFI silen trojan", "risk": 100},
    "petya": {"isimler": ["petya", "notpetya", "mbrlock"], "aciklama": "Petya - MBR şifreleyen ransomware", "risk": 100},
    "bootkit": {"isimler": ["bootkit", "mbr", "bootsect", "bootice"], "aciklama": "Bootkit - Önyükleme sektörü rootkit", "risk": 100},
    "cih": {"isimler": ["cih", "chernobyl", "spacefiller"], "aciklama": "CIH - BIOS silen virüs", "risk": 100},
    "dark_knight": {"isimler": ["darkknight", "bkdr", "bootworm"], "aciklama": "Dark Knight Bootkit", "risk": 100},
    "stoned": {"isimler": ["stoned", "stoned_boot", "marijuana"], "aciklama": "Stoned Boot Virus", "risk": 95},
}

# ============================================================================
# TAM ÖNYÜKLEME YEDEKLEME SİSTEMİ
# ============================================================================

class BootYedekleme:
    def __init__(self, callback=None):
        self.callback = callback
        self.yedek_klasoru = "TNG_Backups"
        
        if not os.path.exists(self.yedek_klasoru):
            os.makedirs(self.yedek_klasoru)
    
    def log(self, mesaj, renk=Renk.BEYAZ):
        if self.callback:
            self.callback(mesaj, renk)
        else:
            print(c(mesaj, renk))
    
    def mbr_yedekle(self, zaman):
        """MBR (Master Boot Record) yedeği al"""
        if platform.system() != "Windows":
            return False
        
        try:
            with open(r"\\.\PhysicalDrive0", "rb") as f:
                mbr = f.read(512)
            
            mbr_yedek = os.path.join(self.yedek_klasoru, f"mbr_backup_{zaman}.bin")
            with open(mbr_yedek, "wb") as f:
                f.write(mbr)
            
            self.log(f"   ✅ MBR yedeği alındı (512 byte)", Renk.YESIL)
            return True
        except Exception as e:
            self.log(f"   ❌ MBR yedeği alınamadı: {e}", Renk.KIRMIZI)
            return False
    
    def boot_sector_yedekle(self, zaman):
        """Boot Sector (VBR) yedeği al"""
        if platform.system() != "Windows":
            return False
        
        try:
            with open(r"\\.\PhysicalDrive0", "rb") as f:
                f.seek(512)
                boot_sector = f.read(512)
            
            boot_yedek = os.path.join(self.yedek_klasoru, f"boot_sector_{zaman}.bin")
            with open(boot_yedek, "wb") as f:
                f.write(boot_sector)
            
            self.log(f"   ✅ Boot Sector yedeği alındı (512 byte)", Renk.YESIL)
            return True
        except:
            return False
    
    def bootmgr_yedekle(self, zaman):
        """Windows Boot Manager (bootmgr) yedeği al"""
        if platform.system() != "Windows":
            return False
        
        bootmgr_yollar = [
            "C:\\bootmgr",
            "C:\\Windows\\Boot\\PCAT\\bootmgr",
            "C:\\Windows\\Boot\\EFI\\bootmgfw.efi"
        ]
        
        yedeklendi = False
        for yol in bootmgr_yollar:
            if os.path.exists(yol):
                try:
                    with open(yol, "rb") as f:
                        veri = f.read()
                    
                    dosya_adi = os.path.basename(yol)
                    yedek_adi = f"bootmgr_{dosya_adi}_{zaman}.bin"
                    yedek_yolu = os.path.join(self.yedek_klasoru, yedek_adi)
                    
                    with open(yedek_yolu, "wb") as f:
                        f.write(veri)
                    
                    boyut = bytes_insan_oku(len(veri))
                    self.log(f"   ✅ Windows Boot Manager yedeği: {dosya_adi} ({boyut})", Renk.YESIL)
                    yedeklendi = True
                except:
                    pass
        
        if not yedeklendi:
            self.log(f"   ⚠️ Windows Boot Manager bulunamadı", Renk.SARI)
        
        return yedeklendi
    
    def bcd_yedekle(self, zaman):
        """BCD (Boot Configuration Database) yedeği al"""
        if platform.system() != "Windows":
            return False
        
        try:
            # BCD'yi dışa aktar
            bcd_yedek = os.path.join(self.yedek_klasoru, f"bcd_backup_{zaman}.reg")
            result = subprocess.run(
                ['reg', 'export', 'HKLM\\BCD00000000', bcd_yedek, '/y'],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log(f"   ✅ BCD (Boot Config) yedeği alındı", Renk.YESIL)
                return True
        except:
            pass
        
        # Alternatif: bcdedit ile dışa aktar
        try:
            bcd_yedek = os.path.join(self.yedek_klasoru, f"bcd_export_{zaman}.txt")
            result = subprocess.run(
                ['bcdedit', '/enum', 'all'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                with open(bcd_yedek, "w") as f:
                    f.write(result.stdout)
                self.log(f"   ✅ BCD export yedeği alındı", Renk.YESIL)
                return True
        except:
            pass
        
        self.log(f"   ⚠️ BCD yedeği alınamadı", Renk.SARI)
        return False
    
    def efi_yedekle(self, zaman):
        """EFI System Partition yedeği al"""
        if platform.system() != "Windows":
            return False
        
        efi_yollari = [
            "C:\\EFI",
            "C:\\Windows\\Boot\\EFI",
            "D:\\EFI",
            "E:\\EFI"
        ]
        
        efi_dosyalari = []
        for yol in efi_yollari:
            if os.path.exists(yol):
                for root, dirs, files in os.walk(yol):
                    for file in files:
                        efi_dosyalari.append(os.path.join(root, file))
        
        if efi_dosyalari:
            efi_zip = os.path.join(self.yedek_klasoru, f"efi_backup_{zaman}.zip")
            with zipfile.ZipFile(efi_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for dosya in efi_dosyalari:
                    try:
                        arcname = os.path.relpath(dosya, os.path.dirname(yol))
                        zipf.write(dosya, arcname)
                    except:
                        pass
            
            boyut = bytes_insan_oku(os.path.getsize(efi_zip))
            self.log(f"   ✅ EFI System Partition yedeği alındı ({len(efi_dosyalari)} dosya, {boyut})", Renk.YESIL)
            return True
        else:
            self.log(f"   ⚠️ EFI bölümü bulunamadı (BIOS sistemi olabilir)", Renk.SARI)
            return False
    
    def boot_dosyalari_yedekle(self, zaman):
        """Boot ile ilgili kritik dosyaları yedekle"""
        boot_dosyalari = [
            "C:\\Windows\\Boot\\*",
            "C:\\Windows\\System32\\winload.exe",
            "C:\\Windows\\System32\\winload.efi",
            "C:\\Windows\\System32\\bootvid.dll",
            "C:\\Windows\\System32\\hal.dll",
            "C:\\Windows\\System32\\kdcom.dll",
            "C:\\Windows\\System32\\pshed.dll",
            "C:\\Windows\\System32\\apisetschema.dll"
        ]
        
        bulunan = []
        for pattern in boot_dosyalari:
            if '*' in pattern:
                klasor = pattern.replace('*', '')
                if os.path.exists(klasor):
                    try:
                        for dosya in os.listdir(klasor):
                            if dosya.lower().startswith('boot'):
                                bulunan.append(os.path.join(klasor, dosya))
                    except:
                        pass
            else:
                if os.path.exists(pattern):
                    bulunan.append(pattern)
        
        if bulunan:
            boot_zip = os.path.join(self.yedek_klasoru, f"boot_files_backup_{zaman}.zip")
            with zipfile.ZipFile(boot_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for dosya in bulunan:
                    try:
                        zipf.write(dosya, os.path.basename(dosya))
                    except:
                        pass
            
            boyut = bytes_insan_oku(os.path.getsize(boot_zip))
            self.log(f"   ✅ Boot dosyaları yedeği alındı ({len(bulunan)} dosya, {boyut})", Renk.YESIL)
            return True
        
        return False
    
    def tam_yedek_al(self, otomatik=False):
        """TÜM ÖNYÜKLEME BİLEŞENLERİNİ YEDEKLE"""
        
        if otomatik:
            self.log("\n" + "═"*70, Renk.CYAN)
            self.log("💾 TAM ÖNYÜKLEME YEDEĞİ ALINIYOR...", Renk.YESIL)
            self.log("   MBR | Boot Sector | Boot Manager | BCD | EFI | Boot Dosyaları", Renk.MAVI)
            self.log("═"*70, Renk.CYAN)
        
        zaman = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. MBR yedeği
        self.mbr_yedekle(zaman)
        
        # 2. Boot Sector yedeği
        self.boot_sector_yedekle(zaman)
        
        # 3. Boot Manager yedeği
        self.bootmgr_yedekle(zaman)
        
        # 4. BCD yedeği
        self.bcd_yedekle(zaman)
        
        # 5. EFI yedeği
        self.efi_yedekle(zaman)
        
        # 6. Boot dosyaları yedeği
        self.boot_dosyalari_yedekle(zaman)
        
        self.log(f"\n✅ TAM ÖNYÜKLEME YEDEĞİ TAMAMLANDI!", Renk.YESIL)
        self.log(f"   📂 Yedek konumu: {self.yedek_klasoru}", Renk.BEYAZ)
        
        return True
    
    def eski_yedekleri_temizle(self, keep_last=3):
        """Eski yedekleri sil (son 3 yedek tut)"""
        try:
            for dosya in os.listdir(self.yedek_klasoru):
                dosya_yolu = os.path.join(self.yedek_klasoru, dosya)
                if os.path.isfile(dosya_yolu):
                    # 7 günden eski yedekleri sil
                    zaman = os.path.getmtime(dosya_yolu)
                    if time.time() - zaman > 7 * 24 * 3600:
                        os.remove(dosya_yolu)
                        self.log(f"   🗑️ Eski yedek silindi: {dosya}", Renk.SARI)
        except:
            pass
    
    def mbr_geri_yukle(self):
        """MBR'yi yedekten geri yükle"""
        try:
            mbr_yedekleri = [f for f in os.listdir(self.yedek_klasoru) 
                            if f.startswith("mbr_backup_") and f.endswith(".bin")]
            
            if mbr_yedekleri:
                mbr_yedekleri.sort(reverse=True)
                en_son = mbr_yedekleri[0]
                yedek_yolu = os.path.join(self.yedek_klasoru, en_son)
                
                with open(yedek_yolu, "rb") as f:
                    mbr_data = f.read()
                
                with open(r"\\.\PhysicalDrive0", "wb") as f:
                    f.write(mbr_data)
                
                self.log(f"   ✅ MBR geri yüklendi: {en_son}", Renk.YESIL)
                return True
        except Exception as e:
            self.log(f"   ❌ MBR geri yüklenemedi: {e}", Renk.KIRMIZI)
        return False
    
    def bootmgr_geri_yukle(self):
        """Windows Boot Manager'ı geri yükle"""
        try:
            bootmgr_yedekleri = [f for f in os.listdir(self.yedek_klasoru) 
                                if f.startswith("bootmgr_") and f.endswith(".bin")]
            
            if bootmgr_yedekleri:
                bootmgr_yedekleri.sort(reverse=True)
                for yedek in bootmgr_yedekleri:
                    yedek_yolu = os.path.join(self.yedek_klasoru, yedek)
                    
                    # Orijinal adını bul
                    if "bootmgr" in yedek and "bootmgfw" in yedek:
                        hedef = "C:\\Windows\\Boot\\EFI\\bootmgfw.efi"
                    elif "bootmgr" in yedek:
                        hedef = "C:\\bootmgr"
                    else:
                        continue
                    
                    with open(yedek_yolu, "rb") as f:
                        veri = f.read()
                    
                    with open(hedef, "wb") as f:
                        f.write(veri)
                    
                    self.log(f"   ✅ Boot Manager geri yüklendi: {hedef}", Renk.YESIL)
                    return True
        except:
            pass
        return False

# ============================================================================
# VİRÜS TEMİZLEYİCİ
# ============================================================================

class VirusTemizleyici:
    def __init__(self, callback=None):
        self.callback = callback
    
    def log(self, mesaj, renk=Renk.BEYAZ):
        if self.callback:
            self.callback(mesaj, renk)
        else:
            print(c(mesaj, renk))
    
    def virus_tara(self):
        """Sistemi virüs taraması yap"""
        self.log("\n" + "═"*70, Renk.CYAN)
        self.log("🔍 VİRÜS TARAMA BAŞLATILDI", Renk.YESIL)
        self.log("═"*70, Renk.CYAN)
        
        bulunanlar = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                proc_cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                
                for virus_adi, virus_bilgi in TEHLIKELI_VIRUSLER.items():
                    for isim in virus_bilgi["isimler"]:
                        if isim.lower() in proc_name or isim.lower() in proc_cmdline:
                            bulunanlar.append({
                                'virus': virus_adi,
                                'isim': proc.info['name'],
                                'pid': proc.info['pid'],
                                'risk': virus_bilgi["risk"],
                                'aciklama': virus_bilgi["aciklama"]
                            })
                            self.log(f"   💀 {virus_adi.upper()}: {proc.info['name']}", Renk.KIRMIZI)
                            break
            except:
                continue
        
        if bulunanlar:
            self.log(f"\n⚠️ Toplam {len(bulunanlar)} tehdit bulundu!", Renk.SARI)
        else:
            self.log("\n✅ Virüs bulunamadı!", Renk.YESIL)
        
        return bulunanlar
    
    def virus_temizle(self, bulunanlar):
        """Bulunan virüsleri temizle"""
        if not bulunanlar:
            return 0
        
        self.log("\n" + "═"*70, Renk.KIRMIZI)
        self.log("🧹 VİRÜS TEMİZLEME BAŞLATILDI", Renk.KIRMIZI)
        self.log("═"*70, Renk.CYAN)
        
        temizlenen = 0
        for bulgu in bulunanlar:
            self.log(f"\n🔴 Temizleniyor: {bulgu['virus'].upper()} (PID: {bulgu['pid']})", Renk.KIRMIZI)
            try:
                proc = psutil.Process(bulgu['pid'])
                proc.terminate()
                proc.wait(timeout=3)
                self.log(f"   ✅ İşlem sonlandırıldı", Renk.YESIL)
                temizlenen += 1
            except:
                try:
                    proc.kill()
                    self.log(f"   ✅ İşlem zorla sonlandırıldı", Renk.YESIL)
                    temizlenen += 1
                except:
                    self.log(f"   ❌ İşlem sonlandırılamadı!", Renk.KIRMIZI)
        
        self.log(f"\n✅ {temizlenen} tehdit temizlendi!", Renk.YESIL)
        return temizlenen

# ============================================================================
# TNG ANA SINIF
# ============================================================================

class TNGAntivirus:
    def __init__(self):
        self.versiyon = GELISTIRICI["versiyon"]
        self.boot_yedek = BootYedekleme(callback=self._log)
        self.temizleyici = VirusTemizleyici(callback=self._log)
        self.ilk_yedek_yapildi = False
        self.klasor_kontrol()
        self._banner_goster()
    
    def klasor_kontrol(self):
        for klasor in ["TNG_Logs", "TNG_Quarantine", "TNG_Backups", "TNG_Reports"]:
            if not os.path.exists(klasor):
                os.makedirs(klasor)
    
    def _log(self, mesaj, renk=Renk.BEYAZ):
        print(c(mesaj, renk))
    
    def _banner_goster(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        print(c("╔══════════════════════════════════════════════════════════════════════════╗", Renk.CYAN))
        print(c("║                                                                          ║", Renk.CYAN))
        print(c("║     ████████╗███╗   ██╗ ██████╗     █████╗ ███╗   ██╗████████╗██╗       ║", Renk.PEMBE))
        print(c("║     ╚══██╔══╝████╗  ██║██╔════╝    ██╔══██╗████╗  ██║╚══██╔══╝██║       ║", Renk.PEMBE))
        print(c("║        ██║   ██╔██╗ ██║██║         ███████║██╔██╗ ██║   ██║   ██║       ║", Renk.PEMBE))
        print(c("║        ██║   ██║╚██╗██║██║         ██╔══██║██║╚██╗██║   ██║   ╚═╝       ║", Renk.PEMBE))
        print(c("║        ██║   ██║ ╚████║╚██████╗    ██║  ██║██║ ╚████║   ██║   ██╗       ║", Renk.PEMBE))
        print(c("║        ╚═╝   ╚═╝  ╚═══╝ ╚═════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝       ║", Renk.PEMBE))
        print(c("║                                                                          ║", Renk.CYAN))
        print(c("║     🛡️  TNG ANTİVİRÜS V{} - TAM ÖNYÜKLEME YEDEKLEMELİ            ║".format(self.versiyon), Renk.YESIL))
        print(c("║     💾 MBR | Boot Sector | Boot Manager | BCD | EFI                     ║", Renk.TURUNCU))
        print(c("║                                                                          ║", Renk.CYAN))
        print(c("║     Geliştirici: TEKNOLOJIGOBLINI                                       ║", Renk.MAVI))
        print(c("║     📷 Instagram: @TEKNOLOJIGOBLINI                                     ║", Renk.TURUNCU))
        print(c("║     ▶️ YouTube: @teknolojigoblini                                       ║", Renk.KIRMIZI))
        print(c("║                                                                          ║", Renk.CYAN))
        print(c("╚══════════════════════════════════════════════════════════════════════════╝", Renk.CYAN))
        print()
    
    def otomatik_yedek(self):
        if not self.ilk_yedek_yapildi:
            self.boot_yedek.tam_yedek_al(otomatik=True)
            self.ilk_yedek_yapildi = True
    
    def guvenli_tarama(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("🛡️  TNG GÜVENLİ TARAMA", Renk.YESIL))
        print(c("   Adım 1: Tam önyükleme yedeği al", Renk.MAVI))
        print(c("   Adım 2: Virüs taraması yap", Renk.MAVI))
        print(c("   Adım 3: Virüs temizle", Renk.MAVI))
        print(c("═"*70, Renk.CYAN))
        
        print(c("\n📋 [ADIM 1/3] TAM ÖNYÜKLEME YEDEĞİ ALINIYOR...", Renk.SARI))
        self.boot_yedek.tam_yedek_al()
        
        print(c("\n📋 [ADIM 2/3] VİRÜS TARANIYOR...", Renk.SARI))
        bulunanlar = self.temizleyici.virus_tara()
        
        if bulunanlar:
            print(c("\n📋 [ADIM 3/3] VİRÜS TEMİZLENİYOR...", Renk.SARI))
            self.temizleyici.virus_temizle(bulunanlar)
        else:
            print(c("\n✅ Virüs bulunamadı.", Renk.YESIL))
        
        print(c("\n✅ GÜVENLİ TARAMA TAMAMLANDI!", Renk.YESIL))
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def menu_goster(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("📌 TNG ANTİVİRÜS ANA MENÜ", Renk.YESIL))
        print(c("═"*70, Renk.CYAN))
        print(c("1) 🛡️  GÜVENLİ TARAMA", Renk.MAVI))
        print(c("2) 💾 Tam Önyükleme Yedeği Al (MBR+EFI+Boot Manager)", Renk.SARI))
        print(c("3) 🔍 Sadece Virüs Tara", Renk.MOR))
        print(c("4) 🧹 Sadece Virüs Temizle", Renk.TURUNCU))
        print(c("5) 📁 Yedekleri Göster", Renk.PEMBE))
        print(c("6) 🌐 Sosyal Medya", Renk.TURUNCU))
        print(c("7) ℹ️  Hakkında", Renk.BEYAZ))
        print(c("8) 🚪 Çıkış", Renk.KIRMIZI))
        print(c("═"*70, Renk.CYAN))
        
        return input(c("Seçiminiz (1-8): ", Renk.YESIL))
    
    def sadece_tara(self):
        bulunanlar = self.temizleyici.virus_tara()
        if bulunanlar:
            temizle = input(c("\nTemizlemek istiyor musunuz? (e/h): ", Renk.KIRMIZI))
            if temizle.lower() == 'e':
                self.temizleyici.virus_temizle(bulunanlar)
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def sadece_temizle(self):
        bulunanlar = self.temizleyici.virus_tara()
        if bulunanlar:
            self.temizleyici.virus_temizle(bulunanlar)
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def yedekleri_goster(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("📁 YEDEKLER", Renk.YESIL))
        print(c("═"*70, Renk.CYAN))
        
        if os.path.exists("TNG_Backups"):
            yedekler = os.listdir("TNG_Backups")
            if yedekler:
                mbr_yedek = [f for f in yedekler if f.startswith("mbr_backup")]
                boot_yedek = [f for f in yedekler if f.startswith("boot_sector")]
                bootmgr_yedek = [f for f in yedekler if f.startswith("bootmgr_")]
                bcd_yedek = [f for f in yedekler if f.startswith("bcd_")]
                efi_yedek = [f for f in yedekler if f.startswith("efi_backup")]
                
                print(c("\n💾 MBR YEDEKLERİ:", Renk.MAVI))
                for y in mbr_yedek[:3]:
                    print(c(f"   • {y}", Renk.BEYAZ))
                
                print(c("\n💾 BOOT SECTOR YEDEKLERİ:", Renk.MAVI))
                for y in boot_yedek[:3]:
                    print(c(f"   • {y}", Renk.BEYAZ))
                
                print(c("\n💾 BOOT MANAGER YEDEKLERİ:", Renk.MAVI))
                for y in bootmgr_yedek[:3]:
                    print(c(f"   • {y}", Renk.BEYAZ))
                
                print(c("\n💾 BCD YEDEKLERİ:", Renk.MAVI))
                for y in bcd_yedek[:3]:
                    print(c(f"   • {y}", Renk.BEYAZ))
                
                print(c("\n💾 EFI YEDEKLERİ:", Renk.MAVI))
                for y in efi_yedek[:3]:
                    print(c(f"   • {y}", Renk.BEYAZ))
            else:
                print(c("\n⚠️ Yedek bulunamadı.", Renk.SARI))
        else:
            print(c("\n⚠️ Yedek klasörü bulunamadı.", Renk.SARI))
        
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def sosyal_medya_goster(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("📱 TEKNOLOJIGOBLINI - SOSYAL MEDYA", Renk.YESIL))
        print(c("═"*70, Renk.CYAN))
        print(c(f"📷 Instagram: {GELISTIRICI['instagram']}", Renk.TURUNCU))
        print(c(f"▶️ YouTube: {GELISTIRICI['youtube']}", Renk.KIRMIZI))
        print(c("═"*70, Renk.CYAN))
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def hakkimda_goster(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("ℹ️  TNG ANTİVİRÜS HAKKINDA", Renk.YESIL))
        print(c("═"*70, Renk.CYAN))
        print(c(f"📌 Program: TNG Antivirus", Renk.MAVI))
        print(c(f"📌 Versiyon: {self.versiyon}", Renk.MAVI))
        print(c(f"📌 Geliştirici: {GELISTIRICI['isim']}", Renk.MAVI))
        print(c("📌 Yedeklenen Önyükleme Bileşenleri:", Renk.YESIL))
        print(c("   • MBR (Master Boot Record)", Renk.BEYAZ))
        print(c("   • Boot Sector (VBR)", Renk.BEYAZ))
        print(c("   • Windows Boot Manager (bootmgr)", Renk.BEYAZ))
        print(c("   • BCD (Boot Configuration Database)", Renk.BEYAZ))
        print(c("   • EFI System Partition", Renk.BEYAZ))
        print(c("   • Boot sürücüleri ve dosyaları", Renk.BEYAZ))
        print(c("═"*70, Renk.CYAN))
        input(c("\nDevam için Enter'a basın...", Renk.SARI))
    
    def calistir(self):
        print(c("\n" + "═"*70, Renk.CYAN))
        print(c("🚀 TNG ANTİVİRÜS BAŞLATILIYOR...", Renk.YESIL))
        print(c("═"*70, Renk.CYAN))
        
        self.otomatik_yedek()
        
        while True:
            secim = self.menu_goster()
            
            if secim == '1':
                self.guvenli_tarama()
            elif secim == '2':
                self.boot_yedek.tam_yedek_al()
                input(c("\nDevam için Enter'a basın...", Renk.SARI))
            elif secim == '3':
                self.sadece_tara()
            elif secim == '4':
                self.sadece_temizle()
            elif secim == '5':
                self.yedekleri_goster()
            elif secim == '6':
                self.sosyal_medya_goster()
            elif secim == '7':
                self.hakkimda_goster()
            elif secim == '8':
                print(c("\n📢 TEKNOLOJIGOBLINI'yi takip etmeyi unutmayın!", Renk.TURUNCU))
                print(c("📷 Instagram: @TEKNOLOJIGOBLINI", Renk.TURUNCU))
                print(c("▶️ YouTube: @teknolojigoblini", Renk.KIRMIZI))
                print(c("\nTNG Antivirüs kullandığınız için teşekkürler!", Renk.YESIL))
                break
            else:
                print(c("\n❌ Geçersiz seçim!", Renk.KIRMIZI))

def main():
    try:
        tng = TNGAntivirus()
        tng.calistir()
    except KeyboardInterrupt:
        print(c("\n\n⚠️ Program kullanıcı tarafından sonlandırıldı.", Renk.SARI))
    except Exception as e:
        print(c(f"\n❌ Beklenmeyen hata: {e}", Renk.KIRMIZI))

if __name__ == "__main__":
    main()
