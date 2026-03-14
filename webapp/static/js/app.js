/**
 * Pokédex v2.0 - Single Page Application (SPA)
 * 
 * Personal project: Browse Pokémon via PokéAPI, manage personal Pokédex,
 * battle other users, view statistics.
 * 
 * Tech: Vanilla ES6 JavaScript, Flask REST API, PostgreSQL
 */

class PokemonAppV2 {
    constructor() {
        // User state
        this.user = null;
        this.isAuthenticated = false;
        
        // Pokémon state
        this.pokedexResults = [];   // results shown in Pokedex tab (default list or search)
        this.myPokeball = [];       // user's saved Pokémon (max 5)
        this.selectedPokemon = null; // full detail payload from /api/pokemon/<idOrName>
        this.spriteCache = {};       // pokemon_id -> sprite url

        // Pokedex UI state
        this.pokedexTab = "pokedex"; // "pokedex" | "pokeball"
        this.searchQuery = "";
        this.searchTimer = null;
        
        // UI state
        this.currentView = "landing";
        this.loading = false;
        
        console.log("✅ PokemonApp v2.0 initialized");
    }

    /**
     * Initialize app on page load
     */
    async init() {
        try {
            console.log("🔄 Starting app initialization...");
            
            // Check authentication status
            await this.checkAuthStatus();

            if (this.isAuthenticated) {
                await this.loadMyPokeball();
            }
            
            // Render initial view:
            // - If not logged in: landing page with welcome and buttons
            // - If logged in: authenticated home page
            this.currentView = this.isAuthenticated ? "home" : "landing";
            this.render();
            
            console.log("✅ App initialization complete");
        } catch (err) {
            console.error("❌ Init failed:", err);
            this.showError("Failed to initialize app");
        }
    }

    /**
     * Check if user is authenticated via /api/auth/status
     */
    async checkAuthStatus() {
        try {
            const resp = await fetch('/auth/status');
            if (resp.ok) {
                const data = await resp.json();
                if (data.authenticated && data.user) {
                    this.user = data.user;
                    this.isAuthenticated = true;
                    console.log("✅ User authenticated:", this.user.name);
                } else {
                    this.isAuthenticated = false;
                }
            } else {
                this.isAuthenticated = false;
            }
        } catch (err) {
            console.error("❌ Auth check failed:", err);
            this.isAuthenticated = false;
        }
    }

    /**
     * Logout user
     */
    logout() {
        window.location.href = '/auth/logout';
    }

    // ===== API CALLS =====

    async loadDefaultPokedex(limit = 12) {
        const resp = await fetch(`/api/pokemon/default?limit=${encodeURIComponent(limit)}`);
        if (!resp.ok) throw new Error("Failed to load default Pokémon");
        const data = await resp.json();
        this.pokedexResults = Array.isArray(data.results) ? data.results : [];
    }

    async searchPokemonByNameOrId(query) {
        const resp = await fetch(`/api/pokemon/search?query=${encodeURIComponent(query)}`);
        if (!resp.ok) throw new Error("Search failed");
        const data = await resp.json();
        this.pokedexResults = Array.isArray(data.results) ? data.results : [];
    }

    async loadPokemonDetail(idOrName) {
        const resp = await fetch(`/api/pokemon/${encodeURIComponent(idOrName)}`);
        if (!resp.ok) throw new Error("Failed to load Pokémon detail");
        this.selectedPokemon = await resp.json();
        if (this.selectedPokemon && this.selectedPokemon.id && this.selectedPokemon.sprite) {
            this.spriteCache[this.selectedPokemon.id] = this.selectedPokemon.sprite;
        }
    }

    async loadMyPokeball() {
        if (!this.isAuthenticated) return;
        const resp = await fetch("/api/me/pokeball");
        if (!resp.ok) throw new Error("Failed to load My Pokéball");
        const data = await resp.json();
        this.myPokeball = Array.isArray(data.results) ? data.results : [];
    }

    async warmPokeballSprites() {
        // Max 5 items; safe to fetch details to show sprites.
        const missing = this.myPokeball
            .map(p => Number(p.pokemon_id))
            .filter(id => id && !this.spriteCache[id]);

        if (!missing.length) return false;  // return false = nothing new

        await Promise.all(
            missing.map(async (id) => {
                try {
                    const resp = await fetch(`/api/pokemon/${encodeURIComponent(id)}`);
                    if (!resp.ok) return;
                    const d = await resp.json();
                    if (d && d.id && d.sprite) this.spriteCache[d.id] = d.sprite;
                } catch (_) {
                    // ignore sprite failures
                }
            })
        );

        return true;  // return true = new sprites were loaded
    }

