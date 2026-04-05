import os
from datetime import datetime, date
from openpyxl import Workbook, load_workbook


def _project_dir(project_code: str):
    return os.path.join(os.path.dirname(__file__), '..', 'data', project_code)


def _ensure_workbook(path: str, headers):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        wb.save(path)
        return wb
    return load_workbook(path)


def get_km_excel_path(project_code: str):
    return os.path.join(_project_dir(project_code), 'km_data.xlsx')


def get_service_excel_path(project_code: str):
    return os.path.join(_project_dir(project_code), 'service_status.xlsx')


def read_all_km(project_code: str):
    path = get_km_excel_path(project_code)
    wb = _ensure_workbook(path, ['tram_id', 'current_km', 'notes', 'updated_at', 'updated_by'])
    ws = wb.active

    results = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        tram_id = str(row[0]).strip() if row and row[0] is not None else None
        if not tram_id:
            continue
        try:
            current_km = int(float(row[1])) if row[1] is not None and str(row[1]).strip() != '' else 0
        except Exception:
            current_km = 0
        results[tram_id] = {
            'current_km': current_km,
            'notes': str(row[2] or ''),
            'updated_at': str(row[3] or ''),
            'updated_by': str(row[4] or '')
        }

    return results


def upsert_km(project_code: str, tram_id: str, current_km: int, notes: str = '', updated_by: str = 'system'):
    path = get_km_excel_path(project_code)
    wb = _ensure_workbook(path, ['tram_id', 'current_km', 'notes', 'updated_at', 'updated_by'])
    ws = wb.active

    tram_id = str(tram_id)
    updated = False
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for row_idx in range(2, ws.max_row + 1):
        val = ws.cell(row=row_idx, column=1).value
        if val is not None and str(val).strip() == tram_id:
            ws.cell(row=row_idx, column=2).value = int(current_km)
            ws.cell(row=row_idx, column=3).value = notes or ''
            ws.cell(row=row_idx, column=4).value = now_str
            ws.cell(row=row_idx, column=5).value = updated_by
            updated = True
            break

    if not updated:
        ws.append([tram_id, int(current_km), notes or '', now_str, updated_by])

    wb.save(path)


def sync_km_excel_to_equipment(project_code: str):
    from models import Equipment, db

    km_map = read_all_km(project_code)
    if not km_map:
        return 0

    updated = 0
    for tram_id, info in km_map.items():
        equipment = Equipment.query.filter_by(equipment_code=str(tram_id), project_code=project_code).first()
        if not equipment:
            equipment = Equipment(
                equipment_code=str(tram_id),
                name=f'Tramvay {tram_id}',
                equipment_type='Tramvay',
                current_km=info['current_km'],
                monthly_km=0,
                notes=info.get('notes', ''),
                project_code=project_code
            )
            db.session.add(equipment)
            updated += 1
            continue

        new_km = int(info['current_km']) if info.get('current_km') is not None else 0
        if (equipment.current_km or 0) != new_km:
            equipment.current_km = new_km
            updated += 1

    db.session.commit()
    return updated


def bootstrap_km_excel_from_equipment(project_code: str):
    from models import Equipment

    existing = read_all_km(project_code)
    if existing:
        return 0

    seeded = 0
    equipments = Equipment.query.filter_by(parent_id=None, project_code=project_code).all()
    for eq in equipments:
        upsert_km(
            project_code=project_code,
            tram_id=str(eq.equipment_code),
            current_km=int(eq.current_km or 0),
            notes=str(getattr(eq, 'notes', '') or ''),
            updated_by='bootstrap'
        )
        seeded += 1

    return seeded


def upsert_service_status(project_code: str, status_date: str, tram_id: str, status: str,
                          sistem: str = '', alt_sistem: str = '', aciklama: str = '', updated_by: str = 'system'):
    path = get_service_excel_path(project_code)
    wb = _ensure_workbook(path, [
        'date', 'tram_id', 'status', 'sistem', 'alt_sistem', 'aciklama', 'updated_at', 'updated_by'
    ])
    ws = wb.active

    key_date = str(status_date)
    key_tram = str(tram_id)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated = False

    for row_idx in range(2, ws.max_row + 1):
        row_date = ws.cell(row=row_idx, column=1).value
        row_tram = ws.cell(row=row_idx, column=2).value
        if str(row_date or '').strip() == key_date and str(row_tram or '').strip() == key_tram:
            ws.cell(row=row_idx, column=3).value = status
            ws.cell(row=row_idx, column=4).value = sistem or ''
            ws.cell(row=row_idx, column=5).value = alt_sistem or ''
            ws.cell(row=row_idx, column=6).value = aciklama or ''
            ws.cell(row=row_idx, column=7).value = now_str
            ws.cell(row=row_idx, column=8).value = updated_by
            updated = True
            break

    if not updated:
        ws.append([key_date, key_tram, status, sistem or '', alt_sistem or '', aciklama or '', now_str, updated_by])

    wb.save(path)


