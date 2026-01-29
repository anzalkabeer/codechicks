# CodeChicks Development Log

This document tracks all major changes, features, and future plans for the CodeChicks project. Please update this file when completing significant work.

---

## Project Overview

**CodeChicks** is a FastAPI backend application with HTML/CSS/JS frontend, featuring user authentication, a timer/clock feature, dashboard analytics, and global chat functionality.

**Tech Stack:**
- **Backend:** FastAPI, Pydantic, python-jose (JWT), passlib, Beanie ODM
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** MongoDB (via Beanie/Motor)
- **Deployment:** Redis + Netlify

---

## Changelog

### [2026-01-29] - Visual Polish, Persistent Timer & OAuth Integration

**Contributor:** Keshav

#### ✅ Completed

1.  **Social Authentication (OAuth2):**
    *   **Providers:** Implemented secure login via **Google** and **GitHub**.
    *   **Backend Logic:**
        *   Integrated `authlib` for standardized OAuth flow.
        *   Securely loading credentials from `googleOAuthSecret.json` and `githubOAuthSecret.json` (or Environment Variables).
        *   **Smart Username Generation:** Automatically generates unique usernames (`github_user_123`) if collisions occur.
        *   **Conflict Handling:** Handles race conditions using `DuplicateKeyError` checks during user creation.
        *   **Safety:** Validates `CLIENT_ID`/`SECRET` presence on startup to prevent crash-loops.
    *   **Frontend:**
        *   Added "Continue with Google/GitHub" buttons to Login and Register pages.
        *   Accessibility improvements (`aria-label`) for social buttons.
        *   **URL Cleanup:** Automatically removes sensitive Auth tokens from the URL bar after successful redirection to prevent leakage.

2.  **Frost/Cyber Theme Overhaul (Cyan/Blue):**
    *   **New Accent Color:** Changed from Purple to Cyan/Electric Blue (`#00f2ea` -> `#0080ff` gradient).
    *   **Glassmorphism:** Increased transparency (`glass-bg` 0.02 opacity) to better reveal the nebula background.
    *   **Admin Panel:** Updated Admin theme from Gold to match the new global Cyan theme for consistency.
    *   **Fixes:** Purged leftover purple RGB values from Dashboard CSS.

3.  **Persistent Floating Timer ("Literal Mirror"):**
    *   **UI Update:** Replaced the card-style floating timer with a **literal copy** of the `/clock` page layout.
    *   **Features:**
        *   Exact styling match: Big Cyan numbers, standard buttons (Green Start, Burgundy Pause, Gold Reset).
        *   Draggable container.
        *   **Persistence:** Timer state persists across tab switches and page reloads via server polling.
        *   **Dismissal:** 'X' button just hides the UI; timer continues in background.

4.  **Refactoring & Bug Fixes (The "14-Point" Cleanup):**
    *   **Security:** Secured WebSocket handshake (validate token *before* accept).
    *   **OAuth:** Enforced checking both Client ID and Client Secret before registering providers.
    *   **Reliability:** Refined `DuplicateKeyError` logic to distinguish between email collision (fail) and username collision (retry).
    *   **Performance:** Fixed `setInterval` logic in `clock.js` and `timer-overlay.js` to prevent duplicate polling loops.
    *   **Accessibility:** Removed blanket `user-select: none` from Login and Onboarding pages to allow text selection where appropriate. Admin Panel text selection remains disabled by design.
    *   **Visuals:** Fixed `slideIn` animation in timer overlay to not reset drag position.
    *   **Cleanup:** Removed orphan HTML tags and duplicate comments.

**Files Modified:**
- `auth/router.py`, `clock_.py`, `globalchat/main.py`
- `static/js/clock.js`, `static/js/timer-overlay.js`
- `static/admin/style.css`, `static/css/timer-overlay.css`
- `static/login/style.css`, `static/onboarding/style.css`

---

### [2026-01-29] - Repository Sync & Conflict Resolution

**Contributor:** Anzal

#### ✅ Completed

