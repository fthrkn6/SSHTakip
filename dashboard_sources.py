from app import create_app
from models import ServiceStatus, Failure, Equipment
from datetime import date
import pandas as pd
import os

app = create_app()
with app.app_context():
    today = str(date.today())
    
    print("=" * 70)
    print("DASHBOARD - BUGÜNÜN VERİ KAYNAKLARI")
    print("=" * 70)
    
    # 1. ServiceStatus - Tramvay Filosu
    print(f"\n1️⃣ TRAMVAY FILOSU DURUMU (ServiceStatus - {today})")
    print("-" * 70)
    
    today_status = ServiceStatus.query.filter_by(date=today).all()
    print(f"Toplam: {len(today_status)} tramvay\n")
    
    status_breakdown = {}
    for s in today_status:
        status_val = s.status
        if status_val not in status_breakdown:
            status_breakdown[status_val] = []
        status_breakdown[status_val].append({
            'tram_id': s.tram_id,
            'status': s.status,
            'aciklama': s.aciklama,
            'sistem': s.sistem
        })
    
    for status, records in sorted(status_breakdown.items()):
        print(f"📊 {status}: {len(records)} tramvay")
        for r in records:
            print(f"   • {r['tram_id']:6s} - {r['aciklama'][:40] if r['aciklama'] else '-'}")
    
    # 2. Excel - Arıza Verileri
    print(f"\n2️⃣ ARIZA VERİLERİ (Excel - Ariza Listesi)")
    print("-" * 70)
    
    # Tüm projeler için (default: belgrad)
    project = 'belgrad'  # Dashboard'da default proje
    ariza_path = f"logs/{project}/ariza_listesi/Ariza_Listesi_{project.upper()}.xlsx"
    if os.path.exists(ariza_path):
        try:
            df = pd.read_excel(ariza_path, sheet_name='Ariza Listesi', header=3)
            print(f"Toplam arıza kaydı: {len(df)}")
            print(f"Sütunlar: {list(df.columns)[:7]}...\n")
            
            # Son 5
            print("Son 5 arıza:")
            last_5 = df.tail(5)
            for idx, row in last_5.iterrows():
                fracas_id = row.get('FRACAS ID', '-')
                arac = row.get('Araç No', '-')
                taarih = row.get('Tarih', '-')
                ariza_def = str(row.get('Arıza Tanımı', '-'))[:40]
                print(f"   • {fracas_id} | Araç: {arac} | {taarih} | {ariza_def}")
        except Exception as e:
            print(f"❌ Excel okuma hatası: {e}")
    else:
        print(f"❌ Dosya bulunamadı: {ariza_path}")
    
    # 3. Arıza Sınıfları
    print(f"\n3️⃣ ARIZA SINIFI SAYILARI (Excel'den)")
    print("-" * 70)
    if os.path.exists(ariza_path):
        try:
            df = pd.read_excel(ariza_path, sheet_name='Ariza Listesi', header=3)
            if 'Arıza Sınıfı ' in df.columns:
                sinif_counts = df['Arıza Sınıfı '].value_counts()
                for sinif, count in sinif_counts.items():
                    if pd.notna(sinif):
                        print(f"   • {sinif}: {count}")
        except:
            pass
    
    # 4. Son 30 Gün Arıza Toplam
    print(f"\n4️⃣ SON 30 GÜNDE TOPLAM ARIZA (Excel'den)")
    print("-" * 70)
    if os.path.exists(ariza_path):
        try:
            df = pd.read_excel(ariza_path, sheet_name='Ariza Listesi', header=3)
            if 'Tarih' in df.columns:
                df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
                from datetime import datetime, timedelta
                thirty_days_ago = datetime.now() - timedelta(days=30)
                count_30 = len(df[df['Tarih'] >= thirty_days_ago])
                print(f"   Toplam: {count_30} arıza")
        except:
            pass
    
    # 5. Database - Açık Arızalar
    print(f"\n5️⃣ DATABASE - AÇIK ARIZALAR (Failure tablosu)")
    print("-" * 70)
    open_failures = Failure.query.filter(
        Failure.status.in_(['acik', 'devam_ediyor'])
    ).all()
    print(f"Toplam açık arıza: {len(open_failures)}")
    
    # 6. Sistem Kaynakları
    print(f"\n6️⃣ DASHBOARD VERI KAYNAKLARI ÖZET")
    print("-" * 70)
    print("""
    📍 Tramvay Filosu (sol üst):
       → Kaynak: ServiceStatus (database)
       → Tarih: Bugün (2026-02-10)
       → Renkler: Yeşil=Aktif, Turuncu=İşletme Kaynaklı, Kırmızı=Arızalı
    
    📍 Açık Arızalar (sağ üst):
       → Kaynak: Ariza_Listesi_BELGRAD.xlsx (Excel)
       → Arıza Sınıfları: Excel'den dinamik sayı
       → Son 5 arıza: Excel son satırlarından
    
    📍 Metrics (KPI Cards):
       → Filo Kullanılabilirlik: KPISnapshot (database)
       → Son 30 Günde Toplam Arıza: Excel'den tarih filtered
       → İş Emri Tamamlama: WorkOrder (database)
       → Önleyici Bakım Oranı: KPISnapshot (database)
    
    📍 Açık İş Emirleri (alt):
       → Kaynak: WorkOrder (database)
       → Kritik ve bekleyen emirler filtreleniyor
    """)
    
    print("=" * 70)
