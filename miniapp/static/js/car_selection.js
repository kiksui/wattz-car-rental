document.addEventListener('DOMContentLoaded', function() {
    const carList = document.getElementById('carList');

    fetch('/cars/available')
        .then(response => response.json())
        .then(cars => {
            cars.forEach(car => {
                const carElement = document.createElement('div');
                carElement.className = 'car-item';
                carElement.innerHTML = `
                    <h2>${car.model}</h2>
                    <p>Plate: ${car.plate}</p>
                    <button onclick="selectCar('${car.plate}')">Select</button>
                `;
                carList.appendChild(carElement);
            });
        });
});

function selectCar(plate) {
    // Store the selected car plate in localStorage
    localStorage.setItem('selectedCarPlate', plate);
    // Redirect to the booking form
    window.location.href = '/booking_form';
}