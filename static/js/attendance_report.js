
document.addEventListener("DOMContentLoaded", function () {

    // Student Search
    const searchInput = document.getElementById("studentSearch");
    const rows = document.querySelectorAll(".report-row");

    if (searchInput) {
        searchInput.addEventListener("input", function () {

            const search = this.value.toLowerCase().trim();

            rows.forEach(row => {
                const studentData = row.textContent.toLowerCase();

                row.style.display = studentData.includes(search)
                    ? ""
                    : "none";
            });
        });
    }

    // Attendance Progress Bars
    document.querySelectorAll(".percentage-fill").forEach(bar => {

        const percentage = Number(bar.dataset.percentage) || 0;

        const safePercentage = Math.min(
            Math.max(percentage, 0),
            100
        );

        bar.style.width = safePercentage + "%";
    });

});