def read_service_status_by_date(project_code: str, status_date: str):
    path = get_service_excel_path(project_code)
    wb = _ensure_workbook(path, [
        'date', 'tram_id', 'status', 'sistem', 'alt_sistem', 'aciklama', 'updated_at', 'updated_by'
    ])
    ws = wb.active

    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_date = str(row[0]).strip() if row and row[0] is not None else ''
        if row_date != str(status_date):
            continue
        tram_id = str(row[1]).strip() if row[1] is not None else ''
        if not tram_id:
            continue
        out[tram_id] = {
            'status': str(row[2] or ''),
            'sistem': str(row[3] or ''),
            'alt_sistem': str(row[4] or ''),
            'aciklama': str(row[5] or ''),
            'updated_at': str(row[6] or ''),
            'updated_by': str(row[7] or ''),
        }

    return out


def sync_service_excel_to_db(project_code: str, only_date: str = None):
    from models import ServiceStatus, db

    path = get_service_excel_path(project_code)
    wb = _ensure_workbook(path, [
        'date', 'tram_id', 'status', 'sistem', 'alt_sistem', 'aciklama', 'updated_at', 'updated_by'
    ])
    ws = wb.active

    changed = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_date = str(row[0]).strip() if row and row[0] is not None else ''
        tram_id = str(row[1]).strip() if row and row[1] is not None else ''
        if not row_date or not tram_id:
            continue
        if only_date and row_date != str(only_date):
            continue

        status = str(row[2] or '')
        sistem = str(row[3] or '')
        alt_sistem = str(row[4] or '')
        aciklama = str(row[5] or '')

        existing = ServiceStatus.query.filter_by(
            tram_id=tram_id,
            date=row_date,
            project_code=project_code
        ).first()

        if existing:
            if existing.status != status or (existing.sistem or '') != sistem or (existing.alt_sistem or '') != alt_sistem or (existing.aciklama or '') != aciklama:
                existing.status = status
                existing.sistem = sistem
                existing.alt_sistem = alt_sistem
                existing.aciklama = aciklama
                changed += 1
        else:
            db.session.add(ServiceStatus(
                tram_id=tram_id,
                date=row_date,
                status=status,
                sistem=sistem,
                alt_sistem=alt_sistem,
                aciklama=aciklama,
                project_code=project_code
            ))
            changed += 1

    db.session.commit()
    return changed

def get_tramvay_list_with_km(project_code: str):
    """
    Get all tramvay/equipment for a project with their KM values.
    Single source of truth: Database (Equipment table)
    
    Returns: List of Equipment objects with current_km populated
    Strategy:
      1. Get tram ID list from Excel (Veriler.xlsx Sayfa2)
      2. Pull KM from Database (Equipment table) 
      3. Sync Excel->DB first to ensure consistency
      
    This replaces complex logic in /tramvay-km route
    """
    import pandas as pd
    from models import Equipment, db
    
    # NOTE: Equipment tablosu tek kaynak - Excel sync devre dışı
    # KM verileri sadece /tramvay-km sayfasından girilmelidir
    
    # Get tram IDs from Excel
    tram_ids = []
    project_folder = os.path.join(os.path.dirname(__file__), '..', 'data', project_code)
    excel_path = os.path.join(project_folder, 'Veriler.xlsx')
    
    if os.path.exists(excel_path):
        try:
            xls = pd.ExcelFile(excel_path)
            sheet_name = 'Sayfa2' if 'Sayfa2' in xls.sheet_names else (xls.sheet_names[0] if xls.sheet_names else None)
            
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0, engine='openpyxl')
                
                # Find tram_id column
                tram_col = None
                for col in df.columns:
                    if col.lower() in ['tram_id', 'araç', 'equipment_code', 'a']:
                        tram_col = col
                        break
                
                if tram_col:
                    for idx, row in df.iterrows():
                        tram_id = str(row[tram_col]).strip() if pd.notna(row[tram_col]) else None
                        if tram_id and tram_id.lower() not in ['project', 'proje', 'nan', '']:
                            tram_ids.append(tram_id)
        except Exception:
            pass
    
    # Query Database for equipments
    equipments = []
    if tram_ids:
        # Get from DB by equipment_code (which is the tramvay number: 1531, 1532, etc)
        equipments = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids),
            Equipment.project_code == project_code
        ).all()
    
    # If no results, fallback to all equipment in project
    if not equipments:
        equipments = Equipment.query.filter_by(
            equipment_type='Tramvay',
            project_code=project_code
        ).all()
    
    return equipments