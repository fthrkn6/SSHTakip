#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TÜM PROJELERİN VERİ KAYNAKLARI - MEVCUT DURUM ANALİZİ
Konumları ve standartlaştırılmayan öğeleri göster
"""

import os
from pathlib import Path

print("\n" + "="*250)
print("TÜM PROJELERİN VERİ KAYNAKLARI - MEVCUT DURUM".center(250))
print("="*250 + "\n")

projeler = {
    "BELGRAD": {
        "kod": "belgrad",
        "veriler_xlsx": "data/belgrad/Veriler.xlsx",
        "km_data": "data/belgrad/km_data.xlsx",
        "fracas_ana": "data/belgrad/BEL25_FRACAS(...).xlsx",
        "fracas_logs": "logs/belgrad/ariza_listesi/Fracas_BELGRAD.xlsx",
        "ariza_listesi": "logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx"
    },
    "İASİ": {
        "kod": "iasi",
        "veriler_xlsx": "data/iasi/Veriler.xlsx",
        "km_data": "data/iasi/km_data.xlsx (YOK)",
        "fracas_ana": "data/iasi/IASI_18-FR-549_FRACAS(...).xlsx",
        "fracas_logs": "logs/iasi/ariza_listesi/ (YOK/BOŞMUŞ)",
        "ariza_listesi": "logs/iasi/ariza_listesi/ (YOK/BOŞMUŞ)"
    },
    "TİMİŞOARA": {
        "kod": "timisoara",
        "veriler_xlsx": "data/timisoara/Veriler.xlsx",
        "km_data": "data/timisoara/km_data.xlsx (YOK)",
        "fracas_ana": "data/timisoara/TIM16+24_FRACAS(...).xlsx",
        "fracas_logs": "logs/timisoara/ariza_listesi/ (YOK/BOŞMUŞ)",
        "ariza_listesi": "logs/timisoara/ariza_listesi/ (YOK/BOŞMUŞ)"
    },
    "KAYSERI": {
        "kod": "kayseri",
        "veriler_xlsx": "data/kayseri/Veriler.xlsx",
        "km_data": "data/kayseri/km_data.xlsx",
        "fracas_ana": "data/kayseri/FRACAS.xlsx (BOŞMUŞ)",
        "fracas_logs": "logs/kayseri/ariza_listesi/Fracas_KAYSERI.xlsx ✓ KULLANIYOR",
        "ariza_listesi": "logs/kayseri/ariza_listesi/Ariza_Listesi_KAYSERI.xlsx"
    },
    "KOCAELİ": {
        "kod": "kocaeli",
        "veriler_xlsx": "data/kocaeli/Veriler.xlsx",
        "km_data": "data/kocaeli/km_data.xlsx",
        "fracas_ana": "data/kocaeli/KOC10_FRACAS(...).xlsx",
        "fracas_logs": "logs/kocaeli/ariza_listesi/ (YOK/BOŞMUŞ)",
        "ariza_listesi": "logs/kocaeli/ariza_listesi/ (YOK/BOŞMUŞ)"
    },
    "GEBZE": {
        "kod": "gebze",
        "veriler_xlsx": "data/gebze/Veriler.xlsx",
        "km_data": "data/gebze/km_data.xlsx (YOK)",
        "fracas_ana": "data/gebze/GDM7X4_FRACAS(...).xlsx",
        "fracas_logs": "logs/gebze/ariza_listesi/ (YOK/BOŞMUŞ)",
        "ariza_listesi": "logs/gebze/ariza_listesi/ (YOK/BOŞMUŞ)"
    },
    "SAMSUN": {
        "kod": "samsun",
        "veriler_xlsx": "data/samsun/Veriler.xlsx",
        "km_data": "data/samsun/km_data.xlsx",
        "fracas_ana": "data/samsun/KOC10_FRACAS(...).xlsx",
        "fracas_logs": "logs/samsun/ariza_listesi/ (YOK/BOŞMUŞ)",
        "ariza_listesi": "logs/samsun/ariza_listesi/ (YOK/BOŞMUŞ)"
    },
    "İSTANBUL": {
        "kod": "istanbul",
        "veriler_xlsx": "data/istanbul/Veriler.xlsx",
        "km_data": "data/istanbul/km_data.xlsx",
        "fracas_ana": "data/istanbul/KOC10_FRACAS(...).xlsx",
        "fracas_logs": "logs/istanbul/ariza_listesi/Fracas_İSTANBUL.xlsx",
        "ariza_listesi": "logs/istanbul/ariza_listesi/Ariza_Listesi_İSTANBUL.xlsx"
    }
}

print(f"{'PROJE':<15} | {'Veriler.xlsx':<25} | {'KM Data':<20} | {'FRACAS ANA':<30} | {'FRACAS LOGS':<35}")
print("-"*250)

for proje, kaynaklar in projeler.items():
    print(f"{proje:<15} | {kaynaklar['veriler_xlsx']:<25} | {kaynaklar['km_data']:<20} | {kaynaklar['fracas_ana']:<30} | {kaynaklar['fracas_logs']:<35}")

print("\n" + "="*250)
print("STANDART DIŞI PROJELER".center(250))
print("="*250 + "\n")

# KAYSERI'nin standart dışı kullanımı
print("❌ KAYSERI - STANDART DIŞI KAYNAKLAR")
print("-"*250)
print("   • FRACAS dosyasını logs/ klasöründen çekiyor: logs/kayseri/ariza_listesi/Fracas_KAYSERI.xlsx")
print("   • Diğer projeler data/ klasöründen çekiyor")
print("   • Kod özellikle logs/ dizinine bakacak şekilde yazılı (calculate_fleet_mttr() fonksiyonunda)")
print()

print("❌ İASİ, TİMİŞOARA, GEBZE - EKSIK DOSYALAR")
print("-"*250)
print("   • logs/{proje}/ariza_listesi/ klasörleri boş veya eksik")
print("   • Arıza_Listesi_*.xlsx dosyaları yok")
print("   • Dashboard FRACAS bulmuş olsa da, arıza sınıflandırması eksik")
print()

print("✓ BELGRAD, KOCAELİ, SAMSUN, İSTANBUL - NISPETEN STANDART")
print("-"*250)
print("   • data/{proje}/ klasöründe Veriler.xlsx ve FRACAS.xlsx var")
print("   • logs/{proje}/ariza_listesi/ klasöründe Fracas_*.xlsx var")
print("   • İSTANBUL: logs'taki dosya dolu ve işlevsel")
print()

print("\n" + "="*250)
print("STANDARTİZASYON ANALİZİ - HANGI BİÇIM STANDART OLACAK?".center(250))
print("="*250 + "\n")

standartlar = {
    "Seçenek 1: MERKEZ data/ KLASÖRÜNe DOSYA AL": {
        "yapı": """
        data/{proje}/
        ├─ Veriler.xlsx (Araç listesi)
        ├─ km_data.xlsx (KM bilgileriİ)
        ├─ Fracas_{proje}.xlsx (FRACAS arıza verileri)
        └─ Ariza_Listesi_{proje}.xlsx (Tamamlanan arızalar)
        
        logs/{proje}/ariza_listesi/ (BOŞ - işlenmeyecek)
        """,
        "avantajlar": [
            "Merkez yönetim (data/ klasörü)",
            "Kod basitleşir (tek yerden oku)",
            "Yedekleme kolay"
        ],
        "dezavantajlar": [
            "Mevcut logs/ dosyalarını taşıyıp güncelleme gerekli",
            "KAYSERI için ayrı kod kuralı kaldırılır"
        ]
    },
    "Seçenek 2: LOGS KLASÖRÜnü KULLAN (Mevcut)": {
        "yapı": """
        logs/{proje}/ariza_listesi/
        ├─ Fracas_{proje}.xlsx
        └─ Ariza_Listesi_{proje}.xlsx
        
        data/{proje}/ (Veriler.xlsx ve km_data.xlsx için)
        """,
        "avantajlar": [
            "Mevcut yapıyı koru (KAYSERI, BELGRAD, İSTANBUL zaten kullanıyor)",
            "Minimal kod değişikliği"
        ],
        "dezavantajlar": [
            "İASİ, TİMİŞOARA, GEBZE için dosya oluşturma/taşıyıp gerekli",
            "İki bölümlü yapı (data/ + logs/) karışık"
        ]
    },
    "Seçenek 3: KARMA STANDARDİ (Hibrit)": {
        "yapı": """
        data/{proje}/
        ├─ Veriler.xlsx
        ├─ km_data.xlsx
        └─ FRACAS şemsiye klasör
            └─ {proje}_fracas/
                ├─ Fracas_{proje}.xlsx
                └─ Ariza_Listesi_{proje}.xlsx
        """,
        "avantajlar": [
            "Tüm veriler data/ altında merkezi",
            "Proje pozu (içine arızalar)",
            "Gelecekteki skalabilite iyi"
        ],
        "dezavantajlar": [
            "En çok yapı değişikliği",
            "Tüm projelerde dosya taşıyıp gerekli"
        ]
    }
}

for option, details in standartlar.items():
    print(f"\n{option}")
    print("-"*250)
    print(details['yapı'])
    print(f"\n  ✓ Avantajlar:")
    for uygun in details['avantajlar']:
        print(f"    • {uygun}")
    print(f"\n  ✗ Dezavantajlar:")
    for nok in details['dezavantajlar']:
        print(f"    • {nok}")

print("\n\n" + "="*250)
print("STANDARTLAŞTIRMA PLANI - HANGI ADIMlarını YAPMAMIZ GEREKECEK?".center(250))
print("="*250 + "\n")

steps = """
ADIM 1: DOSYA DAĞITIMI
═══════════════════════════════════════════════════════════════════════════════

