# Pokédex Web App - Phase Documentation

## Overview

This document describes each phase of the Pokédex project, including objectives, key concepts, deliverables, and important decisions made.

**Total Project Timeline:** ~11-12 hours  
**Current Status:** ✅ Phase 1 Complete

---

## Phase 0: Environment & Setup ✅

### Objectives
- Establish project structure
- Install and configure dependencies
- Create development environment

### What Was Accomplished
- ✅ Project folders organized (webapp/, static/, templates/)
- ✅ Dependencies specified in requirements.txt
- ✅ Flask app structure with routing
- ✅ Jinja2 templating configured
- ✅ Python module imports resolved
- ✅ Static assets (CSS, JS, images) directory setup

### Key Concepts Introduced

**Project Structure Separation:**
- Frontend assets (CSS, JS, images) in `static/`
- HTML templates in `templates/`
- Backend logic in `app.py`
- Domain models in `A3.py`
- Data persistence in `pokemon.json`

**Development Workflow:**
- Flask debug mode = auto-reload on code changes
- Browser DevTools for JavaScript debugging
- Console logs for execution tracing

---

## Phase 1: Core Display & Navigation ✅

### Objectives
- Implement Single Page Application (SPA) frontend
- Set up Flask REST API backend
- Create list and detail views
- Build professional UI with Pokéball theme

### What Was Accomplished

#### 1.1 Frontend Architecture (app.js)
- **PokemonApp Class:** Encapsulates all frontend state and logic
- **State Management:** Centralized in class properties
- **Async/Await:** Clean asynchronous code for API calls
- **Dynamic Rendering:** Template literals for HTML generation
- **Event Handling:** Onclick handlers for navigation and filtering

#### 1.2 Backend API (app.py)
- **4 REST Endpoints:** GET /api/types, GET /api/pokemon, GET /api/pokemon/<number>, GET /
- **Singleton Pattern:** Pokedex.get_instance() ensures single instance
- **JSON Persistence:** pokemon.json is single source of truth
- **Error Handling:** Proper HTTP status codes (200, 404)
- **Helper Functions:** _ensure_dex_loaded(), _pokemon_to_dict()

#### 1.3 Responsive UI (index.html + style.css)
- **Bootstrap 5:** Pre-built components and responsive grid
- **Pokéball Color Theme:** Red #DC143C, White #FFFFFF, Black #1A1A1A
- **Mobile-First Design:** 1-column mobile → 3-column desktop
- **Professional Styling:** Cards, buttons, progress bars, badges
- **Accessibility:** Focus states, keyboard navigation, semantic HTML

#### 1.4 Views Implemented
- **Home View:** Welcome screen with Pokéball image and CTA button
- **List View:** Card grid with search and type filter
- **Detail View:** Full Pokémon info with stats table and progress bars
- **Create/Edit Placeholders:** Ready for Phase 2

### Key Concepts Explained

#### A. Single Page Application (SPA)
**What it is:** One HTML page that dynamically renders different views without page reloads.

**Why it matters:**
- Fast, responsive experience (no page flicker)
- Desktop app-like feel
- Single source of truth for state

**Flow:**
```
User interaction → JS handler → API call → State update → DOM render
```

#### B. REST API (Representational State Transfer)
**What it is:** Server provides endpoints that return JSON based on HTTP methods.

**Phase 1 Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Serve HTML shell |
| GET | `/api/types` | Get ["Fire", "Grass"] |
| GET | `/api/pokemon` | Get filtered list |
| GET | `/api/pokemon/<number>` | Get full details |

**Why this matters:**
- Clean separation: frontend (display) vs backend (logic)
- Stateless: each request is independent
- Scalable: can be used by mobile, web, desktop apps

#### C. State Management
The `PokemonApp` class holds all frontend state:
```javascript
this.pokemonList = []        // All Pokémon
this.selectedPokemon = null  // Currently viewing
this.types = []              // Fire, Grass
this.currentView = "home"    // Page mode
```

**Why it matters:** Single source of truth prevents bugs from inconsistent data.

#### D. Async/Await Pattern
```javascript
async showDetail(number) {
    await this.loadPokemonDetail(number)  // Wait for API
    this.render()                         // Then update UI
}
```

**Why it matters:** Network requests don't freeze the UI.

