# Pending Fixes & Technical Debt

This document tracks known issues, bugs, and technical debt that need to be addressed in future development cycles.

## 🐛 Bugs & Stability Issues

### 1. Server Shutdown Traceback
**Severity:** Low (Development only)
**Description:** 
When stopping the development server (`fastapi dev`) via Ctrl+C, an exception traceback occasionally occurs during the shutdown process.
**Context:**
- Likely related to `asyncio` loop cleanup or the `motor`/`beanie` database connection closure not completing before the loop terminates.
- Observed in `clock_.py` / `database/connection.py` lifespan handling.
**Action:** Investigate graceful shutdown patterns for Beanie + FastAPI.

### 2. User Profile TOCTOU Vulnerability
**Severity:** High
**Description:**
The username uniqueness check in `routers/profile.py` (lines 71-86) is vulnerable to a Time-of-Check-Time-of-Use race condition.
**Action:**
- Add a unique index on `UserDocument.username` via `UserDocument.Settings`.
- Wrap `await user.save()` in a try/except block catching duplicate key errors to raise a 400 `HTTPException`.

### 3. Missing Disabled User Check
**Severity:** Medium
**Description:**
`auth/router.py` (lines 45-55) fetches users but does not check if they are disabled before returning.
**Action:**
- Add a check for `user.disabled` after fetching.
- Raise `credentials_exception` if true.

### 4. Registration Missing Profile Fields
**Severity:** Medium
**Description:**
`auth/router.py` (lines 72-77) creates users without `username` or `display_name`, which `get_current_user` expects.
**Action:**
- Populate `username`/`display_name` from the incoming payload or set safe defaults during registration.

### 5. Insecure "Host" Binding
**Severity:** High
**Description:**
`.env.example` (line 20) binds `HOST` to `0.0.0.0` by default.
**Action:**
- Update comments to warn that `0.0.0.0` exposes the server to all interfaces.
- Suggest `127.0.0.1` for local/production unless external access is required and secured.

### 6. Insecure "Debug" Mode
**Severity:** High
**Description:**
`.env.example` (line 22) lacks warnings about `DEBUG=true` in production.
**Action:**
- Add warning that `DEBUG=true` exposes sensitive info.
- Recommend `DEBUG=false` as default.

## 🛠️ Technical Debt & TODOs

### 1. WebSocket Integration for Chat
**Severity:** High (Feature Gap)
**Description:** 
The chat system currently uses polling (HTTP requests every 5s) instead of real-time updates.
**Locations:** 
- `routers/chat.py`: `TODO: Broadcast to WebSocket connections`
- `static/chat/index.html`: Remove polling logic.
**Action:** Implement FastAPI WebSockets and `ConnectionManager`.

### 2. CORS Security
**Severity:** High
**Description:**
`clock_.py` (lines 41-54) allows credentials with wildcard origins (`*`) if configured, which is unsafe.
**Action:**
- Set `allow_credentials=False` if `cors_origins` is `*`.
- Only allow credentials with explicit origin whitelists.

### 3. Secret Key Security
**Severity:** High
**Description:**
`auth/utils.py` (line 11) uses a default insecure `SECRET_KEY`.
**Action:**
- Raise `ValueError` in production if `SECRET_KEY` is not set.
- Only allow fallback key in non-production environments.

### 4. Database Connection Cleanup
**Severity:** Medium
**Description:**
`database/connection.py` (lines 43-52) does not set `_client` to `None` after closing.
**Action:**
- Set `global _client = None` after closing to prevent reuse of closed connections.

### 5. MongoDB Models
**Severity:** Medium
**Description:**
`database/models.py` (line 27) uses `unique=True` on an optional `username` field, preventing multiple users with `None` username.
**Action:**
- Remove `unique=True` from the field definition.
- Create a partial unique index for `username` where it exists and is a string.

### 6. Dashboard & Chat API Cleanup
**Severity:** Low
**Description:**
- `routers/dashboard.py`: Uses deprecated `datetime.utcnow()`.
- `routers/dashboard.py`: Defines unused `page`/`page_size` parameters.
**Action:**
- Switch to `datetime.now(timezone.utc)`.
- Remove unused parameters.

### 7. Token Expiry Configuration
**Severity:** Low
**Description:**
`auth/utils.py`: `create_access_token` ignores `ACCESS_TOKEN_EXPIRE_MINUTES` env var default.
**Action:**
- Use `ACCESS_TOKEN_EXPIRE_MINUTES` as default when `expires_delta` is `None`.

### 8. Frontend Polish & Reliability

#### Dashboard (`static/dashboard/index.html`)
- **Action:** Add SRI hashes and `crossorigin` to external CDN links (Fonts/Icons).
- **Action:** Handle `getCurrentUser` failures gracefully (don't stick on "Loading...").
- **Action:** Add defensive checks (optional chaining) for nested data fields (`user_stats`, etc.) to prevent crashes.

#### Chat (`static/chat/index.html`)
- **Action:** Update status dot classes correctly in catch block (remove `connected`).

#### Settings (`static/settings/index.html` & `.css`)
- **Action:** Handle profile load errors by hiding spinner and showing error message.
- **Action:** Ensure UI cleanup (spinner/button) in `finally` block for `authFetch`.
- **Action:** Add `@import` for Outfit font and improved fallback font stack.

#### Styling & UX
- **Action:** Add keyboard focus styles to nav links (`static/dashboard/style.css`).
- **Action:** Use WebKit prefix for backdrop-filter in `.glass-card` (`static/onboarding/style.css`).
- **Action:** Increase placeholder text contrast (`static/onboarding/style.css`).
- **Action:** Validate redirect URLs in login script (`static/login/script.js`).

## 📚 Documentation Updates

### DEVLOG.md
- **Action:** Update environment variable table (Mark `MONGODB_URI` required, add `DATABASE_NAME`).
- **Action:** Clarify "Redis + Netlify" stack description.
- **Action:** Update "Frontend Pages" roadmap status (mark as mockups completed).
- **Action:** Update "User Profiles" roadmap status (already completed).
