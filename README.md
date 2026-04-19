# Pokédex Web App v2.0

A single-page web application for browsing Pokémon via the PokéAPI, managing a personal Pokémon collection ("My Pokéball"), and preparing for turn-based battles. Built with a Flask backend, PostgreSQL database, Google OAuth authentication, and a vanilla JavaScript frontend.


---

## Tech Stack

| Layer       | Technology                                          |
| ----------- | --------------------------------------------------- |
| Backend     | Flask 3.0, Flask-Login, Flask-SQLAlchemy            |
| Database    | PostgreSQL (via psycopg2-binary, SQLAlchemy 2.0)    |
| Frontend    | Vanilla ES6 JavaScript, Bootstrap 5                 |
| Auth        | Google OAuth 2.0 (google-auth-oauthlib)             |
| Pokémon Data| [PokéAPI](https://pokeapi.co/api/v2) (live requests)|

---

## Prerequisites

- **Python 3.10+**
- **PostgreSQL** installed and running
- A **Google Cloud** project with OAuth 2.0 credentials (Client ID and Client Secret)
- A PostgreSQL database created for the app (e.g. `pokedex_v2_dev`)

---

## Installation

1. **Clone the repository** and navigate to the project directory:


2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google OAuth credentials:**

   Place your `client_secrets.json` file (downloaded from Google Cloud Console) in the project root (`A3/client_secrets.json`).

5. **Create the `.env` file** in the project root (see [Environment Variables](#environment-variables) below).

6. **Run the app:**

   ```bash
   python webapp/app.py
   ```

   > Database tables are created automatically on startup via `db.create_all()` in `create_app()`.

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=postgresql://username:password@localhost/pokedex_v2_dev

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# PokéAPI (optional — defaults to https://pokeapi.co/api/v2)
POKEAPI_BASE_URL=https://pokeapi.co/api/v2

# Session (optional)
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_SAMESITE=Lax
```

> **Important:** Never commit `.env` or `client_secrets.json` to source control.

---

## How to Run

### Development

```bash
python webapp/app.py
```

The app starts on [http://localhost:5000](http://localhost:5000) with debug mode enabled.

### Production

Set the environment to production in your `.env`:

```env
FLASK_ENV=production
SESSION_COOKIE_SECURE=True
```

Then run with a production WSGI server (e.g. Gunicorn — not included in `requirements.txt`; add as needed):

```bash
pip install gunicorn
gunicorn "webapp.app:create_app()" --bind 0.0.0.0:5000
```

> In production, `DEBUG` is disabled, `SESSION_COOKIE_SECURE` is enforced, and `SQLALCHEMY_ECHO` logs SQL queries (inherited from base config).

---

## Project Structure

```
├── config.py                  # Flask configuration (Dev / Test / Prod)
├── requirements.txt           # Python dependencies
├── client_secrets.json        # Google OAuth credentials (not committed)
├── .env                       # Environment variables (not committed)
├── .gitignore
├── Pokedex_PRD_v2.md          # Project Requirements Document
├── README.md
│
└── webapp/
    ├── app.py                 # Flask application factory (create_app)
    ├── extensions.py          # Shared Flask extensions (db, login_manager)
    │
    ├── models/
    │   ├── user.py            # User model (Google OAuth, UUID PK)
    │   └── pokemon.py         # UserPokemon model (personal collection)
    │
    ├── routes/
    │   ├── auth.py            # Google OAuth login/logout/status routes
    │   ├── pokemon.py         # PokéAPI browsing + My Pokéball CRUD routes
    │   └── battle.py          # Battle opponent generation + team hydration
    │
    ├── utils/
    │   ├── db_helpers.py      # Shared DB utilities (get_or_create)
    │   └── pokeapi.py         # Shared PokéAPI helper functions
    │
    ├── templates/
    │   └── index.html         # SPA shell (single HTML entry point)
    │
    └── static/
        ├── css/
        │   └── style.css      # Custom styles (Pokéball theme, battle arena)
        ├── js/
        │   └── app.js         # SPA logic (PokemonAppV2 class)
        └── images/
            ├── pokeball.png
            ├── landing.gif
            ├── battle.jpg
            └── arena.webp
```

---

## API Overview

### Authentication

| Method | Path                     | Auth Required | Description                                      |
| ------ | ------------------------ | ------------- | ------------------------------------------------ |
| GET    | `/auth/google`           | No            | Initiates Google OAuth login flow                |
| GET    | `/auth/google/callback`  | No            | OAuth callback — creates/updates user, redirects |
| GET    | `/auth/logout`           | Yes           | Clears session and redirects to `/`              |
| GET    | `/auth/status`           | No            | Returns `{ authenticated, user? }` JSON          |
| GET    | `/auth/profile`          | Yes           | Returns current user's profile JSON              |

### Pokémon Browsing (PokéAPI proxy)

| Method | Path                              | Auth Required | Description                                        |
| ------ | --------------------------------- | ------------- | -------------------------------------------------- |
| GET    | `/api/pokemon/default?limit=12`   | No            | Returns a default list of Pokémon (1–24)           |
| GET    | `/api/pokemon/search?query=<q>`   | No            | Searches Pokémon by name or ID via PokéAPI         |
| GET    | `/api/pokemon/<idOrName>`         | No            | Returns full Pokémon detail (types, stats, sprite) |

### My Pokéball (Personal Collection)

| Method | Path                              | Auth Required | Description                                        |
| ------ | --------------------------------- | ------------- | -------------------------------------------------- |
| GET    | `/api/me/pokeball`                | Yes           | Lists user's saved Pokémon (max 5)                 |
| POST   | `/api/me/pokeball`                | Yes           | Adds a Pokémon. Body: `{ "pokemon_id": <int> }`   |
| DELETE  | `/api/me/pokeball/<pokemon_id>`  | Yes           | Removes a Pokémon from the user's collection       |

### Utility

| Method | Path           | Auth Required | Description                                |
| ------ | -------------- | ------------- | ------------------------------------------ |
| GET    | `/`            | No            | Serves the SPA shell (`index.html`)        |
| GET    | `/api/health`  | No            | Health check with version and auth status  |

---

## Data Models

### User

| Field        | Type         | Description                      |
| ------------ | ------------ | -------------------------------- |
| `id`         | UUID (PK)    | Auto-generated primary key       |
| `google_id`  | String       | Unique Google account identifier |
| `email`      | String       | User email (unique)              |
| `name`       | String       | Display name from Google         |
| `picture`    | String       | Profile picture URL              |
| `is_active`  | Boolean      | Account active flag              |
| `created_at` | DateTime     | First login timestamp (UTC)      |
| `last_login` | DateTime     | Most recent login timestamp      |

### UserPokemon

| Field            | Type         | Description                              |
| ---------------- | ------------ | ---------------------------------------- |
| `id`             | UUID (PK)    | Auto-generated primary key               |
| `user_id`        | UUID (FK)    | References `users.id`                    |
| `pokemon_id`     | Integer      | PokéAPI Pokémon ID                       |
| `pokemon_name`   | String       | Cached Pokémon name                      |
| `pokemon_number` | Integer      | Cached national Pokédex number           |
| `added_at`       | DateTime     | Timestamp when added to collection       |

> **Constraint:** Unique `(user_id, pokemon_id)` — each user can only add a Pokémon once. Maximum 5 Pokémon per user enforced at the application level.

---

## License
Personal project
