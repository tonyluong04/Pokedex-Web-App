# Pokédex Web App — Project Requirements Document
**Version 2.0 · CSIT121 Object Oriented Design and Programming**

---

## Overview

Pokédex Web App v2.0 is a Single Page Application (SPA) with a Flask backend. It provides Google OAuth authentication and gives authenticated users a personal Pokédex experience backed by PostgreSQL and enriched with live Pokémon data from the PokéAPI.

### Product Vision

- Authenticate securely with Google OAuth
- Browse and search real Pokémon data via PokéAPI
- Build a personal Pokémon collection stored in PostgreSQL
- Assemble and use a battle team
- Participate in a turn-based battle experience (later phase)

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask + Flask-Login + Flask-SQLAlchemy + PostgreSQL |
| Frontend | Vanilla JS SPA + Bootstrap 5 |
| Auth | Google OAuth via `client_secrets.json` + `.env` |
| Data | PokéAPI (live); PostgreSQL stores references only |
| Deployment | `localhost:5000` (dev); production hardening later |

---

## Phase 1 — Authentication & Landing Page

> Establish the foundation: secure Google login, user persistence, and a polished landing page.

### Goals

- Users can log in and out via Google OAuth
- User profiles are created/updated in PostgreSQL on login
- The SPA routes correctly between landing, login, and home views
- Landing page is visually polished with a Pokéball animation

### Functional Requirements

| ID | Requirement |
|---|---|
| FR-A1 | User can initiate Google login from the SPA and complete the OAuth flow |
| FR-A2 | After login, backend creates or updates the `User` record by `google_id` and sets `last_login` |
| FR-A3 | SPA queries auth state via `GET /auth/status` on initialization |
| FR-A4 | Logged-in user can log out via `GET /auth/logout`, which clears the session and redirects to `/` |
| FR-A5 | Protected endpoints require authentication via Flask-Login |

### API Endpoints

| Method + Path | Description |
|---|---|
| `GET /` | Serves the SPA shell (`index.html`) |
| `GET /api/health` | Returns JSON health payload with auth state |
| `GET /auth/google` | Begins Google OAuth flow (redirect) |
| `GET /auth/google/callback` | OAuth callback — redirects to `/` on success |
| `GET /auth/logout` | Clears session and redirects to `/` |
| `GET /auth/status` | Returns `{ authenticated: boolean, user?: {...} }` |
| `GET /auth/profile` | Returns user profile JSON (auth required) |

### UI Requirements

- Landing page displays when unauthenticated
- "Login with Google" button is prominent on landing and in navbar
- Navbar reflects auth state — shows profile + logout when logged in
- Spinning Pokéball animation on landing page

### Data Model — `User`

| Field | Description |
|---|---|
| `id` | UUID — primary key |
| `google_id` | Unique Google identifier |
| `email` | User email (unique) |
| `name` | Display name from Google profile |
| `picture` | Profile picture URL |
| `is_active` | Boolean — account active flag |
| `created_at` | Timestamp of first login |
| `last_login` | Timestamp of most recent login |

---

## Phase 2 — Pokédex Search & Browsing

> Connect the app to PokéAPI and give users a real, functional Pokédex with search, detail view, and personal collection management.

### Goals

- Users can search Pokémon by name or ID
- Users can view full Pokémon details (sprite, types, stats)
- Authenticated users can add/remove Pokémon from their personal collection
- Duplicate adds are prevented at both DB and application level

### Functional Requirements

| ID | Requirement |
|---|---|
| FR-P1 | Users can search Pokémon by name or national number |
| FR-P2 | Users can view Pokémon detail: name, number, sprite, types, and base stats |
| FR-P3 | Backend fetches Pokémon data from PokéAPI using the configured base URL |
| FR-P4 | PokéAPI failures return consistent JSON errors (no HTML error pages) |
| FR-C1 | Authenticated users can list all Pokémon in their personal Pokédex |
| FR-C2 | Authenticated users can add a Pokémon to their personal Pokédex |
| FR-C3 | Duplicate adds are prevented by unique constraint and/or application logic |
| FR-C4 | Authenticated users can remove a Pokémon from their personal Pokédex |
| FR-C5 | Collection list includes: `pokemon_id`, `pokemon_name`, `pokemon_number`, `added_at` |

