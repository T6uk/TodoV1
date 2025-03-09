document.getElementById('pickFoodBtn').addEventListener('click', function() {
    // Get selected category and type
    const category = document.getElementById('categorySelector').value;
    const type = document.getElementById('typeSelector').value;

    // Make an AJAX request to the backend
    fetch(`/get_foods/${category}/${type}`)
        .then(response => response.json())
        .then(foods => {
            if (foods.length === 0) {
                alert('No foods found with the selected criteria.');
                return;
            }

            // Pick a random food
            const randomFood = foods[Math.floor(Math.random() * foods.length)];

            // Display the result in the modal
            const congratsMessage = document.getElementById('congratsMessage');
            congratsMessage.textContent = `Söögiks osutus: ${randomFood.name}`;

            // Show the modal
            const congratsModal = new bootstrap.Modal(document.getElementById('congratsModal'));
            congratsModal.show();
        })
        .catch(error => {
            console.error('Error fetching foods:', error);
            alert('An error occurred while fetching foods.');
        });
});