"""
Raporlama Routes - Dashboard, Bakım, KM, Senaryolar, Logs, Yönetim Raporları
"""

from flask import Blueprint, render_template, jsonify, request, send_file, session, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
import json
from pathlib import Path
import pandas as pd
import os
import logging
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER

from utils.utils_reporting import (
    ReportSystem, DashboardReport, MaintenanceReport, KMReport,
    ScenarioAnalysis, init_reporting_system
)
from utils.utils_excel_grid_manager import ExcelGridManager, RCAExcelManager
from models import Equipment, db, WorkOrder, Failure, ServiceStatus

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


# ==================== DASHBOARD RAPOR ====================
@reports_bp.route('/dashboard-rapor', methods=['POST'])
@login_required
def dashboard_rapor():
    """Dashboard snapshot raporunu indir"""
    try:
        project = session.get('current_project', 'belgrad')
        
        # Excel'den araçları yükle (dinamik, sabit limit yok)
        from routes.maintenance import load_trams_from_file
        tram_ids = load_trams_from_file(project)
        
        if tram_ids:
            tramvaylar = Equipment.query.filter(
                Equipment.equipment_code.in_(tram_ids)
            ).all()
        else:
            tramvaylar = Equipment.query.filter_by(
                project_code=project, parent_id=None
            ).all()
        
        # Rapor verisini hazırla
        tram_data = []
        for tram in tramvaylar:
            tram_data.append({
                'equipment_code': tram.equipment_code,
                'status': getattr(tram, 'status', 'Bilinmiyor'),
                'current_km': getattr(tram, 'current_km', 0),
                'total_km': getattr(tram, 'total_km', 0),
                'last_maintenance': getattr(tram, 'last_maintenance', '-'),
                'maintenance_status': 'Gerekli' if getattr(tram, 'current_km', 0) > 0 else 'Tamam',
                'failure_count': 0  # TODO: Failure tablosundan say
            })
        
        # Excel'e dışa aktar
        report_path = DashboardReport.generate(tram_data, project)
        
        return jsonify({
            'success': True,
            'message': f'[OK] Dashboard raporu olusturuldu',
            'file': report_path.name,
            'path': str(report_path)
        })
    
    except Exception as e:
        ReportSystem.log_action('Dashboard Report Error', {'error': str(e)}, 'ERROR')
        return jsonify({'success': False, 'message': f'[ERROR] Rapor hatasii: {str(e)}'}), 500


