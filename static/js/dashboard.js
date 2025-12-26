// Toggle mobile menu
document
  .getElementById("mobile-menu-button")
  ?.addEventListener("click", function () {
    document.querySelector("aside").classList.toggle("hidden");
  });

// Toggle user dropdown
const userMenuButton = document.getElementById("user-menu-button");
const userDropdown = document.getElementById("user-dropdown");

if (userMenuButton && userDropdown) {
  userMenuButton.addEventListener("click", function (e) {
    e.stopPropagation();
    userDropdown.classList.toggle("hidden");
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function () {
    userDropdown.classList.add("hidden");
  });

  userDropdown.addEventListener("click", function (e) {
    e.stopPropagation();
  });
}

// Notification dropdown
const notificationButton = document.getElementById("notification-button");
if (notificationButton) {
  notificationButton.addEventListener("click", function () {
    // Implement notification dropdown
    alert("Notifications feature coming soon!");
  });
}

// Initialize tooltips
function initTooltips() {
  const tooltips = document.querySelectorAll("[data-tooltip]");
  tooltips.forEach((el) => {
    el.addEventListener("mouseenter", function () {
      const tooltip = document.createElement("div");
      tooltip.className =
        "absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg";
      tooltip.textContent = this.dataset.tooltip;
      document.body.appendChild(tooltip);

      const rect = this.getBoundingClientRect();
      tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + "px";
      tooltip.style.left =
        rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px";

      this._tooltip = tooltip;
    });

    el.addEventListener("mouseleave", function () {
      if (this._tooltip) {
        this._tooltip.remove();
      }
    });
  });
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initTooltips();

  // Update current time
  function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    const timeElement = document.getElementById("current-time");
    if (timeElement) {
      timeElement.textContent = timeString;
    }
  }

  updateTime();
  setInterval(updateTime, 60000);
});
