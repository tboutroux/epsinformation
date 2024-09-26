function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const type = field.getAttribute('type') === 'password' ? 'text' : 'password';
    field.setAttribute('type', type);
    }

    document.querySelector('form').addEventListener('submit', function(event) {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    if (password !== confirmPassword) {
        event.preventDefault();
        document.getElementById('password-error').style.display = 'block';
    }
    });

let dateDiv = document.getElementById('date');
let typeInput = document.getElementById('type');
let imgInput = document.getElementById('image');

typeInput.addEventListener('change', (event) => {
    
    // On récupère la valeur de l'input
    let type = event.target.value;

    if (type != 4) {
        dateDiv.style.display = 'block';
        imgInput.style.display = 'block';
    } else {
        dateDiv.style.display = 'none';
        imgInput.style.display = 'none'
    }



});