**Repository Synchronization:**
- Successfully pulled latest changes from `origin/main`
- Resolved divergent branch history

**Conflict Resolution:**
- **`.env.example`**: Merged local Google Auth settings with new remote Admin Key, keeping both configurations.
- **`clock_.py`**: Manually merged conflicting router inclusions (keeping both Admin and Global Chat routers).

**Files Modified:**
- `.env.example`
- `clock_.py`

**Files Added:**
- `globalchat/`
- `clock_.py`
- `auth/router.py`

**New Features Implemented:**

1. **WebSocket Global Chat Logic (`globalchat/main.py`):**
   - **Connection Logic**: Implemented async WebSocket handshake handling.
   - **Storage Logic**: Created `ConnectionManager` class to maintain a registry of active `WebSocket` connections in server memory.
   - **Listening Loop**: Implemented an async `while True` loop to continuously receive messages from connected clients without blocking.
   - **Broadcasting Logic**: Iterates through active connections to broadcast messages to all users in real-time.
   - **Disconnect Logic**: Automatically handles connection cleanup when a user leaves to prevent errors.
   - **Reply to Message Feature**:
     - **Database Schema Update (`database/models.py`)**:
       - Added `reply_to_id` (Optional[str]): Stores the ID of the message being replied to.
       - Added `reply_to_username` (Optional[str]): Caches the username to avoid extra DB lookups.
       - Added `reply_to_content` (Optional[str]): Caches a snippet of the original message for UI rendering.
     - **API Schema Update (`schemas/chat.py`)**:
       - Updated `MessageResponse` model to include the new reply fields, allowing the frontend to receive and render quoted messages.
     - **WebSocket Handler (`globalchat/main.py`)**:
       - Updated logic to accept `reply_to` fields from incoming JSON payloads.
       - Persists reply metadata to MongoDB.
       - Broadcasts reply details to all connected clients.
     - **Frontend Implementation**:
       - **UI Components**: Added a "Reply" button to message actions and a "Reply Preview" bar above the input field (`.message-reply-preview`).
       - **Interaction**: Clicking reply sets the active state; the preview bar appears (anchored via `.chat-input-wrapper`).
       - **Rendering**: Quoted messages are visually embedded within the new message bubble (`.message-quote`).

2. **UI Implementation Details:**
   - **Auth UI**: Built login and registration interfaces using glassmorphism design, integrated with JWT auth flow.
   - **Dashboard UI**: Created a responsive dashboard featuring:
     - Real-time statistics cards.
     - Sidebar navigation.
     - Dynamic user greeting and role display.
   - **Global Chat UI**: Developed a chat interface with:
     - Real-time message appending.
     - Sidebar showing online status (stub).
     - Modern bubble styling for sent vs received messages.
### Date - [24/01/2026]
   - **Floating Stopwatch Widget**:
     - Implemented a draggable, semi-transparent stopwatch overlay.
     - Features: Start, Stop, Reset functionality.
     - Persists state across page navigation (using localStorage or server state, as implemented).

   - **Bug Fixes**:
     - **Admin Upgrade Issue**: Fixed 500 Internal Server Error when upgrading to admin by generating and configuring `ADMIN_KEY` in `.env`.
     - **Auth Router**: Fixed syntax error in `auth/router.py` caused by duplicated exception block.



---

### [2026-01-29] - RBAC Implementation & UI Enhancements

**Contributor:** Keshav

#### ✅ Completed

**Role-Based Access Control (RBAC):**
- Added `UserRole` enum (`user`, `admin`) to `database/models.py`
- Added `role` field to User schema and UserDocument
- Implemented `get_current_admin` dependency for admin-only endpoints
- Created admin router with stats, user management, and moderation endpoints
- Added `ADMIN_KEY` environment variable for secure admin upgrades
- Created `/auth/upgrade-to-admin` and `/auth/downgrade-to-user` endpoints

**Admin Panel:**
- New admin panel at `/admin` with gold/amber accent theme
- Admin stats dashboard (total users, active users, messages, admin count)
- Quick actions for user management and chat moderation
- System status display with server time

