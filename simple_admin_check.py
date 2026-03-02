from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print(f"Total users in DB: {len(users)}")
    
    for user in users[:5]:
        is_admin_val = getattr(user, 'is_admin', None)
        print(f"User {user.username}: is_admin={is_admin_val}")
    
    # Check if there's an admin user
    admin_user = User.query.filter_by(is_admin=True).first()
    if admin_user:
        print(f"RESULT: Admin user found: {admin_user.username}")
    else:
        print("RESULT: No admin user found")
        # Try with is_admin method
        users = User.query.all()
        for u in users:
            if getattr(u, 'is_admin', lambda: False)():
                print(f"RESULT: Found admin via method: {u.username}")
                break
