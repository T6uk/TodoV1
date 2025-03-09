document.addEventListener("DOMContentLoaded", function () {
    const mealTable = document.querySelector("#mealPlanner tbody");
    const editButton = document.getElementById("editMealPlan");
    const saveButton = document.getElementById("saveMealPlan");

    let editingEnabled = false;

    // Fetch and display saved meal plan
    function loadMealPlan() {
        fetch("/get_meal_plan")
            .then(response => response.json())
            .then(data => {
                console.log("Meal plan data received:", data); // Debugging line
                mealTable.innerHTML = ""; // Clear table before appending

                data.forEach(entry => {
                    console.log("Processing entry:", entry); // Debugging line
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${entry.day}</td>
                        <td>
                            <select class="mealSelect" data-type="breakfast" disabled>
                                <option value="${entry.breakfast || ""}">${entry.breakfast || "—"}</option>
                            </select>
                        </td>
                        <td>
                            <select class="mealSelect" data-type="lunch" disabled>
                                <option value="${entry.lunch || ""}">${entry.lunch || "—"}</option>
                            </select>
                        </td>
                        <td>
                            <select class="mealSelect" data-type="dinner" disabled>
                                <option value="${entry.dinner || ""}">${entry.dinner || "—"}</option>
                            </select>
                        </td>
                        <td>
                            <select class="mealSelect" data-type="snack" disabled>
                                <option value="${entry.snack || ""}">${entry.snack || "—"}</option>
                            </select>
                        </td>
                    `;
                    mealTable.appendChild(row);
                });
            })
            .catch(error => console.error("Error loading meal plan:", error));
    }

    loadMealPlan();

    loadMealPlan();

    // Enable editing
    editButton.addEventListener("click", function () {
        editingEnabled = !editingEnabled;

        document.querySelectorAll(".mealSelect").forEach(select => {
            select.disabled = !editingEnabled;

            if (editingEnabled) {
                const mealType = select.dataset.type;
                const currentValue = select.value; // Store selected value

                fetch(`/get_foods/all/${mealType}`)
                    .then(response => response.json())
                    .then(data => {
                        select.innerHTML = ""; // Clear existing options

                        // Add a default empty option
                        const defaultOption = document.createElement("option");
                        defaultOption.textContent = "—";
                        defaultOption.value = "";
                        select.appendChild(defaultOption);

                        // Populate dropdown with fetched options
                        data.forEach(food => {
                            const option = document.createElement("option");
                            option.value = food.name;
                            option.textContent = food.name;
                            select.appendChild(option);
                        });

                        // Restore previously selected value
                        select.value = currentValue || "";
                    })
                    .catch(error => console.error(`Error fetching ${mealType} options:`, error));
            }
        });

        saveButton.style.display = editingEnabled ? "inline-block" : "none";
        editButton.textContent = editingEnabled ? "Cancel" : "Edit";
    });

    // Save Meal Plan
    saveButton.addEventListener("click", function () {
    console.log("Save button clicked!");  // Debugging line

    const mealPlan = [];
    document.querySelectorAll("#mealPlanner tbody tr").forEach(row => {
        const day = row.cells[0].textContent;
        const meals = {
            day: day,
            breakfast: row.querySelector('.mealSelect[data-type="breakfast"]').value || null,
            lunch: row.querySelector('.mealSelect[data-type="lunch"]').value || null,
            dinner: row.querySelector('.mealSelect[data-type="dinner"]').value || null,
            snack: row.querySelector('.mealSelect[data-type="snack"]').value || null
        };
        mealPlan.push(meals);
    });

    console.log("Meal plan data being sent:", mealPlan);  // Debugging line

    fetch("/save_meal_plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mealPlan }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response received:", data);  // Debugging line
        alert(data.message);
        loadMealPlan();
        editingEnabled = false;
        editButton.textContent = "Edit";
        saveButton.style.display = "none";
    })
    .catch(error => console.error("Error saving meal plan:", error));
});
});