### New API Endpoints

| Method + Path | Description |
|---|---|
| `GET /api/pokemon/search?query=<nameOrId>` | Returns list of Pokémon summaries (id, name, sprite URL) |
| `GET /api/pokemon/<idOrName>` | Returns Pokémon detail (id, name, number, types, stats, sprites) |
| `GET /api/me/pokedex` | Returns the user's `UserPokemon[]` collection (auth required) |
| `POST /api/me/pokedex` | Adds a Pokémon. Body: `{ pokemon_id, pokemon_name, pokemon_number }` |
| `DELETE /api/me/pokedex/<pokemon_id>` | Removes a Pokémon from the user's collection (auth required) |

### UI Requirements — My Pokédex View

- Search input for finding Pokémon by name or ID
- Results displayed in a list or grid with sprite thumbnails
- Detail panel showing full Pokémon info when selected
- Add / Remove actions with clear visual feedback
- Inline error messages for API failures — no `alert()` popups

### Data Model — `UserPokemon`

| Field | Description |
|---|---|
| `id` | UUID — primary key |
| `user_id` | Foreign key → `User.id` |
| `pokemon_id` | Integer — PokéAPI Pokémon ID |
| `pokemon_name` | Cached Pokémon name |
| `pokemon_number` | Cached national Pokédex number |
| `added_at` | Timestamp when Pokémon was added |

> **Constraints:** unique `(user_id, pokemon_id)` to prevent duplicates. A `UserPokemon` record must not exist without a valid `User`.

---

## Phase 3 — Battle Mode

> Introduce the Battle Arena. Users build a team from their Pokédex and engage in turn-based battles.

### MVP — Battle Foundation

| ID | Requirement |
|---|---|
| FR-B1 | Authenticated users can create a battle team by selecting Pokémon from their Pokédex |
| FR-B2 | UI shows a Battle Arena view with team selection panel and a placeholder battle log |

### Later — Full Battle Mechanics

| ID | Requirement |
|---|---|
| FR-B3 | Turn-based battle mechanics between two trainers (local simulation or online) |
| FR-B4 | Real-time or pseudo-real-time communication via Socket.IO (optional) |

### Open Questions

- **OQ2:** What battle model is required for assessment — local simulation or online real-time?
- **OQ3:** Should Pokémon data be cached in the DB to reduce PokéAPI calls? If so, what TTL/fields?

---

## Phase 4 — UI/UX Polishing

> Make the app feel complete, responsive, and production-ready. No new features — just refinement.

### Collection Enhancements
- Pagination and filtering for large Pokédex collections
- Cached sprites to reduce PokéAPI load times
- Smooth loading states and skeleton screens

### Error Handling & Reliability
- All API endpoints return consistent JSON errors for 4xx/5xx
- DB sessions roll back automatically on 500 errors
- Inline SPA error messages replace all `alert()` usage

### Performance
- Introduce server-side caching for frequently accessed Pokémon data
- Verified to work on Windows dev environments with `psycopg2-binary`

### Security Hardening
- Session cookies are HTTPOnly; secure cookie settings enabled in production
- OAuth state parameter stored and validated to reduce CSRF risk
- Secrets never committed to source control (`client_secrets.json`, `.env`)
- All data-modifying endpoints require authentication
- Minimal personal data stored: Google ID, email, name, picture, timestamps only

---

## Acceptance Criteria

| ID | Criteria |
|---|---|
| AC1 | Unauthenticated user sees landing page and can navigate to login view |
| AC2 | Google OAuth login creates/updates a `User` record and returns user profile in `/auth/status` |
| AC3 | Authenticated user can view "My Pokédex" and list their saved Pokémon (not placeholders) |
| AC4 | Authenticated user can add a Pokémon from search results; duplicates are prevented |
| AC5 | Authenticated user can remove a Pokémon and see the UI update immediately |
| AC6 | Backend returns consistent JSON errors (4xx/5xx) and rolls back DB sessions on 500s |

---

## Out of Scope

- Username/password account creation — Google OAuth only
- Fully offline Pokédex without PokéAPI access
- Competitive matchmaking, ranking ladders, or anti-cheat systems
- Admin portals or moderation workflows

---

*Pokédex Web App v2.0 · CSIT121 · University of Wollongong*
