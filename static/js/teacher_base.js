
document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("teacherSidebar");
    const menuToggle = document.getElementById("menuToggle");
    const overlay = document.getElementById("sidebarOverlay");

    // Check required elements
    if (!sidebar || !menuToggle || !overlay) {
        return;
    }

    // Open and close sidebar
    function toggleSidebar() {
        const isOpen = sidebar.classList.toggle("sidebar-open");

        overlay.classList.toggle("active", isOpen);
        menuToggle.setAttribute("aria-expanded", isOpen);
    }

    // Close sidebar
    function closeSidebar() {
        sidebar.classList.remove("sidebar-open");
        overlay.classList.remove("active");
        menuToggle.setAttribute("aria-expanded", "false");
    }

    // Menu button click
    menuToggle.addEventListener("click", toggleSidebar);

    // Overlay click
    overlay.addEventListener("click", closeSidebar);

    // Close sidebar after clicking navigation link on mobile
    const navigationLinks = sidebar.querySelectorAll(".nav-link");

    navigationLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                closeSidebar();
            }
        });
    });

    // Close sidebar with Escape key
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    // Reset sidebar when switching to desktop
    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            closeSidebar();
        }
    });

});
