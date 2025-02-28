document.addEventListener("DOMContentLoaded", function(){
    idList = JSON.parse(document.getElementById('id_json').textContent);
});

function validation(){
    let isValid = true;

    const id = document.getElementById("id-input").value;
    const password = document.getElementById("pw-input").value;
    const name = document.getElementById("name-input").value;
    const deptID = document.getElementById("dept-input").value;

    document.getElementById("idError").textContent = "";
    document.getElementById("passwordError").textContent = "";
    document.getElementById("nameError").textContent = "";
    document.getElementById("deptError").textContent = "";

    if (id == ""){
        isValid = false;
        document.getElementById("idError").textContent = "Please enter an ID.";
    } else {
        for (let employee of idList){
            console.log(employee)
            if (id == employee.employeeID){
                isValid = false;
                document.getElementById("idError").textContent = "This ID already exists.";
                break;
            }
        }
    }
    
    if (password.length < 8){
        isValid = false;
        document.getElementById("passwordError").textContent = "Password must be at least 8 characters long.";
    }

    if (name == ""){
        isValid = false;
        document.getElementById("nameError").textContent = "Please enter employee name.";
    }

    if (deptID == ""){
        isValid = false;
        document.getElementById("deptError").textContent = "Please select a department.";
    }

    return isValid;
}