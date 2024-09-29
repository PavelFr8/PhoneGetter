document.getElementById('submitCodeBtn').addEventListener('click', function() {
    const formData = new FormData(document.getElementById('secretCodeForm'));

    fetch('class/new', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token() }}'  // Добавляем CSRF токен в заголовок
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);  // Показать сообщение об успехе
            location.reload();  // Обновить страницу или добавить другую логику
        } else {
            alert(data.message);  // Показать сообщение об ошибке
        }
    })
    .catch(error => console.error('Error:', error));
});