/**
 * PokemonApp - Single Page Application (SPA) for Pokédex
 * 
 * Manages all frontend state, API communication, and UI rendering.
 * This is a pure ES6 class with async/await for clean asynchronous code.
 */
class PokemonApp {
    constructor() {
        this.pokemonList = [];
        this.selectedPokemon = null;
        this.types = [];
        this.currentView = "home"; // Possible values: "home", "list", "detail", "create", "edit"
        console.log("✅ PokemonApp initialized");
    }

    /**
     * Initialize app on page load
     * 1. Load available types from API
     * 2. Load all Pokémon from API
     * 3. Render the initial home view
     */
    async init() {
        try {
            console.log("🔄 Starting app initialization...");
            await this.loadTypes();
            console.log("✅ Types loaded:", this.types);
            
            await this.loadPokemonList();
            console.log("✅ Pokémon list loaded:", this.pokemonList.length, "Pokémon");
            
            this.currentView = "home";
            this.render();
            console.log("✅ App initialization complete");
        } catch (err) {
            console.error("❌ Init failed:", err);
            this.showError("Failed to initialize app");
        }
    }

    // ===== API METHODS (async/await) =====

    /**
     * Load available types from backend
     * GET /api/types → ["Fire", "Grass"]
     */
    async loadTypes() {
        try {
            const resp = await fetch("/api/types");
            if (resp.ok) {
                this.types = await resp.json();
            } else {
                console.error("Failed to load types, status:", resp.status);
            }
        } catch (err) {
            console.error("Failed to load types:", err);
        }
    }

    /**
     * Load Pokémon list with optional filtering
     * GET /api/pokemon?q={query}&type={type}
     * 
     * @param {string} query - Optional search term (name or number)
     * @param {string} type - Optional type filter (Fire or Grass)
     */
    async loadPokemonList(query = "", type = "") {
        try {
            let url = "/api/pokemon";
            const params = new URLSearchParams();
            
            if (query.trim()) params.append("q", query.trim().toLowerCase());
            if (type.trim()) params.append("type", type.trim());
            
            if (params.toString()) url += "?" + params.toString();
            
            console.log("📡 Fetching:", url);
            const resp = await fetch(url);
            
            if (resp.ok) {
                this.pokemonList = await resp.json();
                console.log("📦 Got", this.pokemonList.length, "Pokémon");
            } else {
                console.error("Failed to load list, status:", resp.status);
            }
        } catch (err) {
            console.error("Failed to load Pokémon list:", err);
        }
    }

    /**
     * Load full details for a single Pokémon
     * GET /api/pokemon/{number}
     * 
     * @param {string} number - Pokémon national number (e.g., "0004")
     */
    async loadPokemonDetail(number) {
        try {
            console.log("📡 Fetching detail for Pokémon #" + number);
            const resp = await fetch(`/api/pokemon/${number}`);
            
            if (resp.ok) {
                this.selectedPokemon = await resp.json();
                this.currentView = "detail";
                console.log("📦 Loaded:", this.selectedPokemon.name);
            } else if (resp.status === 404) {
                this.showError(`Pokémon #${number} not found`);
            } else {
                console.error("Failed with status:", resp.status);
                this.showError("Failed to load Pokémon details");
            }
        } catch (err) {
            console.error("Failed to load Pokémon detail:", err);
            this.showError("Network error while loading Pokémon");
        }
    }

    // ===== ACTION METHODS =====

    /**
     * Show home view
     */
    showHome() {
        this.currentView = "home";
        this.render();
    }

    /**
     * Show list view (Pokédex page)
     */
    showList() {
        this.currentView = "list";
        this.render();
    }

    /**
     * Show detail view for a specific Pokémon
     * @param {string} number - Pokémon national number
     */
    async showDetail(number) {
        await this.loadPokemonDetail(number);
        this.render();
    }

    /**
     * Show create form (Phase 2)
     */
    showCreate() {
        this.currentView = "create";
        this.render();
    }

    /**
     * Apply filters from search and type dropdown
     * Reads current values from HTML inputs and filters list
     */
    async applyFilters() {
        const query = document.getElementById("search-input").value;
        const type = document.getElementById("type-filter").value;
        
        console.log("🔍 Applying filters - query:", query, "type:", type);
        await this.loadPokemonList(query, type);
        this.render();
    }

