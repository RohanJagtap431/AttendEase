
document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("recordsSearch");
    const rows = document.querySelectorAll(".record-row");
    const noSearchMessage = document.getElementById("recordsNoSearch");

    if (!searchInput) return;

    searchInput.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();
        let visibleCount = 0;

        rows.forEach(function (row) {

            const rowText = row.textContent.toLowerCase();
            const matches = rowText.includes(searchValue);

            row.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }

        });

        if (noSearchMessage) {
            noSearchMessage.hidden =
                visibleCount !== 0 || searchValue === "";
        }

    });

});
