from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, KPISnapshot, Failure, ServiceLog, ServiceStatus
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
import pandas as pd
import os

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def get_failures_from_excel():
    """Excel dosyasından arıza verilerini oku"""
    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'ariza_listesi')
    ariza_listesi_file = os.path.join(ariza_listesi_dir, "Ariza_Listesi_BELGRAD.xlsx")
    
    if not os.path.exists(ariza_listesi_file):
        return [], {}
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        # Son 5 açık arızayı al (son 5 satır)
        recent = df.tail(5).to_dict('records') if len(df) > 0 else []
        
        # Arıza sınıfı istatistikleri
        sinif_counts = {}
        if 'Arıza Sınıfı' in df.columns:
            sinif_counts = df['Arıza Sınıfı'].value_counts().to_dict()
        
        return recent, sinif_counts
    except Exception as e:
        print(f"Excel okuma hatası: {e}")
        return [], {}


def get_ariza_counts_by_class():
    """Excel'den arızaları sınıflara göre say (A, B, C, D)"""
    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'ariza_listesi')
    ariza_listesi_file = os.path.join(ariza_listesi_dir, "Ariza_Listesi_BELGRAD.xlsx")
    
    # Sınıf tanımları (Veriler.xlsx'den)
    class_definitions = {
        'A': 'A-Kritik/Emniyet Riski',
        'B': 'B-Yüksek/Operasyon Engeller',
        'C': 'C-Hafif/Kısıtlı Operasyon',
        'D': 'D-Arıza Değildir'
    }
    
    # Başlangıçta tüm sınıfları 0 ile init et
    counts = {
        'A': {'label': 'A-Kritik/Emniyet Riski', 'count': 0},
        'B': {'label': 'B-Yüksek/Operasyon Engeller', 'count': 0},
        'C': {'label': 'C-Hafif/Kısıtlı Operasyon', 'count': 0},
        'D': {'label': 'D-Arıza Değildir', 'count': 0}
    }
    
    if not os.path.exists(ariza_listesi_file):
        return counts
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        if 'Arıza Sınıfı' in df.columns:
            # Her arızayı kategorize et
            for sinif in df['Arıza Sınıfı'].dropna():
                sinif_str = str(sinif).strip()
                
                # Sınıfın ilk harfini al (A, B, C, D)
                if sinif_str.startswith('A'):
                    counts['A']['count'] += 1
                elif sinif_str.startswith('B'):
                    counts['B']['count'] += 1
                elif sinif_str.startswith('C'):
                    counts['C']['count'] += 1
                elif sinif_str.startswith('D'):
                    counts['D']['count'] += 1
        
        return counts
    except Exception as e:
        print(f"Arıza sınıfı hesaplama hatası: {e}")
        return counts


