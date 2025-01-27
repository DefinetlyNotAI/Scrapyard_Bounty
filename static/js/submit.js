document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        const flagInput = document.getElementById('flag');
        if (flagInput.value.trim() === '') {
            event.preventDefault();
            alert('Please enter a flag.');
        }
    });
});
