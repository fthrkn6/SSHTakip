#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os
from pathlib import Path

# Arıza Listesi yolunu oluştur
project = 'belgrad'
ariza_dir = f'logs/{project}/ariza_listesi'

print(f"🔍 Arıza Listesi klasörü taranıyor: {ariza_dir}")
print(f"📁 Dosyalar: {os.listdir(ariza_dir)}")
print()

# Excel dosyasını oku
xlsx_files = [f for f in os.listdir(ariza_dir) if f.endswith('.xlsx') and not 'backup' in f]

if not xlsx_files:
    print("❌ Excel dosyası bulunamadı!")
else:
    filepath = os.path.join(ariza_dir, xlsx_files[0])
    print(f"📂 Yüklenen dosya: {filepath}")
    print()
    
    # Başlıkları kontrol et
    try:
        df = pd.read_excel(filepath, header=3)
        print(f"✅ Dosya başarıyla yüklendi (header=3)")
        print(f"📊 Satır sayısı: {len(df)}")
        print()
        
        print("📋 Kolon Adları:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}'")
        print()
        
        print("📈 İlk 5 satır:")
        print(df.head())
        print()
        
        # Arıza sınıfı kontrol et
        print("🔍 Arıza Sınıfı dağılımı:")
        if 'Arıza Sınıfı' in df.columns:
            print(df['Arıza Sınıfı'].value_counts())
        else:
            print("  → 'Arıza Sınıfı' sütunu bulunamadı")
        print()
        
        # Sistem/modül kontrol et
        print("🔍 Sistem dağılımı:")
        sistem_cols = [c for c in df.columns if 'sistem' in c.lower() or 'modül' in c.lower()]
        if sistem_cols:
            for col in sistem_cols:
                print(f"  {col}:")
                print(f"    Değer sayısı: {df[col].nunique()}")
                print(f"    İlk 5 değer: {df[col].value_counts().head()}")
        else:
            print("  → Sistem/modül sütunu bulunamadı")
        print()
        
        # Tarih kontrol et
        print("🔍 Tarih bilgisi:")
        date_cols = [c for c in df.columns if 'tarih' in c.lower() or 'date' in c.lower()]
        if date_cols:
            for col in date_cols:
                print(f"  {col}:")
                print(f"    Data type: {df[col].dtype}")
                print(f"    İlk 3 değer: {df[col].head(3).tolist()}")
        else:
            print("  → Tarih sütunu bulunamadı")
        print()
        
        # Tedarikçi kontrol et
        print("🔍 Tedarikçi dağılımı:")
        supplier_cols = [c for c in df.columns if 'tedarikçi' in c.lower() or 'supplier' in c.lower()]
        if supplier_cols:
            for col in supplier_cols:
                print(f"  {col}:")
                print(f"    Unique: {df[col].nunique()}")
                print(f"    Top 5:")
                print(f"    {df[col].value_counts().head()}")
        else:
            print("  → Tedarikçi sütunu bulunamadı")
        print()
        
        # Araç ID sütununu bul
        print("🔍 Araç ID sütunları:")
        vehicle_cols = [c for c in df.columns if 'araç' in c.lower() or 'tram' in c.lower() or 'vehicle' in c.lower()]
        if vehicle_cols:
            for col in vehicle_cols:
                print(f"  {col}:")
                print(f"    Unique: {df[col].nunique()}")
                print(f"    Top 5:")
                print(f"    {df[col].value_counts().head()}")
        else:
            print("  → Araç sütunu bulunamadı")
        print()
        
        # Dönem/time range
        print("⏱️  Veri aralığı:")
        for col in date_cols if date_cols else []:
            try:
                df['parsed'] = pd.to_datetime(df[col], errors='coerce')
                valid = df[df['parsed'].notna()]['parsed']
                if len(valid) > 0:
                    print(f"  {col}:")
                    print(f"    Min: {valid.min()}")
                    print(f"    Max: {valid.max()}")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
