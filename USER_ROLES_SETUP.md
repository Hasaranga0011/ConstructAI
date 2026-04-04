# ConstructAI User Role System Setup

## Overview
This update adds a role-based access control system with three roles:
- **ADMIN** - Full system access
- **PROJECT_MANAGER** - Manages projects and teams
- **SITE_ENGINEER** - Executes on-site work (default role)

## What Changed

### 1. Backend Model Updates
✅ `app/models/user.py` - Added UserRole enum and role column
✅ `app/schemas/user.py` - Added UserRoleEnum and role to UserCreate/UserResponse
✅ `app/services/auth_service.py` - Updated to handle role during registration

### 2. Database Changes Required
Run this SQL in pgAdmin to add the role column to existing users table:

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'site_engineer';
```

## Setup Instructions

### Step 1: Update Database in pgAdmin
1. Open pgAdmin (http://localhost:5050)
2. Navigate to Databases → constructai_db
3. Right-click → Query Tool
4. Run the SQL migration from `add_user_roles.sql`:

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'site_engineer';
```

### Step 2: Restart Backend
```cmd
cd f:\ConstructAI\constructai-backend
uvicorn app.main:app --reload
```

### Step 3: Test Registration with Roles

**Register as ADMIN:**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"admin@constructai.com\",
    \"username\": \"admin_user\",
    \"full_name\": \"System Administrator\",
    \"password\": \"AdminPassword@123\",
    \"role\": \"admin\"
  }"
```

**Register as PROJECT_MANAGER:**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"pm@constructai.com\",
    \"username\": \"pm_user\",
    \"full_name\": \"Project Manager\",
    \"password\": \"PMPassword@123\",
    \"role\": \"project_manager\"
  }"
```

**Register as SITE_ENGINEER (default):**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"engineer@constructai.com\",
    \"username\": \"engineer_user\",
    \"full_name\": \"Site Engineer\",
    \"password\": \"EngineerPassword@123\",
    \"role\": \"site_engineer\"
  }"
```

### Step 4: Verify User Roles
Query in pgAdmin:
```sql
SELECT id, email, username, role FROM users;
```

## Files Modified
- ✅ app/models/user.py
- ✅ app/schemas/user.py
- ✅ app/services/auth_service.py
- ✅ add_user_roles.sql (migration script)

## Next Steps
1. Run the SQL migration in pgAdmin
2. Restart the backend
3. Test registration with different roles
4. (Optional) Add role-based access control to endpoints