#### E. Data Flow
```
PAGE LOAD
├─ init()
├─ loadTypes()              → GET /api/types
├─ loadPokemonList()        → GET /api/pokemon
└─ render()                 → Show home view

USER SEARCHES "char"
├─ applyFilters()
├─ loadPokemonList("char")  → GET /api/pokemon?q=char
└─ render()                 → Update card grid

USER CLICKS CARD
├─ showDetail("0004")
├─ loadPokemonDetail()      → GET /api/pokemon/0004
├─ render()                 → Show detail view
```

### Important Design Decisions

**1. Pokéball Color Theme**
- Red `#DC143C` - Primary actions, accents
- White `#FFFFFF` - Backgrounds, text
- Black `#1A1A1A` - Headers, contrast

**Why:** Creates visual identity tied to Pokémon brand.

**2. Bootstrap 5 for Grid System**
- `col-md-6 col-lg-4 col-xl-3` - Responsive card layout
- Pre-built components (cards, buttons, alerts)
- Mobile-first approach

**Why:** Speeds up development, ensures consistency, guaranteed responsiveness.

**3. Singleton Pattern for Pokedex**
```python
dex = Pokedex.get_instance()  # Always same instance
```

**Why:** All Flask routes access same data, prevents duplicates, ensures consistency.

**4. JSON as Database**
- `pokemon.json` is the single source of truth
- Loaded once per app startup
- Simple debugging and transparency

**Why:** Meets assignment requirements, no SQL complexity, easy to inspect.

**5. Vanilla JavaScript (No Frameworks)**
- Pure ES6 classes
- No jQuery, React, Vue, etc.

**Why:** Meets course requirements, simpler debugging, full control.

### Common Patterns Used

#### Template Literals
```javascript
const html = `
    <div>
        <h1>${p.name}</h1>
        <p>${p.species}</p>
    </div>
`;
```

**Why:** Cleaner HTML generation than string concatenation.

#### Array Map/Filter
```javascript
const typeOptions = this.types
    .map(t => `<option value="${t}">${t}</option>`)
    .join("");
```

**Why:** Functional programming, less imperative code.

#### Conditional Rendering
```javascript
${this.pokemonList.length === 0 
    ? '<div>No results</div>'
    : this.pokemonList.map(...)
}
```

**Why:** Simple if/else in templates.

### Testing Checklist (Verify Phase 1)

When you return to this project, run through these tests:

- [ ] Page loads showing home with Pokéball image
- [ ] Click "Enter Pokédex" → shows list of 5 cards
- [ ] Search "char" → shows Charmander + Charmeleon only
- [ ] Filter "Fire" → shows only Fire types (Charmander, Vulpix)
- [ ] Filter "Grass" → shows only Grass types (Bulbasaur, Oddish, Ivysaur)
- [ ] Click card → shows detail view with all 6 stats
- [ ] Back button → returns to list
- [ ] Navbar responsive (hamburger menu on mobile)
- [ ] Card grid responsive (1 col mobile, 3 cols desktop)
- [ ] No console errors
- [ ] Network tab shows GET requests (not 404s)

---

## Phase 2: CRUD Operations (Planned)

### Objectives
- Implement Create (POST)
- Implement Update (PUT)
- Implement Delete (DELETE)
- Add form validation
- Persist changes to JSON

### Key Concepts (Preview)

**Form Validation**
```javascript
// Client-side: prevent bad submission
if (!Validator.valid_name(name)) {
    alert("Name must be letters only");
    return;
}

// Server-side: never trust client
@app.route("/api/pokemon", methods=["POST"])
def api_create_pokemon():
    if not Validator.valid_name(name):
        return jsonify({"error": "..."}), 400
```

**Why both?**
- Client: fast feedback, better UX
- Server: security (user can disable JS)

**HTTP Status Codes**
- `200 OK` - Success
- `201 Created` - Resource made
- `400 Bad Request` - Validation failed
- `404 Not Found` - Doesn't exist