Seçilen standarda göre:
  • İASİ → logs/iasi/ariza_listesi/'ye Fracas_IASI.xlsx kopyala
  • TİMİŞOARA → logs/timisoara/ariza_listesi/'ye Fracas_TIMISOARA.xlsx kopyala
  • GEBZE → logs/gebze/ariza_listesi/'ye Fracas_GEBZE.xlsx kopyala
  • Eksik Ariza_Listesi_*.xlsx dosyaları şablon olarak oluştur


ADIM 2: KOD STANDARTLAŞTIRMASI
═══════════════════════════════════════════════════════════════════════════════

routes/dashboard.py:
  • calculate_fleet_mttr() fonksiyonundaki özel KAYSERI kuralını kaldır
  • Tüm projeler için tek bir kuralı geçer
  • ProjectManager.get_fracas_file() otomatik uyar

utils/project_manager.py:
  • FRACAS dosya arama sırası standartlaştır
  • Tüm projeler için aynı logik


ADIM 3: DOĞRULAMA
═══════════════════════════════════════════════════════════════════════════════

  • Tüm 8 proje için MTTR hesapla → İş yapıyor mı kontrol et
  • Dashboard'u tüm projeler ile test et
  • Dosya konum öneri de çalışıyor mu kontrol et


ADIM 4: DOKÜMANTASYON
═══════════════════════════════════════════════════════════════════════════════

  • README.md güncelle → Yeni standart yapıyı yazı
  • Proje yöneticisine referans tablo sun
