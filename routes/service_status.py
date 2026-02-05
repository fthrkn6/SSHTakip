"""
Servis Durumu ve Availability Route'ları
Araç servis durumunu yönet, raporla ve analiz et
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from models import db, ServiceLog, AvailabilityMetrics, RootCauseAnalysis, Failure, Equipment
from datetime import datetime, timedelta, date
from utils_availability import (
    log_service_status_change
)
from utils_service_status import AvailabilityAnalyzer, ExcelReportGenerator as EnhancedExcelGenerator
import os
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('service_status', __name__, url_prefix='/servis')


@bp.route('/durumu', methods=['GET'])
@login_required
def service_status_page():
    """Servis durumu dashboard sayfası"""
    try:
        # Tüm araçları getir
        equipment_list = Equipment.query.all()
        tram_ids = [eq.equipment_code for eq in equipment_list]
        
        # Son 30 gün verilerini hazırla
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        # Seçili dönem (query parameter'dan al)
        period = request.args.get('period', 'monthly')
        
        # Son availability raporlarını getir
        availability_data = []
        for tram_id in tram_ids:
            latest_metric = AvailabilityMetrics.query.filter_by(tram_id=tram_id).order_by(
                AvailabilityMetrics.created_at.desc()
            ).first()
            
            if latest_metric:
                availability_data.append({
                    'tram_id': tram_id,
                    'availability': latest_metric.availability_percentage,
                    'downtime': latest_metric.downtime_hours,
                    'operational': latest_metric.operational_hours
                })
        
        # Son servis durumu loglarını getir
        recent_logs = ServiceLog.query.order_by(ServiceLog.log_date.desc()).limit(50).all()
        
        return render_template('servis_durumu_enhanced.html', 
                             tram_ids=tram_ids,
                             availability_data=availability_data,
                             recent_logs=recent_logs,
                             period=period,
                             current_date=datetime.now())
    
    except Exception as e:
        logger.error(f"Error loading service status page: {str(e)}")
        flash('Servis durumu sayfası yüklenirken hata oluştu', 'danger')
        return redirect(url_for('dashboard.index'))


@bp.route('/durumu/tablo', methods=['GET'])
@login_required
def service_status_table():
    """Servis durumu tablosunu getir"""
    try:
        tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
        
        table_data = []
        for tram_id in tram_ids:
            equipment = Equipment.query.filter_by(equipment_code=tram_id).first()
            
            # Son log'u getir
            latest_log = ServiceLog.query.filter_by(tram_id=tram_id).order_by(
                ServiceLog.log_date.desc()
            ).first()
            
            # Availability hesapla
            start_date = date.today() - timedelta(days=30)
            daily_availability = AvailabilityCalculator.calculate_daily_availability(tram_id)
            
            table_data.append({
                'tram_id': tram_id,
                'name': equipment.name if equipment else '-',
                'status': latest_log.new_status if latest_log else 'Bilinmiyor',
                'sistem': latest_log.sistem if latest_log else '-',
                'alt_sistem': latest_log.alt_sistem if latest_log else '-',
                'last_status_change': latest_log.log_date.strftime('%d.%m.%Y %H:%M') if latest_log else '-',
                'availability': daily_availability.availability_percentage if daily_availability else 0,
                'downtime': daily_availability.downtime_hours if daily_availability else 0
            })
        
        return jsonify(table_data)
    
    except Exception as e:
        logger.error(f"Error getting service status table: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/durumu/log', methods=['POST'])
@login_required
def log_service_status():
    """Servis durumu değişikliğini log'la"""
    try:
        data = request.get_json()
        
        tram_id = data.get('tram_id')
        new_status = data.get('status')
        sistem = data.get('sistem')
        alt_sistem = data.get('alt_sistem')
        reason = data.get('reason')
        duration_hours = float(data.get('duration_hours', 0))
        
        if not tram_id or not new_status:
            return jsonify({'error': 'Tram ID ve durum gerekli'}), 400
        
        # Log'u kaydet
        log_entry = log_service_status_change(
            tram_id=tram_id,
            new_status=new_status,
            sistem=sistem,
            alt_sistem=alt_sistem,
            reason=reason,
            duration_hours=duration_hours,
            user_id=current_user.id
        )
        
        # Günlük availability'i güncelle
        AvailabilityCalculator.calculate_daily_availability(tram_id)
        
        logger.info(f"Service status logged for {tram_id}: {new_status}")
        
        return jsonify({
            'success': True,
            'message': 'Servis durumu başarıyla kaydedildi',
            'log_id': log_entry.id
        })
    
    except Exception as e:
        logger.error(f"Error logging service status: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/gunluk', methods=['GET'])
@login_required
def daily_report():
    """Günlük availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        target_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        if tram_id:
            metric = AvailabilityCalculator.calculate_daily_availability(tram_id, target_date)
            data = {
                'tram_id': tram_id,
                'date': target_date.strftime('%d.%m.%Y'),
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/haftalik', methods=['GET'])
@login_required
def weekly_report():
    """Haftalık availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        start_date = request.args.get('start_date')
        
        if not start_date:
            start_date = date.today() - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=6)
        
        if tram_id:
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'weekly'
            )
            data = {
                'tram_id': tram_id,
                'period': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/aylik', methods=['GET'])
@login_required
def monthly_report():
    """Aylık availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        start_date = request.args.get('start_date')
        
        if not start_date:
            today = date.today()
            start_date = date(today.year, today.month, 1)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Ayın son günü
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        
        if tram_id:
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'monthly'
            )
            data = {
                'tram_id': tram_id,
                'period': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/3aylik', methods=['GET'])
@login_required
def quarterly_report():
    """3 aylık availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        
        if tram_id:
            today = date.today()
            start_date = today - timedelta(days=90)
            end_date = today
            
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'quarterly'
            )
            data = {
                'tram_id': tram_id,
                'period': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating quarterly report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/6aylik', methods=['GET'])
@login_required
def biannual_report():
    """6 aylık availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        
        if tram_id:
            today = date.today()
            start_date = today - timedelta(days=180)
            end_date = today
            
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'biannual'
            )
            data = {
                'tram_id': tram_id,
                'period': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating biannual report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/yillik', methods=['GET'])
@login_required
def yearly_report():
    """Yıllık availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        year = request.args.get('year', date.today().year)
        
        if tram_id:
            start_date = date(int(year), 1, 1)
            end_date = date(int(year), 12, 31)
            
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'yearly'
            )
            data = {
                'tram_id': tram_id,
                'period': f"01.01.{year} - 31.12.{year}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating yearly report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/rapor/total', methods=['GET'])
@login_required
def total_report():
    """Toplam availability raporu"""
    try:
        tram_id = request.args.get('tram_id')
        
        if tram_id:
            # İlk log'dan bugüne kadar
            first_log = ServiceLog.query.filter_by(tram_id=tram_id).order_by(
                ServiceLog.log_date.asc()
            ).first()
            
            if first_log:
                start_date = first_log.log_date.date()
            else:
                start_date = date.today() - timedelta(days=365)
            
            end_date = date.today()
            
            metric = AvailabilityCalculator.calculate_period_availability(
                tram_id, start_date, end_date, 'total'
            )
            data = {
                'tram_id': tram_id,
                'period': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'availability': metric.availability_percentage,
                'operational_hours': metric.operational_hours,
                'downtime_hours': metric.downtime_hours,
                'failure_count': metric.failure_count
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Tram ID gerekli'}), 400
    
    except Exception as e:
        logger.error(f"Error generating total report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/excel/availability', methods=['GET', 'POST'])
@login_required
def export_availability_excel():
    """Availability raporunu Excel'e aktar"""
    try:
        tram_ids = [eq.id_tram for eq in Equipment.query.all()]
        
        start_date_str = request.args.get('start_date', str(date.today() - timedelta(days=30)))
        end_date_str = request.args.get('end_date', str(date.today()))
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Klasör oluştur
        output_dir = 'availability_analiz'
        os.makedirs(output_dir, exist_ok=True)
        
        # Dosya adı
        filename = f"Availability_Raporu_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Excel oluştur
        ExcelReportGenerator.create_availability_report_excel(tram_ids, start_date, end_date, filepath)
        
        logger.info(f"Availability report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        logger.error(f"Error exporting availability report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/excel/rootcause', methods=['GET', 'POST'])
@login_required
def export_rootcause_excel():
    """Root Cause Analysis raporunu Excel'e aktar"""
    try:
        tram_ids = [eq.id_tram for eq in Equipment.query.all()]
        
        # Klasör oluştur
        output_dir = 'availability_analiz'
        os.makedirs(output_dir, exist_ok=True)
        
        # Dosya adı
        filename = f"Root_Cause_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Excel oluştur
        ExcelReportGenerator.create_root_cause_analysis_excel(tram_ids, filepath)
        
        logger.info(f"Root cause analysis report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        logger.error(f"Error exporting root cause analysis report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/root-cause', methods=['GET', 'POST'])
@login_required
def root_cause_analysis():
    """Root cause analysis yönetimi"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            analysis = RootCauseAnalysis(
                tram_id=data.get('tram_id'),
                sistem=data.get('sistem'),
                alt_sistem=data.get('alt_sistem'),
                failure_description=data.get('failure_description'),
                root_cause=data.get('root_cause'),
                contributing_factors=json.dumps(data.get('contributing_factors', [])),
                preventive_actions=json.dumps(data.get('preventive_actions', [])),
                corrective_actions=json.dumps(data.get('corrective_actions', [])),
                analyzed_by=current_user.id,
                severity_level=data.get('severity_level', 'medium'),
                frequency=int(data.get('frequency', 1))
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            logger.info(f"Root cause analysis created for {data.get('tram_id')}")
            
            return jsonify({
                'success': True,
                'message': 'Root cause analysis başarıyla oluşturuldu',
                'id': analysis.id
            })
        
        # GET - Raporları listele
        tram_ids = [eq.id_tram for eq in Equipment.query.all()]
        analyses = RootCauseAnalysis.query.all()
        
        return render_template('root_cause_analysis.html', 
                             tram_ids=tram_ids,
                             analyses=analyses)
    
    except Exception as e:
        logger.error(f"Error in root cause analysis: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/excel/comprehensive-report', methods=['GET', 'POST'])
@login_required
def export_comprehensive_report():
    """Kapsamlı availability ve root cause raporu"""
    try:
        tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
        
        # Klasör oluştur
        output_dir = 'logs/rapor_cikti'
        os.makedirs(output_dir, exist_ok=True)
        
        # Dosya adı
        filename = f"Kapsamli_Servis_Durumu_Raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Excel oluştur
        EnhancedExcelGenerator.create_comprehensive_availability_report(tram_ids, filepath)
        
        logger.info(f"Comprehensive report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        logger.error(f"Error exporting comprehensive report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/excel/root-cause-report', methods=['GET', 'POST'])
@login_required
def export_root_cause_report():
    """Root cause analysis raporu"""
    try:
        tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
        
        # Klasör oluştur
        output_dir = 'logs/rapor_cikti'
        os.makedirs(output_dir, exist_ok=True)
        
        # Dosya adı
        filename = f"Root_Cause_Analiz_Raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Excel oluştur
        EnhancedExcelGenerator.create_root_cause_analysis_report(tram_ids, filepath)
        
        logger.info(f"Root cause report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        logger.error(f"Error exporting root cause report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/excel/daily-report/<tram_id>', methods=['GET'])
@login_required
def export_daily_report(tram_id):
    """Günlük servis durumu raporu"""
    try:
        # Klasör oluştur
        output_dir = 'logs/rapor_cikti'
        os.makedirs(output_dir, exist_ok=True)
        
        # Dosya adı
        filename = f"Gunluk_Durum_{tram_id}_{date.today().strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Excel oluştur
        EnhancedExcelGenerator.create_detailed_daily_report(tram_id, filepath)
        
        logger.info(f"Daily report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        logger.error(f"Error exporting daily report: {str(e)}")
        return jsonify({'error': str(e)}), 400


@bp.route('/api/root-cause-summary/<tram_id>', methods=['GET'])
@login_required
def get_root_cause_summary(tram_id):
    """Root cause analizi özeti"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        summary = AvailabilityAnalyzer.get_root_cause_summary(tram_id, start_date, end_date)
        
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error getting root cause summary: {str(e)}")
        return jsonify({'error': str(e)}), 400


# TEST ENDPOINT - Debug için
@bp.route('/test/export/<report_type>', methods=['GET'])
def test_export(report_type):
    """Test export endpoint - debug amaçlı (login gerektirmez)"""
    try:
        output_dir = 'logs/rapor_cikti'
        os.makedirs(output_dir, exist_ok=True)
        
        if report_type == 'comprehensive':
            tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
            filename = f"TEST_Kapsamli_Servis_Durumu_Raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(output_dir, filename)
            EnhancedExcelGenerator.create_comprehensive_availability_report(tram_ids, filepath)
            
        elif report_type == 'rootcause':
            tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
            filename = f"TEST_Root_Cause_Analiz_Raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(output_dir, filename)
            EnhancedExcelGenerator.create_root_cause_analysis_report(tram_ids, filepath)
            
        elif report_type == 'daily':
            tram_id = request.args.get('tram_id', Equipment.query.first().equipment_code if Equipment.query.first() else 'TEST')
            filename = f"TEST_Gunluk_Durum_{tram_id}_{date.today().strftime('%Y%m%d')}.xlsx"
            filepath = os.path.join(output_dir, filename)
            EnhancedExcelGenerator.create_detailed_daily_report(tram_id, filepath)
        else:
            return jsonify({'error': 'Bilinmeyen rapor türü'}), 400
        
        logger.info(f"Test report exported to {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        logger.error(f"Error in test export: {str(e)}")
        return jsonify({'error': f'Hata: {str(e)}'}), 400