**API Endpoints (Phase 2)**
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/pokemon` | Create new |
| PUT | `/api/pokemon/<number>` | Update entire |
| PATCH | `/api/pokemon/<number>/stats` | Update just stats |
| DELETE | `/api/pokemon/<number>` | Remove |

### What Will Be Added

**Create Form View:**
- Input fields for all Pokémon attributes
- Type dropdown (Fire/Grass)
- Stats fields (HP, Attack, Defense, etc.)
- Submit button (POST to `/api/pokemon`)
- Cancel button (back to list)

**Edit Form View:**
- Pre-filled with current Pokémon data
- Read-only fields (Number, Type)
- Editable stats
- Submit button (PUT to `/api/pokemon/<number>`)

**Delete Confirmation:**
- Modal dialog asking for confirmation
- Yes button (DELETE to `/api/pokemon/<number>`)
- No button (cancel)

**File Persistence:**
- After POST: `dex.add(p)` → auto-calls `dex.save_json()`
- After PUT: `dex.save_json()` explicitly called
- After DELETE: `dex.remove_by_national_no()` → auto-calls `dex.save_json()`

---

## Phase 3: Advanced Filtering (Planned)

### Objectives
- Add height/weight range filters
- Add sorting (by name, HP, total, etc.)
- Persist filter state
- Enhanced UX with filter indicators

### Key Concepts (Preview)

**Query Parameters:**
```
GET /api/pokemon?q=char&type=Fire&sort=attack&height_min=0.5&height_max=1.0
```

**Sorting Options:**
- Name (A-Z)
- Number (ascending)
- Type (alphabetical)
- HP / Attack / Defense / Total Stats

**Filter State:**
```javascript
this.filters = {
    query: "char",
    type: "Fire",
    heightMin: 0.5,
    heightMax: 1.0,
    sortBy: "attack"
}
```

---

## Phase 4: Stats Visualization (Planned)

### Objectives
- Generate Matplotlib charts
- Display on detail view
- Create dashboard with type comparisons

### Key Concepts (Preview)

**Chart Types:**
1. **Bar Chart** - Single Pokémon's 6 stats
2. **Line Chart** - Fire vs Grass average comparison
3. **Pie Chart** - Single Pokémon's stat distribution

**API Endpoint:**
```
GET /api/stats/chart?type=single&number=0004
```

**Implementation:**
```python
# Server-side: generate PNG, convert to Base64
img_bytes = BytesIO()
Visualizer.bar_stats_single(p, save_path=None)
plt.savefig(img_bytes, format="png")
img_base64 = base64.b64encode(img_bytes.getvalue()).decode()

# Return as data URL
return jsonify({"image": f"data:image/png;base64,{img_base64}"})

# Client-side: embed in HTML
<img src="${response.image}" />
```

---

## Phase 5: Battle Mode (Planned)

### Objectives
- Implement turn-based battle system
- Create battle UI and flow
- Add random opponent selection
- Calculate damage and declare winner

### Key Concepts (Preview)

**Battle Logic:**
1. User selects Pokémon
2. Random opponent chosen
3. User attacks (damage calculated)
4. Opponent counter-attacks
5. Repeat until HP ≤ 0
6. Winner declared

**Damage Calculation:**
```
Damage = (Attacker.Attack - Defender.Defense) * 0.5 + Random(0-10)
```

**API Endpoints (Phase 5):**
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/battle/start` | Initialize battle |
| POST | `/api/battle/<id>/turn` | Execute one turn |

---

## Architecture Overview

### Three-Tier Architecture

```
┌────────────────────────────┐
│  Presentation Layer        │
│  (Browser / JavaScript)    │
│  - PokemonApp class        │
│  - render() methods        │
│  - Event handlers          │
└─────────────┬──────────────┘
              ↕ HTTP JSON
┌────────────────────────────┐
│  Application Layer         │
│  (Flask Backend)           │
│  - Routes (@app.route)     │
│  - API endpoints           │
│  - Validation              │
└─────────────┬──────────────┘
              ↕ Object calls
┌────────────────────────────┐
│  Data Layer                │
│  (A3.py + JSON)            │
│  - Pokedex class           │
│  - BasePokemon hierarchy   │
│  - Stats, Validator, etc.  │
│  - pokemon.json file       │
└────────────────────────────┘
```

### Request-Response Cycle

```
1. FRONTEND makes HTTP request
   ├─ Method: GET/POST/PUT/DELETE
   ├─ URL: /api/pokemon or /api/pokemon/<number>
   ├─ Headers: { "Content-Type": "application/json" }
   └─ Body: JSON data (for POST/PUT)

2. FLASK receives request
   ├─ Routes request to handler
   ├─ Loads Pokedex (singleton)
   ├─ Processes request (filter, create, update, delete)
   └─ Saves changes to pokemon.json

3. FLASK returns response
   ├─ Status: 200/201/400/404
   ├─ Headers: { "Content-Type": "application/json" }
   └─ Body: JSON data or error message

4. FRONTEND receives response
   ├─ Parses JSON
   ├─ Updates app state
   ├─ Calls render()
   └─ User sees new view
```

