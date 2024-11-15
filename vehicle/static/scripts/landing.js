// Configuración de animaciones con ScrollReveal
ScrollReveal().reveal(".hero.title h1", {
  duration: 1000, // Duración de la animación en milisegundos
  origin: "top", // Origen desde donde aparece la animación
  distance: "50px", // Distancia desde la que aparece el elemento
});

ScrollReveal().reveal(".autoAnimation .car", {
  duration: 1200,
  origin: "left",
  distance: "100px",
  delay: 300, // Retraso antes de iniciar la animación
});

ScrollReveal().reveal(".autoAnimation .wheel", {
  duration: 1200,
  origin: "bottom",
  distance: "50px",
  delay: 500,
});

ScrollReveal().reveal(".botones .button-primary", {
  duration: 800,
  origin: "bottom",
  distance: "30px",
  interval: 200, // Intervalo entre elementos si son varios
});

ScrollReveal().reveal(".about .hero h1", {
  duration: 1000,
  origin: "left",
  distance: "50px",
});

ScrollReveal().reveal(".cards .card", {
  duration: 1000,
  origin: "right",
  distance: "50px",
  interval: 200, // Intervalo entre tarjetas para crear un efecto secuencial
});
