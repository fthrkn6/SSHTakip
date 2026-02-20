"""
STATS DICTIONARY VERİ AKIŞ ANALIZI
===================================

Kod Akışı ve Veri Kaynakları:
"""

# 1. TRAMVAY LİSTESİ
# ==================
# Satır 411-431: Veriler.xlsx'ten tram_id'leri oku
tram_ids_from_excel = get_tram_ids_from_veriler(current_project)
# ↓ KAYSERI örneği: ['1531', '1532', '1533', ..., '1555']

# Satır 433-445: Equipment tablosundan tram_id'lere göre tramvayları çek
tramvaylar = Equipment.query.filter(
    Equipment.equipment_code.in_(tram_ids_from_excel),  # ← Excel'den gelen ID'ler
    Equipment.parent_id.is_(None),
    Equipment.project_code == current_project
).order_by(Equipment.equipment_code).all()
# ↓ SONUÇ: Database'den gelen Equipment nesneleri


# 2. HER TRAMVAY İÇİN BUGÜN'ÜN DURUMU
# =====================================
# Satır 437-476: tramvay_statuses listesi oluştur
tramvay_statuses = []
for tramvay in tramvaylar:  # ← Equipment listesi
    # Satır 441-443: ServiceStatus tablosundan bugünün kaydı al
    status_record = ServiceStatus.query.filter_by(
        tram_id=tramvay.equipment_code,  # ← Equipment'den gelen kod
        date=today  # ← str(date.today())
    ).first()  # ← DATABASE kaynağı
    
    # Satır 451-468: ServiceStatus'ten gelen değeri işle
    if status_record:
        status_value = status_record.status  # ← DB'den gelen durum
        if 'İşletme' in status_value:
            status_display = 'işletme'
        elif 'Dışı' in status_value:
            status_display = 'ariza'
        else:
            status_display = 'aktif'
    else:
        status_display = 'aktif'  # ← DEFAULT: Eğer kaydı yoksa aktif
    
    # Satır 470-476: tramvay_statuses'e ekle
    tramvay_statuses.append({
        'status': status_display,  # ← 'aktif', 'işletme' veya 'ariza'
        ...
    })


# 3. STATS DICTIONARY TEMELİ
# ===========================
# Satır 498-507: Sayıları hesapla
aktif_count = 0
isletme_count = 0
ariza_count = 0

for tramvay_status in tramvay_statuses:  # ← Yukarıda oluşturulan liste
    if tramvay_status['status'] == 'aktif':
        aktif_count += 1
    elif tramvay_status['status'] == 'işletme':
        isletme_count += 1
    else:
        ariza_count += 1

# Satır 512-517: Hesaplamalar
total_tram = len(tramvay_statuses)  # ← Toplam
kullanilabilir = aktif_count + isletme_count  # ← Çalışabilir
fleet_availability = round(kullanilabilir / total_tram * 100, 1) if total_tram > 0 else 0


# 4. STATS DICTIONARY
# ====================
stats = {
    'total_tramvay': len(tramvay_statuses),           # ← tramvay_statuses listesi
    'aktif_servis': aktif_count,                      # ← Döngü ile sayılan değer
    'bakimda': isletme_count,                          # ← Döngü ile sayılan değer (İşletme Kaynaklı)
    'arizali': ariza_count,                            # ← Döngü ile sayılan değer
    'fleet_availability': fleet_availability,          # ← Hesaplanan oran
    'aktif_ariza': len(son_arizalar),                 # ← Excel'den çekilen arıza sayısı
    'bekleyen_is_emri': wo_summary.get('pending', 0), # ← WorkOrder DB'si
    'devam_eden_is_emri': wo_summary.get('in_progress', 0),
    'mttr': mttr_data,                                 # ← calculate_fleet_mttr()
}


"""
VERİ KAYNAKLARI ÖZETI
====================

✓ total_tramvay
  Kaynak: len(tramvay_statuses)
  Nerede?: Veriler.xlsx'ten alınan tram_id'ler + Equipment DB
  Nasıl?: get_tram_ids_from_veriler() → tram_id'leri al → Equipment tablosundan çek

✓ aktif_servis  
  Kaynak: tramvay_status['status'] == 'aktif' olan sayı
  Nerede?: ServiceStatus table (date = bugün)
  Nasıl?: Her tramvay için bugün kaydı → durum belirle → say

✓ bakimda
  Kaynak: tramvay_status['status'] == 'işletme' olan sayı
  Nerede?: ServiceStatus table (status = 'İşletme Kaynaklı Servis Dışı')
  Nasıl?: ServiceStatus durum alanı kontrolü

✓ arizali
  Kaynak: tramvay_status['status'] == 'ariza' olan sayı
  Nerede?: ServiceStatus table (status = 'Servis Dışı' veya başka)
  Nasıl?: ServiceStatus durum alanı kontrolü

✓ fleet_availability
  Kaynak: (aktif_servis + bakimda) / total_tramvay * 100
  Hesaplama: Aktif + İşletme Kaynaklı / Toplam * 100
  Örnek: (10 + 2) / 25 * 100 = 48%


ÖNEMLI NOT
==========
Stats içindeki TÜM SAYILAR ServiceStatus tablosundan gelen BUGÜN'ÜN verilerine dayanıyor!

Eğer bir tramvay için ServiceStatus kaydı yoksa:
→ Otomatik olarak 'aktif' sayılıyor (satır 447)

Bu nedenle:
- Yeni araclar otomatik aktif olur
- ServiceStatus kaydı düzenli güncellenmezse yanlış sonuç olur
"""
