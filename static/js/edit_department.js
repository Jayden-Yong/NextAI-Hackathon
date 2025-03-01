document.addEventListener("DOMContentLoaded", function(){
    deptDB = JSON.parse(document.getElementById('deptDB_json').textContent);
    deptData = JSON.parse(document.getElementById('deptData_json').textContent);
});

function validation(){
    let isValid = true;

    const id = document.getElementById("id-input").value;
    const name = document.getElementById("name-input").value;

    document.getElementById("idError").textContent = "";
    document.getElementById("nameError").textContent = "";

    if (id == ""){
        isValid = false;
        document.getElementById("idError").textContent = "Please enter an ID.";
    } else if (id != deptData.departmentID) {
        for (let dept of deptDB){
            if (id == dept.departmentID){
                isValid = false;
                document.getElementById("idError").textContent = "This ID already exists.";
                break;
            }
        }
    }

    if (name == ""){
        isValid = false;
        document.getElementById("nameError").textContent = "Please enter employee name.";
    }

    return isValid;
}