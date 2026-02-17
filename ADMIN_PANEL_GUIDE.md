## Admin Panel - Access & Usage Guide

### ✅ System Status
- **Admin Panel**: Fully operational
- **Role-Based Access Control**: Working
- **Database Schema**: Complete (23 columns)
- **Authentication**: Configured and tested
- **Admin Routes**: 12 endpoints available

---

## Default Admin Account

```
Username: admin
Password: admin123
Email: admin@bozankaya-tramway.com
Role: admin
```

---

## Admin Panel Routes

| Route | Purpose | Access |
|-------|---------|--------|
| `/admin/dashboard` | Admin dashboard overview | Admin only |
| `/admin/users` | User management | Admin only |
| `/admin/users/add` | Add new user | Admin only |
| `/admin/users/<id>/edit` | Edit user details | Admin only |
| `/admin/projects` | Project management | Admin only |
| `/admin/projects/add` | Add new project | Admin only |
| `/admin/backups` | Backup management | Admin only |
| `/admin/api/stats` | API statistics | Admin only |

---

## Role System

### Admin Role
- Can access all projects and routes
- Can manage users and projects
- Can create and manage backups
- Access to `/admin/*` routes

### Saha Role (Field Users)
- Can only access assigned projects
- Limited to their assigned project scope
- Cannot access admin routes
- Read-only access based on project assignment

---

## Creating New Users

### Via Python Script:
```python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    user = User(
        username='field_user',
        email='user@example.com',
        full_name='Field Technician',
        role='saha',
        is_active=True
    )
    user.set_password('password123')
    user.set_assigned_projects(['belgrad', 'ankara'])  # Assign projects
    db.session.add(user)
    db.session.commit()
```

### Via Admin Dashboard:
1. Login with admin credentials
2. Navigate to `/admin/users`
3. Click "Add New User"
4. Fill in user details
5. Select projects to assign
6. Save

---

## Project Access Control

### Admin User:
- Automatically has access to ALL projects
- Shows "*" (wildcard) in assigned_projects

### Saha User:
- Can only see and work in assigned projects
- Projects stored as JSON list in `assigned_projects` column
- Example: `["belgrad", "ankara", "iasi"]`

---

## Testing the Admin Panel

Run the test script:
```bash
python test_admin_panel.py
```

Expected output:
- ✓ Admin user exists
- ✓ Role: admin
- ✓ Admin password verified
- ✓ is_admin(): True
- ✓ can_access_project(): True for all projects

---

## Troubleshooting

### Admin routes return 302 (not logged in)
- This is expected. You must first login at `/login` with admin credentials

### "assigned_projects" column not found
- Run: `python add_column.py` to add missing column

### Database errors on startup
- Run: `python init_db.py` to reinitialize database

---

## Key Features Implemented

✅ Role-based decorators (@require_admin, @require_saha)
✅ Project-based access control
✅ Admin dashboard with statistics
✅ User management interface
✅ Project management interface
✅ Backup integration
✅ User authentication with password hashing
✅ Session-based project switching
✅ Navbar project selector dropdown

---

**Last Updated**: 2025-02-17
**Status**: Production Ready
