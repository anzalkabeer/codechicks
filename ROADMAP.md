# CodeChicks Roadmap 🗺️

This is the current Roadmap we need to work on for this project.

Last updated: Jan 29, 2026

---

## 🔥 High Priority (Need ASAP)

### Admin Panel — Actually Make It Useful

Right now the admin panel just shows stats. Cool, but kinda useless. Need to build out the actual pages:

- [ ] **Users Tab** (`/admin/users`)
  - List all registered users with search/filter
  - Show user details (email, username, role, join date)
  - Quick actions: disable/enable account, change role
  - Maybe add a "last active" column eventually
  - Export users as CSV would be nice

- [ ] **Messages Tab** (`/admin/messages`)
  - View all chat messages (paginated obviously)
  - Delete individual messages
  - Bulk delete option for spam cleanup
  - Filter by user or date range
  - Flag system? For reported messages

- [ ] **System Tab** (`/admin/system`)
  - Database connection status & stats
  - API endpoint health checks
  - Server uptime tracker
  - Maybe some basic logs viewer
  - Environment info (version, debug mode, etc)

### Real-time Chat (WebSockets)

The current polling every 5 seconds is... not great. Every time I test with friends the delay is noticeable.

- [x] Implement WebSocket connection manager (Partial Support - Logic added)
- [ ] Replace polling with WS push (Frontend pending)
- [ ] Typing indicators (who's currently typing)
- [ ] "User X joined/left" system messages
- [ ] Online presence — who's actually online right now

---

## 🟡 Medium Priority

### Profile Enhancements

- [ ] Avatar upload (not just URL)
- [ ] Profile page viewable by others (`/user/username`)
- [ ] Bio with markdown support 
- [ ] Social links(GitHub, Twitter, etc)
- [ ] "Member since" badge tiers (1 month, 6 months, 1 year...)
- [ ] Forgot password flow — Medium/High priority (Owner: TBD, ETA: Q1 2026)
  - [ ] Reset token generation & secure delivery
  - [ ] Account recovery UX & token expiry
  - [ ] See PENDING_FIXES.md for security compliance notes

### Timer/Stopwatch Upgrades

- [x] **Persistence Overlay** (Done!)
  - Draggable, persists across tabs, "exact clone" UI.
- [ ] Session tracking — log how long each session was
- [ ] Daily/weekly timer stats on dashboard
- [ ] Pomodoro mode (25 min work, 5 min break cycles)
- [ ] Custom timer presets
- [ ] Focus mode that dims the rest of the page

### Notifications System

- [ ] In-app notification bell
- [ ] Get notified when someone mentions you in chat
- [ ] Admin broadcasts to all users
- [ ] Email notifications (opt-in obviously)

---

## 🟢 Nice-to-Have (Eventually)

### Private Messaging

- [ ] DM other users
- [ ] Message read receipts
- [ ] Block users --> only can be done by admin
### Activity & Gamification

I kinda want to make it fun? Not sure how far to take this.

- [ ] Daily login streak
- [ ] XP system based on activity
- [ ] Badges/achievements
- [ ] Leaderboard (most messages, longest timer sessions, etc)

### Dark/Light Mode Toggle

Everything is dark theme right now. Some people apparently like light mode. Weird, but fine.

- [ ] Theme toggle in settings
- [ ] Remember preference
- [ ] Auto switch based on system preference

### Mobile App

This is way down the line, but:

- [ ] React Native wrapper?
- [ ] Or just make the PWA better
- [ ] Push notifications

---

## 🛠️ Tech Debt & Cleanup

Stuff that won't add features but needs doing:

- [ ] Add proper logging throughout (not just print statements lol)
- [ ] Rate limiting on auth endpoints
- [ ] API documentation (OpenAPI is auto but could be better)
- [ ] Unit tests... any tests really
- [ ] CI/CD pipeline for auto deploys

---

## 💡 Random Ideas (Parking Lot)

Just throwing these here so I don't forget:

- Voice channels? (probably overkill)
- Collaborative code editor (like a mini CodePen)
- Integration with GitHub (show commits, PRs)
- Custom user themes[abhi ke liye not neccessary ]
- Bot/webhook system for chat
- Two-factor authentication

---

## ✅ Recently Completed

Just so I remember what's actually done:

- [x] **Frost/Cyber Theme** (Cyan Accent + Glassmorphism)
- [x] **Persistent Timer Overlay** (Exact Clone)
- [x] **Global Text Selection Disable** (Refined: Admin only)
- [x] RBAC system (user/admin roles)
- [x] Admin panel with overview stats & **Cyan Theme Update**
- [x] Password change in settings
- [x] Admin key upgrade flow
- [x] Unified background across all pages
- [x] Onboarding page redesign
- [x] Clock page sidebar navigation
- [x] Fixed TOCTOU vulnerability
- [x] CORS security fixes
- [x] Production secret key check

---

*Note to self: Don't try to do everything at once. Ship one feature properly > half-finish five.*
