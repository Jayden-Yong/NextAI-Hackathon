document.addEventListener("DOMContentLoaded", function() {
    const editBtn = document.getElementById("password-edit-btn");
    const passwordForm = document.getElementById("password-form");
    const saveBtn = document.getElementById("password-save-btn");
    const newPasswordInput = document.getElementById("new-password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const toggleNewPassword = document.getElementById("toggle-new-password");
    const toggleConfirmPassword = document.getElementById("toggle-confirm-password");

    // When Edit is clicked, show the form and hide the button
    editBtn.addEventListener("click", function() {
        passwordForm.style.display = "block";
        editBtn.style.display = "none";
    });

    // Toggle visibility of new password
    toggleNewPassword.addEventListener("change", function() {
        newPasswordInput.type = this.checked ? "text" : "password";
    });

    // Toggle visibility of confirm password
    toggleConfirmPassword.addEventListener("change", function() {
        confirmPasswordInput.type = this.checked ? "text" : "password";
    });

    // Function to validate password strength
    function isStrongPassword(password) {
        // Must be at least 8 characters and include letters and numbers
        const regex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        return regex.test(password);
    }

    // Handle Save button click
    saveBtn.addEventListener("click", function() {
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Validate that the two passwords match
        if(newPassword !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }
        // Validate password strength
        if(!isStrongPassword(newPassword)) {
            alert("Password is too weak! It must be at least 8 characters long and include both letters and numbers.");
            return;
        }
        // Ask for confirmation before proceeding
        if(!confirm("Are you sure you want to change your password?")) {
            return;
        }

        // Send new password to the backend using Fetch API
        fetch("/change_password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ new_password: newPassword })
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert("Password changed successfully!");
                // Hide form and show Edit button again
                passwordForm.style.display = "none";
                editBtn.style.display = "block";
                // Optionally clear the inputs
                newPasswordInput.value = "";
                confirmPasswordInput.value = "";
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while changing the password.");
        });
    });
});