**Password Change Feature:**
- Added `POST /api/profile/password` endpoint
- Validates current password before allowing change
- Enforces minimum 8 character requirement
- Added password change form to Settings page

**Unified UI Design:**
- Applied `bg.png` background image to dashboard, chat, settings, clock pages
- Added role badges (USER/ADMIN) in page headers
- Added "Admin Panel" link in sidebar for admin users
- Dashboard hides admin-only stats ("Total Users") for regular users
- Onboarding page matches login/register glassmorphism design
- Clock page updated with sidebar navigation

**Files Modified:**
- `database/models.py` - Added UserRole enum and role field
- `auth/schemas.py` - Added role, PasswordChange, AdminKeyRequest schemas
- `auth/router.py` - Added role to user response, admin endpoints
- `auth/utils.py` - Added ADMIN_KEY configuration
- `routers/profile.py` - Added password change endpoint
- `routers/admin.py` - New admin router (stats, user management)
- `clock_.py` - Added admin router, /admin route
- `.env` - Added ADMIN_KEY
- `static/dashboard/index.html` - Role badge, admin link, admin-only stats
- `static/dashboard/style.css` - Background image, admin styles
- `static/chat/index.html` - Admin link in sidebar
- `static/chat/style.css` - Background image, admin styles
- `static/settings/index.html` - Password change, admin upgrade section
- `static/settings/style.css` - Background image, admin styles
- `static/clock/index.html` - Sidebar navigation, unified design
- `static/onboarding/index.html` - Removed mockup banner
- `static/onboarding/style.css` - Matches login design with bg.png
- `static/admin/index.html` - New admin panel
- `static/admin/style.css` - Gold/amber admin theme

---

### [2026-01-28] - Glassmorphism UI Integration

**Contributor:** Keshav

#### ✅ Completed

**New Dashboard UI:**
- Replaced mockup UI with modern dark glassmorphism design
- Updated to Inter font family
- Added sidebar navigation (Dashboard, Chat, Timer, Settings)
- Stat cards connected to existing API endpoints
- Floating stopwatch widget with drag functionality
- Activity summary and online users indicators

**New Chat UI:**
- Replaced mockup UI with matching glassmorphism design
- Sidebar with navigation and online users section
- Modern message bubbles (self vs. other styling with avatar colors)
- Maintained IST timezone formatting for timestamps
- Preserved all existing messaging functionality

**New Settings UI:**
- Replaced mockup UI with matching glassmorphism design
- Profile editing form with validation
- Account actions section
- App info display with member since date

**Files Modified:**
- `static/dashboard/index.html` - New glassmorphism dashboard layout
- `static/dashboard/style.css` - New dark theme styles
- `static/chat/index.html` - New glassmorphism chat layout
- `static/chat/style.css` - New dark theme styles
- `static/settings/index.html` - New glassmorphism settings layout
- `static/settings/style.css` - New dark theme styles

---

### [2026-01-28] - Username/Display Name & Settings Navigation

**Contributor:** Keshav

#### ✅ Completed

**Dashboard Username Display:**
- Updated `auth/schemas.py` to include `username` and `display_name` in User schema
- Modified `auth/router.py` `get_current_user()` to return username/display_name from database
- Dashboard now shows username instead of email in the header

**Chat Display Name:**
- Updated `routers/chat.py` to use `display_name` for new messages
- Fallback chain: `display_name` → `username` → email prefix
- New messages now show proper display names instead of email prefix

**Settings Navigation:**
- Added "Settings" option to sidebar navigation in `/dashboard`
- Added "Settings" option to sidebar navigation in `/chat`
- Now consistent with `/settings` page navigation

**Chat IST Timestamps:**
- Updated `formatTime()` in chat UI to display timestamps in IST timezone
- Uses `Intl.DateTimeFormat` with `Asia/Kolkata` timezone for accurate IST display
- "Today" detection now also considers IST timezone

