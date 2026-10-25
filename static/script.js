
document.addEventListener("DOMContentLoaded", function () {
    // MOBILE NAVIGATION
    const menuToggle = document.getElementById("menuToggle");
    const navLinks = document.getElementById("navLinks");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", function () {
            const isOpen = navLinks.classList.toggle("open");

            menuToggle.setAttribute("aria-expanded", String(isOpen));
            menuToggle.setAttribute(
                "aria-label",
                isOpen ? "Close navigation menu" : "Open navigation menu"
            );

            menuToggle.textContent = isOpen ? "✕" : "☰";
        });

        navLinks.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                navLinks.classList.remove("open");
                menuToggle.setAttribute("aria-expanded", "false");
                menuToggle.setAttribute(
                    "aria-label",
                    "Open navigation menu"
                );
                menuToggle.textContent = "☰";
            });
        });
    }

    // REPORT POPUP
    const reportModal = document.getElementById("reportModal");
    const closeReportButton = document.getElementById("closeReportModal");

    if (reportModal && closeReportButton) {
        closeReportButton.addEventListener("click", function () {
            if (typeof window.closeReportModal === "function") {
                window.closeReportModal();
            }
        });

        reportModal.addEventListener("click", function (event) {
            if (event.target.classList.contains("modal-backdrop")) {
                if (typeof window.closeReportModal === "function") {
                    window.closeReportModal();
                }
            }
        });
    }
});
