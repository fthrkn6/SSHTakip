"""
Tramvay Kilometre Takip Blueprint
KM güncelleme, toplu güncelleme ve Excel senkronizasyonu
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models import db, Equipment
from utils.utils_km_logger import log_km_change
from utils.utils_km_excel_logger import KMExcelLogger
from utils.utils_km_takip_excel import log_km_takip, read_latest_km_from_takip
from utils.utils_project_excel_store import upsert_km
import logging

logger = logging.getLogger('ssh_takip')

bp = Blueprint('tramvay_km', __name__)


@bp.route('/tramvay-km')
@login_required
def index():
    """Tram kilometer tracking - Single source of truth: Equipment DB"""
    project_code = session.get('current_project', 'belgrad').lower()

    try:
        from utils.utils_project_excel_store import get_tramvay_list_with_km
        equipments = get_tramvay_list_with_km(project_code)
    except Exception as e:
        logger.error(f"tramvay_km error: {e}")
        equipments = Equipment.query.filter_by(project_code=project_code).all()

    stats = {
        'toplam_tramvay': len(equipments),
        'toplam_km': sum(getattr(e, 'current_km', 0) or 0 for e in equipments),
        'ortalama_km': sum(getattr(e, 'current_km', 0) or 0 for e in equipments) // len(equipments) if equipments else 0,
        'max_km': max([getattr(e, 'current_km', 0) or 0 for e in equipments]) if equipments else 0,
    }

    return render_template('tramvay_km.html',
                           stats=stats,
                           equipments=equipments,
                           project_name=session.get('project_name', 'Belgrad'))


@bp.route('/tramvay-km/guncelle', methods=['POST'])
@login_required
def guncelle():
    """Update tram km - Single source: Equipment table"""
    logger.info("tramvay_km_guncelle called")
    try:
        tram_id = request.form.get('tram_id')
        current_km = request.form.get('current_km', 0)
        notes = request.form.get('notes', '')
        project_code = session.get('current_project', 'belgrad').lower()

        equipment = Equipment.query.filter_by(equipment_code=str(tram_id), project_code=project_code).first()
        if not equipment and str(tram_id).isdigit():
            equipment = Equipment.query.filter_by(id=int(tram_id), project_code=project_code).first()

        tram_code = str(equipment.equipment_code) if equipment else str(tram_id)
        old_km = equipment.current_km if equipment else 0

        if not equipment:
            equipment = Equipment(
                equipment_code=tram_code,
                name=f'Tramvay {tram_code}',
                equipment_type='Tramvay',
                current_km=0,
                monthly_km=0,
                notes='',
                project_code=project_code
            )
            db.session.add(equipment)

        new_km = int(current_km) if current_km else 0
        equipment.current_km = new_km
        equipment.notes = notes
        db.session.commit()

        log_km_change(
            tram_id=tram_code,
            old_km=old_km,
            new_km=new_km,
            user=current_user.username if current_user else 'system',
            project_code=project_code,
            notes=notes
        )

        try:
            km_excel_logger = KMExcelLogger(project_code)
            km_excel_logger.log_km_to_excel(
                tram_id=tram_code,
                previous_km=old_km,
                new_km=new_km,
                reason=notes or 'Gün sonu sayımı',
                user=current_user.username if current_user else 'Sistem',
                system_type='Manuel'
            )
        except Exception as excel_err:
            logger.warning(f'KM Excel logging failed for {tram_code}: {excel_err}')

        try:
            log_km_takip(project_code, tram_code, new_km)
        except Exception as takip_err:
            logger.warning(f'KM takip Excel hatasi {tram_code}: {takip_err}')

        flash(f'✅ {tram_code} KM bilgileri kaydedildi', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ Kaydedilme hatası: {str(e)}', 'danger')

    return redirect(url_for('tramvay_km.index'))


@bp.route('/tramvay-km/toplu-guncelle', methods=['POST'])
@login_required
def toplu_guncelle():
    """Bulk KM update - clean single path via Equipment table"""
    try:
        updates = request.get_json() or {}
        count = 0
        errors = []
        project_code = session.get('current_project', 'belgrad').lower()

        for tram_id, data in updates.items():
            try:
                tram_code = str(tram_id)

                equipment = Equipment.query.filter_by(
                    equipment_code=tram_code,
                    project_code=project_code
                ).first()

                if not equipment and tram_code.isdigit():
                    equipment = Equipment.query.filter_by(
                        id=int(tram_code),
                        project_code=project_code
                    ).first()
                    if equipment:
                        tram_code = str(equipment.equipment_code)

                if not equipment:
                    equipment = Equipment(
                        equipment_code=tram_code,
                        name=f'Tramvay {tram_code}',
                        equipment_type='Tramvay',
                        current_km=0,
                        monthly_km=0,
                        notes='',
                        project_code=project_code
                    )
                    db.session.add(equipment)

                if 'current_km' in data and data['current_km']:
                    try:
                        new_km = int(float(data['current_km']))
                        old_km = equipment.current_km if equipment else 0
                        equipment.current_km = new_km

                        upsert_km(
                            project_code=project_code,
                            tram_id=tram_code,
                            current_km=new_km,
                            notes=str(data.get('notes', '') or ''),
                            updated_by=current_user.username if current_user else 'admin'
                        )

                        try:
                            km_excel_logger = KMExcelLogger(project_code)
                            km_excel_logger.log_km_to_excel(
                                tram_id=tram_code,
                                previous_km=old_km,
                                new_km=new_km,
                                reason=data.get('notes', '') or 'Toplu güncelleme',
                                user=current_user.username if current_user else 'Sistem',
                                system_type='Manuel'
                            )
                        except Exception as excel_err:
                            logger.warning(f'KM Excel logging failed for {tram_code}: {excel_err}')

                        try:
                            log_km_takip(project_code, tram_code, new_km)
                        except Exception as takip_err:
                            logger.warning(f'KM takip Excel hatasi {tram_code}: {takip_err}')

                    except Exception as km_err:
                        errors.append(f"{tram_id}: Geçersiz KM değeri ({km_err})")
                        continue

                if 'notes' in data:
                    equipment.notes = str(data['notes']).strip()

                count += 1

            except Exception as e:
                errors.append(f"Tramvay {tram_id}: {str(e)}")

        db.session.commit()

        message = f'✅ {count} araç başarıyla kaydedildi'
        if errors:
            message += f' ({len(errors)} hata)'

        return jsonify({'success': True, 'message': message}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Toplu guncelle error: {e}")
        return jsonify({'success': False, 'message': f'❌ Hata: {str(e)}'}), 500


@bp.route('/tramvay-km/excel-sync', methods=['POST'])
@login_required
def excel_sync():
    """KM Takip Excel'inden DB'ye senkronizasyon"""
    try:
        project_code = session.get('current_project', 'belgrad').lower()
        excel_data = read_latest_km_from_takip(project_code)

        if not excel_data:
            flash('Excel dosyası bulunamadı veya boş.', 'warning')
            return redirect(url_for('tramvay_km.index'))

        updated = 0
        skipped = 0
        for tram_id, info in excel_data.items():
            excel_km = info['km']
            equipment = Equipment.query.filter_by(
                equipment_code=str(tram_id),
                project_code=project_code
            ).first()

            if not equipment:
                equipment = Equipment(
                    equipment_code=str(tram_id),
                    name=f'Tramvay {tram_id}',
                    equipment_type='Tramvay',
                    current_km=0,
                    monthly_km=0,
                    notes='',
                    project_code=project_code
                )
                db.session.add(equipment)

            old_km = equipment.current_km or 0
            if excel_km != old_km:
                equipment.current_km = excel_km
                log_km_change(
                    tram_id=str(tram_id),
                    old_km=old_km,
                    new_km=excel_km,
                    user=current_user.username if current_user else 'system',
                    project_code=project_code,
                    notes='Excel senkronizasyonu'
                )
                updated += 1
            else:
                skipped += 1

        db.session.commit()
        flash(f'✅ Excel senkronizasyonu tamamlandı: {updated} güncellendi, {skipped} değişmedi', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f'Excel sync error: {e}')
        flash(f'❌ Senkronizasyon hatası: {str(e)}', 'danger')

    return redirect(url_for('tramvay_km.index'))