**Files Modified:**
- `auth/schemas.py` - Added username/display_name fields to User
- `auth/router.py` - Return username/display_name from get_current_user
- `routers/chat.py` - Use display_name for message sender
- `static/dashboard/index.html` - Display username, added Settings nav
- `static/chat/index.html` - Added Settings nav, IST timestamp formatting

---

### [2026-01-28] - IST Timezone, Onboarding & Settings

**Contributor:** Keshav

#### ✅ Completed

> ⚠️ **MOCKUP**: UI is temporary for testing.

**IST Timezone (`utils/timezone.py`):**
- Created `now_ist()`, `utc_to_ist()`, `format_ist()` helpers
- Updated `database/models.py` to use IST for timestamps

**User Profile System:**
- Extended `UserDocument` with profile fields: `username`, `display_name`, `age`, `bio`, `avatar_url`
- Added `profile_complete` flag
- Created `schemas/profile.py` and `routers/profile.py`

**Onboarding Flow (`/onboarding`):**
- New users redirected after registration
- Collects: username (required), display name, age, bio
- Marks profile complete on submit

**Settings Page (`/settings`):**
- View/edit profile info
- Change password (stub)
- Account info

**New Files:**
```
utils/
└── timezone.py      # IST timezone helpers
schemas/
└── profile.py       # Profile Pydantic schemas
routers/
└── profile.py       # Profile CRUD endpoints
static/
├── onboarding/
│   ├── index.html
│   └── style.css
└── settings/
    ├── index.html
    └── style.css
```

**API Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/profile | Get user profile |
| PATCH | /api/profile | Update profile fields |
| POST | /api/profile/complete | Complete onboarding |
| GET | /api/profile/status | Check if profile complete |

---

### [2026-01-28] - Dashboard & Chat UI Mockups

**Contributor:** Keshav

#### ✅ Completed

> ⚠️ **MOCKUP**: These are temporary interfaces for testing. Design will change.

**Shared Auth Module (`static/js/auth.js`):**
- Top-level token validation (redirects to login if no token)
- `getAuthHeaders()` helper for API calls
- `authFetch()` with automatic 401 handling
- `logout()` function

**Dashboard UI (`/dashboard`):**
- Stats cards showing real MongoDB data
- User metrics (total, active, new today)
- Global metrics (total messages)
- Navigation sidebar

**Chat UI (`/chat`):**
- Message list with auto-refresh (5s polling)
- Send message form
- Own messages styled differently
- Real-time message count

**New Files:**
```
static/
├── js/auth.js           # Shared auth module
├── dashboard/
│   ├── index.html
│   └── style.css
└── chat/
    ├── index.html
    └── style.css
```

**Updated Files:**
- `clock_.py` - Added `/dashboard` and `/chat` routes
- `static/login/script.js` - Login redirects to `/dashboard`

---

### [2026-01-27] - MongoDB Integration with Beanie

**Contributor:** Keshav

#### ✅ Completed

**Database Layer:**
- Integrated **Beanie ODM** for Mongoose-like MongoDB experience
- Created `database/` package with connection management
- Added `UserDocument` and `MessageDocument` Beanie models
- Implemented lifespan events for DB init/shutdown

**Migrations:**
- Migrated `auth/router.py` from `fake_users_db` to MongoDB
- Migrated `routers/chat.py` from `fake_messages_db` to MongoDB
- Updated `routers/dashboard.py` with real database queries

**New Files:**
```
database/
├── __init__.py
├── connection.py    # MongoDB init/close
└── models.py        # Beanie Document models
```

**Environment Updates:**
- Added `MONGODB_URI` and `DATABASE_NAME` to `.env`
- Added `beanie` and `motor` to requirements

**Verified Working:**
- ✅ User registration persists to MongoDB
- ✅ Dashboard shows real user counts
- ✅ Chat messages persist across server restarts

---

### [2026-01-27] - Dashboard & Chat Endpoints Implementation

**Contributor:** Keshav

#### ✅ Completed

