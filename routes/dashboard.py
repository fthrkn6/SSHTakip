from flask import Blueprint, render_template, jsonify, session, current_app
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, KPISnapshot, Failure, ServiceLog, ServiceStatus
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
import pandas as pd
import os


def get_tram_ids_from_veriler(project_code=None):
    """Veriler.xlsx Sayfa2'den tram_id'leri yükle - tüm sayfalarda tek kaynak"""
    if project_code is None:
        project_code = session.get('current_project', 'belgrad')
    
    veriler_path = os.path.join(current_app.root_path, 'data', project_code, 'Veriler.xlsx')
    
    if not os.path.exists(veriler_path):
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]
    
    try:
        df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
        if 'tram_id' in df.columns:
            tram_ids = df['tram_id'].dropna().unique().tolist()
            # String'e dönüştür
            return [str(t) for t in tram_ids]
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]
    except Exception as e:
        print(f"Veriler.xlsx okuma hatası ({project_code}): {e}")
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def get_failures_from_excel():
    """Excel dosyasından arıza verilerini oku - logs/{project}/ariza_listesi/ birincil"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    
    # Birincil konum: logs/{project}/ariza_listesi/
    ariza_listesi_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    ariza_listesi_file = None
    use_sheet = None
    header_row = 0
    
    if os.path.exists(ariza_listesi_dir):
        for file in os.listdir(ariza_listesi_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                use_sheet = 'Ariza Listesi'
                header_row = 3
                break
    
    # Fallback: data/{project}/Veriler.xlsx
    if not ariza_listesi_file:
        veriler_file = os.path.join(current_app.root_path, 'data', current_project, 'Veriler.xlsx')
        if os.path.exists(veriler_file):
            ariza_listesi_file = veriler_file
            use_sheet = 'Veriler'
            header_row = 0
    
    if not ariza_listesi_file:
        return [], {}
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name=use_sheet, header=header_row)
        
        # Son 5 açık arızayı al (son 5 satır)
        recent = df.tail(5).to_dict('records') if len(df) > 0 else []
        
        # Arıza sınıfı istatistikleri
        sinif_counts = {}
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_counts = df[col].value_counts().to_dict()
                break
        
        return recent, sinif_counts
    except Exception as e:
        print(f"Excel okuma hatası: {e}")
        return [], {}


def get_today_completed_failures_count():
    """Excel Arıza Listesi'nden bugünün tamamlanan arızalarını say - Proje-dinamik"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # Arıza Listesi dosyasını bul
    ariza_listesi_file = None
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                break
    
    if not ariza_listesi_file:
        return 0
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        # Bugünün tarihi
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # Tarih ve durum sütunlarını bul
        tarih_col = None
        durum_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if tarih_col is None and ('tarih' in col_lower or 'date' in col_lower):
                tarih_col = col
            if durum_col is None and ('durum' in col_lower or 'status' in col_lower):
                durum_col = col
        
        if tarih_col is None or durum_col is None:
            return 0
        
        # Bugünün verileri ve "Kaydedildi" durumundaki arızaları filtrele
        today_completed = 0
        for idx, row in df.iterrows():
            try:
                # Tarih kontrolü
                tarih = row[tarih_col]
                if pd.isna(tarih):
                    continue
                
                # Tarih stringine çevir
                tarih_str = pd.Timestamp(tarih).strftime('%Y-%m-%d')
                
                # Bugünün mü?
                if tarih_str == today_str:
                    # Durum kontrolü
                    durum = str(row[durum_col]).strip() if not pd.isna(row[durum_col]) else ''
                    
                    # "Kaydedildi" statusu = tamamlanan
                    if durum == 'Kaydedildi':
                        today_completed += 1
            except Exception as e:
                print(f"Satır işlenirken hata ({idx}): {e}")
                continue
        
        return today_completed
    except Exception as e:
        print(f"Excel'den bugünün tamamlanan arıza sayısı alınırken hata: {e}")
        return 0