@bp.route('/')
@login_required
def index():
    """Ana dashboard - Genel bakış"""
    
    # Ekipman durumu özeti
    equipment_stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None).group_by(Equipment.status).all()
    
    equipment_summary = {status: count for status, count in equipment_stats}
    
    # İş emri durumu özeti
    wo_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id)
    ).group_by(WorkOrder.status).all()
    
    wo_summary = {status: count for status, count in wo_stats}
    
    # Kritik öncelikli açık iş emirleri
    critical_work_orders = WorkOrder.query.filter(
        WorkOrder.priority == 'critical',
        WorkOrder.status.in_(['pending', 'scheduled', 'in_progress'])
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Yaklaşan bakımlar (7 gün içinde)
    upcoming_maintenance = WorkOrder.query.filter(
        WorkOrder.status.in_(['pending', 'scheduled']),
        WorkOrder.planned_start >= datetime.utcnow(),
        WorkOrder.planned_start <= datetime.utcnow() + timedelta(days=7)
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Son arızalar - Excel'den çek
    recent_failures, ariza_sinif_counts = get_failures_from_excel()
    
    # Son KPI'lar
    latest_kpi = KPISnapshot.query.order_by(
        KPISnapshot.snapshot_date.desc()
    ).first()
    
    # ===== Tramvay Filosu - ServiceStatus'ten Veri Çek (BUGÜNÜN VERİSİ) =====
    # Tüm tramvayları getir
    tramvaylar = Equipment.query.filter_by(parent_id=None).all()
    
    # Bugünün tarihi
    today = str(date.today())
    
    # Her tramvay için bugünün ServiceStatus kaydını al
    tramvay_statuses = []
    for tramvay in tramvaylar:
        # ServiceStatus'ten bugünün kaydını getir
        status_record = ServiceStatus.query.filter_by(
            tram_id=tramvay.equipment_code,
            date=today
        ).first()
        
        # Durum belirle
        status_display = 'aktif'
        status_color = 'success'
        status_from_db = 'Servis'
        
        if status_record:
            status_value = status_record.status if status_record.status else 'Servis'
            aciklama = status_record.aciklama if status_record.aciklama else ''
            
            # Status'u belirle
            if 'işletme kaynaklı' in status_value.lower():
                # İşletme kaynaklı = aktif (işletmede)
                status_display = 'aktif'
                status_color = 'success'
                status_from_db = 'İşletme Kaynaklı Servis Dışı'
            elif 'servis dışı' in status_value.lower():
                # Servis Dışı = arızalı
                status_display = 'ariza'
                status_color = 'danger'
                status_from_db = 'Servis Dışı'
            else:
                # Servis = aktif
                status_display = 'aktif'
                status_color = 'success'
                status_from_db = 'Servis'
        
        tramvay_statuses.append({
            'id': tramvay.id,
            'equipment_code': tramvay.equipment_code,
            'name': tramvay.name,
            'location': tramvay.location if hasattr(tramvay, 'location') else '',
            'total_km': tramvay.total_km if hasattr(tramvay, 'total_km') else 0,
            'current_km': tramvay.current_km if hasattr(tramvay, 'current_km') else 0,
            'status': status_display,
            'status_db': status_from_db,
            'status_color': status_color
        })
    
    # Toplam arızaları getir - SADECE Excel'den çek, Database'den değil
    son_arizalar_list, _ = get_failures_from_excel()
    son_arizalar = son_arizalar_list
    
    # Excel'deki TOPLAM arıza sayısı
    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'ariza_listesi')
    ariza_listesi_file = os.path.join(ariza_listesi_dir, "Ariza_Listesi_BELGRAD.xlsx")
    
    total_failures_last_30_days = 0
    if os.path.exists(ariza_listesi_file):
        try:
            df_for_count = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
            # Tüm arıza sayısı (filtreleme yok, sadece excel'deki tüm)
            total_failures_last_30_days = len(df_for_count[df_for_count.iloc[:, 0].notna()])
        except:
            total_failures_last_30_days = len(son_arizalar_list)
    
    # Arıza sınıflarına göre sayı hesapla
    ariza_by_class = get_ariza_counts_by_class()
    
    # Filo durumu istatistikleri - Servis durumundan hesapla
    aktif_count = 0
    ariza_count = 0
    bakim_count = 0
    
    for tramvay_status in tramvay_statuses:
        if tramvay_status['status'] == 'aktif':
            aktif_count += 1
        elif 'warning' in tramvay_status['status_color']:
            bakim_count += 1
        else:
            ariza_count += 1
    
    stats = {
        'total_tramvay': len(tramvay_statuses),
        'aktif_servis': aktif_count,
        'bakimda': bakim_count,
        'arizali': ariza_count,
        'aktif_ariza': len(son_arizalar),
        'bekleyen_is_emri': wo_summary.get('pending', 0),
        'devam_eden_is_emri': wo_summary.get('in_progress', 0),
        'bugun_tamamlanan': wo_summary.get('completed', 0),
    }
    
    return render_template('dashboard.html',
                         equipment_summary=equipment_summary,
                         wo_summary=wo_summary,
                         critical_work_orders=critical_work_orders,
                         upcoming_maintenance=upcoming_maintenance,
                         recent_failures=recent_failures,
                         latest_kpi=latest_kpi,
                         tramvaylar=tramvay_statuses,
                         son_arizalar=son_arizalar,
                         stats=stats,
                         kpi=latest_kpi,
                         total_failures_last_30_days=total_failures_last_30_days,
                         ariza_sinif_counts=ariza_by_class)


@bp.route('/api/equipment-status')
@login_required
def equipment_status_api():
    """Ekipman durumu grafiği için API"""
    stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None).group_by(Equipment.status).all()
    
    data = {
        'labels': [status for status, _ in stats],
        'values': [count for _, count in stats]
    }
    
    return jsonify(data)


@bp.route('/api/work-order-trend')
@login_required
def work_order_trend_api():
    """İş emri trend grafiği için API"""
    # Son 12 ay
    data = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = WorkOrder.query.filter(
            WorkOrder.created_at >= month_start,
            WorkOrder.created_at < month_end
        ).count()
        
        data.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    return jsonify(data[::-1])  # Ters çevir (eskiden yeniye)


@bp.route('/api/failures')
@bp.route('/api/failures/<equipment_code>')
@login_required
def get_equipment_failures(equipment_code=None):
    """Araçla ilgili son 5 arızayı Al - Arıza Listesi dosyasından
    Eğer equipment_code yoksa TÜM son 5 arızayı getir"""
    import pandas as pd
    import os
    
    ariza_listesi_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'ariza_listesi')
    ariza_listesi_file = os.path.join(ariza_listesi_dir, 'Ariza_Listesi_BELGRAD.xlsx')
    
    failures = []
    
    if os.path.exists(ariza_listesi_file):
        try:
            df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
            
            # Araç No sütununu bul
            arac_no_col = None
            # Doğrudan "Araç No" sütununu ara
            if 'Araç No' in df.columns:
                arac_no_col = 'Araç No'
            else:
                # Alternatif olarak fuzzy search yap
                for col in df.columns:
                    col_lower = str(col).lower().strip()
                    if 'no' in col_lower and any(word in col_lower for word in ['araç', 'arac', 'aracno']):
                        arac_no_col = col
                        break
            
            if arac_no_col:
                # Eğer equipment_code verildiyse filtrele
                if equipment_code and equipment_code.strip():
                    filtered_df = df[df[arac_no_col].astype(str).str.strip() == str(equipment_code).strip()]
                    # Son 5'i al
                    filtered_df = filtered_df.tail(5)
                else:
                    # Tüm son 5 arızayı al
                    filtered_df = df.tail(5)
                
                # Sütunları hazırla
                for idx, row in filtered_df.iterrows():
                    failures.append({
                        'fracas_id': str(row.get('FRACAS ID', '')).strip(),
                        'arac_no': str(row.get(arac_no_col, '')).strip(),
                        'sistem': str(row.get('Sistem', '')).strip(),
                        'ariza_tanimi': str(row.get('Arıza Tanımı', '')).strip(),
                        'tarih': str(row.get('Tarih', '')).strip(),
                        'durum': str(row.get('Durum', '')).strip()
                    })
        except Exception as e:
            print(f"Arıza Listesi hatası: {e}")
    
    return jsonify({'failures': failures})
