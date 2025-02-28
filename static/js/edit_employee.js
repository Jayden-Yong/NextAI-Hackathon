document.addEventListener("DOMContentLoaded", function(){
    idList = JSON.parse(document.getElementById('id_json').textContent);
    data = JSON.parse(document.getElementById('data_json').textContent);
});

function validation(){
    let isValid = true;

    const id = document.getElementById("id-input").value;
    const name = document.getElementById("name-input").value;
    const deptID = document.getElementById("dept-input").value;
    const prefInput = document.getElementById("pref-input");

    document.getElementById("idError").textContent = "";
    document.getElementById("prefError").textContent = "";
    document.getElementById("nameError").textContent = "";
    document.getElementById("deptError").textContent = "";

    if (id == ""){
        isValid = false;
        document.getElementById("idError").textContent = "Please enter an ID.";
    } else if (id != data.employeeID) {
        for (let employee of idList){
            if (id == employee.employeeID){
                isValid = false;
                document.getElementById("idError").textContent = "This ID already exists.";
                break;
            }
        }
    }
    
    // Check if pref-input exists
    if (prefInput) {
        const pref = prefInput.value;
        if (pref === "") {
            isValid = false;
            document.getElementById("prefError").textContent = "Please select preferred in-office days.";
        }
    }

    if (name == ""){
        isValid = false;
        document.getElementById("nameError").textContent = "Please enter employee name.";
    }

    if (deptID == ""){
        isValid = false;
        document.getElementById("deptError").textContent = "Please select a department.";
    }

    console.log("Validation result:", isValid);

    return isValid;
}