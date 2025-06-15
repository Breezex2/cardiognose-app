function data() {
  function getThemeFromLocalStorage() {
    // if user already changed the theme, use it
    if (window.localStorage.getItem("dark")) {
      return JSON.parse(window.localStorage.getItem("dark"));
    }

    // else return their preferences
    return (
      !!window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  function setThemeToLocalStorage(value) {
    window.localStorage.setItem("dark", value);
  }

  return {
    dark: getThemeFromLocalStorage(),
    toggleTheme() {
      this.dark = !this.dark;
      setThemeToLocalStorage(this.dark);
    },
    isSideMenuOpen: false,
    toggleSideMenu() {
      this.isSideMenuOpen = !this.isSideMenuOpen;
    },
    closeSideMenu() {
      this.isSideMenuOpen = false;
    },
    isNotificationsMenuOpen: false,
    toggleNotificationsMenu() {
      this.isNotificationsMenuOpen = !this.isNotificationsMenuOpen;
    },
    closeNotificationsMenu() {
      this.isNotificationsMenuOpen = false;
    },
    isProfileMenuOpen: false,
    toggleProfileMenu() {
      this.isProfileMenuOpen = !this.isProfileMenuOpen;
    },
    closeProfileMenu() {
      this.isProfileMenuOpen = false;
    },
    isPagesMenuOpen: false,
    togglePagesMenu() {
      this.isPagesMenuOpen = !this.isPagesMenuOpen;
    },
    // Modal
    isModalOpen: false,
    trapCleanup: null,
    openModal() {
      this.isModalOpen = true;
      this.trapCleanup = focusTrap(document.querySelector("#modal"));
    },
    closeModal() {
      this.isModalOpen = false;
      this.trapCleanup();
    },
  };
}

// Function to dynamically load pages (made global)
window.loadPage = async function (pageName) {
  const contentDiv = document.getElementById("page-content");
  if (contentDiv) {
    let fetchUrl;
    const pageType = pageName.split("?")[0]; // Extract page type without query params

    // Define which pages are served by FastAPI endpoints and which are static HTML
    const fastapiPages = ["patients_table", "patient_profile"];

    if (fastapiPages.includes(pageType)) {
      if (pageType === "patients_table") {
        fetchUrl = "/search_patients";
      } else if (pageType === "patient_profile") {
        const urlParams = new URLSearchParams(pageName.split("?")[1]);
        const patientId = urlParams.get("id");
        if (patientId) {
          fetchUrl = `/patient/${patientId}`;
        } else {
          console.error("Patient ID not found for patient_profile page.");
          contentDiv.innerHTML =
            '<p style="color: red; text-align: center;">Error: Patient ID missing.</p>';
          return;
        }
      }
    } else {
      // Assume it's a static HTML page
      fetchUrl = `/static/pages/${pageType}.html`;
    }

    try {
      // Remove existing page-specific scripts before loading new content
      document.querySelectorAll('script[src*="/static/js/"]').forEach((s) => {
        if (
          !s.src.includes("init-alpine.js") &&
          !s.src.includes("analytics.js")
        ) {
          s.remove();
        }
      });

      const response = await fetch(fetchUrl, { credentials: "include" });
      if (!response.ok) {
        throw new Error(`Failed to load ${pageName}: ${response.statusText}`);
      }
      const html = await response.text();
      contentDiv.innerHTML = html;

      // Dynamically load page-specific JavaScript
      let scriptSrc = "";
      if (pageType === "patients_table") {
        scriptSrc = "/static/js/patients_table.js";
      } else if (pageType === "patient_profile") {
        scriptSrc = "/static/js/patient_profile.js";
      } else if (pageType === "create_patient_profile") {
        scriptSrc = "/static/js/create_patient_profile.js";
      } else if (pageType === "change_password") {
        scriptSrc = "/static/js/change_password.js";
      } else if (pageType === "users_table") {
        scriptSrc = "/static/js/users_table.js";
      } else if (pageType === "user_profile") {
        scriptSrc = "/static/js/user_profile.js";
      }

      if (scriptSrc) {
        const scriptElement = document.createElement("script");
        scriptElement.src = scriptSrc;
        scriptElement.onload = () => {
          // Call specific initialization functions after content and script are loaded
          if (
            pageType === "patients_table" &&
            typeof window.initializePatientsTable === "function"
          ) {
            window.initializePatientsTable(); // Correctly call the initialization function
          } else if (
            pageType === "analytics" &&
            typeof window.initializeAnalyticsCharts === "function"
          ) {
            window.initializeAnalyticsCharts(); // Initialize analytics charts
          } else if (
            pageType === "patient_profile" &&
            typeof window.initializePatientProfile === "function"
          ) {
            window.initializePatientProfile();
          } else if (
            pageType === "create_patient_profile" &&
            typeof window.initializeCreatePatientProfile === "function"
          ) {
            window.initializeCreatePatientProfile();
          } else if (
            pageType === "change_password" &&
            typeof window.initializeChangePassword === "function"
          ) {
            window.initializeChangePassword();
          } else if (
            pageType === "users_table" &&
            typeof window.fetchUsers === "function"
          ) {
            window.fetchUsers("", 1);
          } else if (
            pageType === "user_profile" &&
            typeof window.initializeUserProfile === "function"
          ) {
            window.initializeUserProfile();
          }
        };
        document.body.appendChild(scriptElement);
      } else if (
        pageType === "analytics" &&
        typeof window.initializeAnalyticsCharts === "function"
      ) {
        window.initializeAnalyticsCharts();
      }
    } catch (error) {
      console.error("Error loading page:", error);
      contentDiv.innerHTML = `<p style="color: red; text-align: center;">Error loading page: ${error.message}</p>`;
    }
  }
};

// Helper function to set active link styling (made global)
window.setActiveLink = function (element) {
  // Remove active class from all links
  document.querySelectorAll("aside a").forEach((link) => {
    link.classList.remove("active", "dark:text-gray-100");
    const span = link.previousElementSibling;
    if (span && span.classList.contains("bg-teal-500")) {
      span.classList.remove("bg-teal-500");
    }
  });
  document.querySelectorAll("aside button").forEach((button) => {
    button.classList.remove("active");
  });

  // Add active class to the clicked link/button
  if (element.tagName === "BUTTON") {
    element.classList.add("active");
  } else {
    element.classList.add("active", "dark:text-gray-100");
    const span = element.previousElementSibling;
    if (span) {
      span.classList.add("bg-teal-500");
    }
  }
};

// Initial page load (centralized here)
document.addEventListener("DOMContentLoaded", () => {
  const hash = window.location.hash.substring(1);
  if (hash) {
    window.loadPage(hash);
    // Set active link for the current page
    const activeLink = document.querySelector(
      `a[onclick*="loadPage('${hash.split("?")[0]}')"]`
    );
    if (activeLink) {
      window.setActiveLink(activeLink);
    }
  } else {
    // Default to patients table
    window.loadPage("patients_table");
    const defaultLink = document.querySelector(
      "a[onclick*=\"loadPage('patients_table')\"]"
    );
    if (defaultLink) {
      window.setActiveLink(defaultLink);
    }
  }
});
