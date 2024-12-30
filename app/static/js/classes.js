document.getElementById('submitCodeBtn').addEventListener('click', function() {
    const formData = new FormData(document.getElementById('secretCodeForm'));

    fetch('class/new', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token() }}'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});