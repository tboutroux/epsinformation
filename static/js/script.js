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