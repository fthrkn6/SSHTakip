"""
Language translation helper - supports Turkish (tr) and English (en)
Usage in templates: {{ t('key') }}
Usage in Python: from utils.translations import get_translation
"""

TRANSLATIONS = {
    # === NAVIGATION / SIDEBAR ===
    'Dashboard': {'tr': 'Dashboard', 'en': 'Dashboard'},
    'main_menu': {'tr': 'Ana Menü', 'en': 'Main Menu'},
    'work_management': {'tr': 'İş Yönetimi', 'en': 'Work Management'},
    'inventory': {'tr': 'Envanter', 'en': 'Inventory'},
    'reports_analysis': {'tr': 'Raporlar & Analiz', 'en': 'Reports & Analysis'},
    'documentation': {'tr': 'Dokümantasyon', 'en': 'Documentation'},
    'management': {'tr': 'Yönetim', 'en': 'Management'},
    'report_failure': {'tr': 'Yeni Arıza Bildir', 'en': 'Report New Failure'},
    'failure_list': {'tr': 'Arıza Listesi - Veriler', 'en': 'Failure List - Data'},
    'hbr_list': {'tr': 'HBR Listesi', 'en': 'HBR List'},
    'maintenance_plans': {'tr': 'Bakım Planları', 'en': 'Maintenance Plans'},
    'tram_km': {'tr': 'Tramvay KM', 'en': 'Tram KM'},
    'service_status': {'tr': 'Servis Durumu', 'en': 'Service Status'},
    'spare_parts': {'tr': 'Yedek Parça', 'en': 'Spare Parts'},
    'fracas_analysis': {'tr': 'FRACAS Analiz', 'en': 'FRACAS Analysis'},
    'kpi_dashboard': {'tr': 'KPI Dashboard', 'en': 'KPI Dashboard'},
    'project_analysis': {'tr': 'Proje Analizi', 'en': 'Project Analysis'},
    'recent_reports': {'tr': 'Son Raporlar', 'en': 'Recent Reports'},
    'system_logs': {'tr': 'Sistem Logları', 'en': 'System Logs'},
    'tech_docs': {'tr': 'Teknik Dokümanlar', 'en': 'Technical Documents'},
    'admin_panel': {'tr': 'Admin Paneli', 'en': 'Admin Panel'},
    'user_management': {'tr': 'Kullanıcı Yönetimi', 'en': 'User Management'},
    'project_management': {'tr': 'Proje Yönetimi', 'en': 'Project Management'},
    'backup': {'tr': 'Yedekleme', 'en': 'Backup'},
    'permission_management': {'tr': 'Yetki Yönetimi', 'en': 'Permission Management'},
    'management_dashboard': {'tr': 'Yönetim Dashboard', 'en': 'Management Dashboard'},

    # === NAVBAR ===
    'search_placeholder': {'tr': 'Ara... (ekipman, arıza, iş emri)', 'en': 'Search... (equipment, failure, work order)'},
    'select_project': {'tr': 'Proje Seç', 'en': 'Select Project'},
    'dark_mode': {'tr': 'Karanlık Mod', 'en': 'Dark Mode'},
    'notifications': {'tr': 'Bildirimler', 'en': 'Notifications'},
    'mark_all_read': {'tr': 'Tümünü Okundu İşaretle', 'en': 'Mark All as Read'},
    'no_notifications': {'tr': 'Bildirim yok', 'en': 'No notifications'},
    'profile': {'tr': 'Profil', 'en': 'Profile'},
    'logout': {'tr': 'Çıkış Yap', 'en': 'Logout'},
    'skip_to_content': {'tr': 'İçeriğe Atla', 'en': 'Skip to Content'},
    'open_menu': {'tr': 'Menüyü aç', 'en': 'Open menu'},
    'close_menu': {'tr': 'Menüyü kapat', 'en': 'Close menu'},

    # === QUICK ACTIONS ===
    'quick_actions': {'tr': 'Hızlı İşlemler', 'en': 'Quick Actions'},

    # === DASHBOARD ===
    'welcome': {'tr': 'Hoş Geldiniz', 'en': 'Welcome'},
    'overview': {'tr': 'Genel Bakış', 'en': 'Overview'},
    'total_equipment': {'tr': 'Toplam Ekipman', 'en': 'Total Equipment'},
    'active_failures': {'tr': 'Aktif Arızalar', 'en': 'Active Failures'},
    'pending_work_orders': {'tr': 'Bekleyen İş Emirleri', 'en': 'Pending Work Orders'},
    'completed_today': {'tr': 'Bugün Tamamlanan', 'en': 'Completed Today'},
    'availability': {'tr': 'Kullanılabilirlik', 'en': 'Availability'},
    'recent_failures': {'tr': 'Son Arızalar', 'en': 'Recent Failures'},
    'recent_work_orders': {'tr': 'Son İş Emirleri', 'en': 'Recent Work Orders'},
    'fleet_status': {'tr': 'Filo Durumu', 'en': 'Fleet Status'},
    'view_all': {'tr': 'Tümünü Gör', 'en': 'View All'},
    'no_data': {'tr': 'Veri bulunamadı', 'en': 'No data found'},

    # === KPI ===
    'mtbf': {'tr': 'MTBF', 'en': 'MTBF'},
    'mttr': {'tr': 'MTTR', 'en': 'MTTR'},
    'oee': {'tr': 'OEE', 'en': 'OEE'},
    'reliability': {'tr': 'Güvenilirlik', 'en': 'Reliability'},
    'kpi_title': {'tr': 'KPI Göstergeleri', 'en': 'KPI Indicators'},
    'performance_trend': {'tr': 'Performans Trendi', 'en': 'Performance Trend'},
    'mean_time_between_failures': {'tr': 'Ortalama Arıza Arası Süre', 'en': 'Mean Time Between Failures'},
    'mean_time_to_repair': {'tr': 'Ortalama Onarım Süresi', 'en': 'Mean Time To Repair'},
    'overall_equipment_effectiveness': {'tr': 'Genel Ekipman Etkinliği', 'en': 'Overall Equipment Effectiveness'},

    # === EQUIPMENT ===
    'equipment': {'tr': 'Ekipman', 'en': 'Equipment'},
    'equipment_id': {'tr': 'Ekipman ID', 'en': 'Equipment ID'},
    'equipment_name': {'tr': 'Ekipman Adı', 'en': 'Equipment Name'},
    'equipment_type': {'tr': 'Ekipman Tipi', 'en': 'Equipment Type'},
    'equipment_status': {'tr': 'Durum', 'en': 'Status'},
    'criticality': {'tr': 'Kritiklik', 'en': 'Criticality'},
    'location': {'tr': 'Konum', 'en': 'Location'},
    'operational': {'tr': 'Operasyonel', 'en': 'Operational'},
    'maintenance': {'tr': 'Bakımda', 'en': 'Under Maintenance'},
    'repair': {'tr': 'Onarımda', 'en': 'Under Repair'},
    'decommissioned': {'tr': 'Hizmet Dışı', 'en': 'Decommissioned'},

    # === FAILURES ===
    'failure': {'tr': 'Arıza', 'en': 'Failure'},
    'failure_date': {'tr': 'Arıza Tarihi', 'en': 'Failure Date'},
    'failure_description': {'tr': 'Arıza Açıklaması', 'en': 'Failure Description'},
    'failure_type': {'tr': 'Arıza Tipi', 'en': 'Failure Type'},
    'severity': {'tr': 'Şiddet', 'en': 'Severity'},
    'priority': {'tr': 'Öncelik', 'en': 'Priority'},
    'status': {'tr': 'Durum', 'en': 'Status'},
    'critical': {'tr': 'Kritik', 'en': 'Critical'},
    'high': {'tr': 'Yüksek', 'en': 'High'},
    'medium': {'tr': 'Orta', 'en': 'Medium'},
    'low': {'tr': 'Düşük', 'en': 'Low'},
    'reported_by': {'tr': 'Bildiren', 'en': 'Reported By'},
    'assigned_to': {'tr': 'Atanan', 'en': 'Assigned To'},
    'root_cause': {'tr': 'Kök Neden', 'en': 'Root Cause'},

    # === WORK ORDERS ===
    'work_order': {'tr': 'İş Emri', 'en': 'Work Order'},
    'work_orders': {'tr': 'İş Emirleri', 'en': 'Work Orders'},
    'wo_number': {'tr': 'İş Emri No', 'en': 'Work Order No'},
    'wo_type': {'tr': 'Tip', 'en': 'Type'},
    'wo_status_pending': {'tr': 'Bekliyor', 'en': 'Pending'},
    'wo_status_scheduled': {'tr': 'Planlandı', 'en': 'Scheduled'},
    'wo_status_in_progress': {'tr': 'Devam Ediyor', 'en': 'In Progress'},
    'wo_status_completed': {'tr': 'Tamamlandı', 'en': 'Completed'},
    'start_date': {'tr': 'Başlangıç Tarihi', 'en': 'Start Date'},
    'end_date': {'tr': 'Bitiş Tarihi', 'en': 'End Date'},
    'duration': {'tr': 'Süre', 'en': 'Duration'},
    'technician': {'tr': 'Teknisyen', 'en': 'Technician'},

    # === MAINTENANCE ===
    'maintenance_plan': {'tr': 'Bakım Planı', 'en': 'Maintenance Plan'},
    'preventive': {'tr': 'Önleyici', 'en': 'Preventive'},
    'corrective': {'tr': 'Düzeltici', 'en': 'Corrective'},
    'predictive': {'tr': 'Öngörücü', 'en': 'Predictive'},
    'scheduled_date': {'tr': 'Planlanan Tarih', 'en': 'Scheduled Date'},
    'frequency': {'tr': 'Frekans', 'en': 'Frequency'},
    'add_maintenance_plan': {'tr': 'Bakım Planı Ekle', 'en': 'Add Maintenance Plan'},

    # === COMMON ===
    'save': {'tr': 'Kaydet', 'en': 'Save'},
    'cancel': {'tr': 'İptal', 'en': 'Cancel'},
    'delete': {'tr': 'Sil', 'en': 'Delete'},
    'edit': {'tr': 'Düzenle', 'en': 'Edit'},
    'add': {'tr': 'Ekle', 'en': 'Add'},
    'create': {'tr': 'Oluştur', 'en': 'Create'},
    'update': {'tr': 'Güncelle', 'en': 'Update'},
    'search': {'tr': 'Ara', 'en': 'Search'},
    'filter': {'tr': 'Filtrele', 'en': 'Filter'},
    'export': {'tr': 'Dışa Aktar', 'en': 'Export'},
    'import': {'tr': 'İçe Aktar', 'en': 'Import'},
    'download': {'tr': 'İndir', 'en': 'Download'},
    'upload': {'tr': 'Yükle', 'en': 'Upload'},
    'close': {'tr': 'Kapat', 'en': 'Close'},
    'confirm': {'tr': 'Onayla', 'en': 'Confirm'},
    'back': {'tr': 'Geri', 'en': 'Back'},
    'next': {'tr': 'İleri', 'en': 'Next'},
    'loading': {'tr': 'Yükleniyor...', 'en': 'Loading...'},
    'success': {'tr': 'Başarılı', 'en': 'Success'},
    'error': {'tr': 'Hata', 'en': 'Error'},
    'warning': {'tr': 'Uyarı', 'en': 'Warning'},
    'info': {'tr': 'Bilgi', 'en': 'Info'},
    'actions': {'tr': 'İşlemler', 'en': 'Actions'},
    'details': {'tr': 'Detaylar', 'en': 'Details'},
    'description': {'tr': 'Açıklama', 'en': 'Description'},
    'date': {'tr': 'Tarih', 'en': 'Date'},
    'time': {'tr': 'Saat', 'en': 'Time'},
    'name': {'tr': 'Ad', 'en': 'Name'},
    'notes': {'tr': 'Notlar', 'en': 'Notes'},
    'yes': {'tr': 'Evet', 'en': 'Yes'},
    'no': {'tr': 'Hayır', 'en': 'No'},
    'all': {'tr': 'Tümü', 'en': 'All'},
    'active': {'tr': 'Aktif', 'en': 'Active'},
    'inactive': {'tr': 'Pasif', 'en': 'Inactive'},
    'total': {'tr': 'Toplam', 'en': 'Total'},
    'count': {'tr': 'Sayı', 'en': 'Count'},
    'percentage': {'tr': 'Yüzde', 'en': 'Percentage'},
    'trend': {'tr': 'Trend', 'en': 'Trend'},
    'report': {'tr': 'Rapor', 'en': 'Report'},
    'generate_report': {'tr': 'Rapor Oluştur', 'en': 'Generate Report'},
    'export_excel': {'tr': 'Excel İndir', 'en': 'Export Excel'},
    'export_pdf': {'tr': 'PDF İndir', 'en': 'Export PDF'},
    'no_project_selected': {'tr': 'Proje Seçilmedi', 'en': 'No Project Selected'},
    'language': {'tr': 'Dil', 'en': 'Language'},
    'turkish': {'tr': 'Türkçe', 'en': 'Turkish'},
    'english': {'tr': 'İngilizce', 'en': 'English'},

    # === AUTH ===
    'login': {'tr': 'Giriş Yap', 'en': 'Login'},
    'username': {'tr': 'Kullanıcı Adı', 'en': 'Username'},
    'password': {'tr': 'Şifre', 'en': 'Password'},
    'remember_me': {'tr': 'Beni Hatırla', 'en': 'Remember Me'},
    'login_title': {'tr': 'SSH Takip - Giriş', 'en': 'SSH Takip - Login'},
    'login_subtitle': {'tr': 'Bakım Yönetim Sistemine Giriş', 'en': 'Login to Maintenance Management System'},
    'invalid_credentials': {'tr': 'Geçersiz kullanıcı adı veya şifre', 'en': 'Invalid username or password'},

    # === PAGE TITLES ===
    'app_title': {'tr': 'SSH Takip - Bakım Yönetim Sistemi', 'en': 'SSH Takip - Maintenance Management System'},
    'app_subtitle': {'tr': 'Bakım Yönetim Sistemi', 'en': 'Maintenance Management System'},

    # === SERVICE STATUS ===
    'in_service': {'tr': 'Hizmette', 'en': 'In Service'},
    'out_of_service': {'tr': 'Hizmet Dışı', 'en': 'Out of Service'},
    'standby': {'tr': 'Bekleme', 'en': 'Standby'},
    'depot': {'tr': 'Depoda', 'en': 'In Depot'},
    'planned_maintenance': {'tr': 'Planlı Bakım', 'en': 'Planned Maintenance'},
    'unplanned_maintenance': {'tr': 'Plansız Bakım', 'en': 'Unplanned Maintenance'},

    # === PROJECT SELECT ===
    'project_select_title': {'tr': 'Proje Seçimi', 'en': 'Project Selection'},
    'project_select_subtitle': {'tr': 'Devam etmek istediğiniz projeyi seçin', 'en': 'Select the project you want to continue with'},
    'continue': {'tr': 'Devam Et', 'en': 'Continue'},

    # === ROLES ===
    'role_admin': {'tr': 'Sistem Yöneticisi', 'en': 'System Administrator'},
    'role_manager': {'tr': 'Yönetici', 'en': 'Manager'},
    'role_technician': {'tr': 'Teknisyen', 'en': 'Technician'},
    'role_operator': {'tr': 'Operatör', 'en': 'Operator'},
    'role_saha': {'tr': 'Saha Kullanıcısı', 'en': 'Field User'},
}


def get_translation(key: str, lang: str = 'en') -> str:
    """Return translation for key in given language."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get('tr', key))


def get_all_translations(lang: str = 'en') -> dict:
    """Return all translations as a flat dict for template context."""
    return {k: v.get(lang, v.get('tr', k)) for k, v in TRANSLATIONS.items()}
