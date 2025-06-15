async function change_password() {
  const passwordInput = document.getElementById("new_password");
  const newPassword = passwordInput.value;
  const responseDiv = document.getElementById("response");

  try {
    const response = await fetch("/change-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include", // include cookies
      body: JSON.stringify({ new_password: newPassword })
    });

    const resultText = await response.text();
    let result;
    try {
      result = JSON.parse(resultText);
    } catch {
      throw new Error(resultText);
    }

    if (response.ok) {
      responseDiv.innerHTML = `<span style="color:green;">${result.message}</span>`;
      passwordInput.value = "";
    } else {
      responseDiv.innerHTML = `<span style="color:red;">${result.detail || result.message || "Error occurred"}</span>`;
    }

  } catch (error) {
    responseDiv.innerHTML = `<span style="color:red;">Request failed: ${error.message}</span>`;
  }
}
