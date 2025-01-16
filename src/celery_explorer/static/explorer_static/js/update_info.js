async function updateField() {
    var selectElement = document.getElementById("id_task_name");
    var selectedValue = selectElement.value;
    if (selectedValue != "------"){
    const response = await fetch(`/celery_explorer/task_detail?name=${selectedValue}`);
    const data = await response.json();
    document.getElementById("description").textContent = data.description;
    document.getElementById("signature").textContent = data.signature;}
    else {
        document.getElementById("description").textContent = "";
    document.getElementById("signature").textContent = "";
    }
}

var selectElement = document.getElementById("id_task_name");
selectElement.addEventListener("change", updateField);