@reports_bp.route('/dashboard-logs', methods=['GET'])
@login_required
def dashboard_logs():
    """Dashboard raporlarını listele"""
    try:
        project = session.get('current_project', 'belgrad')
        reports = ReportSystem.get_recent_reports('dashboard', project, days=90)
        
        return jsonify({
            'success': True,
            'reports': [
                {
                    'filename': r['filename'],
                    'size': f"{r['size'] / 1024:.1f} KB",
                    'created': r['created'].strftime('%d.%m.%Y %H:%M'),
                    'path': r['path']
                }
                for r in reports
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== BAKIM RAPOR ====================
@reports_bp.route('/maintenance-rapor', methods=['POST'])
@login_required
def maintenance_rapor():
    """Bakım Planları raporunu indir"""
    try:
        project = session.get('current_project', 'belgrad')
        
        # Excel'den araçları yükle (dinamik, sabit limit yok)
        from routes.maintenance import load_trams_from_file
        tram_ids = load_trams_from_file(project)
        
        if tram_ids:
            tramvaylar = Equipment.query.filter(
                Equipment.equipment_code.in_(tram_ids)
            ).all()
        else:
            tramvaylar = Equipment.query.filter_by(
                project_code=project, parent_id=None
            ).all()
        
        # Rapor verisini hazırla
        maintenance_data = []
        for tram in tramvaylar:
            maintenance_data.append({
                'tram_id': tram.equipment_code,
                'name': f"Tramvay {tram.equipment_code}",
                'current_km': getattr(tram, 'current_km', 0),
                'total_km': getattr(tram, 'total_km', 0),
                'next_maintenance_km': getattr(tram, 'current_km', 0) + 500,
                'maintenance_type': 'A' if getattr(tram, 'current_km', 0) % 2 == 0 else 'B',
                'urgency': 'Kritik' if getattr(tram, 'current_km', 0) > 50000 else 'Normal',
                'last_operation': '2026-02-01'
            })
        
        # Excel'e dışa aktar
        report_path = MaintenanceReport.generate(maintenance_data, project)
        
        return jsonify({
            'success': True,
            'message': f'[OK] Bakim Planlari raporu olusturuldu',
            'file': report_path.name
        })
    
    except Exception as e:
        ReportSystem.log_action('Maintenance Report Error', {'error': str(e)}, 'ERROR')
        return jsonify({'success': False, 'message': f'[ERROR] Rapor hatasii: {str(e)}'}), 500


# ==================== KM RAPOR ====================
@reports_bp.route('/km-rapor', methods=['POST'])
@login_required
def km_rapor():
    """KM verilerinin raporunu indir"""
    try:
        project = session.get('current_project', 'belgrad')
        
        # km_data.json'ı oku
        km_file = Path(__file__).parent.parent / 'data' / project / 'km_data.json'
        km_data_dict = {}
        
        if km_file.exists():
            with open(km_file, 'r', encoding='utf-8') as f:
                km_data_dict = json.load(f)
        
        # Verileri hazırla
        km_data = []
        for tram_id, km_info in km_data_dict.items():
            km_data.append({
                'equipment_code': tram_id,
                'current_km': km_info.get('current_km', 0),
                'total_km': km_info.get('total_km', 0),
                'monthly_km': 0,
                'last_update': km_info.get('last_update', '-'),
                'updated_by': km_info.get('updated_by', '-'),
                'status': 'Aktif'
            })
        
        # Excel'e dışa aktar
        report_path = KMReport.generate(km_data, project)
        
        return jsonify({
            'success': True,
            'message': f'[OK] KM raporu olusturuldu',
            'file': report_path.name
        })
    
    except Exception as e:
        ReportSystem.log_action('KM Report Error', {'error': str(e)}, 'ERROR')
        return jsonify({'success': False, 'message': f'[ERROR] Rapor hatasii: {str(e)}'}), 500


# ==================== SENARYOLAR ====================
@reports_bp.route('/scenarios', methods=['GET'])
@login_required
def scenarios_page():
    """Senaryo analiz sayfası"""
    try:
        project = session.get('current_project', 'belgrad')
        
        # ServiceStatus DB'den benzersiz araç sayısını al
        from routes.service_status import get_tram_ids_from_veriler
        valid_trams = get_tram_ids_from_veriler(project)
        
        if not valid_trams:
            # Veriler.xlsx yoksa DB'den al
            tram_ids = db.session.query(ServiceStatus.tram_id).filter_by(
                project_code=project
            ).distinct().all()
            valid_trams = [t[0] for t in tram_ids if t[0]]
        
        if not valid_trams:
            # Fallback: Equipment tablosundan al
            tramvaylar = Equipment.query.filter_by(parent_id=None, project_code=project).all()
            if not tramvaylar:
                tramvaylar = Equipment.query.filter_by(project_code=project).all()
            valid_trams = [t.equipment_code for t in tramvaylar]
        
        # Veriyi hazırla
        tram_data = []
        for tram_id in valid_trams:
            tram_data.append({
                'equipment_code': tram_id,
                'current_km': 0,
                'total_km': 0,
                'failure_count': 0
            })
        
        # Senaryoları hesapla
        high_failure = ScenarioAnalysis.get_high_failure_trams(tram_data, threshold=5)
        high_km = ScenarioAnalysis.get_high_km_trams(tram_data, percentile=75)
        
        return render_template('scenarios.html', 
            high_failure_count=len(high_failure),
            high_km_count=len(high_km),
            total_trams=len(tram_data)
        )
    
    except Exception as e:
        return render_template('error.html', error=str(e)), 500


@reports_bp.route('/scenarios/data', methods=['GET'])
@login_required
def scenarios_status_data():
    """Senaryo Analiz sayfası için durum verilerini getir - ServiceStatus DB'den
    
    Query parametreleri:
    - period: 'haftalik' | 'aylik' | 'ucaylik' | 'altiylik' | 'yillik' | 'toplam'
    """
    try:
        from collections import defaultdict
        from routes.service_status import get_tram_ids_from_veriler
        
        project = session.get('current_project', 'belgrad')
        period = request.args.get('period', 'haftalik')
        
        # Tarih aralığını belirle
        today = date.today()
        if period == 'haftalik':
            start_date = today - timedelta(days=7)
        elif period == 'aylik':
            start_date = today - timedelta(days=30)
        elif period == 'ucaylik':
            start_date = today - timedelta(days=90)
        elif period == 'altiylik':
            start_date = today - timedelta(days=180)
        elif period == 'yillik':
            start_date = today - timedelta(days=365)
        else:  # 'toplam'
            start_date = None
        
        # Veriler.xlsx'ten geçerli araç listesini al
        valid_trams = get_tram_ids_from_veriler(project)
        valid_trams_set = set(valid_trams) if valid_trams else None
        
        # ServiceStatus DB'den verileri al
        query = ServiceStatus.query.filter_by(project_code=project)
        if start_date:
            query = query.filter(ServiceStatus.date >= start_date.strftime('%Y-%m-%d'))
        
        all_records = query.all()
        
        # Seçilen periyotta veri yoksa tüm verilere fallback
        fallback_used = False
        if not all_records and period != 'toplam':
            all_records = ServiceStatus.query.filter_by(project_code=project).all()
            fallback_used = True
        
        # Araç bazında availability hesapla: {tram_id: {active_days, total_days}}
        tram_stats = defaultdict(lambda: {'active': 0, 'total': 0})
        
        for record in all_records:
            if valid_trams_set and record.tram_id not in valid_trams_set:
                continue
            tram_stats[record.tram_id]['total'] += 1
            if record.status and 'Servis' in record.status and 'Dışı' not in record.status:
                tram_stats[record.tram_id]['active'] += 1
        
        # Availability dict oluştur
        availability = {}
        for tram_id, stats in sorted(tram_stats.items()):
            if stats['total'] > 0:
                availability[tram_id] = round((stats['active'] / stats['total']) * 100)
            else:
                availability[tram_id] = 0
        
        # Tarih aralığı metni
        if period == 'toplam' or start_date is None:
            date_range_str = "Tümü"
        elif fallback_used:
            date_range_str = "Seçilen periyotta veri yok — Tüm veriler gösteriliyor"
        else:
            date_range_str = f"{start_date.strftime('%d.%m.%Y')} - {today.strftime('%d.%m.%Y')}"
        
        return jsonify({
            'success': True,
            'period': period,
            'data': availability,
            'date_range': date_range_str
        })
    
    except Exception as e:
        logger.error(f"Error getting scenarios data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@reports_bp.route('/scenarios/rca-stats', methods=['GET'])
@login_required
def scenarios_rca_stats():
    """RCA analitiği - Sistem ve Alt Sistem arıza istatistikleri
    
    Query parametreleri:
    - period: 'haftalik' | 'aylik' | 'ucaylik' | 'altiylik' | 'yillik' | 'toplam'
    - stat_type: 'sistem' | 'altsistem' | 'ikisi'
    """
    try:
        project = session.get('current_project', 'belgrad')
        period = request.args.get('period', 'haftalik')
        stat_type = request.args.get('stat_type', 'ikisi')
        
        # RCA Manager ile oku
        rca_manager = RCAExcelManager(project)
        
        # Tarih aralığını belirle
        today = date.today()
        if period == 'haftalik':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'aylik':
            start_date = today - timedelta(days=30)
            end_date = today
        elif period == 'ucaylik':
            start_date = today - timedelta(days=90)
            end_date = today
        elif period == 'altiylik':
            start_date = today - timedelta(days=180)
            end_date = today
        elif period == 'yillik':
            start_date = today - timedelta(days=365)
            end_date = today
        else:  # 'toplam'
            start_date = None
            end_date = None
        
        # İstatistikleri al
        system_stats = {}
        subsystem_stats = {}
        
        if stat_type in ['sistem', 'ikisi']:
            system_stats = rca_manager.get_system_stats(
                current_app.root_path,
                start_date,
                end_date
            )
        
        if stat_type in ['altsistem', 'ikisi']:
            subsystem_stats = rca_manager.get_subsystem_stats(
                current_app.root_path,
                start_date,
                end_date
            )
        
        # Seçilen periyotta veri yoksa tüm verilere fallback yap
        if not system_stats and not subsystem_stats and period != 'toplam':
            if stat_type in ['sistem', 'ikisi']:
                system_stats = rca_manager.get_system_stats(
                    current_app.root_path, None, None
                )
            if stat_type in ['altsistem', 'ikisi']:
                subsystem_stats = rca_manager.get_subsystem_stats(
                    current_app.root_path, None, None
                )
        
        return jsonify({
            'success': True,
            'period': period,
            'system_stats': system_stats,
            'subsystem_stats': subsystem_stats,
            'date_range': f"{start_date.strftime('%d.%m.%Y') if start_date else 'Tümü'} - {end_date.strftime('%d.%m.%Y') if end_date else 'Bugün'}"
        })
    
    except Exception as e:
        logger.error(f"Error getting RCA stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@reports_bp.route('/scenarios/availability-trend', methods=['GET'])
@login_required
def scenarios_availability_trend():
    """Availability trend verilerini getir - Zamansal trend analizi
    Günlük rapor Excel ile aynı veri kaynağından (ServiceStatus DB) okur.
    
    Query parametreleri:
    - period: 'haftalik' | 'aylik' | 'ucaylik' | 'altiylik' | 'yillik' | 'toplam'
    """
    try:
        from collections import defaultdict
        from routes.service_status import get_tram_ids_from_veriler
        
        project = session.get('current_project', 'belgrad')
        period = request.args.get('period', 'haftalik')
        
        # Veriler.xlsx'ten geçerli araç listesini al
        valid_trams = get_tram_ids_from_veriler(project)
        valid_trams_set = set(valid_trams) if valid_trams else None
        
        # Tarih aralığını belirle ve granülarity'yi seç
        today = date.today()
        granularity = 'daily'
        
        if period == 'haftalik':
            start_date = today - timedelta(days=7)
            granularity = 'daily'
        elif period == 'aylik':
            start_date = today - timedelta(days=30)
            granularity = 'weekly'
        elif period == 'ucaylik':
            start_date = today - timedelta(days=90)
            granularity = 'monthly'
        elif period == 'altiylik':
            start_date = today - timedelta(days=180)
            granularity = 'monthly'
        elif period == 'yillik':
            start_date = today - timedelta(days=365)
            granularity = 'monthly'
        else:  # 'toplam'
            start_date = None
            granularity = 'monthly'
        
        # DB'den ServiceStatus verilerini al (günlük rapor Excel ile aynı kaynak)
        query = ServiceStatus.query.filter_by(project_code=project)
        if start_date:
            query = query.filter(ServiceStatus.date >= start_date.strftime('%Y-%m-%d'))
        
        all_records = query.order_by(ServiceStatus.date).all()
        
        if not all_records:
            return jsonify({
                'success': True, 'period': period, 'granularity': granularity,
                'data': {'dates': [], 'averages': []}
            })
        
        # Geçerli araçlara filtrele ve tarihe göre grupla
        # {tarih_str: {tram_id: status}}
        date_tram_status = defaultdict(dict)
        for record in all_records:
            if valid_trams_set and record.tram_id not in valid_trams_set:
                continue
            date_tram_status[record.date][record.tram_id] = record.status
        
        # Granülarite'ye göre bucket'la
        buckets = defaultdict(list)  # {bucket_key: [availability_pct_per_day]}
        
        for date_str, tram_statuses in date_tram_status.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                continue
            
            # Bucket key belirle
            if granularity == 'daily':
                bucket_key = date_str
            elif granularity == 'weekly':
                year, week, _ = date_obj.isocalendar()
                bucket_key = f"{year}-W{week:02d}"
            elif granularity == 'monthly':
                bucket_key = date_obj.strftime('%Y-%m')
            else:
                bucket_key = date_str
            
            # Bu gün için availability hesapla
            total = len(tram_statuses)
            if total > 0:
                active = sum(1 for s in tram_statuses.values() 
                           if s and 'Servis' in s and 'Dışı' not in s)
                day_availability = round((active / total) * 100, 1)
                buckets[bucket_key].append(day_availability)
        
        # Bucket'ları sırala ve ortalama al
        sorted_keys = sorted(buckets.keys())
        dates = []
        averages = []
        
        for key in sorted_keys:
            dates.append(str(key))
            vals = buckets[key]
            avg = round(sum(vals) / len(vals), 1) if vals else 0
            averages.append(avg)
        
        return jsonify({
            'success': True,
            'period': period,
            'granularity': granularity,
            'data': {
                'dates': dates,
                'averages': averages
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting availability trend: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400



@reports_bp.route('/scenarios/high-failure', methods=['GET'])
@login_required
def scenario_high_failure():
    """Yüksek arıza oranı senaryosu"""
    try:
        project = session.get('current_project', 'belgrad')
        tramvaylar = Equipment.query.all()
        
        tram_data = [{
            'equipment_code': t.equipment_code,
            'failure_count': 0
        } for t in tramvaylar]
        
        high_failure = ScenarioAnalysis.get_high_failure_trams(tram_data, 5)
        
        report_path = ScenarioAnalysis.generate_scenario_report(
            'Yuksek Ariza Orani',
            high_failure,
            project
        )
        
        return jsonify({
            'success': True,
            'message': '[OK] Senaryo raporu olusturuldu',
            'file': report_path.name,
            'count': len(high_failure)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@reports_bp.route('/scenarios/high-km', methods=['GET'])
@login_required
def scenario_high_km():
    """Yüksek KM senaryosu"""
    try:
        project = session.get('current_project', 'belgrad')
        tramvaylar = Equipment.query.all()
        
        tram_data = [{
            'equipment_code': t.equipment_code,
            'current_km': getattr(t, 'current_km', 0)
        } for t in tramvaylar]
        
        high_km = ScenarioAnalysis.get_high_km_trams(tram_data, 75)
        
        report_path = ScenarioAnalysis.generate_scenario_report(
            'Yuksek KM Tramvaylar',
            high_km,
            project
        )
        
        return jsonify({
            'success': True,
            'message': '[OK] Senaryo raporu olusturuldu',
            'file': report_path.name,
            'count': len(high_km)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== SISTEM LOGS ====================
@reports_bp.route('/system-logs', methods=['GET'])
@login_required
def system_logs_page():
    """Sistem loglarını görüntüle"""
    logs = ReportSystem.get_system_logs(hours=24)
    
    return render_template('system_logs.html', logs=logs, log_count=len(logs))


@reports_bp.route('/system-logs/api', methods=['GET'])
@login_required
def system_logs_api():
    """Sistem loglarını JSON olarak döndür"""
    hours = request.args.get('hours', 24, type=int)
    logs = ReportSystem.get_system_logs(hours=hours)
    
    return jsonify({
        'success': True,
        'logs': logs,
        'total': len(logs),
        'hours': hours
    })


@reports_bp.route('/recent-reports', methods=['GET'])
@login_required
def recent_reports():
    """Son raporları listele"""
    try:
        project = session.get('current_project', 'belgrad')
        
        dashboard_reports = ReportSystem.get_recent_reports('dashboard', project, 30)
        maintenance_reports = ReportSystem.get_recent_reports('maintenance', project, 30)
        km_reports = ReportSystem.get_recent_reports('km', project, 30)
        
        return render_template('recent_reports.html',
            dashboard_reports=dashboard_reports,
            maintenance_reports=maintenance_reports,
            km_reports=km_reports
        )
    
    except Exception as e:
        return render_template('error.html', error=str(e)), 500


@reports_bp.route('/cleanup-old', methods=['POST'])
@login_required
def cleanup_old_reports():
    """60 gün önceki raporları sil"""
    try:
        deleted = ReportSystem.cleanup_old_reports(days=60)
        
        return jsonify({
            'success': True,
            'message': f'[OK] {deleted} eski rapor silindi'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== YÖNETIM RAPORLARI ====================

def _load_projects():
    """projects_config.json + data/ klasöründen dinamik proje listesi oluştur"""
    projects = {}
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'projects_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for p in config.get('projects', []):
                if p.get('status') == 'aktif':
                    projects[p['code']] = p.get('name', p['code'].capitalize())
    except Exception:
        pass
    # data/ klasöründen Veriler.xlsx olan projeleri de ekle
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                if item not in projects and os.path.isdir(os.path.join(data_dir, item)):
                    if os.path.exists(os.path.join(data_dir, item, 'Veriler.xlsx')):
                        projects[item] = item.capitalize()
    except Exception:
        pass
    if not projects:
        # Fallback
        projects = {
            'belgrad': 'Belgrad', 'iasi': 'Iași', 'timisoara': 'Timișoara',
            'kayseri': 'Kayseri', 'kocaeli': 'Kocaeli', 'gebze': 'Gebze',
            'samsun': 'Samsun', 'istanbul': 'İstanbul', 'napoli': 'Napoli'
        }
    return projects

# Modül seviyesinde PROJECTS - diğer fonksiyonlar tarafından kullanılıyor
PROJECTS = _load_projects()

PERIODS = {
    'weekly': ('Haftalık', 7),
    'monthly': ('Aylık', 30),
    '6months': ('6 Aylık', 180),
    'yearly': ('Yıllık', 365),
    'total': ('Total', None)
}


def get_fracas_data(project=None):
    """Seçili projenin FRACAS verilerini yükle - Flask context dışında çalışır"""
    try:
        if project is None:
            project = session.get('current_project', 'belgrad')
        
        # Flask app path'i - app context'i olmasa da çalışır
        try:
            from flask import current_app
            app_path = current_app.root_path
        except:
            # Flask context'i yoksa, bu script dosyasının üstünü kullan
            app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        project_upper = project.upper()
        ariza_listesi_dir = os.path.join(app_path, 'logs', project_upper, 'ariza_listesi')
        
        logger.info(f'FRACAS veri yükleme: {ariza_listesi_dir}')
        
        if not os.path.exists(ariza_listesi_dir):
            logger.error(f'Dizin bulunamadi: {ariza_listesi_dir}')
            return None
        
        excel_files = [f for f in os.listdir(ariza_listesi_dir) 
                      if f.upper().startswith('FRACAS') and f.endswith('.xlsx') and not f.startswith('~$')]
        
        if not excel_files:
            logger.error(f'FRACAS Excel dosyasi bulunamadi: {ariza_listesi_dir}')
            return None
        
        filepath = os.path.join(ariza_listesi_dir, excel_files[0])
        logger.info(f'Yuklenen dosya: {filepath}')
        
        try:
            # Şeeti al (bazen 0, bazen 3 olabilir)
            df = pd.read_excel(filepath, sheet_name='FRACAS', header=3)
            
            # Sütun adlarını temizle
            df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
            
            # FRACAS ID'si boş satırları kaldır
            fracas_id_col = None
            for col in df.columns:
                if 'fracas' in col.lower() and 'id' in col.lower():
                    fracas_id_col = col
                    break
            
            if fracas_id_col:
                df = df[df[fracas_id_col].notna()]
            
            if df.empty:
                logger.error(f'Excel bos: {filepath}')
                return None
            
            logger.info(f'Yuklendi: {len(df)} satir, {len(df.columns)} sutun')
            return df
            
        except Exception as e:
            logger.error(f'Excel okuma hatasi ({excel_files[0]}): {e}', exc_info=True)
            return None
    
    except Exception as e:
        logger.error(f'get_fracas_data hatasi: {e}', exc_info=True)
        return None


def filter_by_period(df, period, end_date=None):
    """Verileri periyoda göre filtrele"""
    if df is None or df.empty:
        return None
    
    if period == 'total':
        return df
    
    if end_date is None:
        end_date = datetime.now()
    
    days = PERIODS[period][1]
    start_date = end_date - timedelta(days=days)
    
    date_col = None
    for col in df.columns:
        if 'tarih' in col.lower() and 'hata' in col.lower():
            date_col = col
            break
    
    if date_col and date_col in df.columns:
        try:
            # Ensure all values are converted to datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            # Remove rows with NaT (invalid dates)
            df_clean = df.dropna(subset=[date_col])
            
            # Ensure start_date and end_date are proper datetime
            start_date = pd.Timestamp(start_date)
            end_date = pd.Timestamp(end_date)
            
            # Use astype to ensure date column is datetime64
            df_clean[date_col] = df_clean[date_col].astype('datetime64[ns]')
            
            filtered = df_clean[(df_clean[date_col] >= start_date) & (df_clean[date_col] <= end_date)]
            return filtered if not filtered.empty else df_clean
        except Exception as e:
            return df
    
    return df


def get_vehicle_analysis(df):
    """Araç bazında analiz"""
    if df is None or df.empty:
        return None
    
    vehicle_col = None
    km_col = None
    for col in df.columns:
        if 'araç numarası' in col.lower():
            vehicle_col = col
        if 'araç kilometresi' in col.lower():
            km_col = col
    
    if not vehicle_col:
        return None
    
    vehicles = []
    for vehicle in df[vehicle_col].dropna().unique():
        v_data = df[df[vehicle_col] == vehicle]
        
        # KM değerini güvenli şekilde al
        km = 0
        if km_col:
            try:
                km_values = pd.to_numeric(v_data[km_col], errors='coerce')
                km = km_values.max()
                if pd.isna(km):
                    km = 0
            except:
                km = 0
        
        failure_count = len(v_data)
        
        if failure_count > 0 and km > 0:
            mtbf = km / failure_count
        else:
            mtbf = 0
        
        vehicles.append({
            'vehicle': str(vehicle),
            'total_km': km,
            'failure_count': failure_count,
            'mtbf': round(mtbf, 0) if mtbf > 0 else 0,
            'availability': round(max(0, 98 - (failure_count * 0.5)), 1)
        })
    
    return sorted(vehicles, key=lambda x: x['failure_count'], reverse=True)


def get_system_analysis(df):
    """Sistem bazında root cause analizi"""
    if df is None or df.empty:
        return None
    
    system_col = None
    repair_col = None
    for col in df.columns:
        if 'sistem' in col.lower() and 'alt' not in col.lower():
            system_col = col
        if 'tamir süresi' in col.lower():
            repair_col = col
    
    if not system_col:
        return None
    
    systems = []
    for system in df[system_col].dropna().unique():
        s_data = df[df[system_col] == system]
        count = len(s_data)
        
        downtime = 0
        if repair_col and repair_col in s_data.columns:
            try:
                s_data[repair_col] = pd.to_numeric(s_data[repair_col], errors='coerce')
                downtime = s_data[repair_col].sum()
            except:
                pass
        
        systems.append({
            'system': str(system),
            'count': count,
            'downtime_hours': round(downtime / 60, 1) if downtime > 0 else 0,
            'percentage': 0
        })
    
    total = sum(s['count'] for s in systems)
    for s in systems:
        s['percentage'] = round((s['count'] / total * 100), 1) if total > 0 else 0
    
    return sorted(systems, key=lambda x: x['count'], reverse=True)


def get_downtime_analysis(workorder_df):
    """Servis dışı sebebi analizi (WorkOrder'dan)"""
    if workorder_df is None or workorder_df.empty:
        return None
    
    downtime_data = workorder_df[workorder_df['status'].str.contains('Maintenance|Servis', case=False, na=False)]
    
    if downtime_data.empty:
        return None
    
    systems = []
    for system in downtime_data['system'].dropna().unique():
        s_data = downtime_data[downtime_data['system'] == system]
        count = len(s_data)
        avg_duration = s_data['duration'].mean()
        
        subsystems = s_data['subsystem'].value_counts().head(3).to_dict()
        
        systems.append({
            'system': str(system),
            'count': count,
            'avg_duration': round(avg_duration, 2),
            'subsystems': {str(k): int(v) for k, v in subsystems.items() if pd.notna(k)}
        })
    
    return sorted(systems, key=lambda x: x['count'], reverse=True)


def get_supplier_system_matrix(df):
    """Tedarikçi-Sistem Matrisi"""
    if df is None or df.empty:
        return None
    
    supplier_col = None
    system_col = None
    for col in df.columns:
        if 'tedarikçi' in col.lower():
            supplier_col = col
        if 'sistem' in col.lower() and 'alt' not in col.lower():
            system_col = col
    
    if not supplier_col or not system_col:
        return None
    
    matrix = {}
    for supplier in df[supplier_col].dropna().unique():
        if pd.isna(supplier):
            continue
        s_data = df[df[supplier_col] == supplier]
        for system in s_data[system_col].dropna().unique():
            if pd.isna(system):
                continue
            count = len(s_data[s_data[system_col] == system])
            
            if str(system) not in matrix:
                matrix[str(system)] = {}
            matrix[str(system)][str(supplier)] = count
    
    return matrix if matrix else None


@reports_bp.route('/dashboard-yonetim', methods=['GET'])
@login_required
def management_dashboard():
    """Yönetim raporları sunumsal dashboard - Tüm projeler KPI"""
    return render_template('management_dashboard.html')


@reports_bp.route('/api/projects-kpi', methods=['GET'])
@login_required
def get_projects_kpi():
    """Tüm projeler için kapsamlı KPI verilerini döndür - Enhanced"""
    logger.info("/reports/api/projects-kpi endpoint called")
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        projects_data = {}
        active_projects = _load_projects()
        
        for project_code, project_name in active_projects.items():
            try:
                # === TEMEL KPİ'LAR ===
                # Proje için tüm araçları say
                total_vehicles = Equipment.query.filter_by(
                    project_code=project_code,
                    parent_id=None
                ).count()
                
                # Aktif araçları say
                active_vehicles = Equipment.query.filter_by(
                    project_code=project_code,
                    parent_id=None,
                    status='aktif'
                ).count()
                
                availability = round((active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0)
                
                # Bugünkü araç durumu sayıları (DB'den - ServiceStatus)
                servis_disi_count = 0
                isletme_kaynakli_count = 0
                aktif_count = 0
                try:
                    from utils.utils_project_excel_store import normalize_status
                    today_str = date.today().strftime('%Y-%m-%d')
                    # Önce bugünü dene, yoksa en son tarihli kaydı bul
                    day_records = ServiceStatus.query.filter_by(
                        project_code=project_code, date=today_str
                    ).all()
                    if not day_records:
                        latest_date = db.session.query(
                            db.func.max(ServiceStatus.date)
                        ).filter_by(project_code=project_code).scalar()
                        if latest_date:
                            day_records = ServiceStatus.query.filter_by(
                                project_code=project_code, date=latest_date
                            ).all()
                    if day_records:
                        for rec in day_records:
                            ns = normalize_status(rec.status)
                            if ns == 'Servis':
                                aktif_count += 1
                            elif ns == 'İşletme Kaynaklı Servis Dışı':
                                isletme_kaynakli_count += 1
                            elif ns == 'Servis Dışı':
                                servis_disi_count += 1
                        # DB'de olmayan araçları servis dışı say
                        counted = aktif_count + servis_disi_count + isletme_kaynakli_count
                        if counted < total_vehicles:
                            servis_disi_count += (total_vehicles - counted)
                    else:
                        aktif_count = active_vehicles
                        servis_disi_count = total_vehicles - active_vehicles
                except Exception:
                    aktif_count = active_vehicles
                    servis_disi_count = total_vehicles - active_vehicles
                
                # Toplam arıza sayısı (tüm FRACAS kayıtları)
                total_failures_all = 0
                try:
                    _fracas = get_fracas_data(project_code)
                    if _fracas is not None and not _fracas.empty:
                        total_failures_all = len(_fracas)
                except:
                    total_failures_all = 0
                
                # Tüm zamanların availability ortalaması (DB'den - ServiceStatus)
                avg_availability_all = 0
                try:
                    from sqlalchemy import func as _fn
                    from collections import defaultdict
                    # Her tarih+status için kayıt sayısı
                    date_status_counts = db.session.query(
                        ServiceStatus.date,
                        ServiceStatus.status,
                        _fn.count(ServiceStatus.id)
                    ).filter(
                        ServiceStatus.project_code == project_code
                    ).group_by(ServiceStatus.date, ServiceStatus.status).all()
                    
                    if date_status_counts:
                        date_totals = defaultdict(lambda: {'total': 0, 'available': 0})
                        for date_val, status_val, cnt in date_status_counts:
                            ns = normalize_status(status_val)
                            date_totals[date_val]['total'] += cnt
                            if ns in ('Servis', 'İşletme Kaynaklı Servis Dışı'):
                                date_totals[date_val]['available'] += cnt
                        avail_values = []
                        for dt, counts in date_totals.items():
                            if counts['total'] > 0:
                                avail_values.append(counts['available'] / counts['total'] * 100)
                        if avail_values:
                            avg_availability_all = round(sum(avail_values) / len(avail_values))
                        else:
                            avg_availability_all = availability
                    else:
                        avg_availability_all = availability
                except Exception:
                    avg_availability_all = availability
                
                # MTTR (FRACAS'tan dakika cinsinden)
                mttr_minutes = 0
                try:
                    _fracas2 = get_fracas_data(project_code)
                    if _fracas2 is not None and not _fracas2.empty:
                        repair_col = None
                        for col in _fracas2.columns:
                            col_lower = col.lower()
                            if 'personel' in col_lower:
                                continue
                            if ('tamir süresi' in col_lower and 'dakika' in col_lower) or 'repair time' in col_lower:
                                repair_col = col
                                break
                        if not repair_col:
                            for col in _fracas2.columns:
                                col_lower = col.lower()
                                if 'personel' in col_lower:
                                    continue
                                if 'tamir süresi' in col_lower or 'tamir suresi' in col_lower:
                                    repair_col = col
                                    break
                        if repair_col:
                            vals = pd.to_numeric(_fracas2[repair_col], errors='coerce').dropna()
                            vals = vals[vals > 0]
                            if len(vals) > 0:
                                # IQR outlier filter
                                q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
                                iqr = q3 - q1
                                upper = max(q3 + 3 * iqr, 1440)
                                vals = vals[vals <= upper]
                                mttr_minutes = round(vals.sum() / max(len(_fracas2), 1))
                except:
                    mttr_minutes = 0
                
                # Son 30 günde arıza sayısı
                thirty_days_ago = datetime.now() - timedelta(days=30)
                failures_30 = 0
                try:
                    failures_30 = Failure.query.join(Equipment).filter(
                        Equipment.project_code == project_code,
                        Failure.failure_date >= thirty_days_ago
                    ).count()
                except:
                    # Database schema mismatch - get from FRACAS instead
                    try:
                        fracas_df = get_fracas_data(project_code)
                        if fracas_df is not None and not fracas_df.empty:
                            # Son 30 güne göre filtrele
                            filtered_df = filter_by_period(fracas_df, 'monthly')
                            failures_30 = len(filtered_df) if filtered_df is not None else 0
                    except:
                        failures_30 = 0
                
                # Ortalama MTTR hesapla (iş emirlerinden gerçek tamir süresi)
                mttr = 0
                try:
                    from sqlalchemy import func as sa_func
                    mttr_result = db.session.query(
                        sa_func.avg(WorkOrder.labor_hours)
                    ).filter(
                        WorkOrder.project_code == project_code,
                        WorkOrder.status == 'Completed',
                        WorkOrder.labor_hours > 0
                    ).scalar()
                    mttr = round(mttr_result, 1) if mttr_result else 0
                except:
                    # Fallback: downtime_minutes from failures
                    try:
                        from sqlalchemy import func as sa_func
                        avg_downtime = db.session.query(
                            sa_func.avg(Failure.downtime_minutes)
                        ).filter(
                            Failure.project_code == project_code,
                            Failure.downtime_minutes > 0
                        ).scalar()
                        mttr = round(avg_downtime / 60, 1) if avg_downtime else 0
                    except:
                        mttr = 0
                
                # === GELIŞMIŞ KPİ'LAR ===
                # Sınıf A (Kritik) Arıza Sayısı
                critical_failures = 0
                try:
                    # FRACAS dosyasından sınıf A arızaları oku
                    fracas_df = get_fracas_data(project_code)
                    if fracas_df is not None and not fracas_df.empty:
                        # Sınıf sütununu bul
                        class_col = None
                        for col in fracas_df.columns:
                            if 'sınıf' in col.lower() or 'class' in col.lower():
                                class_col = col
                                break
                        
                        if class_col:
                            critical_failures = len(fracas_df[fracas_df[class_col].astype(str).str.contains('A', case=False, na=False)])
                except:
                    critical_failures = 0
                
                # Önleyici Bakım Oranı (%)
                preventive_maintenance_ratio = 0
                try:
                    total_wo = WorkOrder.query.filter_by(project_code=project_code).count()
                    preventive_wo = WorkOrder.query.filter(
                        WorkOrder.project_code == project_code,
                        WorkOrder.work_type == 'Preventive'
                    ).count()
                    preventive_maintenance_ratio = round(
                        (preventive_wo / total_wo * 100) if total_wo > 0 else 0, 1
                    )
                except Exception as e:
                    logger.debug(f"Preventive ratio calculation failed for {project_code}: {e}")
                    preventive_maintenance_ratio = 0
                
                # Ortalama Tamir Süresi (saat)
                avg_repair_time = 0
                try:
                    completed_wo = WorkOrder.query.filter(
                        WorkOrder.project_code == project_code,
                        WorkOrder.status == 'Completed'
                    ).all()
                    
                    if completed_wo:
                        total_hours = 0
                        count = 0
                        for wo in completed_wo:
                            if wo.labor_hours and wo.labor_hours > 0:
                                total_hours += wo.labor_hours
                                count += 1
                        avg_repair_time = round(total_hours / count, 1) if count > 0 else 0
                except:
                    avg_repair_time = 0
                
                # Son 30 Günde Arızasız Araç Sayısı
                problem_free_vehicles = 0
                try:
                    all_vehicles = Equipment.query.filter_by(
                        project_code=project_code,
                        parent_id=None
                    ).all()
                    
                    for vehicle in all_vehicles:
                        try:
                            vehicle_failures = Failure.query.filter(
                                Failure.equipment_id == vehicle.id,
                                Failure.failure_date >= thirty_days_ago
                            ).count()
                            if vehicle_failures == 0:
                                problem_free_vehicles += 1
                        except:
                            # If Failure query fails, assume no failures
                            problem_free_vehicles += 1
                except Exception as e:
                    logger.debug(f"Problem-free vehicles calculation failed for {project_code}: {e}")
                    problem_free_vehicles = 0
                
                # Proje durumunu belirle
                if availability >= 85:
                    status = 'active'
                elif availability >= 75:
                    status = 'maintenance'
                else:
                    status = 'issues'
                
                projects_data[project_code] = {
                    'name': project_name,
                    # Temel
                    'vehicles': total_vehicles,
                    'availability': availability,
                    'failures30': failures_30,
                    'mttr': mttr,
                    'status': status,
                    # Gelişmiş
                    'critical_failures': critical_failures,
                    'preventive_ratio': preventive_maintenance_ratio,
                    'avg_repair_time': avg_repair_time,
                    'problem_free_vehicles': problem_free_vehicles,
                    'active_vehicles': active_vehicles,
                    'ariza_arazlari': total_vehicles - active_vehicles,
                    # Yeni alanlar
                    'aktif_count': aktif_count,
                    'servis_disi_count': servis_disi_count,
                    'isletme_kaynakli_count': isletme_kaynakli_count,
                    'total_failures_all': total_failures_all,
                    'avg_availability_all': avg_availability_all,
                    'mttr_minutes': mttr_minutes
                }
            except Exception as e:
                logger.warning(f"Error getting KPI for {project_code}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                projects_data[project_code] = {
                    'name': project_name,
                    'vehicles': 0,
                    'availability': 0,
                    'failures30': 0,
                    'mttr': 0,
                    'status': 'issues',
                    'critical_failures': 0,
                    'preventive_ratio': 0,
                    'avg_repair_time': 0,
                    'problem_free_vehicles': 0,
                    'active_vehicles': 0,
                    'ariza_arazlari': 0,
                    'aktif_count': 0,
                    'servis_disi_count': 0,
                    'isletme_kaynakli_count': 0,
                    'total_failures_all': 0,
                    'avg_availability_all': 0,
                    'mttr_minutes': 0
                }
        
        # NaN/None/inf değerlerini temizle (JSON serializable değiller)
        import math
        for pcode, pdata in projects_data.items():
            for k, v in pdata.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    projects_data[pcode][k] = 0
                elif v is None and k != 'name' and k != 'status':
                    projects_data[pcode][k] = 0
        
        return jsonify({
            'success': True,
            'data': projects_data
        })
    
    except Exception as e:
        logger.error(f"Error in get_projects_kpi: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@reports_bp.route('/management', methods=['GET', 'POST'])
@login_required
def management_report():
    """Yönetim raporu seçim sayfası - Müdür rolü"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        project = request.form.get('project')
        periods = request.form.getlist('periods')
        
        if not project or (project != 'all' and project not in PROJECTS):
            flash('Lütfen geçerli bir proje seçiniz.', 'warning')
            return redirect(url_for('reports.management_report'))
        
        if not periods:
            flash('Lütfen en az bir periyot seçiniz.', 'warning')
            return redirect(url_for('reports.management_report'))
        
        return redirect(url_for('reports.generate_management_pdf', project=project, periods=','.join(periods)))
    
    return render_template('reports/form.html', projects=PROJECTS, periods=PERIODS)


@reports_bp.route('/management/generate/<project>')
@login_required
def generate_management_pdf(project):
    """PDF rapor oluştur (tek proje veya tüm projeler)"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard.index'))
    
    periods = request.args.get('periods', 'monthly').split(',')
    
    try:
        # Tüm projeler seçimi
        if project == 'all':
            projects_list = list(PROJECTS.keys())
            report_title = 'Tüm Projeler'
            
            # Tüm projeler için veri yükle
            fracas_dfs = {}
            for proj in projects_list:
                df = get_fracas_data(proj)
                if df is not None and not df.empty:
                    fracas_dfs[proj] = df
            
            pdf_buffer = create_management_pdf_multi(projects_list, periods, fracas_dfs)
        
        # Tek proje seçimi
        elif project in PROJECTS:
            report_title = PROJECTS[project]
            fracas_df = get_fracas_data(project)
            
            if fracas_df is None or fracas_df.empty:
                flash('Bu proje için veri bulunamadı.', 'error')
                return redirect(url_for('reports.management_report'))
            
            pdf_buffer = create_management_pdf(project, fracas_df, periods)
        
        else:
            flash('Geçersiz proje.', 'error')
            return redirect(url_for('reports.management_report'))
        
        pdf_buffer.seek(0)
        filename = f'Yonetim_Raporu_{report_title}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f'PDF oluşturma hatasi: {e}')
        flash(f'Rapor oluştururken hata: {str(e)}', 'error')
        return redirect(url_for('reports.management_report'))


def create_management_pdf(project, fracas_df, periods):
    """PDF rapor oluştur - KPI Dashboard stili"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.7*cm, leftMargin=0.7*cm,
                           rightMargin=0.7*cm, bottomMargin=0.7*cm)
    story = []
    
    styles = getSampleStyleSheet()
    
    # KPI Stili - Başlık
    title_style = ParagraphStyle(
        'KPITitle', parent=styles['Heading1'], fontSize=22,
        textColor=colors.white, spaceAfter=8, alignment=TA_CENTER,
        fontName='Helvetica-Bold', leading=26
    )
    
    # Bilgi metni
    info_style = ParagraphStyle(
        'InfoText', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#555'), spaceAfter=6
    )
    
    # KPI Card başlığı
    kpi_heading_style = ParagraphStyle(
        'KPIHeading', parent=styles['Heading2'], fontSize=12,
        textColor=colors.white, spaceAfter=6, fontName='Helvetica-Bold'
    )
    
    # Tablo header
    table_heading_style = ParagraphStyle(
        'TableHeading', parent=styles['Heading3'], fontSize=11,
        textColor=colors.white, spaceAfter=4, fontName='Helvetica-Bold'
    )
    
    # Normal metni
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333')
    )
    
    # Project adını normalize et
    project_key = project.lower()
    project_display = PROJECTS.get(project_key, project)
    
    for idx, period in enumerate(periods):
        if period not in PERIODS:
            continue
        
        period_name, _ = PERIODS[period]
        filtered_fracas = filter_by_period(fracas_df, period)
        
        if filtered_fracas is None or filtered_fracas.empty:
            # Başlık
            header_table = Table([['YONETIM RAPORU - ' + project_display.upper()]], 
                                colWidths=[19*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 16),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.2*cm))
            
            info_text = f'Periyot: {period_name} | {datetime.now().strftime("%d.%m.%Y %H:%M")}'
            story.append(Paragraph(info_text, info_style))
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph('[!] Bu periyot icin veri bulunamadi', normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            if idx < len(periods) - 1:
                story.append(PageBreak())
            continue
        
        # ==== BAŞLIK BÖLÜMÜ ====
        header_table = Table([['YONETIM RAPORU - ' + project_display.upper()]], 
                            colWidths=[19*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.2*cm))
        
        # Tarih ve rapor bilgisi
        if period == 'total':
            date_range = 'Tum Zamanlar'
        else:
            end_date = datetime.now()
            days = PERIODS[period][1]
            start_date = end_date - timedelta(days=days)
            date_range = f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'
        
        info_line = f'Periyot: <b>{period_name}</b> ({date_range}) | Rapor: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
        story.append(Paragraph(info_line, info_style))
        story.append(Spacer(1, 0.3*cm))
        
        # ==== KPI METRICS CARDS ====
        vehicle_data = get_vehicle_analysis(filtered_fracas)
        system_data = get_system_analysis(filtered_fracas)
        
        if vehicle_data or system_data:
            # KPI özeti 4 card halinde
            kpi_metrics = []
            
            if vehicle_data:
                total_vehicles = len(vehicle_data)
                avg_availability = sum(v['availability'] for v in vehicle_data) / len(vehicle_data)
                kpi_metrics.append(f'<b>ARACLAR</b><br/>{total_vehicles} Arac<br/>Avail: {avg_availability:.0f}%')
            else:
                kpi_metrics.append('<b>ARACLAR</b><br/>0 Arac')
            
            if system_data:
                total_systems = len(system_data)
                total_failures = sum(s['count'] for s in system_data)
                kpi_metrics.append(f'<b>SISTEMLER</b><br/>{total_systems} Sistem<br/>{total_failures} Ariza')
            else:
                kpi_metrics.append('<b>SISTEMLER</b><br/>0 Sistem')
            
            if system_data:
                avg_downtime = sum(s['downtime_hours'] for s in system_data) / len(system_data)
                kpi_metrics.append(f'<b>ORTALAMA</b><br/>Downtime<br/>{avg_downtime:.1f} saat')
            else:
                kpi_metrics.append('<b>ORTALAMA</b><br/>Downtime<br/>0 saat')
            
            if vehicle_data:
                avg_mtbf = sum(v['mtbf'] for v in vehicle_data) / len(vehicle_data)
                kpi_metrics.append(f'<b>MTBF</b><br/>{avg_mtbf:,.0f} km<br/>Ort Deger')
            else:
                kpi_metrics.append('<b>MTBF</b><br/>N/A')
            
            # KPI Cards tablosu
            colors_list = [colors.HexColor('#667eea'), colors.HexColor('#764ba2'),
                          colors.HexColor('#27ae60'), colors.HexColor('#f39c12')]
            
            kpi_rows = [[Paragraph(m, kpi_heading_style) for m in kpi_metrics]]
            kpi_table = Table(kpi_rows, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors_list[0]),
                ('BACKGROUND', (1, 0), (1, 0), colors_list[1]),
                ('BACKGROUND', (2, 0), (2, 0), colors_list[2]),
                ('BACKGROUND', (3, 0), (3, 0), colors_list[3]),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('HEIGHT', (0, 0), (-1, -1), 1.2*cm),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 0.3*cm))
        
        # ==== ARAC BAZINDA TABLO ====
        if vehicle_data:
            section_header = Table([['1. ARAC BAZINDA ANALIZ']], colWidths=[19*cm])
            section_header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(section_header)
            story.append(Spacer(1, 0.15*cm))
            
            try:
                # Basit text tablosu spring - daha kolay okunabilir
                # Format: Arac No | KM | Ariza | MTBF | Avail
                text_table = '<font face="Courier" size="8">'
                text_table += '<b>Arac No      KM            Ariza    MTBF        Avail</b><br/>'
                for v in vehicle_data[:10]:
                    vehicle_no = str(v.get('vehicle', 'N/A')).ljust(11)
                    total_km = f"{float(v.get('total_km', 0)):>12,.0f}"
                    failure = str(v.get('failure_count', 0)).rjust(8)
                    mtbf_val = f"{float(v.get('mtbf', 0)):>10,.0f}"
                    avail_val = f"{float(v.get('availability', 0)):>6.1f}%"
                    
                    line = f"{vehicle_no}{total_km}{failure}{mtbf_val}{avail_val}<br/>"
                    text_table += line
                
                text_table += '</font>'
                story.append(Paragraph(text_table, normal_style))
                story.append(Spacer(1, 0.15*cm))
                
                # PyPDF2 Table (stylize hali) de ekle
                table_data = [['Arac No', 'Toplam KM', 'Ariza', 'MTBF (km)', 'Avail %']]
                for v in vehicle_data[:10]:
                    vehicle_no = str(v.get('vehicle', 'N/A'))
                    total_km = f"{float(v.get('total_km', 0)):,.0f}"
                    failure = str(v.get('failure_count', 0))
                    mtbf_val = f"{float(v.get('mtbf', 0)):,.0f}"
                    avail_val = f"{float(v.get('availability', 0)):.1f}%"
                    
                    table_data.append([vehicle_no, total_km,  failure, mtbf_val, avail_val])
                
                
                table = Table(table_data, colWidths=[2.2*cm, 3.2*cm, 2.2*cm, 3.2*cm, 2.8*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.25*cm))
            except Exception as e:
                logger.error(f'Vehicle tablo hatasi: {e}')
                story.append(Paragraph(f'[TABLO HATASI] Arac bazinda tablo olusturulamadi:', normal_style))
                story.append(Spacer(1, 0.1*cm))
        
        # ==== SISTEM BAZINDA TABLO ====
        if system_data:
            section_header = Table([['2. SISTEM BAZINDA ROOT CAUSE ANALIZI']], colWidths=[19*cm])
            section_header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(section_header)
            story.append(Spacer(1, 0.15*cm))
            
            try:
                # Basit text tablosu
                text_table = '<font face="Courier" size="8">'
                text_table += '<b>Sistem                   Ariza    Yuzde    Downtime</b><br/>'
                for s in system_data[:8]:
                    sistem = str(s.get('system', 'N/A')).ljust(24)
                    count = str(s.get('count', 0)).rjust(8)
                    pct = f"{float(s.get('percentage', 0)):>8.1f}%"
                    downtime = f"{float(s.get('downtime_hours', 0)):>9.1f} saat"
                    
                    line = f"{sistem}{count}{pct}{downtime}<br/>"
                    text_table += line
                
                text_table += '</font>'
                story.append(Paragraph(text_table, normal_style))
                story.append(Spacer(1, 0.15*cm))
                
                # Styled table da ekle (görsel uyumun için)
                table_data = [['Sistem', 'Ariza Sayisi', 'Yuzde', 'Downtime (saat)']]
                for s in system_data[:8]:
                    sistem = str(s.get('system', 'N/A'))
                    count = str(s.get('count', 0))
                    pct = f"{float(s.get('percentage', 0)):.1f}%"
                    downtime = f"{float(s.get('downtime_hours', 0)):.1f}"
                    
                    table_data.append([sistem, count, pct, downtime])
                
                
                table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f8f5')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f8f5')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.25*cm))
            except Exception as e:
                logger.error(f'Sistem tablo hatasi: {e}')
                story.append(Paragraph(f'[TABLO HATASI] Sistem bazinda tablo olusturulamadi:', normal_style))
                story.append(Spacer(1, 0.1*cm))
        
        # ==== TEDARIKCI-SISTEM MATRISI ====
        matrix_data = get_supplier_system_matrix(filtered_fracas)
        if matrix_data:
            section_header = Table([['3. TEDARIKCI-SISTEM MATRISI']], colWidths=[19*cm])
            section_header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(section_header)
            story.append(Spacer(1, 0.15*cm))
            
            try:
                # Basit text matrisi
                text_table = '<font face="Courier" size="8">'
                text_table += '<b>Sistem ve Tedarikçi Iliskisi:</b><br/>'
                for system, suppliers in sorted(matrix_data.items())[:6]:
                    supplier_str = ', '.join([f'{supp}({cnt})' for supp, cnt in suppliers.items()])
                    line = f"{str(system)}: {supplier_str}<br/>"
                    text_table += line
                
                text_table += '</font>'
                story.append(Paragraph(text_table, normal_style))
                story.append(Spacer(1, 0.15*cm))
                
                # Styled table da ekle
                all_suppliers = set()
                for sys_suppliers in matrix_data.values():
                    all_suppliers.update(sys_suppliers.keys())
                all_suppliers = sorted(list(all_suppliers))[:4]
                
                table_data = [['Sistem'] + all_suppliers]
                for system, suppliers in sorted(matrix_data.items())[:6]:
                    row = [str(system)]
                    for supplier in all_suppliers:
                        row.append(str(suppliers.get(supplier, 0)))
                    table_data.append(row)
                
                col_width = 15.5*cm / (len(all_suppliers) + 1) if (len(all_suppliers) + 1) > 0 else 3.875*cm
                table = Table(table_data, colWidths=[col_width] * (len(all_suppliers) + 1))
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff8e1')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
            except Exception as e:
                logger.error(f'Matrix tablo hatasi: {e}')
                story.append(Paragraph(f'[TABLO HATASI] Tedarikci-Sistem matrisi olusturulamadi:', normal_style))
        
        # Sayfa sonu
        if idx < len(periods) - 1:
            story.append(PageBreak())
    
    doc.build(story)
    return buffer


def create_management_pdf_multi(all_projects, periods, loaded_data):
    """Tüm projeler için kapsamlı PDF rapor oluştur - KPI Dashboard stili"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.7*cm, leftMargin=0.7*cm,
                           rightMargin=0.7*cm, bottomMargin=0.7*cm)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Ayni stil set'leri
    info_style = ParagraphStyle(
        'InfoText', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#555'), spaceAfter=6
    )
    
    kpi_heading_style = ParagraphStyle(
        'KPIHeading', parent=styles['Heading2'], fontSize=12,
        textColor=colors.white, spaceAfter=6, fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333')
    )
    
    # Tüm 8 proje için işle
    for proj_idx, project in enumerate(all_projects):
        if project not in loaded_data:
            continue
        
        project_key = project.lower()
        project_display = PROJECTS.get(project_key, project)
        fracas_df = loaded_data[project]
        
        # Periyodlar döngüsü
        for period_idx, period in enumerate(periods):
            if period not in PERIODS:
                continue
            
            period_name, _ = PERIODS[period]
            filtered_fracas = filter_by_period(fracas_df, period)
            
            # Başlık
            header_table = Table([['YONETIM RAPORU - ' + project_display.upper()]], 
                                colWidths=[19*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 16),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.2*cm))
            
            # Bilgi satırı
            if period == 'total':
                date_range = 'Tum Zamanlar'
            else:
                end_date = datetime.now()
                days = PERIODS[period][1]
                start_date = end_date - timedelta(days=days)
                date_range = f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'
            
            info_line = f'Periyot: <b>{period_name}</b> ({date_range}) | Rapor: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
            story.append(Paragraph(info_line, info_style))
            story.append(Spacer(1, 0.3*cm))
            
            # Veri kontrol
            if filtered_fracas is None or filtered_fracas.empty:
                story.append(Paragraph('[!] Bu periyot icin veri bulunamadi', normal_style))
                story.append(Spacer(1, 0.5*cm))
            else:
                # KPI Metrics
                vehicle_data = get_vehicle_analysis(filtered_fracas)
                system_data = get_system_analysis(filtered_fracas)
                
                if vehicle_data or system_data:
                    kpi_metrics = []
                    
                    if vehicle_data:
                        total_vehicles = len(vehicle_data)
                        avg_availability = sum(v['availability'] for v in vehicle_data) / len(vehicle_data)
                        kpi_metrics.append(f'<b>ARACLAR</b><br/>{total_vehicles} Arac<br/>Avail: {avg_availability:.0f}%')
                    else:
                        kpi_metrics.append('<b>ARACLAR</b><br/>0 Arac')
                    
                    if system_data:
                        total_systems = len(system_data)
                        total_failures = sum(s['count'] for s in system_data)
                        kpi_metrics.append(f'<b>SISTEMLER</b><br/>{total_systems} Sistem<br/>{total_failures} Ariza')
                    else:
                        kpi_metrics.append('<b>SISTEMLER</b><br/>0 Sistem')
                    
                    if system_data:
                        avg_downtime = sum(s['downtime_hours'] for s in system_data) / len(system_data)
                        kpi_metrics.append(f'<b>ORTALAMA</b><br/>Downtime<br/>{avg_downtime:.1f} saat')
                    else:
                        kpi_metrics.append('<b>ORTALAMA</b><br/>Downtime<br/>0 saat')
                    
                    if vehicle_data:
                        avg_mtbf = sum(v['mtbf'] for v in vehicle_data) / len(vehicle_data)
                        kpi_metrics.append(f'<b>MTBF</b><br/>{avg_mtbf:,.0f} km<br/>Ort Deger')
                    else:
                        kpi_metrics.append('<b>MTBF</b><br/>N/A')
                    
                    colors_list = [colors.HexColor('#667eea'), colors.HexColor('#764ba2'),
                                  colors.HexColor('#27ae60'), colors.HexColor('#f39c12')]
                    
                    kpi_rows = [[Paragraph(m, kpi_heading_style) for m in kpi_metrics]]
                    kpi_table = Table(kpi_rows, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
                    kpi_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, 0), colors_list[0]),
                        ('BACKGROUND', (1, 0), (1, 0), colors_list[1]),
                        ('BACKGROUND', (2, 0), (2, 0), colors_list[2]),
                        ('BACKGROUND', (3, 0), (3, 0), colors_list[3]),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('HEIGHT', (0, 0), (-1, -1), 1.2*cm),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ]))
                    story.append(kpi_table)
                    story.append(Spacer(1, 0.3*cm))
                
                # Arac tablosu
                if vehicle_data:
                    section_header = Table([['1. ARAC BAZINDA ANALIZ']], colWidths=[19*cm])
                    section_header.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#764ba2')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(section_header)
                    story.append(Spacer(1, 0.15*cm))
                    
                    table_data = [['Arac No', 'Toplam KM', 'Ariza', 'MTBF (km)', 'Avail %']]
                    for v in vehicle_data[:8]:
                        table_data.append([
                            str(v['vehicle']), f"{v['total_km']:,.0f}",
                            str(v['failure_count']), f"{v['mtbf']:,.0f}",
                            f"{v['availability']:.1f}%"
                        ])
                    
                    table = Table(table_data, colWidths=[2.2*cm, 3.2*cm, 2.2*cm, 3.2*cm, 2.8*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.2*cm))
                
                # Sistem tablosu
                if system_data:
                    section_header = Table([['2. SISTEM BAZINDA ROOT CAUSE ANALIZI']], colWidths=[19*cm])
                    section_header.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#27ae60')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(section_header)
                    story.append(Spacer(1, 0.15*cm))
                    
                    table_data = [['Sistem', 'Ariza Sayisi', 'Yuzde', 'Downtime (saat)']]
                    for s in system_data[:6]:
                        table_data.append([
                            str(s['system']), str(s['count']),
                            f"{s['percentage']:.1f}%", f"{s['downtime_hours']:.1f}"
                        ])
                    
                    table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3.5*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f8f5')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f8f5')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.2*cm))
                
                # Matrix tablosu
                matrix_data = get_supplier_system_matrix(filtered_fracas)
                if matrix_data:
                    section_header = Table([['3. TEDARIKCI-SISTEM MATRISI']], colWidths=[19*cm])
                    section_header.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f39c12')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(section_header)
                    story.append(Spacer(1, 0.15*cm))
                    
                    all_suppliers = set()
                    for sys_suppliers in matrix_data.values():
                        all_suppliers.update(sys_suppliers.keys())
                    all_suppliers = sorted(list(all_suppliers))[:3]
                    
                    table_data = [['Sistem'] + all_suppliers]
                    for system, suppliers in sorted(matrix_data.items())[:4]:
                        row = [system]
                        for supplier in all_suppliers:
                            row.append(str(suppliers.get(supplier, 0)))
                        table_data.append(row)
                    
                    col_width = 15.5*cm / (len(all_suppliers) + 1)
                    table = Table(table_data, colWidths=[col_width] * (len(all_suppliers) + 1))
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff8e1')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(table)
            
            # Sayfa sonu
            is_last_project = (proj_idx == len(all_projects) - 1)
            is_last_period = (period_idx == len(periods) - 1)
            if not (is_last_project and is_last_period):
                story.append(PageBreak())
                table_data = [['Arac No', 'Toplam KM', 'Ariza Sayisi', 'MTBF (km)', 'Availability %']]
                for v in vehicle_data[:10]:
                    table_data.append([v['vehicle'], f"{v['total_km']:,.0f}", str(v['failure_count']),
                                     f"{v['mtbf']:,.0f}", f"{v['availability']:.1f}%"])
                
                table = Table(table_data, colWidths=[1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
            
            # 2. SISTEM BAZINDA
            if system_data:
                story.append(Paragraph('2. SISTEM BAZINDA ROOT CAUSE ANALIZI', heading_style))
                table_data = [['Sistem', 'Ariza Sayisi', 'Yuzde', 'Downtime (saat)']]
                for s in system_data[:10]:
                    table_data.append([s['system'], str(s['count']), f"{s['percentage']:.1f}%", f"{s['downtime_hours']:.1f}"])
                
                table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
            
            # 3. TEDARIKCI-SISTEM MATRISI
            matrix_data = get_supplier_system_matrix(filtered_fracas)
            if matrix_data:
                story.append(Paragraph('3. TEDARIKCI-SISTEM MATRISI', heading_style))
                
                all_suppliers = set()
                for systems in matrix_data.values():
                    all_suppliers.update(systems.keys())
                all_suppliers = sorted(list(all_suppliers))[:5]
                
                table_data = [['Sistem'] + all_suppliers]
                for system, suppliers in sorted(matrix_data.items())[:8]:
                    row = [system]
                    for supplier in all_suppliers:
                        row.append(str(suppliers.get(supplier, 0)))
                    table_data.append(row)
                
                col_width = 9*cm / (len(all_suppliers) + 1)
                table = Table(table_data, colWidths=[2.5*cm] + [col_width]*len(all_suppliers))
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                story.append(table)
            
            if idx < len(periods) - 1:
                story.append(PageBreak())
    
    doc.build(story)
    return buffer


def create_management_pdf_multi(all_projects, periods, loaded_data):
    """Tüm projeler için kapsamlı PDF rapor oluştur"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*cm, bottomMargin=0.5*cm)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=20,
        textColor=colors.HexColor('#667eea'), spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#764ba2'), spaceAfter=10, fontName='Helvetica-Bold'
    )
    
    # Tüm 8 proje için işle (veri olsun olmasın)
    for proj_idx, project in enumerate(all_projects):
        # Her proje için periyodlar
        for period_idx, period in enumerate(periods):
            if period not in PERIODS:
                continue
            
            # Proje başlığı ve periyot bilgisi
            story.append(Paragraph(f'YONETIM RAPORU - {PROJECTS[project].upper()}', title_style))
            
            period_name, _ = PERIODS[period]
            if period == 'total':
                date_range = 'Tum Zamanlar'
            else:
                end_date = datetime.now()
                days = PERIODS[period][1]
                start_date = end_date - timedelta(days=days)
                date_range = f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'
            
            info_text = f'<b>Periyot:</b> {period_name} ({date_range}) | <b>Rapor:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}'
            story.append(Paragraph(info_text, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
            
            # Veri kontrol
            if project not in loaded_data:
                story.append(Paragraph('[!] Bu proje icin veri bulunamadi.', styles['Normal']))
                story.append(Spacer(1, 0.5*cm))
            else:
                fracas_df = loaded_data[project]
                filtered_fracas = filter_by_period(fracas_df, period)
                
                if filtered_fracas is None or filtered_fracas.empty:
                    story.append(Paragraph('[!] Bu periyot icin veri bulunamadi.', styles['Normal']))
                    story.append(Spacer(1, 0.5*cm))
                else:
                    # 1. ARAÇ BAZINDA
                    vehicle_data = get_vehicle_analysis(filtered_fracas)
                    if vehicle_data:
                        story.append(Paragraph('1. ARAÇ BAZINDA ANALİZ', heading_style))
                        table_data = [['Araç No', 'Toplam KM', 'Arıza Sayısı', 'MTBF (km)', 'Availability %']]
                        for v in vehicle_data[:10]:
                            table_data.append([v['vehicle'], f"{v['total_km']:,.0f}", str(v['failure_count']),
                                             f"{v['mtbf']:,.0f}", f"{v['availability']:.1f}%"])
                        
                        table = Table(table_data, colWidths=[1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 0.3*cm))
                    else:
                        story.append(Paragraph('⚠ Araç verisi bulunamadı.', styles['Normal']))
                        story.append(Spacer(1, 0.3*cm))
                    
                    # 2. SİSTEM BAZINDA
                    system_data = get_system_analysis(filtered_fracas)
                    if system_data:
                        story.append(Paragraph('2. SİSTEM BAZINDA ROOT CAUSE ANALİZİ', heading_style))
                        table_data = [['Sistem', 'Arıza Sayısı', 'Yüzde', 'Downtime (saat)']]
                        for s in system_data[:10]:
                            table_data.append([s['system'], str(s['count']), f"{s['percentage']:.1f}%",
                                             f"{s['downtime_hours']:.1f}"])
                        
                        table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2.5*cm])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 0.3*cm))
                    
                    # 3. TEDARİKÇİ-SİSTEM MATRİSİ
                    matrix_data = get_supplier_system_matrix(filtered_fracas)
                    if matrix_data:
                        story.append(Paragraph('3. TEDARİKÇİ-SİSTEM MATRİSİ', heading_style))
                        
                        all_suppliers = set()
                        for systems in matrix_data.values():
                            all_suppliers.update(systems.keys())
                        all_suppliers = sorted(list(all_suppliers))[:5]
                        
                        table_data = [['Sistem'] + all_suppliers]
                        for system, suppliers in sorted(matrix_data.items())[:8]:
                            row = [system]
                            for supplier in all_suppliers:
                                row.append(str(suppliers.get(supplier, 0)))
                            table_data.append(row)
                        
                        table = Table(table_data, colWidths=[2.5*cm] + [1.5*cm] * len(all_suppliers))
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ]))
                        story.append(table)
            
            # Sayfa sonu - son proje ve son periyot değilse
            is_last_project = (proj_idx == len(all_projects) - 1)
            is_last_period = (period_idx == len(periods) - 1)
            if not (is_last_project and is_last_period):
                story.append(PageBreak())
    
    doc.build(story)
    return buffer
