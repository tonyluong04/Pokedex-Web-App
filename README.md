# Pokédex Web App
A full-stack web app for browsing and managing Pokémon data. Built with Flask (Python backend) and Vanilla JavaScript (frontend SPA).

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Modern web browser

### Installation & Running

```bash
# 1. Navigate to webapp directory
cd webapp

# 2. Install dependencies
pip install -r ../requirements.txt

# 3. Run Flask development server
python app.py

# 4. Open browser
# Visit http://localhost:5000
```

The app will start on `http://localhost:5000` with debug mode enabled (auto-reload on code changes).

---

## Project Structure

```
A3/
├── README.md              ← You are here
├── PHASES.md              ← Detailed phase documentation
├── requirements.txt       ← Python dependencies
├── A3.py                  ← Domain logic (Pokémon classes, Pokedex)
├── pokemon.json           ← Data file (persisted Pokémon)
└── webapp/
    ├── app.py             ← Flask REST API backend
    ├── static/
    │   ├── css/
    │   │   └── style.css  ← Pokéball theme styling
    │   ├── js/
    │   │   └── app.js     ← Frontend SPA (PokemonApp class)
    │   └── images/
    │       └── pokeball.png
    └── templates/
        └── index.html     ← Single HTML template
```

---

## Features by Phase

### ✅ Phase 1: Core Display & Navigation (Complete)
- **Homepage** - Welcome screen with Pokéball image
- **List View** - Browse all Pokémon as cards (responsive grid)
- **Detail View** - See full stats, abilities, physical info
- **Search** - Find Pokémon by name or number (partial match)
- **Filter** - Filter by type (Fire/Grass)
- **Responsive Design** - Works on mobile, tablet, desktop
- **Professional UI** - Pokéball color theme (red/white/black)

### 🔄 Phase 2: CRUD Operations (Upcoming)
- Create new Pokémon (form validation)
- Edit existing Pokémon stats
- Delete Pokémon (with confirmation)
- Form validation (client + server)
- File persistence (auto-save to JSON)

### Phase 3-5: Advanced Features (Planned)
- Advanced filtering & sorting
- Stats visualization (charts)
- Turn-based battle mode

---

## How It Works

### Architecture
```
Browser (JavaScript SPA) ←→ Flask Server (REST API) ←→ JSON File
```

**Data Flow:**
1. User opens app → HTML loads → JavaScript initializes
2. App fetches `/api/types` and `/api/pokemon` → populates state
3. User interacts (search, click card, etc.)
4. JavaScript makes API request (GET, POST, PUT, DELETE)
5. Flask processes → accesses Pokedex → returns JSON
6. JavaScript updates state & DOM
7. User sees new view

### Key Technologies
- **Frontend:** Vanilla JavaScript (ES6 classes), HTML5, CSS3, Bootstrap 5
- **Backend:** Flask 3.0.0 (Python web framework)
- **Styling:** Custom CSS with Pokéball color theme
- **Data:** JSON file (pokemon.json)
- **Visualization:** Matplotlib, NumPy (Phase 4)

---

## API Reference

### GET `/api/types`
Returns available Pokémon types.
```
Response: ["Fire", "Grass"]
```

### GET `/api/pokemon`
Returns filtered Pokémon list.
```
Query Parameters:
  ?q=char          - Search by name or number
  ?type=Fire       - Filter by type

Response: [{number, name, type, hp, attack, defense}, ...]
```

### GET `/api/pokemon/<number>`
Returns full Pokémon details.
```
Example: GET /api/pokemon/0004

Response: {
  number: "0004",
  name: "Charmander",
  type: "Fire",
  species: "Lizard Pokemon",
  height_m: 0.6,
  weight_kg: 10.0,
  abilities: ["Blaze"],
  stats: {hp, attack, defense, sp_atk, sp_def, speed, total}
}
```

**See PHASES.md for complete API documentation and Phase 2+ endpoints.**

---

## Development

### Browser Console (F12)
```javascript
// Check app state
app.pokemonList
app.selectedPokemon
app.currentView

// Test API manually
fetch("/api/pokemon?type=Fire")
  .then(r => r.json())
  .then(console.log)
```

### Adding a New View
1. Add `renderNewView()` method to `PokemonApp` class
2. Add case to `render()` dispatcher
3. Add action method `showNewView()`
4. Update navbar link if needed

### Code Style
- **JavaScript:** ES6 classes, async/await, JSDoc comments
- **Python:** Type hints, docstrings, PEP 8
- **CSS:** CSS variables for colors, semantic class names

---

## Current Status

✅ **Phase 1 Complete** - Core display & navigation working

**What works:**
- All 5 Pokémon display correctly
- Search/filter functional
- Detail view shows complete stats
- Responsive design tested
- No console errors

---

## Testing

Run the app and verify:
```
1. Navigate to http://localhost:5000
2. See homepage with Pokéball image
3. Click "Enter Pokédex" → see list of 5 cards
4. Search "char" → Charmander + Charmeleon appear
5. Filter "Fire" → only Fire types show
6. Click card → detail view loads with stats
7. Click back → returns to list
8. Resize window → layout adapts (responsive)
```

---

## Troubleshooting

**"No such file or directory: 'pokemon.json'"**
- Ensure `pokemon.json` is in `A3/` (project root)
- Not in `webapp/` folder

**"Module 'A3' not found"**
- Flask path includes parent directory
- Check `sys.path.insert(0, PARENT_DIR)` in `app.py`

**API returns 404**
- Check Pokémon number format (should be "0004" not "4")
- Verify pokemon.json has correct data

**Styling looks wrong**
- Clear browser cache (Ctrl+Shift+Delete)
- Check CSS file is loading (Network tab in DevTools)

---

## Resources & Documentation

- **PHASES.md** - Phase-by-phase breakdown with key concepts
- **ARCHITECTURE.md** - Technical deep dives (future)
- Flask Docs: https://flask.palletsprojects.com/
- Bootstrap 5: https://getbootstrap.com/
- MDN Web Docs: https://developer.mozilla.org/

---

## Author
CSIT121 Assignment A3

## License
Educational use only