"""
Notification helpers - Bildirim oluşturma yardımcıları
"""
from models import db, Notification


def notify_user(user_id, title, message=None, category='info', link=None):
    """Tek bir kullanıcıya bildirim gönder"""
    n = Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        link=link
    )
    db.session.add(n)
    db.session.commit()
    return n


def notify_users(user_ids, title, message=None, category='info', link=None):
    """Birden fazla kullanıcıya bildirim gönder"""
    notifications = []
    for uid in user_ids:
        n = Notification(
            user_id=uid,
            title=title,
            message=message,
            category=category,
            link=link
        )
        db.session.add(n)
        notifications.append(n)
    db.session.commit()
    return notifications
