ScrollReveal({
  reset: true, // Repite la animación al hacer scroll
  distance: "50px", // Distancia de desplazamiento
  duration: 1200, // Duración de la animación en milisegundos
  delay: 200, // Retraso antes de que comience la animación
});

// Animaciones para las diferentes secciones
ScrollReveal().reveal(".hero", { origin: "top", delay: 300 });
ScrollReveal().reveal(".Cards .card", { origin: "bottom", interval: 200 });
ScrollReveal().reveal(".diagram", { origin: "left", interval: 300 });
ScrollReveal().reveal(".diagram2", { origin: "right", delay: 400 });
ScrollReveal().reveal(".sec-rev", { origin: "bottom", delay: 500 });
ScrollReveal().reveal(".rev", { origin: "bottom", interval: 200 });
ScrollReveal().reveal(".rev-con", { origin: "top", delay: 300 });
