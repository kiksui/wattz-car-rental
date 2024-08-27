document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById('bookingForm');
    const carPlate = localStorage.getItem('selectedCarPlate');
    
    document.getElementById('carPlate').value = carPlate;

    bookingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(bookingForm);
        const bookingData = Object.fromEntries(formData);
        
        fetch('/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData),
        })
        .then(response => response.json())
        .then(booking => {
            // Send the booking data back to the Telegram Bot
            window.Telegram.WebApp.sendData(JSON.stringify(booking));
            window.Telegram.WebApp.close();
        });
    });
});