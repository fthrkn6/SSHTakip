"""
SSH Takip - Bilgisayarlı Bakım Yönetim Sistemi
Bozankaya Hafif Raylı Sistem için Kapsamlı Bakım Yönetimi
EN 13306, ISO 55000, EN 15341, ISO 27001 Standartlarına Uygun
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, date
from models import (db, User, Equipment, Failure, WorkOrder, MaintenancePlan, 
                   SparePartInventory, DowntimeRecord, MeterReading, KPISnapshot, 
                   SystemAlert, StockTransaction, WorkOrderPart, SensorData,
                   FailurePrediction, ComponentHealthIndex, EN15341_KPI, AuditLog,
                   ResourceAllocation, CostCenter, MaintenanceBudget, TechnicalDocument,
                   MaintenanceTrigger, MaintenanceAlert, OperationalImpact, FleetAvailability,
                   SkillMatrix, TeamAssignment)
from werkzeug.utils import secure_filename
import os
import io
import json
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.utils import get_column_letter


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'dwg', 'jpg', 'png', 'jpeg'}

# ==================== GLOBAL CACHE SİSTEMİ ====================
# Excel verileri bir kez okunup bellekte tutulur
EXCEL_CACHE = {}

PROJECTS = [
    {'code': 'belgrad', 'name': 'Belgrad', 'country': 'Sırbistan', 'flag': '🇷🇸'},
    {'code': 'iasi', 'name': 'Iași', 'country': 'Romanya', 'flag': '🇷🇴'},
    {'code': 'timisoara', 'name': 'Timișoara', 'country': 'Romanya', 'flag': '🇹🇷'},
    {'code': 'kayseri', 'name': 'Kayseri', 'country': 'Türkiye', 'flag': '🇹🇷'},
    {'code': 'kocaeli', 'name': 'Kocaeli', 'country': 'Türkiye', 'flag': '🇹🇷'},
    {'code': 'gebze', 'name': 'Gebze', 'country': 'Türkiye', 'flag': '🇹🇷'},
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    """Flask uygulaması oluştur ve yapılandır"""
    print('create_app started')
    try:
        app = Flask(__name__, static_folder='static', static_url_path='/static')
        
        # Konfigürasyon
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bozankaya-ssh_takip-2024-gizli')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssh_takip_bozankaya.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

        # Veritabanı başlatma
        db.init_app(app)

        # Login Manager
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        login_manager.login_message = 'Bu sayfayı görüntülemek için giriş yapmalısınız.'
        login_manager.login_message_category = 'warning'

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        # ==================== YARDIMCI FONKSİYONLAR ====================

        def get_cached_fracas_data(project_code):
            """Cache'den FRACAS verisi al veya yükle"""
            global EXCEL_CACHE
            if project_code in EXCEL_CACHE:
                return EXCEL_CACHE[project_code]
            
            # Cache'de yok, yükle
            df = _load_fracas_from_excel(project_code)
            EXCEL_CACHE[project_code] = df
            return df

        def clear_cache(project_code=None):
            """Cache'i temizle"""
            global EXCEL_CACHE
            if project_code:
                EXCEL_CACHE.pop(project_code, None)
            else:
                EXCEL_CACHE = {}

        def _load_fracas_from_excel(project_code):
            """Excel'den FRACAS verilerini yükle"""
            excel_path = get_fracas_excel_path_for_project(project_code)
            if not excel_path:
                return None
            try:
                df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
                df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
                df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
                fracas_col = get_column(df, ['FRACAS ID'])
                if fracas_col:
                    df = df[df[fracas_col].notna()]
                print(f"  OK {project_code}: {len(df)} records loaded")
                return df
            except Exception as e:
                print(f"  ERROR {project_code}: Error - {e}")
                return None

        def get_column(df, possible_names):
            """Birden fazla olası isimden sütun bul"""
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in col.lower():
                        return col
            return None

        def get_fracas_excel_path_for_project(project_code):
            """FRACAS Excel dosya yolunu döndür"""
            project_folder = os.path.join(app.root_path, 'data', project_code)
            
            if os.path.exists(project_folder):
                for filename in os.listdir(project_folder):
                    if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
                        return os.path.join(project_folder, filename)
            
            if project_code == 'belgrad':
                data_folder = os.path.join(app.root_path, 'data')
                if os.path.exists(data_folder):
                    for filename in os.listdir(data_folder):
                        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$') and 'FRACAS' in filename.upper():
                            return os.path.join(data_folder, filename)
            
            return None

        def preload_all_projects():
            """Tüm projeleri önceden yükle"""
            print("\nLoading Excel data...")
            for p in PROJECTS:
                get_cached_fracas_data(p['code'])
            print("OK All projects loaded into cache!\n")

        # ==================== MODÜL BASLANGIC ====================
        
        print("DEBUG: About to preload projects")
        # preload_all_projects()  # Disabled for now
        print("DEBUG: Skipped preload_all_projects")
        
        print('create_app finished')
        print(f'App object type: {type(app)}')
        print(f'App object: {app}')
        return app
        
    except Exception as e:
        print(f'CRITICAL ERROR in create_app: {e}')
        import traceback
        traceback.print_exc()
        return None


def init_sample_data(app):
    """Örnek verileri ekle"""
    with app.app_context():
        db.create_all()
        
        if User.query.filter_by(username='admin').first():
            return
        
        admin = User(
            username='admin',
            email='admin@bozankaya-tramway.com',
            full_name='Sistem Yöneticisi',
            role='admin',
            department='IT',
            employee_id='EMP001',
            hourly_rate=50
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Örnek veriler başarıyla eklendi!')


def print_project_status():
    """All projects FRACAS status print"""
    print("\n" + "=" * 70)
    print("                    BOZANKAYA SSH Takip - PROJECT STATUS")
    print("=" * 70)
    print(f"{'Project':<20} {'File':<30} {'Size':<10} {'Records':<8} {'Vehicles':<6}")
    print("-" * 70)
    print(f"{'TOTAL':<20} {'':<30} {'':<10} {'0':>6} {'0':>6}")
    print("=" * 70)
    print()


if __name__ == '__main__':
    app = create_app()
    if app:
        init_sample_data(app)
        print_project_status()
    print("\nSSH Takip System starting...")
    print("URL: http://localhost:5000")
    print("User: admin / admin123\n")
    if app:
        app.run(debug=True, port=5000)
