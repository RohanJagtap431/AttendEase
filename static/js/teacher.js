
document.addEventListener("DOMContentLoaded", function () {

    // Highlight dashboard cards on hover
    const statCards = document.querySelectorAll(".stat-card");

    statCards.forEach(function (card) {
        card.addEventListener("mouseenter", function () {
            card.classList.add("card-hover");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("card-hover");
        });
    });

    // Confirm before opening attendance marking page
    const attendanceButtons = document.querySelectorAll(
        ".primary-btn"
    );

    attendanceButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {

            const confirmed = confirm(
                "Do you want to open the attendance marking page?"
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    // Search/filter recent attendance table
    const searchInput = document.getElementById(
        "attendanceSearch"
    );

    const tableRows = document.querySelectorAll(
        ".dashboard-table tbody tr"
    );

    if (searchInput) {
        searchInput.addEventListener("input", function () {

            const searchValue = this.value.toLowerCase().trim();

            tableRows.forEach(function (row) {

                const rowText = row.textContent.toLowerCase();

                row.style.display = rowText.includes(searchValue)
                    ? ""
                    : "none";
            });
        });
    }

});
