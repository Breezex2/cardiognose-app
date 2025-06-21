// static/js/analytics.js

// Function to fetch data from the API
async function fetchAnalyticsData() {
  try {
    const response = await fetch("/api/patient-status", {
      credentials: "include",
    });
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error(
          "Access Denied: You must be logged in as a doctor to view analytics."
        );
      } else {
        throw new Error("Network response was not ok: " + response.statusText);
      }
    }
    const rawData = await response.json();

    // Process rawData to get age_distribution and arrhythmia_distribution
    const ageGroups = { "0-20": 0, "21-40": 0, "41-60": 0, "61+": 0 };
    const arrhythmiaStats = {};

    const currentYear = new Date().getFullYear();

    rawData.forEach((patient) => {
      // Age distribution
      if (patient.dob) {
        const birthYear = new Date(patient.dob).getFullYear();
        const age = currentYear - birthYear;
        if (age <= 20) ageGroups["0-20"]++;
        else if (age <= 40) ageGroups["21-40"]++;
        else if (age <= 60) ageGroups["41-60"]++;
        else ageGroups["61+"]++;
      }

      // Arrhythmia status distribution
      if (patient.status) {
        arrhythmiaStats[patient.status] =
          (arrhythmiaStats[patient.status] || 0) + 1;
      }
    });

    return {
      age_distribution: ageGroups,
      arrhythmia_distribution: arrhythmiaStats,
    };
  } catch (error) {
    console.error("Error fetching analytics data:", error);
    showError(
      error.message || "Failed to load analytics data. Please try again later."
    );
    return null;
  }
}

// Function to show error message
function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
  setTimeout(() => errorDiv.remove(), 5000);
}

// Function to create age distribution chart
function createAgeDistributionChart(data) {
  const ageData = Object.entries(data.age_distribution).map(
    ([ageGroup, count]) => ({
      name: ageGroup,
      y: count,
    })
  );

  JSC.chart("ageChartDiv", {
    type: "column",
    title_label_text: "Patient Age Distribution",
    legend_visible: false,
    yAxis_label_text: "Number of Patients",
    xAxis_label_text: "Age Groups",
    series: [
      {
        name: "Age Groups",
        points: ageData,
      },
    ],
    // toolbar_items: {
    //   "change chart type": {
    //     type: "select",
    //     position: "inside top left",
    //     value: "Column",
    //     items: ["Column", "Line", "Area"],
    //     events_change: function (val) {
    //       this.options({ type: val.toLowerCase() });
    //     },
    //   },
    // },
  });
}

// Function to create arrhythmia distribution chart
function createArrhythmiaChart(data) {
  const arrhythmiaData = Object.entries(data.arrhythmia_distribution).map(
    ([status, count]) => ({
      name: status,
      y: count,
    })
  );

  JSC.chart("arrhythmiaChartDiv", {
    type: "pie",
    title_label_text: "Arrhythmia Status Distribution",
    legend_visible: true,
    series: [
      {
        name: "Arrhythmia Types",
        points: arrhythmiaData,
      },
    ],
    // toolbar_items: {
    //   "change chart type": {
    //     type: "select",
    //     position: "inside top left",
    //     value: "Pie",
    //     items: ["Pie", "Donut"],
    //     events_change: function (val) {
    //       this.options({ type: val === "Donut" ? "pie donut" : "pie" });
    //     },
    //   },
    // },
  });
}

// Function to show loading state
function showLoading() {
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "loading";
  loadingDiv.textContent = "Loading analytics data...";
  document.body.appendChild(loadingDiv);
  return loadingDiv;
}

// Function to hide loading state
function hideLoading(loadingDiv) {
  if (loadingDiv) {
    loadingDiv.remove();
  }
}

// Make initializeCharts globally accessible
window.initializeAnalyticsCharts = async function () {
  const loadingDiv = showLoading();
  try {
    const data = await fetchAnalyticsData();
    if (data) {
      createAgeDistributionChart(data);
      createArrhythmiaChart(data);
    }
  } catch (error) {
    console.error("Error initializing charts:", error);
    showError("Failed to initialize charts. Please refresh the page.");
  } finally {
    hideLoading(loadingDiv);
  }
};

// Add refresh button functionality - this button will now call the global function
function addRefreshButton() {
  const refreshButton = document.createElement("button");
  refreshButton.className = "refresh-button";
  refreshButton.textContent = "Refresh Data";
  refreshButton.style = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    padding: 10px 15px;
    background-color: #03989e; /* teal-500 */
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  `;
  refreshButton.onclick = window.initializeAnalyticsCharts;
  document.body.appendChild(refreshButton);

  // Remove the button if the analytics page is unloaded
  // Deprecated DOMSubtreeModified replaced with MutationObserver
  const pageContentObserver = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.type === "childList" && mutation.removedNodes.length > 0) {
        const analyticsContainerRemoved = Array.from(
          mutation.removedNodes
        ).some(
          (node) =>
            node.nodeType === 1 &&
            node.querySelector(".analytics-chart-container")
        );

        if (
          analyticsContainerRemoved ||
          !document.querySelector(".analytics-chart-container")
        ) {
          const existingButton = document.querySelector(".refresh-button");
          if (existingButton) {
            existingButton.remove();
            pageContentObserver.disconnect(); // Disconnect once button is removed
          }
        }
      }
    });
  });

  // Start observing the #page-content div
  const pageContentDiv = document.getElementById("page-content");
  if (pageContentDiv) {
    pageContentObserver.observe(pageContentDiv, {
      childList: true,
      subtree: true,
    });
  }
}

// Initial setup when analytics.js is loaded, only if not already initialized via loadPage
// This DCL is a fallback or for direct access, but loadPage will trigger the global function.
// This part of the script runs only once when analytics.js is first parsed by the browser.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", addRefreshButton);
} else {
  addRefreshButton();
}
