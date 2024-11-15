ScrollReveal({
  reset: true, // Repite la animación al hacer scroll
  distance: "50px", // Distancia de desplazamiento
  duration: 1500, // Duración de la animación (ms)
  delay: 200, // Retraso antes de iniciar la animación (ms)
});

// Animaciones para diferentes secciones
ScrollReveal().reveal(".filter", { origin: "top", delay: 300 });
ScrollReveal().reveal(".cards .card", { origin: "bottom", interval: 200 });
ScrollReveal().reveal(".text", { origin: "left", delay: 400 });
ScrollReveal().reveal(".diagrams", { origin: "right", interval: 300 });
ScrollReveal().reveal(".images", { origin: "bottom", delay: 500 });
