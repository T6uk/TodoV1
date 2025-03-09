document.addEventListener("DOMContentLoaded", getRandomFact);

function getRandomFact() {
    fetch("/random_fact")
        .then(response => response.json())
        .then(data => {
            document.getElementById("fact-text").textContent = data.fact;
        })
        .catch(error => console.error("Error fetching fact:", error));
}