def get_ariza_counts_by_class():
    """Excel'den arızaları sınıflara göre say (A, B, C, D) - Proje-dinamik"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # Arıza Listesi dosyasını bul
    ariza_listesi_file = None
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                break
    
    # Sınıf tanımları
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
    
    if not ariza_listesi_file:
        return counts
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        # Arıza sınıfı sütununu bul
        sinif_col = None
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_col = col
                break
        
        if sinif_col:
            # Her arızayı kategorize et
            for sinif in df[sinif_col].dropna():
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
    
    current_project = session.get('current_project', 'belgrad')
    
    # Ekipman durumu özeti
    equipment_stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None, project_code=current_project).group_by(Equipment.status).all()
    
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
    
    # ===== Tramvay Filosofu - Veriler.xlsx Sayfa2'den Tram ID'leri Al =====
    tram_ids = get_tram_ids_from_veriler(current_project)
    
    # Tram ID'lerine göre Equipment'i filtrele (DB'den status, name, location vb al)
    if tram_ids:
        tramvaylar = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids),
            Equipment.parent_id == None
        ).all()
    else:
        # Fallback: Equipment tablosundan direkt çek (eğer Veriler.xlsx'ten tram_id çekemezse)
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
            
            # Status'u belirle - DB exact match
            if status_value == 'İşletme Kaynaklı Servis Dışı' or 'İşletme' in status_value:
                # İşletme Kaynaklı Servis Dışı = turuncu (işletme kaynaklı arıza)
                status_display = 'işletme'
                status_color = 'warning'
                status_from_db = 'İşletme Kaynaklı Servis Dışı'
            elif status_value == 'Servis Dışı' or 'Dışı' in status_value:
                # Servis Dışı = arızalı (kırmızı)
                status_display = 'ariza'
                status_color = 'danger'
                status_from_db = 'Servis Dışı'
            else:
                # Servis = aktif (yeşil)
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
    
    # Excel'deki TOPLAM arıza sayısı - Proje-dinamik
    from flask import current_app
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # Arıza Listesi dosyasını bul
    ariza_listesi_file = None
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                break
    
    total_failures_last_30_days = 0
    if ariza_listesi_file:
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
        'bugun_tamamlanan': get_today_completed_failures_count(),  # Excel Arıza Listesi'nden bugünün tamamlanan arızaları
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
    try:
        import pandas as pd
        import os
        
        ariza_listesi_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'ariza_listesi')
        ariza_listesi_file = os.path.join(ariza_listesi_dir, 'Ariza_Listesi_BELGRAD.xlsx')
        
        failures = []
        
        if not os.path.exists(ariza_listesi_file):
            print(f"[API] Dosya bulunamadı: {ariza_listesi_file}")
            return jsonify({'failures': [], 'error': 'File not found'})
        
        try:
            df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
            print(f"[API] Excel okundu - {len(df)} satır, Sütunlar: {list(df.columns)[:5]}...")
            
            # FRACAS ID sütununu doğrula
            if 'FRACAS ID' not in df.columns:
                print("[API] FRACAS ID sütunu bulunamadı")
                return jsonify({'failures': [], 'error': 'FRACAS ID column not found'})
            
            # Araç No sütununu bul
            arac_no_col = None
            if 'Araç No' in df.columns:
                arac_no_col = 'Araç No'
            
            # Eğer equipment_code verildiyse filtrele, değilse son 5'i getir
            if equipment_code and equipment_code.strip():
                if arac_no_col:
                    filtered_df = df[df[arac_no_col].astype(str).str.strip() == str(equipment_code).strip()]
                    filtered_df = filtered_df.tail(5)
                else:
                    filtered_df = df.tail(5)
            else:
                # Boş satırları hariç tut, son 5'i getir
                filtered_df = df[df['FRACAS ID'].notna()].tail(5)
            
            print(f"[API] Filtrelenen satır sayısı: {len(filtered_df)}")
            
            # Sütunları hazırla
            for idx, row in filtered_df.iterrows():
                try:
                    # Pandas Series olarak erişim
                    fracas_id = str(row['FRACAS ID']).strip() if pd.notna(row['FRACAS ID']) else ''
                    arac_no = str(row[arac_no_col]).strip() if arac_no_col and pd.notna(row[arac_no_col]) else ''
                    sistem = str(row['Sistem']).strip() if pd.notna(row['Sistem']) else ''
                    ariza_tanimi = str(row['Arıza Tanımı']).strip() if pd.notna(row['Arıza Tanımı']) else ''
                    tarih = str(row['Tarih']).strip() if pd.notna(row['Tarih']) else ''
                    durum = str(row['Durum']).strip() if pd.notna(row['Durum']) else ''
                    
                    failures.append({
                        'fracas_id': fracas_id,
                        'arac_no': arac_no,
                        'sistem': sistem,
                        'ariza_tanimi': ariza_tanimi,
                        'tarih': tarih,
                        'durum': durum
                    })
                    print(f"[API] Satır {idx}: {fracas_id} - {arac_no}")
                except Exception as e:
                    print(f"[API] Satır {idx} işleme hatası: {e}")
                    continue
            
            print(f"[API] Toplam {len(failures)} arıza döndürülüyor")
            return jsonify({'failures': failures, 'count': len(failures)})
            
        except Exception as excel_error:
            print(f"[API] Excel okuma hatası: {type(excel_error).__name__}: {excel_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'failures': [], 'error': f'Excel read error: {str(excel_error)}'})
    
    except Exception as e:
        print(f"[API] Genel hata: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'failures': [], 'error': f'General error: {str(e)}'})