    /**
     * Show error message to user (simple alert for Phase 1)
     * @param {string} message - Error message to display
     */
    showError(message) {
        alert("❌ " + message);
    }

    // ===== RENDER METHODS =====

    /**
     * Main render dispatcher
     * Clears #app and renders appropriate view based on currentView
     */
    render() {
        const app = document.getElementById("app");
        app.innerHTML = "";
        
        console.log("🎨 Rendering view:", this.currentView);

        if (this.currentView === "home") {
            app.appendChild(this.renderHome());
        } else if (this.currentView === "list") {
            app.appendChild(this.renderList());
        } else if (this.currentView === "detail") {
            app.appendChild(this.renderDetail());
        } else if (this.currentView === "create") {
            app.appendChild(this.renderCreate());
        } else if (this.currentView === "edit") {
            app.appendChild(this.renderEdit());
        }
    }

    /**
     * Render home view with Pokéball image and welcome message
     * 
     * Features:
     * - Large Pokéball image
     * - Welcome message
     * - Call-to-action button to enter Pokédex
     */
    renderHome() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <!-- Pokéball Image -->
                <div style="margin-bottom: 40px;">
                    <img 
                        src="/static/images/pokeball.png" 
                        alt="Pokéball" 
                        style="width: 200px; height: 200px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));"
                    >
                </div>

                <!-- Welcome Text -->
                <h1 class="display-3 fw-bold" style="color: var(--pokeball-red); margin-bottom: 20px;">
                    Welcome to Your Pokédex
                </h1>
                <p class="lead text-muted" style="font-size: 1.3rem; margin-bottom: 40px;">
                    Explore, discover, and manage your Pokémon collection
                </p>

                <!-- Call-to-Action Button -->
                <button 
                    class="btn btn-primary btn-lg" 
                    style="padding: 15px 50px; font-size: 1.2rem;"
                    onclick="app.showList()"
                >
                     Enter Pokédex
                </button>

                <!-- Optional: Secondary info -->
                <div style="margin-top: 60px; padding: 30px; background-color: var(--pokeball-white); border-radius: 12px; border: 2px solid var(--pokeball-red);">
                    <h3 style="color: var(--pokeball-black); margin-bottom: 15px;">Get Started</h3>
                    <p style="color: var(--text-dark); font-size: 1rem;">
                        Click the button above to browse all available Pokémon,<br/>
                        search by name or type, and view detailed statistics.
                    </p>
                </div>
            </div>
        `;
        return div;
    }

    /**
     * Render list view with search/filter controls and Pokémon cards
     * 
     * Features:
     * - Search input (searches by name or number)
     * - Type filter dropdown (populated from API)
     * - Grid of Pokémon cards (responsive: 3 cols on desktop, 2 on tablet, 1 on mobile)
     * - Each card is clickable to show detail view
     * - Empty state message if no Pokémon
     */
    renderList() {
        const div = document.createElement("div");
        
        // Build type options HTML
        const typeOptions = this.types
            .map(t => `<option value="${t}">${t}</option>`)
            .join("");
        
        div.innerHTML = `
            <!-- Header -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold">Pokédex</h1>
                <p class="text-muted">Browse all Pokémon in your collection</p>
            </div>

            <!-- Filter Panel -->
            <div class="card mb-4 shadow-sm">
                <div class="card-body">
                    <div class="row g-3 align-items-end">
                        <!-- Search Input -->
                        <div class="col-md-6">
                            <label for="search-input" class="form-label fw-bold">🔍 Search Pokémon</label>
                            <input 
                                class="form-control form-control-lg" 
                                id="search-input" 
                                type="search" 
                                placeholder="Search by name (e.g., 'Char') or number (e.g., '0004')..."
                                onkeypress="if(event.key==='Enter') app.applyFilters();"
                            >
                        </div>

                        <!-- Type Filter Dropdown -->
                        <div class="col-md-3">
                            <label for="type-filter" class="form-label fw-bold">🔥❄️ Filter by Type</label>
                            <select class="form-select form-select-lg" id="type-filter">
                                <option value="">All Types</option>
                                ${typeOptions}
                            </select>
                        </div>

