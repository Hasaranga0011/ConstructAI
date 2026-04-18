cd F:\ConstructAI\constructai-backend

# Backend runකරන්න
uvicorn app.main:app --reload

# ඔබගේ network එකෙන් access කිරීමට (වැදගත් --host 0.0.0.0)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Swagger API documentation
http://127.0.0.1:8000/swagger

---

## 🔒 Email Uniqueness Policy

**Only ONE account can be created per email!**

✅ Database unique constraint enforcement  
✅ Service layer validation  
✅ Frontend error handling  
✅ User-friendly error messages  

See `EMAIL_UNIQUENESS_POLICY.md` for complete details.

---

## 📧 Password Reset Email - Demo Mode ✅

Reset password links are **printed to the backend console** (no email setup needed):

### How It Works:

```
1. User: Click "Forgot Password?" on login page
2. Enter: Email address (e.g., test@example.com)
3. Backend: Generates unique reset token
4. Console: Shows email details and token
5. Copy: Token from console output
6. Reset: Paste token + enter new password
7. Done: Login with new password ✅
```

### Console Output Example:

```
================================================================================
📧 PASSWORD RESET EMAIL
================================================================================
To: test@example.com
Subject: ConstructAI - Password Reset Request

Reset Token: abc123xyz456def789ghi...
Reset Link: http://localhost:5173/forgot-password?email=test@example.com&token=abc123xyz456def789ghi...
================================================================================
```

### Demo Test:

```
Email: test@example.com
1. Click "Forgot Password?"
2. Enter: test@example.com
3. Check backend console ↑
4. Copy token: abc123xyz456...
5. Paste in reset form
6. New password: newpass123
7. Confirm: newpass123
8. Reset ✅
9. Login with new password
```

### Optional: Real Email Setup

To send actual emails instead of console output:

1. See: `EMAIL_SETUP_GUIDE.md` (in project root)
2. Create `.env` file with Gmail credentials
3. Real emails will be sent automatically

---

## 🔐 Security Features

✅ **Unique Tokens**: 32-character random tokens  
✅ **Token Expiry**: Expires in 1 hour for security  
✅ **Password Hashing**: bcrypt algorithm (never stored plain)  
✅ **One-time Use**: Token deleted after use  
✅ **Email Validation**: Real email verification  
✅ **Email Uniqueness**: One account per email (enforced)  

---

## 📖 Documentation

- **[EMAIL_SETUP_GUIDE.md](../EMAIL_SETUP_GUIDE.md)** - Real email setup (optional)
- **[EMAIL_TROUBLESHOOTING.md](../EMAIL_TROUBLESHOOTING.md)** - Issues & solutions
- **[FORGET_PASSWORD_SINHALA_GUIDE.md](../FORGET_PASSWORD_SINHALA_GUIDE.md)** - සිංහල guide
- **[EMAIL_UNIQUENESS_POLICY.md](../EMAIL_UNIQUENESS_POLICY.md)** - Email policy

---

## 🚀 Quick Test

```bash
# Terminal 1: Backend
cd F:\ConstructAI\constructai-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd F:\ConstructAI\constructai-fontend
npm run dev

# Browser:
http://localhost:5173/login
→ Forgot Password? → test@example.com
→ Check backend console for token
→ Copy & use token ✅
```

---

**Status**: ✅ Email working in Demo Mode  
**Alternative**: Setup real email - see EMAIL_SETUP_GUIDE.md