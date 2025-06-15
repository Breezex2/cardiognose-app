function editProperty(spn) {
  const prop_name = spn.dataset.prop_name;
  const prop_value = spn.dataset.prop_value;

  // Create overlay
  const overlay = document.createElement("div");
  overlay.style = `
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = () => document.body.removeChild(overlay);

  // Create popup
  const popup = document.createElement("div");
  popup.style = `
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    width: 400px;
    height: 200px;
    position: fixed;
    top: 30%; left: 50%;
    transform: translate(-50%, -30%);
    background: white;
    border: 1px solid #ccc;
    padding: 20px;
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
  `;
  popup.onclick = (event) => {
    event.stopPropagation(); // prevent overlay click when interacting with popup
  };

  const label = document.createElement("label");
  label.textContent = prop_name;
  label.style = "font-size:12px; color:#474747";
  popup.appendChild(label);

  const input = document.createElement("input");
  let select; // Outer scope for select element

  // Create appropriate input/select based on property name
  if (prop_name === "Fullname") {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 12;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    input.addEventListener("input", function () {
      this.value = this.value.replace(/[^a-zA-Z\s]/g, ""); // allow only letters and spaces
    });
    popup.appendChild(input);
  } else if (prop_name === "Password") {
    input.type = "text";
    input.value = "";
    input.maxLength = 10;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Phone number") {
    input.type = "tel";
    input.value = prop_value;
    input.maxLength = 8;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Date of birth") {
    input.type = "date";
    input.value = prop_value;
    input.max = new Date().toISOString().split("T")[0];
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Email") {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 64;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    input.addEventListener("blur", function () {
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
      if (!isValid && this.value.trim() !== "") {
        alert("Please enter a valid email address.");
      }
    });
    popup.appendChild(input);
  } else if (prop_name === "Address") {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 80;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Role") {
    select = document.createElement("select");
    select.style = "margin:10px 0; display:block; padding: 6px;";
    select.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";

    const options = ["doctor", "admin"];
    options.forEach((optionText) => {
      const option = document.createElement("option");
      option.value = optionText;
      option.textContent = optionText;
      if (prop_value === optionText) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    popup.appendChild(select);
  } else if (prop_name === "is Active") {
    select = document.createElement("select"); // assign to outer select
    select.style = "margin:10px 0; display:block; padding: 6px;";
    select.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";

    const options = [
      { value: 1, label: "Yes" },
      { value: 0, label: "No" },
    ];

    options.forEach((opt) => {
      const option = document.createElement("option");
      option.value = opt.value;
      option.textContent = opt.label;
      if (prop_value == opt.value) {
        // use == to match "1" and 1
        option.selected = true;
      }
      select.appendChild(option);
    });
    popup.appendChild(select);
  }

  const button = document.createElement("button");
  button.textContent = "Save";
  button.style = "padding:5px 10px; text-align: left;";
  button.className =
    "w-full px-4 py-2 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-teal-500 border border-transparent rounded-lg active:bg-teal-500 hover:bg-teal-600 focus:outline-none focus:shadow-outline-teal";

  button.onclick = () => {
    let value;

    if (prop_name === "Role" || prop_name === "is Active") {
      value = select.value;
      if (prop_name === "is Active") {
        value = value === "1" ? "1" : "0";
      }
    } else {
      value = input.value.trim();
    }

    const formattedProp = prop_name.trim().replace(/\s+/g, "_").toLowerCase();

    const data = {
      user_id: spn.dataset.userId,
      prop: formattedProp,
      value: value,
    };

    fetch("/update-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(data),
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json();
          console.error("Update error:", err);
          alert("Update failed: " + (err.detail || res.statusText));
          return;
        }

        document.body.removeChild(overlay);
        fetch(`/user/${spn.dataset.userId}`)
          .then((res) => res.text())
          .then((html) => {
            resultsDiv.innerHTML = html;
          })
          .catch((err) => {
            console.error("Error loading profile:", err);
            resultsDiv.innerHTML = "<p>Error loading user profile.</p>";
          });
      })
      .catch((err) => {
        console.error("Error:", err);
        alert("An error occurred.");
      });
  };

  popup.appendChild(button);
  overlay.appendChild(popup);
  document.body.appendChild(overlay);

  // Input mask for telephone inputs
  if (input.type === "tel") {
    input.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "");
    });
  }
}

function deleteUser(id) {
  if (!confirm("Are you sure you want to delete this user?")) return;

  fetch(`/delete-user/${id}`, {
    method: "DELETE",
  })
    .then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to delete user");
      }
      return response.json();
    })
    .then((data) => {
      fetchResults("", 1); // Refresh the list after deletion
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
}
