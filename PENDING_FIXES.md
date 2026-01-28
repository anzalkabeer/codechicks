# Pending Fixes & Technical Debt

This document tracks known issues, bugs, and technical debt that need to be addressed.

---

## ✅ Fixed (2026-01-29)

### Security (Critical)
- [x] **Timing Attack on Admin Key**: Used `secrets.compare_digest()` for constant-time comparison
- [x] **DEBUG Defaults to True**: Changed default to `false` so debug is opt-in
- [x] **ADMIN_KEY Missing Production Check**: Added validation to prevent default key in production
- [x] **Admin Page No Server-Side Auth**: Added `Depends(get_current_admin)` to `/admin` route
- [x] **Last Admin Self-Downgrade**: Added safeguard against downgrading the last admin
- [x] **Username Generation Collisions**: Added sanitization and uniqueness check loop

### Backend
- [x] **PydanticObjectId Import Location**: Moved import to top, added specific exception handling
- [x] **Timezone Mismatch in Admin Stats**: Aligned `today_start` with `now_ist()`
- [x] **Unbounded Limit in get_all_users**: Added `Query(limit=1000)` constraint
- [x] **update_user_role Design Issues**: Switched to body parameter and added self-demotion check

### Frontend & UI
- [x] **Admin checkAdminAccess Silent Failure**: Added redirect to dashboard on failure
- [x] **refreshStats Implicit Event**: explicit `event` passing
- [x] **Mobile Sidebar Hidden**: Added toggleable mobile navigation and hamburger menu (Admin & Clock)
- [x] **Missing Keyboard Focus Styles**: Added `:focus-visible` styles to interactive elements
- [x] **Safari Backdrop-Filter Prefix**: Added `-webkit-backdrop-filter` for iOS compatibility
- [x] **Clock Page getCurrentUser Unhandled**: Wrapped in try-catch to prevent errors
- [x] **Dashboard usersCard Flash**: Hidden by default via inline style to prevent flash
- [x] **Onboarding Mobile Height**: Allowed vertical scrolling on mobile views
- [x] **Settings Early Returns**: Fixed password/upgrade logic to ensure UI state resets

### Documentation
- [x] **DEVLOG ADMIN_KEY Entry**: Added to Environment Variables section
- [x] **ROADMAP Future Date**: Corrected "Last updated" date
- [x] **Forgot Password Priority**: Promoted to Medium Priority section

---

## ⚠️ Notes

### ADMIN_KEY Architecture
User selected **Option 1 (Improve current)**. The `ADMIN_KEY` pattern is kept but secured with constant-time comparison and production checks. Future improvements may include audit logs.

---

## ✅ Previously Fixed

- [x] TOCTOU Vulnerability (sparse index + try/except)
- [x] Disabled User Check
- [x] Registration Defaults
- [x] .env Security Warnings
- [x] CORS Security (credentials + wildcard)
- [x] SECRET_KEY Production Check
- [x] DB Connection Cleanup
- [x] Deprecated datetime.utcnow()
- [x] Token Expiry Default
