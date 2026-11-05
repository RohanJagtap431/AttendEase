
document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("attendanceSearch");
    const statusFilter = document.getElementById("statusFilter");
    const table = document.getElementById("attendanceTable");

    if (!searchInput || !statusFilter || !table) {
        return;
    }

    const rows = table.querySelectorAll("tbody tr[data-status]");
    const noResults = document.getElementById("noSearchResults");

    function filterAttendance() {

        const searchValue = searchInput.value.toLowerCase().trim();
        const selectedStatus = statusFilter.value.toLowerCase();

        let visibleCount = 0;

        rows.forEach(function (row) {

            const rowText = row.textContent.toLowerCase();
            const rowStatus = row.dataset.status.toLowerCase();

            const matchesSearch = rowText.includes(searchValue);

            const matchesStatus =
                selectedStatus === "" || rowStatus === selectedStatus;

            if (matchesSearch && matchesStatus) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }

        });

        if (noResults) {
            noResults.style.display = visibleCount === 0 ? "" : "none";
        }
    }

    searchInput.addEventListener("input", filterAttendance);
    statusFilter.addEventListener("change", filterAttendance);

});
