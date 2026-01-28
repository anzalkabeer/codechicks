# Pending Fixes & Technical Debt

This document tracks known issues, bugs, and technical debt that need to be addressed.

---

## ⚠️ NEEDS USER INPUT

### ADMIN_KEY Security Pattern
**Severity:** High  
**Status:** ⏳ Awaiting Decision

The current shared ADMIN_KEY pattern is insecure. Options:
1. **Improve current**: Add audit logging, rate limiting, MFA
2. **Replace entirely**: Database-backed roles with User.isAdmin + AuditLog
3. **Hybrid**: Keep for bootstrap, require DB promotion thereafter

**Action Required:** User to decide architecture before implementation.

---

## 🔴 Critical Security Issues

### 1. Timing Attack on Admin Key
**Severity:** High  
**File:** `auth/router.py` lines 149-154  
**Issue:** Direct string comparison vulnerable to timing attacks  
**Fix:** Use `secrets.compare_digest()` for constant-time comparison

### 2. DEBUG Defaults to True
**Severity:** High  
**File:** `auth/utils.py` line 14  
**Issue:** Debug mode enabled by default exposes sensitive info  
**Fix:** Change default to `"false"` so debug is opt-in

### 3. ADMIN_KEY Missing Production Check
**Severity:** High  
**File:** `auth/utils.py` lines 17-21  
**Issue:** No production check like SECRET_KEY has  
**Fix:** Add ValueError when DEBUG=false and ADMIN_KEY is default

### 4. Admin Page No Server-Side Auth
**Severity:** High  
**File:** `clock_.py` lines 163-167  
**Issue:** Admin HTML served without authorization check  
**Fix:** Add `Depends(get_current_admin)` to route handler

### 5. Last Admin Self-Downgrade
**Severity:** Medium  
**File:** `auth/router.py` lines 170-185  
**Issue:** Last admin can remove their own admin role  
**Fix:** Add check for admin count before allowing downgrade

---

## 🟠 Backend Issues

### 6. Username Generation Collisions
**Severity:** Medium  
**File:** `auth/router.py` lines 91-102  
**Issue:** Email prefix may contain special chars, cause collisions  
**Fix:** Sanitize input, check uniqueness, append suffix if needed

### 7. PydanticObjectId Import Location
**Severity:** Low  
**File:** `routers/admin.py` lines 154-162  
**Issue:** Import inside function, bare except clause  
**Fix:** Move import to top, catch specific `InvalidId` exception

### 8. Timezone Mismatch in Admin Stats
**Severity:** Medium  
**File:** `routers/admin.py` lines 39-45  
**Issue:** today_start timezone may not match DB timestamps  
**Fix:** Ensure consistent timezone handling

### 9. Unbounded Limit in get_all_users
**Severity:** Medium  
**File:** `routers/admin.py` lines 56-67  
**Issue:** No max limit allows fetching entire DB  
**Fix:** Use `Query(default=100, ge=1, le=1000)`

### 10. update_user_role Design Issues
**Severity:** Medium  
**File:** `routers/admin.py` lines 83-110  
**Issue:** Role as function param (not body), allows self-demotion  
**Fix:** Accept role from request body, prevent self-demotion

---

## 🟡 Frontend Issues

### 11. Admin checkAdminAccess Silent Failure
**Severity:** Medium  
**File:** `static/admin/index.html` lines 152-154  
**Issue:** Early return on failure leaves user on page  
**Fix:** Redirect to login/dashboard on failure

### 12. refreshStats Implicit Event
**Severity:** Low  
**File:** `static/admin/index.html` lines 185-195  
**Issue:** Uses implicit global `event` variable  
**Fix:** Pass event as function parameter

### 13. Mobile Sidebar Completely Hidden
**Severity:** Medium  
**Files:** `static/admin/style.css`, `static/clock/index.html`  
**Issue:** Sidebar hidden on mobile removes navigation  
**Fix:** Add hamburger menu / toggleable mobile nav

### 14. Missing Keyboard Focus Styles
**Severity:** Medium  
**Files:** Multiple CSS files  
**Issue:** No `:focus-visible` styles for interactive elements  
**Fix:** Add focus styles matching hover states

### 15. Safari Backdrop-Filter Prefix
**Severity:** Low  
**Files:** `static/chat/style.css`, `static/settings/style.css`  
**Issue:** Missing `-webkit-backdrop-filter` for Safari  
**Fix:** Add webkit prefix before standard property

### 16. Clock Page getCurrentUser Unhandled
**Severity:** Low  
**File:** `static/clock/index.html` lines 390-395  
**Issue:** No try-catch around async call  
**Fix:** Wrap in try-catch, hide adminLink on failure

### 17. Dashboard usersCard Flash
**Severity:** Low  
**File:** `static/dashboard/index.html` lines 84-85  
**Issue:** Admin-only card may flash before JS hides it  
**Fix:** Add inline `style="display: none;"` as default

### 18. Onboarding Mobile Height
**Severity:** Low  
**File:** `static/onboarding/style.css` lines 276-284  
**Issue:** Fixed height causes content clipping  
**Fix:** Replace with max-height: auto, overflow-y: auto

### 19. Settings Password Update Early Return
**Severity:** Medium  
**File:** `static/settings/index.html` lines 364-373  
**Issue:** Early return bypasses finally, leaves UI loading  
**Fix:** Throw error instead of returning

### 20. Settings upgradeToAdmin Early Return
**Severity:** Medium  
**File:** `static/settings/index.html` lines 409-415  
**Issue:** Early return leaves button stuck in loading  
**Fix:** Ensure UI reset in all paths

---

## 📚 Documentation

### 21. DEVLOG Missing ADMIN_KEY Entry
**File:** `DEVLOG.md` lines 32-33  
**Fix:** Add ADMIN_KEY to environment variables section

### 22. ROADMAP Future Date
**File:** `ROADMAP.md` line 5  
**Issue:** Shows "Jan 29, 2026" which is future  
**Fix:** Update to current date

### 23. Forgot Password Priority
**File:** `ROADMAP.md` line 134  
**Issue:** In "Random Ideas" but should be higher priority  
**Fix:** Move to Medium/High priority section

---

## ✅ Previously Fixed (2026-01-29)

- [x] TOCTOU Vulnerability (sparse index + try/except)
- [x] Disabled User Check
- [x] Registration Defaults
- [x] .env Security Warnings
- [x] CORS Security (credentials + wildcard)
- [x] SECRET_KEY Production Check
- [x] DB Connection Cleanup
- [x] Deprecated datetime.utcnow()
- [x] Token Expiry Default
