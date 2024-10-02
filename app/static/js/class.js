function removeStudent(studentId) {
    const classId = document.getElementById("inviteModal").getAttribute("data-class-id");
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    if (!confirm('Are you sure you want to remove this student?')) {
        return;
    }

    fetch(`/classes/class/${classId}/remove/${studentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const row = document.querySelector(`tr[data-student-id="${studentId}"]`);
            if (row) {
                row.remove();
            }
        } else {
            console.error('Failed to remove student:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function copyInviteLink() {
    const copyText = document.getElementById("inviteLink");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
}

function generateInviteLink() {
    const classId = document.getElementById("inviteModal").getAttribute("data-class-id");
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    fetch(`/classes/class/generate_invite/${classId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const inviteLinkInput = document.getElementById("inviteLink");
        inviteLinkInput.value = data.link;
    })
    .catch(error => console.error('Error:', error));
}

document.getElementById("inviteModal").addEventListener("show.bs.modal", generateInviteLink);