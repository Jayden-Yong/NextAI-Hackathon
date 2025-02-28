document.addEventListener("DOMContentLoaded", function () {
    const editBtn = document.getElementById("edit-btn");
    const saveBtn = document.getElementById("save-btn");
    const inputs = document.querySelectorAll("input:not([readonly]) , input:disabled"); // Editable inputs

    editBtn.addEventListener("click", function () {
        inputs.forEach(input => input.removeAttribute("disabled"));  // Enable fields
        editBtn.classList.add("d-none");  // Hide edit button
        saveBtn.classList.remove("d-none");  // Show save button
    });

    saveBtn.addEventListener("click", function () {
        const first_name = document.getElementById("first_name").value;
        const last_name = document.getElementById("last_name").value;
        const email = document.getElementById("email").value;
        const department_name = document.getElementById("department-name").value;
        const id = document.getElementById("id").value;
        const prefDays = document.getElementById("preference-day").value;
        console.log("Sending data:", { first_name, last_name, email, id, department_name, prefDays }); // Debugging

        fetch("/update_employee_profile", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ first_name, last_name, email, id, department_name , prefDays })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Profile updated successfully!");
                document.getElementById("name-display").textContent = first_name + " " + last_name;
                document.getElementById("department-name-display").textContent = department_name;

                // Disable fields again
                inputs.forEach(input => input.setAttribute("disabled", "true"));

                saveBtn.classList.add("d-none");  // Hide save button
                editBtn.classList.remove("d-none");  // Show edit button
            } else {
                alert("Error updating profile!");
            }
        })
        .catch(error => console.error("Error:", error));
    });
});