document.addEventListener('DOMContentLoaded', function() {
    const kycForm = document.getElementById('kycForm');

    kycForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(kycForm);
        const kycData = Object.fromEntries(formData);
        
        fetch('/kyc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(kycData),
        })
        .then(response => response.json())
        .then(user => {
            // Send the KYC data back to the Telegram Bot
            window.Telegram.WebApp.sendData(JSON.stringify(user));
            window.Telegram.WebApp.close();
        });
    });
});