                        <!-- Action Buttons -->
                        <div class="col-md-3">
                            <button 
                                class="btn btn-primary btn-lg w-100" 
                                onclick="app.applyFilters()"
                            >
                                🔍 Filter
                            </button>
                            <button 
                                class="btn btn-success btn-lg w-100 mt-2" 
                                onclick="app.showCreate()"
                            >
                                ➕ New Pokémon
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pokémon Grid -->
            <div class="row g-4" id="pokemon-grid">
                ${this.pokemonList.length === 0 
                    ? `<div class="col-12">
                        <div class="alert alert-info text-center py-5">
                            <h5>No Pokémon found</h5>
                            <p class="text-muted mb-0">Try adjusting your search or filters</p>
                        </div>
                       </div>`
                    : this.pokemonList.map(p => `
                        <!-- Pokémon Card -->
                        <div class="col-md-6 col-lg-4 col-xl-3">
                            <div 
                                class="card h-100 shadow-sm pokemon-card" 
                                style="cursor: pointer; border-radius: 12px;" 
                                onclick="app.showDetail('${p.number}')"
                            >
                                <!-- Card Header with Number -->
                                <div class="card-header bg-gradient text-white" style="background-color: var(--pokeball-red); border: none;">
                                    <h5 class="mb-0">#${p.number}</h5>
                                </div>

                                <!-- Card Body -->
                                <div class="card-body text-center">
                                    <h5 class="card-title fw-bold">${p.name}</h5>
                                    <span class="badge bg-info mb-3">${p.type}</span>
                                    
                                    <!-- Quick Stats -->
                                    <div class="mt-3">
                                        <small class="text-muted d-block">
                                            <strong>HP:</strong> ${p.hp}
                                        </small>
                                        <small class="text-muted d-block">
                                            <strong>ATK:</strong> ${p.attack}
                                        </small>
                                        <small class="text-muted d-block">
                                            <strong>DEF:</strong> ${p.defense}
                                        </small>
                                    </div>
                                </div>

                                <!-- Card Footer (Click hint) -->
                                <div class="card-footer bg-light border-top text-center">
                                    <small class="text-muted">Click to view details →</small>
                                </div>
                            </div>
                        </div>
                    `).join("")
                }
            </div>
        `;
        
        return div;
    }

    /**
     * Render detail view for a single Pokémon
     * 
     * Features:
     * - Back button to return to list
     * - Pokémon name, number, type, species
     * - Physical info (height, weight)
     * - Abilities list
     * - Stats table with progress bars
     * - Total stats
     * - Edit/Delete buttons (Phase 2)
     * - Placeholder for charts (Phase 4)
     */
    renderDetail() {
        const p = this.selectedPokemon;
        if (!p) {
            const div = document.createElement("div");
            div.innerHTML = `<p>Loading...</p>`;
            return div;
        }

        const div = document.createElement("div");
        
        // Calculate stat percentages for progress bars (max 200)
        const getStatPercent = (stat) => (stat / 200) * 100;

        div.innerHTML = `
            <!-- Back Button -->
            <div class="mb-4">
                <button 
                    class="btn btn-outline-secondary btn-lg" 
                    onclick="app.showList()"
                >
                    ← Back to Pokédex
                </button>
            </div>

            <!-- Two-Column Layout -->
            <div class="row">
                <!-- Left Column: Basic Info & Abilities -->
                <div class="col-lg-4 mb-4">
                    <!-- Pokémon Card -->
                    <div class="card shadow-sm mb-4" style="border-radius: 12px; border: none;">
                        <div class="card-body text-center">
                            <h2 class="fw-bold mb-2">${p.name}</h2>
                            <p class="text-muted mb-3">
                                <span class="badge bg-dark">#${p.number}</span>
                            </p>
                            <span class="badge bg-info p-2 fs-6">${p.type}</span>
                            
