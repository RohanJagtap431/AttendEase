
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("menuToggle");
const overlay = document.getElementById("sidebarOverlay");

menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");
});

overlay.addEventListener("click", () => {
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
});

document.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", () => {
        if (window.innerWidth <= 650) {
            sidebar.classList.remove("open");
            overlay.classList.remove("show");
        }
    });
});
