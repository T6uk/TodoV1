// Ensure Bootstrap modal functionality is used
function openAddChallengeModal() {
    let modal = new bootstrap.Modal(document.getElementById('addChallengeModal'));
    modal.show();
}

function closeAddChallengeModal() {
    let modal = bootstrap.Modal.getInstance(document.getElementById('addChallengeModal'));
    modal.hide();
}

function addChallenge() {
    const name = document.getElementById('challengeName').value;
    const description = document.getElementById('challengeDescriptionInput').value;
    const start_time = document.getElementById('startTime').value;
    const end_time = document.getElementById('endTime').value;
    const participants = document.getElementById('participants').value;

    fetch('/add_challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, start_time, end_time, participants })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        renderChallenges();
        closeAddChallengeModal();
    });
}

function openChallengeModal(id) {
    fetch(`/fetch_challenge_details/${id}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('challengeTitle').textContent = data.name;
        document.getElementById('challengeDescription').textContent = data.description;
        currentChallengeId = id;
        let modal = new bootstrap.Modal(document.getElementById('challengeModal'));
        modal.show();
    });
}

function deleteChallenge(id) {
    if (confirm('Are you sure you want to delete this challenge?')) {
        fetch(`/delete_challenge/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            renderChallenges();
        });
    }
}

function deletePermChallenge(id) {
    if (confirm('Are you sure you want to delete this challenge?')) {
        fetch(`/delete_perm_challenge/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            renderChallenges();
        });
    }
}

function renderChallenges() {
    fetch('/fetch_challenges')
    .then(response => response.json())
    .then(data => {
        const activeGrid = document.getElementById('challengeGrid');
        const completedGrid = document.getElementById('completed-challenges-list');
        const deletedGrid = document.getElementById('deletedChallengeGrid');
        activeGrid.innerHTML = completedGrid.innerHTML = deletedGrid.innerHTML = '';

    data.forEach(challenge => {
        const card = document.createElement('div');
        card.className = 'col col-lg-2 card p-3 m-2';
        card.onclick = () => openChallengeModal(challenge.id);

        const now = new Date(), startTime = new Date(challenge.start_time), endTime = new Date(challenge.end_time);
        let statusMessage = now < startTime ? `Algab: ${getTimeDifference(now, startTime)}`
                           : now < endTime ? `Lõppeb: ${getTimeDifference(now, endTime)}`
                           : 'Tehtud';

        let deleteButton = challenge.deleted === "yes"
            ? `<button class='btn btn-danger btn-sm' onclick='deletePermChallenge(${challenge.id}, event)'>Permanent Delete</button>`
            : `<button class='btn btn-danger btn-sm' onclick='deleteChallenge(${challenge.id}, event)'>Delete</button>`;

        card.innerHTML = `<h5>${challenge.name}</h5>
                          <p class='text-muted'>Osalejad: ${challenge.participants}</p>
                          <p>${statusMessage}</p>
                          ${deleteButton}`;

        (challenge.deleted === "yes" ? deletedGrid
        : challenge.completed === "yes" ? completedGrid
        : activeGrid).appendChild(card);
    });
    });
}

function getTimeDifference(currentTime, targetTime) {
    const diff = targetTime - currentTime;
    return `${Math.floor(diff / (1000 * 60 * 60 * 24))}d ${Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))}h ${Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))}m`;
}

function openEditChallengeModal() {
    let modal = new bootstrap.Modal(document.getElementById('editChallengeModal'));
    modal.show();
    fetch(`/fetch_challenge_details/${currentChallengeId}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('editChallengeName').value = data.name;
        document.getElementById('editChallengeDescription').value = data.description;
        document.getElementById('editStartTime').value = data.start_time;
        document.getElementById('editEndTime').value = data.end_time;
        document.getElementById('editParticipants').value = data.participants;
    });
}

function closeEditChallengeModal() {
    let modal = bootstrap.Modal.getInstance(document.getElementById('editChallengeModal'));
    modal.hide();
}

function saveChallengeEdit() {
    const name = document.getElementById('editChallengeName').value;
    const description = document.getElementById('editChallengeDescription').value;
    const start_time = document.getElementById('editStartTime').value;
    const end_time = document.getElementById('editEndTime').value;
    const participants = document.getElementById('editParticipants').value;

    fetch(`/edit_challenge/${currentChallengeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, start_time, end_time, participants })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        renderChallenges();
        closeEditChallengeModal();
    });
}

function openTab(evt, tabName) {
    document.querySelectorAll('.tabcontent').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('.tablink').forEach(link => link.classList.remove('active'));
    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.classList.add('active');
}

function checkAndMoveCompletedChallenges() {
    fetch('/update_completed_challenges', { method: 'POST' })
    .then(response => response.json())
    .then(() => refreshChallenges())
    .catch(error => console.error('Error updating completed challenges:', error));
}

function refreshChallenges() {
    fetch('/fetch_challenges')
    .then(response => response.json())
    .then(challenges => {
        document.getElementById('challenge-list').innerHTML = '';
        document.getElementById('completed-challenges-list').innerHTML = '';
        challenges.forEach(challenge => {
            let challengeElement = document.createElement('div');
            challengeElement.className = 'list-group-item';
            challengeElement.textContent = `${challenge.name} - ${challenge.description}`;
            (challenge.completed === 'yes' ? document.getElementById('completed-challenges-list') : document.getElementById('challenge-list')).appendChild(challengeElement);
        });
    })
    .catch(error => console.error('Error fetching challenges:', error));
}

setInterval(checkAndMoveCompletedChallenges, 5000);

document.addEventListener('DOMContentLoaded', renderChallenges);
