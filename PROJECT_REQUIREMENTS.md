# Project Requirements Document (PRD) — Pokédex Web App v2.0

## Overview
Pokédex Web App v2.0 is a Single Page Application (SPA) with a Flask backend. It provides Google OAuth authentication, and will provide authenticated users with a personal Pokédex experience backed by PostgreSQL and enriched with live Pokémon data from PokéAPI.

## Product vision
Deliver a modern, simple Pokédex experience where a user can:
- authenticate securely with Google,
- browse/search real Pokémon data (PokéAPI),
- add Pokémon to a personal collection (stored in PostgreSQL),
- assemble and use a battle team,
- participate in a (later) turn-based battle experience.

## Goals
- **G1 — Secure sign-in**: Users can log in/out via Google OAuth and the app persists a user profile in the database.
- **G2 — Personal Pokédex**: Users can manage a personal collection (add/remove/list) without duplicating full PokéAPI datasets locally.
- **G3 — Real Pokémon data**: Pokémon details displayed in the UI come from PokéAPI (or a cache derived from it).
- **G4 — Clean SPA UX**: A single page (`/`) renders all views (landing/login/home/pokedex/battle) using client-side rendering.
- **G5 — Extensible phases**: The backend is organized to support future phases (Pokémon API routes, battle, real-time features).

## Non-goals (out of scope for this version unless explicitly added)
- **NG1**: Creating accounts with username/password (Google OAuth only).
- **NG2**: Fully offline Pokédex without internet access to PokéAPI.
- **NG3**: Competitive matchmaking, ranking ladders, or anti-cheat systems (battle system is “phase-based” and can start simple).
- **NG4**: Admin portals and moderation workflows.

## Stakeholders
- **Primary**: Student developer (project owner), course assessor/marker.
- **Secondary**: End users (trainers) who want a simple Pokédex and lightweight battling.

## Target users & key use cases
- **Authenticated trainer**: wants to build and revisit their personal collection from any device.
- **Casual browser (unauthenticated)**: wants to see a landing page and be prompted to log in to access personal features.

## Assumptions & constraints
- **A1 — Tech stack**: Flask + Flask-Login + Flask-SQLAlchemy + PostgreSQL; vanilla JS SPA and Bootstrap 5.
- **A2 — OAuth**: Google OAuth credentials are configured via `client_secrets.json` and environment variables (`.env`).
- **A3 — Deployment**: Initial development target is local (`localhost:5000`); production hardening is a later concern.
- **A4 — Data**: Pokémon canonical data is sourced from PokéAPI; DB stores references/cached key fields only.

## Current implementation (as-is)
### Frontend (SPA)
- **Shell**: `GET /` serves `webapp/templates/index.html`.
- **Views** (client-side): landing, login, authenticated home, pokedex (placeholder), battle (placeholder).
- **Auth status check**: frontend calls `GET /auth/status` during initialization to decide landing vs home.

### Backend
- **App factory**: `webapp/app.py:create_app()` configures Flask, DB, login manager, CORS.
- **Auth**: routes under `/auth/*` support Google OAuth login, callback, logout, status, profile.
- **Health**: `GET /api/health` returns version, environment, and authentication flag.
- **Database**: tables are created automatically on app start (`db.create_all()`).

### Database models (already present)
- **`User`**: stores Google identity and profile fields.
- **`UserPokemon`** (present in code, used in later phases): stores a user’s captured/added Pokémon references with a uniqueness constraint on `(user_id, pokemon_id)`.

## Scope (to-be requirements)
This section defines what the app must do beyond the current placeholders, while staying consistent with the existing architecture.

## Functional requirements
### Authentication & session
- **FR-A1**: A user can initiate Google login from the SPA and complete the OAuth flow.
- **FR-A2**: After login, the backend must create or update the `User` record (by `google_id`) and set `last_login`.
- **FR-A3**: The SPA can query the user’s auth state via `GET /auth/status`.
- **FR-A4**: A logged-in user can log out via `GET /auth/logout`, which clears the session and returns to `/`.
- **FR-A5**: Protected endpoints must require authentication (Flask-Login).

### Pokédex browsing (PokéAPI integration)
- **FR-P1**: Users can search Pokémon by name or ID.
- **FR-P2**: Users can view Pokémon detail: name, national number, official sprite, types, and base stats.
- **FR-P3**: The backend must fetch Pokémon data from PokéAPI using the configured base URL.
- **FR-P4**: API failures must return consistent JSON errors (no HTML error pages).

### Personal Pokédex (collection management)
- **FR-C1**: Authenticated users can list Pokémon in their personal Pokédex.
- **FR-C2**: Authenticated users can add a Pokémon to their personal Pokédex.
- **FR-C3**: Duplicate adds must be prevented (by unique constraint and/or application logic).
- **FR-C4**: Authenticated users can remove a Pokémon from their personal Pokédex.
- **FR-C5**: Collection list must include at minimum: `pokemon_id`, `pokemon_name`, `pokemon_number`, `added_at`.

### Battle Arena (phase-based)
Initial battle requirements can be implemented progressively; the PRD defines a minimum viable foundation first.
- **FR-B1 (MVP)**: Authenticated users can create a “battle team” by selecting Pokémon from their personal Pokédex.
- **FR-B2 (MVP)**: The UI shows a battle arena view with team selection and a placeholder battle log.
- **FR-B3 (Later)**: Turn-based battle mechanics between two trainers (local simulation or online).
- **FR-B4 (Later)**: Real-time or pseudo-real-time communication can be introduced (e.g., Socket.IO), aligned with dependencies already listed.