"""

print(steps)

print("\n" + "="*250)
print("DAVRANMIŞ KODUM ÖZEL HALINLER".center(250))
print("="*250 + "\n")

special_cases = """
routes/dashboard.py - calculate_fleet_mttr() (satır 338-350):
───────────────────────────────────────────────────────────────────────────────

Mevcut kod:
───────────────────────────────────────────────────────────────────────────────
    # 2. Yoksa logs/{project}/ariza_listesi/ klasöründe ara (Kayseri için)
    if not fracas_file:
        logs_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if 'fracas' in file.lower() and file.endswith('.xlsx'):
                    fracas_file = os.path.join(logs_dir, file)
                    break

Problem: KAYSERI için özel kuralı var (logs'ta bakıp), bu standart değil


ProjectManager.get_fracas_file() (utils/project_manager.py, satır 140-160):
───────────────────────────────────────────────────────────────────────────────

Mevcut kod:
───────────────────────────────────────────────────────────────────────────────
    @staticmethod
    def get_fracas_file(project_code):
        \"\"\"logs/{project}/ariza_listesi/*FRACAS*.xlsx dosyasını bul\"\"\"
        
        ariza_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'logs', project_code, 'ariza_listesi'
        )
        
        if os.path.exists(ariza_dir):
            for file in os.listdir(ariza_dir):
                if 'fracas' in file.lower() and file.endswith('.xlsx'):
                    return os.path.join(ariza_dir, file)
        
        return None

Problem: Sadece logs/ klasörüne bakıyor, data/'yı kontrol etmiyor
"""

print(special_cases)

print("\n" + "="*250 + "\n")