**Environment Setup:**
- Added `.env` file for configuration management
- Created `.env.example` as template for collaborators
- Integrated `python-dotenv` for environment variable loading
- Updated `.gitignore` to exclude `.env`

**New Directory Structure:**
```
routers/          # API endpoint routers
├── __init__.py
├── dashboard.py  # Dashboard endpoints
└── chat.py       # Chat endpoints

schemas/          # Pydantic request/response models
├── __init__.py
├── dashboard.py  # Dashboard schemas
└── chat.py       # Chat schemas

models/           # Database models
├── __init__.py
└── message.py    # Message model
```

**Dashboard Endpoints (`/api/dashboard`):**
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/dashboard` | Global dashboard with stats | ✅ Required |
| GET | `/api/dashboard/me` | User-specific dashboard | ✅ Required |

**Chat Endpoints (`/api/chat`):**
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/chat/messages` | Paginated message history | ✅ Required |
| POST | `/api/chat/messages` | Send new message | ✅ Required |
| GET | `/api/chat/messages/{id}` | Get specific message | ✅ Required |
| DELETE | `/api/chat/messages/{id}` | Soft-delete message | ✅ Required |
| GET | `/api/chat/status` | Chat system status | ✅ Required |

**Other Changes:**
- Added CORS middleware to `clock_.py`
- Removed old unprotected `/api/dashboard` endpoint
- All new endpoints use JWT authentication via `get_current_user` dependency

#### 📁 Files Changed
- `clock_.py` - Added router imports, CORS middleware
- `auth/utils.py` - Environment variable integration
- `.gitignore` - Added `.env`

#### 📁 Files Added
- `.env` / `.env.example`
- `routers/__init__.py`, `routers/dashboard.py`, `routers/chat.py`
- `schemas/__init__.py`, `schemas/dashboard.py`, `schemas/chat.py`
- `models/__init__.py`, `models/message.py`

---

### [Previous] - Initial Authentication System

**Contributor:** Anzal

#### ✅ Completed
- JWT-based authentication with OAuth2PasswordBearer
- User registration and login endpoints
- Protected `/auth/me` endpoint
- Password hashing with PBKDF2-SHA256
- Timer/clock functionality with start/stop/reset

---

## Roadmap

### ✅ Recently Completed

- [x] **MongoDB Integration**
  - Replaced in-memory storage with MongoDB via Beanie ODM
  - Users and messages now persist across restarts
  - Automatic index creation on collections

- [x] **Real Dashboard Metrics**
  - Dashboard shows actual user counts from MongoDB
  - Chat status shows real message counts
  - User-specific message count on /me endpoint

### 🔜 Short-term (Next Steps)

- [ ] **WebSocket for Real-time Chat**
  - Implement `ConnectionManager` for WebSocket connections
  - Broadcast messages to connected clients
  - Track online users

### 🎯 Medium-term

- [ ] **User Profiles**
  - Add username/display name field
  - Profile picture support
  - User settings

- [ ] **Chat Rooms**
  - Private messaging
  - Create/join rooms
  - Room-specific permissions

- [ ] **Frontend Pages**
  - Dashboard HTML/JS page
  - Chat interface
  - User profile page

### 🚀 Long-term

- [ ] **Admin Panel**
  - User management
  - System metrics
  - Moderation tools

- [ ] **Notifications**
  - In-app notifications
  - Email notifications (optional)

- [ ] **Mobile Responsiveness**
  - Responsive design for all pages
  - PWA support

---

## Development Setup

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd codechicks

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Unix/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### Running the Server
```bash
# Development mode (with hot reload)
fastapi dev clock_.py

# Or using uvicorn directly
python -m uvicorn clock_:app --reload --host 127.0.0.1 --port 8000
```

### API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (required) | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `MONGODB_URI` | (optional) | MongoDB connection string |
| `ADMIN_KEY` | (required) | Secret key for admin upgrades |

---

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. **Update this DEVLOG.md with your changes**
4. Create a pull request
5. Request review from team members

---

*Last Updated: 2026-01-29 by Keshav - Refactoring & Fixes*