---

## File Reference

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `app.py` | Flask routing | `_ensure_dex_loaded()`, `api_list_pokemon()`, `api_get_pokemon()` |
| `app.js` | Frontend SPA | `PokemonApp` class, `render()` methods |
| `A3.py` | Domain logic | `Pokedex`, `BasePokemon`, `Stats`, `Validator` |
| `style.css` | Styling | CSS variables, responsive grid |
| `index.html` | SPA shell | Single `<div id="app">` container |
| `pokemon.json` | Data persistence | Array of Pokémon objects |

---

## Debugging Tips

### JavaScript Console (F12)
```javascript
// Check state
console.log("Current view:", app.currentView)
console.log("Pokémon list:", app.pokemonList)

// Test API
fetch("/api/pokemon")
    .then(r => r.json())
    .then(console.log)

// Check specific Pokémon
app.pokemonList.filter(p => p.type === "Fire")
```

### Network Tab (F12)
- See all HTTP requests/responses
- Check status codes (200, 404, etc.)
- Inspect JSON payloads
- Verify headers

### Flask Console
```
POST /api/pokemon 201 -
GET /api/pokemon?type=Fire 200 -
GET /api/pokemon/0004 200 -
```

---

## Quick Reference: Adding a New Feature

### To Add a New View
1. Create `renderNewView()` method in `PokemonApp`
2. Add case to `render()` dispatcher:
   ```javascript
   } else if (this.currentView === "newview") {
       app.appendChild(this.renderNewView());
   ```
3. Create action method `showNewView()`
4. Add navbar link if needed

### To Add an API Endpoint
1. Create Flask route in `app.py`:
   ```python
   @app.route("/api/newroute", methods=["GET"])
   def api_new_route():
       # Logic here
       return jsonify(result)
   ```
2. Call from JavaScript:
   ```javascript
   const resp = await fetch("/api/newroute");
   const data = await resp.json();
   ```
3. Handle response and update state

### To Add Form Validation
1. Client-side (JavaScript):
   ```javascript
   if (!Validator.valid_name(name)) {
       alert("Invalid name!");
       return;
   }
   ```
2. Server-side (Python):
   ```python
   if not Validator.valid_name(name):
       return jsonify({"error": "..."}), 400
   ```

---

## Notes & Decisions

### Why JSON and not CSV?
- Hierarchical data (stats object within Pokémon)
- Easier to parse and serialize
- Matches Python dicts naturally
- Standard format for web APIs

### Why Singleton for Pokedex?
- Ensures all routes access same instance
- Prevents accidental duplicates
- Single source of truth
- Makes dependency injection simpler

### Why Async/Await over Promises?
- More readable syntax
- Easier error handling with try/catch
- Matches Python's async style (familiar to you)
- Looks like synchronous code

### Why Vanilla JS instead of Framework?
- Meets course requirements (CSIT121)
- Simpler debugging
- Full control over architecture
- Smaller bundle size
- Better learning opportunity

---

## Testing Workflow

### Before committing code:
1. Test in browser (http://localhost:5000)
2. Open DevTools (F12)
3. Check Console for errors
4. Check Network tab for API calls
5. Test on mobile (resize window)
6. Test each feature in the checklist

### Manual Testing:
```bash
# Terminal 1: Run Flask
cd webapp
python app.py

# Terminal 2: Test API
curl http://localhost:5000/api/types
curl http://localhost:5000/api/pokemon
curl http://localhost:5000/api/pokemon/0004
```

---

## Maintenance

### When returning to the project:
1. Read this PHASES.md document (key concepts section)
2. Run `python app.py` and verify page loads
3. Check browser console for errors
4. Run through testing checklist
5. Review code comments in app.js and app.py

### Code Quality Checklist:
- [ ] No console errors
- [ ] No trailing whitespace
- [ ] Comments explain WHY not WHAT
- [ ] Functions are under 50 lines
- [ ] Variable names are descriptive
- [ ] HTML is semantic (not divs everywhere)

---

**Last Updated:** Phase 1 Complete  
**Next Phase:** Phase 2 - CRUD Operations

For questions about any phase, refer to this document's key concepts section.