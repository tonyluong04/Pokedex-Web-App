/**
 * Pokédex v2.0 - Single Page Application (SPA)
 * 
 * Personal project: Browse Pokémon via PokéAPI, manage personal Pokédex,
 * battle other users, view statistics.
 * 
 * Tech: Vanilla ES6 JavaScript, Flask REST API, PostgreSQL
 */

class PokemonAppV2 {

    // ===== BATTLE TYPE CHART =====
    static TYPE_CHART = {
        fire: "grass",
        water: "fire",
        grass: "water",
        electric: "water",
        ice: "grass",
        psychic: "fighting",
        fighting: "normal",
        ground: "electric",
        flying: "fighting",
        rock: "flying",
        bug: "grass",
        ghost: "psychic",
        dragon: "dragon",
        dark: "psychic",
        steel: "ice",
    };

    constructor() {
        // User state
        this.user = null;
        this.isAuthenticated = false;
        
        // Pokémon state
        this.pokedexResults = [];
        this.myPokeball = [];
        this.selectedPokemon = null;
        this.spriteCache = {};

        // Pokedex UI state
        this.pokedexTab = "pokedex";
        this.searchQuery = "";
        this.searchTimer = null;
        
        // UI state
        this.currentView = "landing";
        this.loading = false;

        // Battle state
        this.battleState = null;
        
        console.log("✅ PokemonApp v2.0 initialized");
    }

    async init() {
        try {
            console.log("🔄 Starting app initialization...");
            await this.checkAuthStatus();
            if (this.isAuthenticated) {
                await this.loadMyPokeball();
            }
            this.currentView = this.isAuthenticated ? "home" : "landing";
            this.render();
            console.log("✅ App initialization complete");
        } catch (err) {
            console.error("❌ Init failed:", err);
            this.showError("Failed to initialize app");
        }
    }

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
        const missing = this.myPokeball
            .map(p => Number(p.pokemon_id))
            .filter(id => id && !this.spriteCache[id]);

        if (!missing.length) return false;

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

        return true;
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

    // ===== BATTLE HELPERS =====

    calcTypeMultiplier(attackerTypes, defenderTypes) {
        let multiplier = 1.0;
        for (const aType of attackerTypes) {
            for (const dType of defenderTypes) {
                const strongAgainst = PokemonAppV2.TYPE_CHART[aType];
                if (strongAgainst === dType) {
                    multiplier *= 2.0;
                }
                const defStrong = PokemonAppV2.TYPE_CHART[dType];
                if (defStrong === aType) {
                    multiplier *= 0.5;
                }
            }
        }
        return multiplier;
    }

    calcDamage(attacker, defender) {
        const typeMult = this.calcTypeMultiplier(attacker.types || [], defender.types || []);
        const raw = Math.floor((attacker.attack / defender.defense) * 20 * typeMult);
        return Math.max(1, raw);
    }

    hpBarClass(current, max) {
        const pct = (current / max) * 100;
        if (pct > 50) return "hp-green";
        if (pct > 25) return "hp-yellow";
        return "hp-red";
    }

    resetBattleState() {
        this.battleState = {
            playerTeam: [],
            opponentTeam: [],
            roundIndex: 0,
            playerKOs: 0,
            opponentKOs: 0,
            turnLog: [],
            phase: "select",
        };
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
            if (btn) return;
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

        div.querySelector("#landing-login-btn").onclick = () => {
            this.currentView = "login";
            this.render();
        };

        return div;
    }

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
                    <div class="feature-card card-pokedex" id="home-card-pokedex">
                        <img src="/static/images/pokeball.png" alt="Pokédex" class="feature-card-img">
                        <div class="feature-card-body">
                            <h3>Pokédex</h3>
                            <p>Browse, search, and collect Pokémon. Build your Pokéball team of 5 for battle.</p>
                        </div>
                    </div>

