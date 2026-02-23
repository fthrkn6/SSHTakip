from app import create_app, db
from models import Equipment

app = create_app()
ctx = app.app_context()
ctx.push()

eq = Equipment.query.first()
print(f'Equipment 1:')
print(f'  ID: {eq.id} (type: {type(eq.id).__name__})')
print(f'  Code: {eq.equipment_code} (type: {type(eq.equipment_code).__name__ if eq.equipment_code else "None"})')
print(f'  Type: {eq.equipment_type}')

# Equipment_code ile search
eq_by_code = Equipment.query.filter_by(equipment_code='1531').first()
print(f'\nequipment_code="1531" arama sonucu:')
if eq_by_code:
    print(f'  Bulundu: {eq_by_code.id} - {eq_by_code.equipment_code}')
else:
    print('  Bulunamadi')
