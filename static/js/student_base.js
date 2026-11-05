
document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("studentSidebar");
    const menuToggle = document.getElementById("menuToggle");
    const overlay = document.getElementById("sidebarOverlay");

    if (!sidebar || !menuToggle || !overlay) {
        return;
    }

    function openSidebar() {
        sidebar.classList.add("sidebar-open");
        overlay.classList.add("show");
    }

    function closeSidebar() {
        sidebar.classList.remove("sidebar-open");
        overlay.classList.remove("show");
    }

    menuToggle.addEventListener("click", function () {
        if (sidebar.classList.contains("sidebar-open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    sidebar.querySelectorAll(".nav-link").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                closeSidebar();
            }
        });
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            closeSidebar();
        }
    });

});
