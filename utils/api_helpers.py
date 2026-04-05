"""
API Response Helpers - Standart JSON yanıt formatı
"""
from flask import request


def paginate(query, max_per_page=100):
    """SQLAlchemy sorgusuna sayfalama uygula.
    
    ?page=1&per_page=20 query-string parametrelerini okur.
    Returns: (items, pagination_meta) tuple
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), max_per_page)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    meta = {
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    }
    return pagination.items, meta


def api_success(data=None, message='OK', status=200):
    """Standart başarılı API yanıtı"""
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return response, status


def api_error(message='Bir hata oluştu', status=400, errors=None):
    """Standart hata API yanıtı"""
    response = {'success': False, 'message': message}
    if errors:
        response['errors'] = errors
    return response, status


def api_paginated(items, total, page, per_page, message='OK'):
    """Sayfalanmış API yanıtı"""
    return {
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }, 200
