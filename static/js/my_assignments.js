
document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("assignmentSearch");
    const cards = document.querySelectorAll(".my-assignment-card");
    const emptyMessage = document.getElementById("searchEmpty");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchValue = this.value.toLowerCase().trim();
        let visibleCount = 0;

        cards.forEach(function (card) {

            const cardText = card.textContent.toLowerCase();

            const matches = cardText.includes(searchValue);

            card.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }

        });

        if (emptyMessage) {
            emptyMessage.hidden = visibleCount !== 0;
        }

    });

});
