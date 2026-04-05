"""
Input validation helpers - Giriş verisi doğrulama yardımcıları
"""
import re
from functools import wraps
from flask import request, jsonify
import html


def sanitize_string(value, max_length=500):
    """Temel string temizleme: strip + HTML escape + uzunluk sınırı"""
    if value is None:
        return None
    value = str(value).strip()
    value = html.escape(value)
    return value[:max_length]


def validate_required(data, fields):
    """Zorunlu alanları kontrol et. Eksik olanları döndür."""
    missing = [f for f in fields if not data.get(f)]
    return missing


def validate_json_payload(*required_fields):
    """JSON payload doğrulama decorator'ı.
    
    Kullanım:
        @validate_json_payload('title', 'description')
        def create_item():
            data = request.get_json()
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({'success': False, 'message': 'Geçersiz JSON verisi'}), 400
            
            missing = validate_required(data, required_fields)
            if missing:
                return jsonify({
                    'success': False,
                    'message': f'Zorunlu alanlar eksik: {", ".join(missing)}'
                }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def is_valid_date(date_str, fmt='%Y-%m-%d'):
    """Tarih formatını doğrula"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, fmt)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_email(email):
    """Basit email format doğrulama"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