## API requirements (backend)
The current codebase has `/auth/*` and `/api/health`. The following API surface is required to support Pokédex features.

### Existing endpoints (must remain compatible)
- **GET `/`**: SPA shell.
- **GET `/api/health`**: JSON health payload.
- **GET `/auth/google`**: begin Google OAuth flow (redirect).
- **GET `/auth/google/callback`**: OAuth callback (redirect to `/` on success).
- **GET `/auth/logout`**: logout (redirect to `/`).
- **GET `/auth/status`**: JSON `{ authenticated: boolean, user?: {...} }`.
- **GET `/auth/profile`**: JSON user profile (auth required).

### Required new endpoints (to implement)
Suggested REST endpoints and payloads (exact naming can vary, but behavior must match):
- **GET `/api/pokemon/search?query=<nameOrId>`**  
  - Returns: list of Pokémon summaries (id, name, sprite URL).
- **GET `/api/pokemon/<idOrName>`**  
  - Returns: Pokémon detail (id, name, number, types, stats, sprites).
- **GET `/api/me/pokedex`** (auth required)  
  - Returns: user’s `UserPokemon[]`.
- **POST `/api/me/pokedex`** (auth required)  
  - Body: `{ pokemon_id, pokemon_name, pokemon_number }` (or `{ pokemon_id }` if server derives the rest from PokéAPI).
  - Returns: added entry or a “duplicate” response.
- **DELETE `/api/me/pokedex/<pokemon_id>`** (auth required)  
  - Removes entry for that user.

## Data requirements
### Entities
- **User**
  - **Fields**: `id (UUID)`, `google_id`, `email`, `name`, `picture`, `is_active`, `created_at`, `last_login`.
  - **Rules**: `google_id` and `email` unique.
- **UserPokemon**
  - **Fields**: `id (UUID)`, `user_id (FK)`, `pokemon_id (int)`, `pokemon_name`, `pokemon_number`, `added_at`.
  - **Rules**: unique `(user_id, pokemon_id)` to prevent duplicates.

### Data integrity
- **DI1**: A `UserPokemon` record must not exist without a valid `User`.
- **DI2**: Removing a user (if ever supported) must remove their collection entries.

## UX/UI requirements
- **UX1**: The app loads into a clear landing page when unauthenticated.
- **UX2**: “Login with Google” is accessible from landing and navbar.
- **UX3**: Navbar reflects auth state (shows profile + logout when logged in).
- **UX4**: “My Pokédex” view provides:
  - search input,
  - results list/grid,
  - detail panel,
  - add/remove actions with clear feedback.
- **UX5**: Errors (e.g., PokéAPI failures) are shown inline in the SPA (not only via `alert()`).

## Security & privacy requirements
- **S1**: Session cookies are HTTPOnly; secure cookie settings are enabled in production.
- **S2**: OAuth state parameter is stored and validated to reduce CSRF risk.
- **S3**: The app must not commit secrets to source control (`client_secrets.json`, `.env`).
- **S4**: API endpoints that modify user data must require authentication.
- **S5**: Minimal personal data stored: Google id, email, name, picture, timestamps only.

## Non-functional requirements
- **NFR1 — Reliability**: `/api/health` returns JSON and indicates auth state.
- **NFR2 — Performance**: Common Pokémon detail pages should feel responsive; introduce caching if PokéAPI latency is high.
- **NFR3 — Maintainability**: Keep separation via blueprints (`auth`, `pokemon`) and shared extensions (`db`, `login_manager`).
- **NFR4 — Portability**: Works on Windows dev environments with `psycopg2-binary`.
- **NFR5 — Observability**: Log meaningful errors for auth and API calls (no sensitive token logging).

## Acceptance criteria (minimum)
- **AC1**: Unauthenticated user sees landing page and can navigate to login view.
- **AC2**: Google OAuth login creates/updates a `User` record and returns user profile in `/auth/status`.
- **AC3**: Authenticated user can view “My Pokédex” and list their saved Pokémon (not placeholders).
- **AC4**: Authenticated user can add a Pokémon by selecting from search results; duplicates are prevented.
- **AC5**: Authenticated user can remove a Pokémon and see the UI update.
- **AC6**: Backend returns consistent JSON errors for API endpoints (4xx/5xx) and rolls back DB sessions on 500s.

## Delivery phases (suggested, aligned with existing placeholders)
- **Phase 0 (done)**: SPA shell + Google OAuth + user persistence.
- **Phase 1 (next)**: PokéAPI integration + Pokémon search + detail endpoints + “My Pokédex” real UI.
- **Phase 2**: Collection enhancements (pagination, filters, cached sprites), improved error handling UX.
- **Phase 3**: Battle Arena implementation (team selection → local simulation → online battle), optional Socket.IO.

## Open questions (to decide during implementation)
- **OQ1**: Will `/api/me/pokedex` accept only `pokemon_id` and have the server fetch name/number, or will the client pass cached fields?
- **OQ2**: What battle model is required for assessment (local simulation vs online real-time)?
- **OQ3**: Should Pokémon data be cached in DB to reduce PokéAPI calls (and if so, what TTL/fields)?

