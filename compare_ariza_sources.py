#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arıza Listesi Veri Kaynakları - Mevcut vs Önerilen Karşılaştırması
Tüm projeleri Fracas_{proje_adi}.xlsx kullanacak şekilde yapılandırmayı göster
"""

import os
from pathlib import Path
from flask import Flask
from utils.project_manager import ProjectManager

# Flask app set up
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

with app.app_context():
    pm = ProjectManager()
    projects = pm.get_all_projects()
    
    print("\n" + "="*100)
    print("ARIZA LİSTESİ KAYNAK KARŞILAŞTIRMASI - MEVCUT vs ÖNERİLEN")
    print("="*100 + "\n")
    
    print(f"{'Proje':<20} {'Mevcut Kaynak':<40} {'Önerilen Kaynak':<40}")
    print("-" * 100)
    
    proposed_changes = []
    
    for project in projects:
        project_code = project['code']
        project_name = project['name']
        
        # Check current sources
        base_logs_path = f"logs/{project_code}/ariza_listesi"
        base_data_path = f"data/{project_code}"
        
        current_source = "Yok (Varsayılan)"
        
        # Check if FRACAS exists
        fracas_files = list(Path(".").glob(f"{base_logs_path}/Fracas_*.xlsx"))
        if fracas_files:
            current_source = f"Fracas_*.xlsx ✅"
        else:
            # Check if Ariza_Listesi exists
            ariza_files = list(Path(".").glob(f"{base_logs_path}/Ariza_Listesi_*.xlsx"))
            if ariza_files:
                current_source = f"Ariza_Listesi_*.xlsx ✅"
            else:
                # Check Veriler.xlsx
                veriler_path = Path(f"{base_data_path}/Veriler.xlsx")
                if veriler_path.exists():
                    current_source = f"Veriler.xlsx (fallback) ✅"
        
        # Proposed source - all should use Fracas_{project_code}.xlsx
        proposed_source = f"Fracas_{project_code.upper()}.xlsx"
        
        # Check if proposed file would exist
        proposed_fracas_files = list(Path(".").glob(f"{base_logs_path}/Fracas_{project_code.upper()}.xlsx"))
        
        # Determine project name format
        project_display = f"{project_name} ({project_code})"
        
        # Mark if it would be a change
        mark = ""
        if "Fracas_*.xlsx" not in current_source:
            mark = " ⚠️ DEĞIŞECEK"
            proposed_changes.append({
                'code': project_code,
                'name': project_name,
                'current': current_source,
                'proposed': proposed_source
            })
        else:
            mark = " ✓ Zaten Fracas"
        
        print(f"{project_display:<20} {current_source:<40} {proposed_source:<40}{mark}")
    
    print("\n" + "="*100)
    print("ÖZET")
    print("="*100)
    
    if proposed_changes:
        print(f"\n⚠️  Değiştirilecek Proje Sayısı: {len(proposed_changes)}")
        print("\nDeğiştirilecek Projeler:")
        for change in proposed_changes:
            print(f"  • {change['name']} ({change['code']})")
            print(f"    Mevcut: {change['current']}")
            print(f"    Önerilen: {change['proposed']}")
    else:
        print("\n✅ Tüm projeler zaten Fracas_*.xlsx kullanıyor")
    
    print("\n" + "="*100)
    print("YAPILACAK İŞLEM:")
    print("="*100)
    print("""
Eğer ilerlemek istiyorsanız, aşağıdaki adımları yapabiliriz:

1. MANUEL KONTROL:
   - Yukarıdaki tabloyu inceleyerek değişiklikleri doğrulayın
   - Eksik Fracas_{proje_adi}.xlsx dosyalarını logs/{proje}/ariza_listesi/ içine kopyalayın

2. KAYNAĞIN GÜNCELLENMESİ (DATA LOADING KODUNDAKİ):
   - /dashboard/api/failures endpoint'ini Fracas_*.xlsx'i ilk olarak aramak üzere güncelleyin
   - Diğer formatları fallback olarak tutun

3. VERİ TRANSFERİ:
   - Ariza_Listesi_*.xlsx dosyasındaki veriler Fracas formatına çevrilsin

Lütfen devam etmek istediğinizi onaylayın.
    """)
    
    print("\n✅ Rapor tamamlandı\n")