    async addToPokeball(pokemonId) {
        const resp = await fetch("/api/me/pokeball", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pokemon_id: pokemonId }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.error || "Failed to add to Pokéball");
        }
        await this.loadMyPokeball();
    }

    async removeFromPokeball(pokemonId) {
        const resp = await fetch(`/api/me/pokeball/${encodeURIComponent(pokemonId)}`, { method: "DELETE" });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.error || "Failed to remove from Pokéball");
        }
        await this.loadMyPokeball();
    }

    // ===== UI HELPERS =====

    isInPokeball(pokemonId) {
        return this.myPokeball.some(p => Number(p.pokemon_id) === Number(pokemonId));
    }

    formatDexNumber(n) {
        const num = Number(n || 0);
        if (!num) return "";
        return "#" + String(num).padStart(3, "0");
    }

    typeBadge(type) {
        const t = (type || "").toLowerCase();
        const map = {
            fire: "bg-danger",
            water: "bg-primary",
            grass: "bg-success",
            electric: "bg-warning text-dark",
            poison: "bg-purple",
            flying: "bg-info",
            bug: "bg-success",
            normal: "bg-secondary",
            ground: "bg-warning text-dark",
            rock: "bg-secondary",
            psychic: "bg-info",
            ice: "bg-info",
            dragon: "bg-danger",
            dark: "bg-dark",
            steel: "bg-secondary",
            fairy: "bg-danger",
            fighting: "bg-danger",
            ghost: "bg-dark",
        };
        return map[t] || "bg-secondary";
    }

    renderPokemonCard(p, { showAddButton = true, context = "pokedex" } = {}) {
        const id = p.id ?? p.pokemon_id;
        const name = p.name ?? p.pokemon_name ?? "";
        const number = p.number ?? p.pokemon_number ?? id;
        const sprite = p.sprite || "";
        const inBall = this.isInPokeball(id);

        const col = document.createElement("div");
        col.className = "col";

        col.innerHTML = `
            <div class="pokemon-card card text-center shadow-sm h-100" data-pokemon-id="${id}">
                <div class="card-body py-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-dark">${this.formatDexNumber(number)}</span>
                    </div>
                    <div class="mb-2" style="min-height: 72px;">
                        ${sprite ? `<img src="${sprite}" alt="${name}" style="width:72px;height:72px; image-rendering: pixelated;">` : ""}
                    </div>
                    <div class="fw-bold text-capitalize">${name}</div>
                    <div class="mt-2 d-grid gap-2">
                        ${
                            showAddButton
                                ? (inBall
                                    ? `<button class="btn btn-outline-secondary btn-sm" data-action="remove">Remove</button>`
                                    : `<button class="btn btn-primary btn-sm" data-action="add">Add to Pokéball</button>`)
                                : ``
                        }
                    </div>
                </div>
            </div>
        `;

        const card = col.querySelector("[data-pokemon-id]");
        card.onclick = async (e) => {
            const btn = e.target.closest("button");
            if (btn) return; // handled below
            try {
                await this.loadPokemonDetail(id);
                this.render();
            } catch (err) {
                this.showError(err.message || "Failed to load details");
            }
        };

        const addBtn = col.querySelector('button[data-action="add"]');
        if (addBtn) {
            addBtn.onclick = async (e) => {
                e.stopPropagation();
                try {
                    await this.addToPokeball(id);
                    // keep detail panel in sync
                    if (this.selectedPokemon && Number(this.selectedPokemon.id) === Number(id)) {
                        // no-op; state already updated via loadMyPokeball
                    }
                    this.render();
                } catch (err) {
                    this.showError(err.message || "Add failed");
                }
            };
        }

        const removeBtn = col.querySelector('button[data-action="remove"]');
        if (removeBtn) {
            removeBtn.onclick = async (e) => {
                e.stopPropagation();
                try {
                    await this.removeFromPokeball(id);
                    this.render();
                } catch (err) {
                    this.showError(err.message || "Remove failed");
                }
            };
        }

        return col;
    }

    renderDetailPanel() {
        const d = this.selectedPokemon;
        const wrap = document.createElement("div");

        if (!d) {
            wrap.innerHTML = `
                <div class="card h-100">
                    <div class="card-header"><strong>Pokémon Details</strong></div>
                    <div class="card-body text-muted">
                        Click a Pokémon card to view its stats here.
                    </div>
                </div>
            `;
            return wrap;
        }

        const inBall = this.isInPokeball(d.id);
        const ballFull = this.myPokeball.length >= 5 && !inBall;

        const types = Array.isArray(d.types) ? d.types : [];
        const stats = Array.isArray(d.stats) ? d.stats : [];

        const typeHtml = types.length
            ? types.map(t => `<span class="badge ${this.typeBadge(t)} me-1 text-capitalize">${t}</span>`).join("")
            : `<span class="text-muted">None</span>`;

        const statsHtml = stats.length
            ? stats.map(s => {
                const base = Number(s.base || 0);
                const pct = Math.max(0, Math.min(100, Math.round((base / 200) * 100)));
                return `
                    <div class="mb-2">
                        <div class="d-flex justify-content-between">
                            <small class="text-uppercase text-muted">${s.name}</small>
                            <small class="fw-bold">${base}</small>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar" role="progressbar" style="width: ${pct}%"></div>
                        </div>
                    </div>
                `;
            }).join("")
            : `<div class="text-muted">No stats available.</div>`;

        wrap.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <div class="text-center mb-3">
                        ${d.sprite ? `<img src="${d.sprite}" alt="${d.name}" style="width:160px;height:160px;">` : ""}
                    </div>
                    <h4 class="text-center mb-1">${this.formatDexNumber(d.number)} - <span class="text-capitalize">${d.name}</span></h4>
                    <div class="text-center mb-3">
                        ${
                            inBall
                                ? `<button class="btn btn-outline-secondary btn-sm" id="detail-remove">Remove from Pokéball</button>`
                                : `<button class="btn btn-primary btn-sm" id="detail-add" ${ballFull ? "disabled" : ""}>Add to Pokéball</button>`
                        }
                        ${ballFull ? `<div class="small text-muted mt-2">Pokéball is full (max 5).</div>` : ``}
                    </div>

                    <div class="mb-3">
                        <div class="fw-bold mb-1">Pokémon Info</div>
                        <div class="mb-2">${typeHtml}</div>
                        <div class="row small">
                            <div class="col-6 text-muted">Height: <span class="text-dark">${d.height ?? "-"}</span></div>
                            <div class="col-6 text-muted">Weight: <span class="text-dark">${d.weight ?? "-"}</span></div>
                        </div>
                        <div class="small text-muted mt-1">Base XP: <span class="text-dark">${d.base_experience ?? "-"}</span></div>
                    </div>

                    <div>
                        <div class="fw-bold mb-2">Base Stats</div>
                        ${statsHtml}
                    </div>
                </div>
            </div>
        `;

        const addBtn = wrap.querySelector("#detail-add");
        if (addBtn) {
            addBtn.onclick = async () => {
                try {
                    await this.addToPokeball(d.id);
                    this.render();
                } catch (err) {
                    this.showError(err.message || "Add failed");
                }
            };
        }
        const removeBtn = wrap.querySelector("#detail-remove");
        if (removeBtn) {
            removeBtn.onclick = async () => {
                try {
                    await this.removeFromPokeball(d.id);
                    this.render();
                } catch (err) {
                    this.showError(err.message || "Remove failed");
                }
            };
        }

        return wrap;
    }

    // ===== VIEWS =====

    render() {
        // Clear any pending search timer before re-rendering
        clearTimeout(this.searchTimer);

        const app = document.getElementById("app");
        app.innerHTML = "";
        
        console.log("🎨 Rendering view:", this.currentView);

        if (this.currentView === "landing") {
            app.appendChild(this.renderLanding());
        } else if (this.currentView === "login") {
            app.appendChild(this.renderLogin());
        } else if (this.currentView === "home") {
            app.appendChild(this.renderHome());
        } else if (this.currentView === "pokedex") {
            app.appendChild(this.renderPokedex());
        } else if (this.currentView === "battle") {
            app.appendChild(this.renderBattle());
        } else if (this.currentView === "about") {
            app.appendChild(this.renderAbout());
        } else if (this.currentView === "search") {
            app.appendChild(this.renderSearch());
        } else if (this.currentView === "detail") {
            app.appendChild(this.renderDetail());
        }
    }

    /**
     * 1. Public landing home page (not logged in)
     */
    renderLanding() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="container">
                <section class="landing-hero">
                    <div>
                        <h1 class="display-4 hero-title" style="color: var(--pokeball-red);">
                            Welcome to the Pokédex 
                        </h1>
                        <div class="mt-4">
                            <button class="btn btn-primary btn-lg" id="landing-login-btn">
                                🔐 Log in with Google
                            </button>
                        </div>
                    </div>

                    <div class="pokeball-stage" aria-hidden="true">
                        <img src="/static/images/landing.gif" alt="Pokémon" class="landing-gif">
                    </div>
                </section>
            </div>
        `;

        // Login button
        div.querySelector("#landing-login-btn").onclick = () => {
            this.currentView = "login";
            this.render();
        };

        return div;
    }

    /**
     * 2. Login page with Google button
     */
    renderLogin() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card shadow" style="border-radius: 12px;">
                            <div class="card-body text-center p-5">
                                <img src="/static/images/pokeball.png" alt="Pokéball" 
                                     style="width: 100px; height: 100px; margin-bottom: 20px;">
                                <h1 class="display-5 fw-bold mb-4" style="color: var(--pokeball-red);">
                                    Pokédex v2.0
                                </h1>
                                <p class="text-muted mb-4">
                                    Sign in with Google to access your Pokédex and Battle Arena.
                                </p>
                                
                                <a href="/auth/google" class="btn btn-primary btn-lg w-100">
                                    🔐 Sign in with Google
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    /**
     * 3. Authenticated home page (after login)
     */
    renderHome() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="container">
                <div class="home-hero">
                    <h1>Welcome back,<br>${this.user.name}!</h1>
                    <p>
                        Explore the Pokédex, battle a randomly generated opponent, or learn more about this project.
                        Choose a path below to get started.
                    </p>
                </div>

                <div class="feature-cards-row">
                    <!-- Pokédex Card -->
                    <div class="feature-card card-pokedex" id="home-card-pokedex">
                        <img src="/static/images/pokeball.png" alt="Pokédex" class="feature-card-img">
                        <div class="feature-card-body">
                            <h3>Pokédex</h3>
                            <p>Browse, search, and collect Pokémon. Build your Pokéball team of 5 for battle.</p>
                        </div>
                    </div>

                    <!-- Battle Mode Card -->
                    <div class="feature-card card-battle" id="home-card-battle">
                        <img src="/static/images/battle.jpg" alt="Battle Mode" class="feature-card-img">
                        <div class="feature-card-body">
                            <h3>Battle Mode</h3>
                            <p>Challenge a randomly generated opponent in turn-based battles using your Pokéball team.</p>
                        </div>
                    </div>

                    <!-- About Info Card -->
                    <div class="feature-card card-about" id="home-card-about">
                        <div class="feature-card-placeholder">ℹ️</div>
                        <div class="feature-card-body">
                            <h3>About Info</h3>
                            <p>Learn about this project, the tech stack, and the developer behind it.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Card click handlers
        div.querySelector("#home-card-pokedex").onclick = () => {
            this.currentView = "pokedex";
            this.render();
        };

        div.querySelector("#home-card-battle").onclick = () => {
            this.currentView = "battle";
            this.render();
        };

        div.querySelector("#home-card-about").onclick = () => {
            this.currentView = "about";
            this.render();
        };

        return div;
    }

    renderAbout() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-4">About</h2>
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="h5">About this project</h3>
                                <p class="text-muted mb-0">
                                    This Pokédex is a single-page web app using Flask and vanilla JavaScript.
                                    It pulls real Pokémon data from the public PokéAPI and lets each user
                                    manage their own Pokéball team for battle.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="h5">About the developer</h3>
                                <p class="text-muted mb-0">
                                    I'm a second year Computer Science student at the University of Wollongong, 
                                    currently pursuing AI & Big Data and Software Engineering.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-4">
                    <button class="btn btn-outline-secondary" id="about-back-btn">← Back to Home</button>
                </div>
            </div>
        `;

        div.querySelector("#about-back-btn").onclick = () => {
            this.currentView = "home";
            this.render();
        };

        return div;
    }

    renderPokedex() {
        const div = document.createElement("div");
        if (!this.isAuthenticated) {
            div.innerHTML = `
                <div class="container mt-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3 class="mb-2">Pokédex</h3>
                            <p class="text-muted mb-3">Please log in to use the Pokédex and My Pokéball.</p>
                            <button class="btn btn-primary" id="pokedex-login-btn">🔐 Log in with Google</button>
                        </div>
                    </div>
                </div>
            `;
            div.querySelector("#pokedex-login-btn").onclick = () => {
                this.currentView = "login";
                this.render();
            };
            return div;
        }

        div.innerHTML = `
            <div class="container-fluid mt-4">
                <div class="row mb-3">
                    <div class="col-12 d-flex flex-wrap justify-content-between align-items-center gap-2">
                        <h2 class="mb-0">Pokédex</h2>
                        <div class="d-flex align-items-center gap-2" style="max-width: 520px; width: 100%;">
                            <input type="text" class="form-control" id="pokedex-search" placeholder="Search Pokémon by name (e.g. charmander) or ID (e.g. 4)" value="${this.searchQuery || ""}">
                            <button class="btn btn-outline-secondary" id="pokedex-reset">Reset</button>
                        </div>
                    </div>
                </div>

                <div class="row g-3">
                    <div class="col-lg-8">
                        <div class="card h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <div class="btn-group" role="group" aria-label="Pokedex tabs">
                                    <button class="btn btn-sm ${this.pokedexTab === "pokedex" ? "btn-primary" : "btn-outline-secondary"}" id="tab-pokedex">Pokedex</button>
                                    <button class="btn btn-sm ${this.pokedexTab === "pokeball" ? "btn-primary" : "btn-outline-secondary"}" id="tab-pokeball">My Pokéball (${this.myPokeball.length}/5)</button>
                                </div>
                                <div class="small text-muted">
                                    ${this.pokedexTab === "pokedex" ? "Browse & add Pokémon" : "Reorder your 5 Pokémon for battle"}
                                </div>
                            </div>
                            <div class="card-body">
                                <div id="left-panel"></div>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-4">
                        <div id="detail-panel"></div>
                    </div>
                </div>
            </div>
        `;

        const detailPanel = div.querySelector("#detail-panel");
        detailPanel.appendChild(this.renderDetailPanel());

        const leftPanel = div.querySelector("#left-panel");

        const renderPokedexGrid = () => {
            leftPanel.innerHTML = `
                <div class="row row-cols-2 row-cols-md-3 row-cols-xl-4 g-3" id="pokedex-grid"></div>
            `;
            const grid = leftPanel.querySelector("#pokedex-grid");
            if (!this.pokedexResults.length) {
                grid.innerHTML = `
                    <div class="col-12">
                        <div class="text-muted">No Pokémon found.</div>
                    </div>
                `;
                return;
            }
            for (const p of this.pokedexResults) {
                grid.appendChild(this.renderPokemonCard(p, { showAddButton: true, context: "pokedex" }));
            }
        };

        const renderPokeballList = () => {
            leftPanel.innerHTML = `
                <div class="row row-cols-2 row-cols-md-3 row-cols-xl-4 g-3" id="pokeball-grid"></div>
                <div class="mt-3 small text-muted">
                    Tip: use the arrows to set battle order (saved in this session).
                </div>
            `;
            const grid = leftPanel.querySelector("#pokeball-grid");
            if (!this.myPokeball.length) {
                grid.innerHTML = `
                    <div class="col-12">
                        <div class="text-muted">Your Pokéball is empty. Add Pokémon from the Pokedex tab.</div>
                    </div>
                `;
                return;
            }

            this.myPokeball.forEach((p, idx) => {
                const card = this.renderPokemonCard(
                    { id: p.pokemon_id, name: p.pokemon_name, number: p.pokemon_number, sprite: this.spriteCache[p.pokemon_id] || "" },
                    { showAddButton: true, context: "pokeball" }
                );
                const body = card.querySelector(".card-body");
                const controls = document.createElement("div");
                controls.className = "mt-2 d-flex justify-content-center gap-2";
                controls.innerHTML = `
                    <button class="btn btn-outline-secondary btn-sm" ${idx === 0 ? "disabled" : ""} data-move="up">↑</button>
                    <button class="btn btn-outline-secondary btn-sm" ${idx === this.myPokeball.length - 1 ? "disabled" : ""} data-move="down">↓</button>
                `;

                controls.querySelector('[data-move="up"]').onclick = (e) => {
                    e.stopPropagation();
                    if (idx <= 0) return;
                    const tmp = this.myPokeball[idx - 1];
                    this.myPokeball[idx - 1] = this.myPokeball[idx];
                    this.myPokeball[idx] = tmp;
                    this.render();
                };
                controls.querySelector('[data-move="down"]').onclick = (e) => {
                    e.stopPropagation();
                    if (idx >= this.myPokeball.length - 1) return;
                    const tmp = this.myPokeball[idx + 1];
                    this.myPokeball[idx + 1] = this.myPokeball[idx];
                    this.myPokeball[idx] = tmp;
                    this.render();
                };

                body.appendChild(controls);

                // Ensure clicking shows real details (load by pokemon_id)
                card.querySelector("[data-pokemon-id]").onclick = async (e) => {
                    const btn = e.target.closest("button");
                    if (btn) return;
                    try {
                        await this.loadPokemonDetail(p.pokemon_id);
                        this.render();
                    } catch (err) {
                        this.showError(err.message || "Failed to load details");
                    }
                };

                grid.appendChild(card);
            });
        };

        // Tabs
        div.querySelector("#tab-pokedex").onclick = async () => {
            this.pokedexTab = "pokedex";
            if (!this.pokedexResults.length) {
                try {
                    await this.loadDefaultPokedex();
                } catch (err) {
                    this.showError(err.message || "Failed to load Pokémon");
                }
            }
            this.render();
        };
        div.querySelector("#tab-pokeball").onclick = async () => {
            this.pokedexTab = "pokeball";
            try {
                await this.loadMyPokeball();
            } catch (err) {
                this.showError(err.message || "Failed to load My Pokéball");
            }
            this.render();
        };

        // Search interactions (Pokedex tab)
        const searchInput = div.querySelector("#pokedex-search");
        const resetBtn = div.querySelector("#pokedex-reset");

        const doSearch = async () => {
            const q = (searchInput.value || "").trim().toLowerCase();
            this.searchQuery = q;
            this.pokedexTab = "pokedex";
            try {
                if (!q) {
                    await this.loadDefaultPokedex();
                } else {
                    await this.searchPokemonByNameOrId(q);
                }
                this.render();
            } catch (err) {
                this.showError(err.message || "Search failed");
            }
        };

        searchInput.oninput = () => {
            clearTimeout(this.searchTimer);
            this.searchTimer = setTimeout(doSearch, 350);
        };
        searchInput.onkeydown = (e) => {
            if (e.key === "Enter") {
                clearTimeout(this.searchTimer);
                doSearch();
            }
        };
        resetBtn.onclick = async () => {
            searchInput.value = "";
            this.searchQuery = "";
            try {
                await this.loadDefaultPokedex();
                this.render();
            } catch (err) {
                this.showError(err.message || "Failed to reset");
            }
        };

        // Initial left panel content
        if (this.pokedexTab === "pokeball") {
            renderPokeballList();
            this.warmPokeballSprites().then((hadNew) => {
                if (hadNew) this.render();
            }).catch(() => {});
        } else {
            if (!this.pokedexResults.length && !this.searchQuery) {
                // Only load defaults if there's no active search
                this.loadDefaultPokedex().then(() => this.render()).catch(() => {});
                leftPanel.innerHTML = `<div class="text-muted">Loading Pokémon...</div>`;
            } else {
                renderPokedexGrid();
            }
        }

        return div;
    }

    renderBattle() {
        const div = document.createElement("div");
        div.innerHTML = `
            <div class="container mt-4">
                <h2>Battle Arena</h2>
                <p class="text-muted">
                    This is a placeholder for the online battle mode between users.
                    In later phases, you will be able to select a team from your Pokédex
                    and battle another trainer in a turn-based arena.
                </p>
                <div class="card mt-3">
                    <div class="card-body">
                        <p class="mb-1"><strong>Planned layout:</strong></p>
                        <ul class="mb-0 text-muted">
                            <li>Top section: opponent info and connection status.</li>
                            <li>Middle: battle field with both active Pokémon and HP bars.</li>
                            <li>Bottom: move buttons, switch controls, and battle log.</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    renderSearch() {
        const div = document.createElement("div");
        div.innerHTML = `<p>Search view - Phase 1.2</p>`;
        return div;
    }

    renderDetail() {
        const div = document.createElement("div");
        div.innerHTML = `<p>Detail view - Phase 1.2</p>`;
        return div;
    }

    // ===== UTILITIES =====

    showError(message) {
        alert("❌ " + message);
    }
}

// ===== INITIALIZATION =====

let app;

document.addEventListener("DOMContentLoaded", () => {
    console.log("🌐 DOM loaded, initializing PokemonApp v2.0...");
    app = new PokemonAppV2();
    app.init();
});