                    <div class="feature-card card-battle" id="home-card-battle">
                        <img src="/static/images/battle.jpg" alt="Battle Mode" class="feature-card-img">
                        <div class="feature-card-body">
                            <h3>Battle Mode</h3>
                            <p>Challenge a randomly generated opponent in turn-based battles using your Pokéball team.</p>
                        </div>
                    </div>

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

        const searchInput = div.querySelector("#pokedex-search");
        const resetBtn = div.querySelector("#pokedex-reset");

        const doSearch = async () => {
            // Guard: make sure this input is still in the DOM
            if (!document.contains(searchInput)) return;
            
            const q = (searchInput.value || "").trim().toLowerCase();
            this.searchQuery = q;
            this.pokedexTab = "pokedex";
            try {
                if (!q) {
                    await this.loadDefaultPokedex();
                } else {
                    await this.searchPokemonByNameOrId(q);
                }
                // Guard again: don't re-render if input was detached during the async call
                if (!document.contains(searchInput)) return;
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

        if (this.pokedexTab === "pokeball") {
            renderPokeballList();
            this.warmPokeballSprites().then((hadNew) => {
                if (hadNew) this.render();
            }).catch(() => {});
        } else {
            if (!this.pokedexResults.length && !this.searchQuery) {
                this.loadDefaultPokedex().then(() => this.render()).catch(() => {});
                leftPanel.innerHTML = `<div class="text-muted">Loading Pokémon...</div>`;
            } else {
                renderPokedexGrid();
            }
        }

        return div;
    }

    // ===== BATTLE VIEWS =====

    renderBattle() {
        const div = document.createElement("div");

        if (!this.isAuthenticated) {
            div.innerHTML = `
                <div class="container mt-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3 class="mb-2">Battle Arena</h3>
                            <p class="text-muted mb-3">Please log in to battle.</p>
                            <button class="btn btn-primary" id="battle-login-btn">🔐 Log in with Google</button>
                        </div>
                    </div>
                </div>
            `;
            div.querySelector("#battle-login-btn").onclick = () => {
                this.currentView = "login";
                this.render();
            };
            return div;
        }

        if (!this.battleState) {
            this.resetBattleState();
        }

        const phase = this.battleState.phase;

        if (phase === "select") {
            return this.renderBattleSelect(div);
        } else if (phase === "loading") {
            div.innerHTML = `
                <div class="container mt-4 text-center">
                    <h2>⚔️ Preparing Battle...</h2>
                    <div class="spinner-border text-danger mt-3" role="status"></div>
                    <p class="text-muted mt-2">Fetching Pokémon stats from PokéAPI...</p>
                </div>
            `;
            return div;
        } else {
            return this.renderBattleArena(div);
        }
    }

    renderBattleSelect(div) {
        const hasFive = this.myPokeball.length === 5;

        div.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-3">⚔️ Battle Arena — Team Selection</h2>
                <p class="text-muted">
                    ${hasFive
                        ? "Your Pokéball team of 5 is ready! Hit Start Battle to begin."
                        : `You need exactly 5 Pokémon in your Pokéball to battle. You currently have <strong>${this.myPokeball.length}/5</strong>.`
                    }
                </p>

                <div class="team-select-grid mb-4" id="team-preview"></div>

                <div class="d-flex gap-2">
                    <button class="btn btn-primary btn-lg" id="start-battle-btn" ${hasFive ? "" : "disabled"}>
                        ⚔️ Start Battle
                    </button>
                    <button class="btn btn-outline-secondary" id="goto-pokeball-btn">
                        📦 Go to Pokéball
                    </button>
                </div>
            </div>
        `;

        const grid = div.querySelector("#team-preview");
        if (this.myPokeball.length) {
            this.myPokeball.forEach(p => {
                const sprite = this.spriteCache[p.pokemon_id] || "";
                const card = document.createElement("div");
                card.className = "team-select-card selected";
                card.innerHTML = `
                    ${sprite ? `<img src="${sprite}" alt="${p.pokemon_name}">` : `<div style="width:64px;height:64px;"></div>`}
                    <div class="name">${p.pokemon_name}</div>
                `;
                grid.appendChild(card);
            });
        }

        this.warmPokeballSprites().then(hadNew => {
            if (hadNew) this.render();
        }).catch(() => {});

        div.querySelector("#start-battle-btn").onclick = async () => {
            this.battleState.phase = "loading";
            this.render();

            try {
                const teamIds = this.myPokeball.map(p => Number(p.pokemon_id));
                const resp = await fetch("/api/battle/start", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ team: teamIds }),
                });
                if (!resp.ok) {
                    const err = await resp.json().catch(() => ({}));
                    throw new Error(err.error || "Failed to start battle");
                }
                const data = await resp.json();

                this.battleState.playerTeam = data.playerTeam.map(p => ({ ...p, currentHp: p.hp }));
                this.battleState.opponentTeam = data.opponentTeam.map(p => ({ ...p, currentHp: p.hp }));
                this.battleState.roundIndex = 0;
                this.battleState.playerKOs = 0;
                this.battleState.opponentKOs = 0;
                this.battleState.turnLog = [];
                this.battleState.phase = "round-intro";
                this.render();
            } catch (err) {
                this.battleState.phase = "select";
                this.render();
                this.showError(err.message || "Battle start failed");
            }
        };

        div.querySelector("#goto-pokeball-btn").onclick = () => {
            this.pokedexTab = "pokeball";
            this.currentView = "pokedex";
            this.render();
        };

        return div;
    }

    renderBattleArena(div) {
        const bs = this.battleState;
        const ri = bs.roundIndex;
        const player = bs.playerTeam[ri];
        const opponent = bs.opponentTeam[ri];
        const phase = bs.phase;

        const playerHpPct = player ? Math.max(0, Math.round((player.currentHp / player.hp) * 100)) : 0;
        const oppHpPct = opponent ? Math.max(0, Math.round((opponent.currentHp / opponent.hp) * 100)) : 0;

        // Player score = opponent's KOs (rounds player won), and vice versa
        const playerScore = bs.opponentKOs;
        const opponentScore = bs.playerKOs;

        const logEntries = bs.turnLog.slice(-10).map(entry => {
            let cls = "";
            if (entry.includes("fainted")) cls = "log-faint";
            else if (entry.includes("Round")) cls = "log-round";
            else cls = "log-damage";
            return `<p class="${cls}">${entry}</p>`;
        }).join("");

        div.innerHTML = `
            <div class="container-fluid mt-3">
                <div class="battle-arena" id="battle-arena">
                    <div class="battle-arena-overlay"></div>

                    <div class="battle-score">
                        Score: ${playerScore} - ${opponentScore}
                    </div>

                    ${player ? `
                    <div class="battle-pokemon-card player">
                        ${player.sprite ? `<img src="${player.sprite}" alt="${player.name}" class="battle-sprite">` : ""}
                        <div class="pokemon-name">${player.name}</div>
                        <div>${(player.types || []).map(t => `<span class="badge ${this.typeBadge(t)} me-1">${t}</span>`).join("")}</div>
                        <div class="battle-hp-bar">
                            <div class="progress-bar ${this.hpBarClass(player.currentHp, player.hp)}" id="player-hp-bar" style="width: ${playerHpPct}%"></div>
                        </div>
                        <div class="battle-hp-text">HP: ${player.currentHp} / ${player.hp}</div>
                    </div>
                    ` : ""}

                    ${opponent ? `
                    <div class="battle-pokemon-card opponent">
                        ${opponent.sprite ? `<img src="${opponent.sprite}" alt="${opponent.name}" class="battle-sprite mirrored">` : ""}
                        <div class="pokemon-name">${opponent.name}</div>
                        <div>${(opponent.types || []).map(t => `<span class="badge ${this.typeBadge(t)} me-1">${t}</span>`).join("")}</div>
                        <div class="battle-hp-bar">
                            <div class="progress-bar ${this.hpBarClass(opponent.currentHp, opponent.hp)}" id="opp-hp-bar" style="width: ${oppHpPct}%"></div>
                        </div>
                        <div class="battle-hp-text">HP: ${opponent.currentHp} / ${opponent.hp}</div>
                    </div>
                    ` : ""}
                </div>

                <div class="mt-3">
                    <div class="battle-log" id="battle-log">${logEntries || `<p class="text-muted">Battle log will appear here...</p>`}</div>
                </div>

                <div class="mt-3 d-flex gap-2" id="battle-controls"></div>
            </div>

            <!-- Round Intro Modal -->
            <div class="modal fade round-intro-modal" id="roundIntroModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content p-4">
                        <h2 class="mb-2" id="round-intro-title"></h2>
                        <div class="round-intro-fighters" id="round-intro-fighters"></div>
                    </div>
                </div>
            </div>

            <!-- Round End Modal -->
            <div class="modal fade battle-result-modal" id="roundEndModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content p-4">
                        <h2 id="round-end-title"></h2>
                        <p id="round-end-message"></p>
                        <p id="round-end-score"></p>
                        <div id="round-end-buttons"></div>
                    </div>
                </div>
            </div>
        `;

        setTimeout(() => {
            if (phase === "round-intro") {
                this.showRoundIntro(div);
            } else if (phase === "fighting") {
                this.addFightButton(div);
            } else if (phase === "round-end") {
                this.showRoundEnd(div);
            } else if (phase === "match-end") {
                this.showMatchEnd(div);
            }
        }, 50);

        return div;
    }

    showRoundIntro(div) {
        const bs = this.battleState;
        const ri = bs.roundIndex;
        const player = bs.playerTeam[ri];
        const opponent = bs.opponentTeam[ri];

        player.currentHp = player.hp;
        opponent.currentHp = opponent.hp;

        bs.turnLog.push(`--- Round ${ri + 1} begins! ---`);

        const titleEl = div.querySelector("#round-intro-title");
        const fightersEl = div.querySelector("#round-intro-fighters");

        if (titleEl) {
            titleEl.textContent = `Round ${ri + 1}`;
        }
        if (fightersEl) {
            fightersEl.innerHTML = `
                <div class="text-center">
                    ${player.sprite ? `<img src="${player.sprite}" alt="${player.name}">` : ""}
                    <div class="fighter-name">${player.name}</div>
                </div>
                <div class="vs">VS</div>
                <div class="text-center">
                    ${opponent.sprite ? `<img src="${opponent.sprite}" alt="${opponent.name}">` : ""}
                    <div class="fighter-name">${opponent.name}</div>
                </div>
            `;
        }

        const modalEl = div.querySelector("#roundIntroModal");
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();

            setTimeout(() => {
                modal.hide();
                bs.phase = "fighting";
                this.render();
            }, 2000);
        }
    }

    addFightButton(div) {
        const controls = div.querySelector("#battle-controls");
        if (!controls) return;

        controls.innerHTML = `
            <button class="btn btn-danger btn-lg" id="attack-btn">⚔️ Attack</button>
        `;

        div.querySelector("#attack-btn").onclick = () => {
            this.executeTurn(div);
        };
    }

    executeTurn(div) {
        const bs = this.battleState;
        const ri = bs.roundIndex;
        const player = bs.playerTeam[ri];
        const opponent = bs.opponentTeam[ri];

        let first, second, firstLabel, secondLabel;
        if (player.speed > opponent.speed) {
            first = player; second = opponent;
            firstLabel = "player"; secondLabel = "opponent";
        } else if (opponent.speed > player.speed) {
            first = opponent; second = player;
            firstLabel = "opponent"; secondLabel = "player";
        } else {
            if (Math.random() < 0.5) {
                first = player; second = opponent;
                firstLabel = "player"; secondLabel = "opponent";
            } else {
                first = opponent; second = player;
                firstLabel = "opponent"; secondLabel = "player";
            }
        }

        const dmg1 = this.calcDamage(first, second);
        second.currentHp = Math.max(0, second.currentHp - dmg1);
        bs.turnLog.push(`${first.name} dealt ${dmg1} damage to ${second.name}!`);

        if (second.currentHp <= 0) {
            bs.turnLog.push(`${second.name} fainted!`);
            this.handleKO(secondLabel);
            return;
        }

        const dmg2 = this.calcDamage(second, first);
        first.currentHp = Math.max(0, first.currentHp - dmg2);
        bs.turnLog.push(`${second.name} dealt ${dmg2} damage to ${first.name}!`);

        if (first.currentHp <= 0) {
            bs.turnLog.push(`${first.name} fainted!`);
            this.handleKO(firstLabel);
            return;
        }

        this.render();
    }

    handleKO(loserSide) {
        const bs = this.battleState;
        if (loserSide === "player") {
            bs.playerKOs++;
        } else {
            bs.opponentKOs++;
        }

        if (bs.playerKOs >= 3 || bs.opponentKOs >= 3) {
            bs.phase = "match-end";
        } else {
            bs.phase = "round-end";
        }
        this.render();
    }

    showRoundEnd(div) {
        const bs = this.battleState;
        const ri = bs.roundIndex;
        const player = bs.playerTeam[ri];
        const opponent = bs.opponentTeam[ri];

        const playerFainted = player.currentHp <= 0;
        const winnerName = playerFainted ? opponent.name : player.name;

        const titleEl = div.querySelector("#round-end-title");
        const msgEl = div.querySelector("#round-end-message");
        const scoreEl = div.querySelector("#round-end-score");
        const btnsEl = div.querySelector("#round-end-buttons");

        if (titleEl) titleEl.textContent = `Round ${ri + 1} Complete!`;
        if (msgEl) msgEl.innerHTML = `<span class="text-capitalize">${winnerName}</span> wins this round!`;
        if (scoreEl) scoreEl.textContent = `Score: ${bs.opponentKOs} - ${bs.playerKOs}`;
        if (btnsEl) {
            btnsEl.innerHTML = `<button class="btn btn-primary" id="next-round-btn">Next Round →</button>`;
            btnsEl.querySelector("#next-round-btn").onclick = () => {
                const modal = bootstrap.Modal.getInstance(div.querySelector("#roundEndModal"));
                if (modal) modal.hide();
                bs.roundIndex++;
                bs.phase = "round-intro";
                this.render();
            };
        }

        const modalEl = div.querySelector("#roundEndModal");
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    }

    showMatchEnd(div) {
        const bs = this.battleState;
        const playerWon = bs.opponentKOs >= 3;

        const titleEl = div.querySelector("#round-end-title");
        const msgEl = div.querySelector("#round-end-message");
        const scoreEl = div.querySelector("#round-end-score");
        const btnsEl = div.querySelector("#round-end-buttons");

        if (titleEl) titleEl.textContent = playerWon ? "Victory! 🎉" : "Defeated! 💀";
        if (msgEl) msgEl.textContent = playerWon ? "You defeated the opponent!" : "Your team has been defeated...";
        if (scoreEl) scoreEl.textContent = `Final Score: ${bs.opponentKOs} - ${bs.playerKOs}`;
        if (btnsEl) {
            btnsEl.innerHTML = `
                <button class="btn btn-primary me-2" id="play-again-btn">🔄 Play Again</button>
                <button class="btn btn-outline-secondary" id="back-home-btn">🏠 Back to Home</button>
            `;
            btnsEl.querySelector("#play-again-btn").onclick = () => {
                const modal = bootstrap.Modal.getInstance(div.querySelector("#roundEndModal"));
                if (modal) modal.hide();
                this.resetBattleState();
                this.render();
            };
            btnsEl.querySelector("#back-home-btn").onclick = () => {
                const modal = bootstrap.Modal.getInstance(div.querySelector("#roundEndModal"));
                if (modal) modal.hide();
                this.resetBattleState();
                this.currentView = "home";
                this.render();
            };
        }

        const modalEl = div.querySelector("#roundEndModal");
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
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