                            <!-- Physical Info -->
                            <div class="mt-4 p-3 bg-light rounded">
                                <p class="mb-2">
                                    <strong>Species:</strong><br/>
                                    ${p.species}
                                </p>
                                <p class="mb-2">
                                    <strong>Height:</strong><br/>
                                    ${p.height_m} m
                                </p>
                                <p class="mb-0">
                                    <strong>Weight:</strong><br/>
                                    ${p.weight_kg} kg
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Abilities Card -->
                    <div class="card shadow-sm" style="border-radius: 12px; border: none;">
                        <div class="card-header bg-primary text-white" style="border-radius: 12px 12px 0 0;">
                            <h5 class="mb-0">⚡ Abilities</h5>
                        </div>
                        <div class="card-body">
                            ${p.abilities.length > 0
                                ? p.abilities.map(a => `
                                    <span class="badge bg-secondary p-2 d-block mb-2">
                                        ${a}
                                    </span>
                                  `).join("")
                                : '<p class="text-muted mb-0">No abilities recorded</p>'
                            }
                        </div>
                    </div>
                </div>

                <!-- Right Column: Stats -->
                <div class="col-lg-8">
                    <div class="card shadow-sm" style="border-radius: 12px; border: none;">
                        <div class="card-header bg-danger text-white" style="border-radius: 12px 12px 0 0;">
                            <h5 class="mb-0">📊 Base Stats</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <tbody>
                                        <!-- HP Row -->
                                        <tr>
                                            <td class="fw-bold" style="width: 20%;">HP</td>
                                            <td style="width: 60%;">
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.hp)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.hp}</td>
                                        </tr>

                                        <!-- Attack Row -->
                                        <tr>
                                            <td class="fw-bold">ATK</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.attack)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.attack}</td>
                                        </tr>

                                        <!-- Defense Row -->
                                        <tr>
                                            <td class="fw-bold">DEF</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.defense)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.defense}</td>
                                        </tr>

                                        <!-- Sp. Atk Row -->
                                        <tr>
                                            <td class="fw-bold">SP.A</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.sp_atk)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.sp_atk}</td>
                                        </tr>

                                        <!-- Sp. Def Row -->
                                        <tr>
                                            <td class="fw-bold">SP.D</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.sp_def)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.sp_def}</td>
                                        </tr>

                                        <!-- Speed Row -->
                                        <tr>
                                            <td class="fw-bold">SPE</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar" 
                                                        style="width: ${getStatPercent(p.stats.speed)}%; background-color: var(--pokeball-red);"
                                                    ></div>
                                                </div>
                                            </td>
                                            <td class="text-end fw-bold">${p.stats.speed}</td>
                                        </tr>

                                        <!-- Total Row (highlighted) -->
                                        <tr class="table-dark" style="background-color: #2C3E50 !important;">
                                            <td class="fw-bold text-white">TOTAL</td>
                                            <td colspan="2" class="text-end">
                                                <strong class="fs-5 text-white">${p.stats.total}</strong>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- Action Buttons (Phase 2+) -->
                    <div class="mt-4">
                        <button 
                            class="btn btn-warning btn-lg w-100" 
                            onclick="alert('Edit coming in Phase 2')"
                        >
                            ✏️ Edit Stats
                        </button>
                        <button 
                            class="btn btn-danger btn-lg w-100 mt-2" 
                            onclick="alert('Delete coming in Phase 2')"
                        >
                            🗑️ Delete Pokémon
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return div;
    }

    /**
     * Render create form (Phase 2 placeholder)
     * Shows a message that this is coming in Phase 2
     */
    renderCreate() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="mb-4">
                <button 
                    class="btn btn-outline-secondary btn-lg" 
                    onclick="app.showList()"
                >
                    ← Back to Pokédex
                </button>
            </div>

            <div class="card shadow-sm" style="border-radius: 12px; max-width: 600px; margin: 0 auto; border: none;">
                <div class="card-header bg-success text-white" style="border-radius: 12px 12px 0 0;">
                    <h5 class="mb-0">➕ Create New Pokémon</h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <strong>Coming in Phase 2!</strong><br/>
                        Create form implementation will be added in the next phase.
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    /**
     * Render edit form (Phase 2 placeholder)
     */
    renderEdit() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="alert alert-info">
                <strong>Edit form coming in Phase 2</strong>
            </div>
            <button class="btn btn-secondary" onclick="app.showList()">Back</button>
        `;
        return div;
    }
}

// ===== APP INITIALIZATION =====

/**
 * Global app instance
 */
let app;

/**
 * Initialize app when DOM is fully loaded
 * This is the entry point for the entire application
 */
document.addEventListener("DOMContentLoaded", () => {
    console.log("🌐 DOM loaded, initializing PokemonApp...");
    app = new PokemonApp();
    app.init();
});
