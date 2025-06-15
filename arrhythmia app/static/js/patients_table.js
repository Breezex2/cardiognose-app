window.initializePatientsTable = function () {
  const searchInput = document.getElementById("searchForPatientsInput");
  const resultsDiv = document.getElementById("page-content");
  let currentQuery = "";
  let currentPage = 1;

  // Load search results from backend (with pagination)
  const fetchResults = function (query, page = 1) {
    currentQuery = query;
    currentPage = page;
    fetch(`/search_patients?q=${encodeURIComponent(query)}&page=${page}`, {
      credentials: "include", // This sends cookies/session data
    })
      .then((response) => response.text())
      .then((html) => {
        resultsDiv.innerHTML = html;
        attachPaginationHandlers(); // Re-attach click events to new buttons
        attachProfileHandlers();
      })
      .catch((error) => {
        console.error("Search error:", error);
        resultsDiv.innerHTML = "<p>Error searching patients.</p>";
      });
  };

  // Attach event listeners to pagination buttons
  function attachPaginationHandlers() {
    document.querySelectorAll(".pagination-link").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const page = parseInt(btn.dataset.page);
        fetchResults(currentQuery, page);
      });
    });
  }

  function attachProfileHandlers() {
    document.querySelectorAll(".load-profile").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        if (typeof window.loadPage === "function") {
          window.loadPage(`patient_profile?id=${id}`);
        } else {
          console.error("loadPage function not found.");
          window.location.href = `/patient/${id}`;
        }
      });
    });
  }

  // Initial load and event listener attachment
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const query = searchInput.value.trim();
      fetchResults(query, 1); // Always start from page 1 on new search
    });
  }
  fetchResults("", 1); // Initial load of all patients

  // Re-attach handlers if the page content changes (e.g., after initial load or search)
  document.removeEventListener("htmx:afterSwap", attachPaginationHandlers); // Remove old listener
  document.removeEventListener("htmx:afterSwap", attachProfileHandlers); // Remove old listener
  document.addEventListener("htmx:afterSwap", () => {
    attachPaginationHandlers();
    attachProfileHandlers();
  });
};
