"""
Raporlama Routes - Dashboard, Bakım, KM, Senaryolar, Logs
"""

from flask import Blueprint, render_template, jsonify, request, send_file, session
from flask_login import login_required
from datetime import datetime
import json
from pathlib import Path

from utils_reporting import (
    ReportSystem, DashboardReport, MaintenanceReport, KMReport,
    ScenarioAnalysis, init_reporting_system
)
from models import Equipment, db

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


# ==================== DASHBOARD RAPOR ====================
@reports_bp.route('/dashboard-rapor', methods=['POST'])
@login_required
def dashboard_rapor():
    """Dashboard snapshot raporunu indir"""
    try:
        project = session.get('current_project', 'belgrad')
        
        # 1531-1555 tramvaylarını getir
        tramvaylar = Equipment.query.filter(
            Equipment.equipment_code >= '1531',
            Equipment.equipment_code <= '1555'
        ).all()
        
        if not tramvaylar:
            tramvaylar = Equipment.query.all()
        
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
        
        # 1531-1555 tramvaylarını getir
        tramvaylar = Equipment.query.filter(
            Equipment.equipment_code >= '1531',
            Equipment.equipment_code <= '1555'
        ).all()
        
        if not tramvaylar:
            tramvaylar = Equipment.query.all()
        
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
        
        # Tüm tramvayları getir
        tramvaylar = Equipment.query.filter(
            Equipment.equipment_code >= '1531',
            Equipment.equipment_code <= '1555'
        ).all()
        
        if not tramvaylar:
            tramvaylar = Equipment.query.all()
        
        # Veriyi hazırla
        tram_data = []
        for tram in tramvaylar:
            tram_data.append({
                'equipment_code': tram.equipment_code,
                'current_km': getattr(tram, 'current_km', 0),
                'total_km': getattr(tram, 'total_km', 0),
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
