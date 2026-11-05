const rows = document.querySelectorAll("[data-student-row]");

function updateSummary() {
    let present = 0;
    let absent = 0;
    let late = 0;

    rows.forEach(row => {
        const input = row.querySelector(".status-input");
        const status = input.value;

        if (status === "present") present++;
        if (status === "absent") absent++;
        if (status === "late") late++;

        row.querySelectorAll(".status-btn").forEach(button => {
            button.classList.toggle(
                "selected",
                button.dataset.status === status
            );
        });
    });

    document.getElementById("presentCount").textContent = present;
    document.getElementById("absentCount").textContent = absent;
    document.getElementById("lateCount").textContent = late;
}

rows.forEach(row => {
    const input = row.querySelector(".status-input");
    const buttons = row.querySelectorAll(".status-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            input.value = button.dataset.status;
            updateSummary();
        });
    });
});

function setAllStatus(status) {
    rows.forEach(row => {
        row.querySelector(".status-input").value = status;
    });

    updateSummary();
}

document.getElementById("allPresentBtn")?.addEventListener("click", () => {
    setAllStatus("present");
});

document.getElementById("allAbsentBtn")?.addEventListener("click", () => {
    setAllStatus("absent");
});

updateSummary();