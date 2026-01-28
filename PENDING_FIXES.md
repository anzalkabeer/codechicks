# Pending Fixes & Technical Debt

This document tracks known issues, bugs, and technical debt that need to be addressed in future development cycles.

## 🐛 Bugs & Stability Issues

### 1. Server Shutdown Traceback
**Severity:** Low (Development only)
**Status:** ⏳ Open
**Description:** 
When stopping the development server (`fastapi dev`) via Ctrl+C, an exception traceback occasionally occurs during the shutdown process.
**Context:**
- Likely related to `asyncio` loop cleanup or the `motor`/`beanie` database connection closure not completing before the loop terminates.
- Observed in `clock_.py` / `database/connection.py` lifespan handling.
**Action:** Investigate graceful shutdown patterns for Beanie + FastAPI.

### 2. ~~User Profile TOCTOU Vulnerability~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Changed username index to `sparse=True` to allow multiple None values
- Added try/except around `user.save()` to catch duplicate key errors

### 3. ~~Missing Disabled User Check~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Added `if user.disabled: raise credentials_exception` check in `get_current_user`

### 4. ~~Registration Missing Profile Fields~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Registration now sets `username` from email prefix and `display_name` from capitalized prefix

### 5. ~~Insecure "Host" Binding~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Updated `.env.example` with security warnings
- Changed default `HOST` to `127.0.0.1`

### 6. ~~Insecure "Debug" Mode~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Added warning in `.env.example` about `DEBUG=true` exposing sensitive info

## 🛠️ Technical Debt & TODOs

### 1. WebSocket Integration for Chat
**Severity:** High (Feature Gap)
**Status:** ⏳ Open
**Description:** 
The chat system currently uses polling (HTTP requests every 5s) instead of real-time updates.
**Locations:** 
- `routers/chat.py`: `TODO: Broadcast to WebSocket connections`
- `static/chat/index.html`: Remove polling logic.
**Action:** Implement FastAPI WebSockets and `ConnectionManager`.

### 2. ~~CORS Security~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- `allow_credentials` set to `False` when using wildcard (`*`) origins

### 3. ~~Secret Key Security~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Added production check: raises `ValueError` if default `SECRET_KEY` used with `DEBUG=false`

### 4. ~~Database Connection Cleanup~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- `_client` set to `None` after closing in `close_db()`

### 5. ~~MongoDB Models~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Changed `username` field to use `sparse=True` index

### 6. ~~Dashboard & Chat API Cleanup~~ ✅ FIXED (Partial)
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)`
- Removed unused `page`/`page_size` parameters from dashboard endpoint

### 7. ~~Token Expiry Configuration~~ ✅ FIXED
**Status:** ✅ Fixed (2026-01-29)
**Resolution:**
- `create_access_token` now uses `ACCESS_TOKEN_EXPIRE_MINUTES` from env when `expires_delta` is None

### 8. Frontend Polish & Reliability

#### Dashboard (`static/dashboard/index.html`)
**Status:** ⏳ Open
- **Action:** Add SRI hashes and `crossorigin` to external CDN links (Fonts/Icons).
- **Action:** Handle `getCurrentUser` failures gracefully (don't stick on "Loading...").
- **Action:** Add defensive checks (optional chaining) for nested data fields (`user_stats`, etc.) to prevent crashes.

#### Chat (`static/chat/index.html`)
**Status:** ⏳ Open
- **Action:** Update status dot classes correctly in catch block (remove `connected`).

#### Settings (`static/settings/index.html` & `.css`)
**Status:** ⏳ Open
- **Action:** Handle profile load errors by hiding spinner and showing error message.
- **Action:** Ensure UI cleanup (spinner/button) in `finally` block for `authFetch`.
- **Action:** Add `@import` for Outfit font and improved fallback font stack.

#### Styling & UX
**Status:** ⏳ Open
- **Action:** Add keyboard focus styles to nav links (`static/dashboard/style.css`).
- **Action:** Use WebKit prefix for backdrop-filter in `.glass-card` (`static/onboarding/style.css`).
- **Action:** Increase placeholder text contrast (`static/onboarding/style.css`).
- **Action:** Validate redirect URLs in login script (`static/login/script.js`).

## 📚 Documentation Updates

### DEVLOG.md
**Status:** ⏳ Open
- **Action:** Update environment variable table (Mark `MONGODB_URI` required, add `DATABASE_NAME`).
- **Action:** Clarify "Redis + Netlify" stack description.
- **Action:** Update "Frontend Pages" roadmap status (mark as mockups completed).
- **Action:** Update "User Profiles" roadmap status (already completed).
