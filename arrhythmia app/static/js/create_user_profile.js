function create_new_user() {
    const form = document.getElementById('userCreateForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => data[key] = value);

    fetch('/create-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    })
    .then(async response => {
        if (!response.ok) {
            const errorData = await response.json();

            // Handle validation errors (422)
            if (response.status === 422) {
                const details = errorData.detail.map(d => `• ${d.loc.join('.')} - ${d.msg}`).join('\n');
                document.getElementById('response').innerText = "Validation Error:\n" + details;
            }

            // Handle custom error (e.g., 400 civil_id exists)
            else if (response.status === 400 || response.status === 500) {
                document.getElementById('response').innerText = "Error: " + errorData.detail;
            }

            throw new Error("Request failed");
        }

        return response.json();
    })
    .then(result => {
        // Load user profile
        fetch(`/user/${result.user_id}`)
            .then(res => res.text())
            .then(html => {
                resultsDiv.innerHTML = html;
            })
            .catch(err => {
                console.error("Error loading profile:", err);
                resultsDiv.innerHTML = "<p>Error loading user profile.</p>";
            });

        form.reset();
    })
    .catch(error => {
        console.error("Unhandled Error:", error);
    });
}
