/**
 * Pokéball Globe Animation
 * Uses cobe library for an interactive WebGL globe with Pokéball theming.
 * Call initPokeballGlobe() to start, destroyPokeballGlobe() to clean up.
 */

let globeInstance = null;
let globeRAF = null;
let globeResizeHandler = null;

function initPokeballGlobe() {
    // Clean up any existing instance first
    destroyPokeballGlobe();

    const canvas = document.getElementById("pokeball-globe-canvas");
    if (!canvas || typeof createGlobe === "undefined") {
        console.warn("⚠️ Globe canvas or cobe library not found");
        return;
    }

    // Responsive sizing
    const setCanvasSize = () => {
        const container = canvas.parentElement;
        const size = Math.min(container.offsetWidth, 500);
        canvas.width = size * 2;   // retina
        canvas.height = size * 2;
        canvas.style.width = size + "px";
        canvas.style.height = size + "px";
    };
    setCanvasSize();

    let phi = 0;
    let pointerDown = false;
    let pointerX = 0;
    let velocity = 0;

    globeInstance = createGlobe(canvas, {
        devicePixelRatio: 2,
        width: canvas.width,
        height: canvas.height,
        phi: 0,
        theta: 0.25,
        dark: 1,
        diffuse: 1.2,
        mapSamples: 16000,
        mapBrightness: 6,
        baseColor: [0.9, 0.1, 0.1],        // Pokéball red
        markerColor: [1, 1, 1],             // White dots
        glowColor: [1, 0.4, 0.4],          // Soft red/pink glow
        markers: [
            // Notable Pokémon game regions mapped to real-world locations
            { location: [35.6762, 139.6503], size: 0.06 },   // Tokyo (Kanto)
            { location: [34.6937, 135.5023], size: 0.05 },   // Osaka (Johto)
            { location: [48.8566, 2.3522], size: 0.05 },     // Paris (Kalos)
            { location: [40.4168, -3.7038], size: 0.04 },    // Madrid
            { location: [51.5074, -0.1278], size: 0.05 },    // London (Galar)
            { location: [21.3069, -157.8583], size: 0.05 },  // Hawaii (Alola)
            { location: [40.7128, -74.0060], size: 0.05 },   // New York (Unova)
            { location: [-33.8688, 151.2093], size: 0.04 },  // Sydney
        ],
        onRender: (state) => {
            // Auto-spin when not dragging
            if (!pointerDown) {
                phi += 0.005;
                velocity *= 0.95;
                phi += velocity;
            }
            state.phi = phi;
            state.width = canvas.width;
            state.height = canvas.height;
        },
    });

    // Pointer interaction for drag-to-spin
    const onPointerDown = (e) => {
        pointerDown = true;
        pointerX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
        canvas.style.cursor = "grabbing";
    };

    const onPointerUp = () => {
        pointerDown = false;
        canvas.style.cursor = "grab";
    };

    const onPointerMove = (e) => {
        if (!pointerDown) return;
        const x = e.clientX || (e.touches && e.touches[0].clientX) || 0;
        const delta = x - pointerX;
        velocity = delta * 0.003;
        pointerX = x;
    };

    canvas.addEventListener("pointerdown", onPointerDown);
    canvas.addEventListener("pointerup", onPointerUp);
    canvas.addEventListener("pointerleave", onPointerUp);
    canvas.addEventListener("pointermove", onPointerMove);

    // Touch support
    canvas.addEventListener("touchstart", onPointerDown, { passive: true });
    canvas.addEventListener("touchend", onPointerUp);
    canvas.addEventListener("touchmove", onPointerMove, { passive: true });

    canvas.style.cursor = "grab";

    // Resize handler
    globeResizeHandler = () => {
        setCanvasSize();
    };
    window.addEventListener("resize", globeResizeHandler);
}

function destroyPokeballGlobe() {
    if (globeInstance) {
        globeInstance.destroy();
        globeInstance = null;
    }
    if (globeRAF) {
        cancelAnimationFrame(globeRAF);
        globeRAF = null;
    }
    if (globeResizeHandler) {
        window.removeEventListener("resize", globeResizeHandler);
        globeResizeHandler = null;
    }
}