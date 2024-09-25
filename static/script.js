const startVoiceButton = document.getElementById('startVoice');

const formFields = {
    'nama': document.getElementById('nama'),
    'tempat_lahir': document.getElementById('tempat_lahir'),
    'tanggal_lahir': document.getElementById('tanggal_lahir'),
    'tanggungan': document.getElementById('tanggungan'),
    'status': document.querySelectorAll('input[name="status"]'),
    'alamat': document.getElementById('alamat')
};

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
    recognition.lang = 'id-ID';
    recognition.continuous = false;

    startVoiceButton.addEventListener('click', () => {
        recognition.start();
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.toLowerCase().trim();

        // Save transcript to the server
        fetch('/log_transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ transcript }),
        })
        .then(response => response.json())
        .then(() => {
            // After logging the transcript, process it to fill the form
            fetch('/process_voicelog', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    const apiResponse = data.response;

                    // Now fill the form with the API response
                    fillFormFields(apiResponse);
                }
            })
            .catch(error => console.error('Error processing voicelog:', error));
        })
        .catch(error => console.error('Error logging transcript:', error));
    };

    recognition.onspeechend = () => {
        recognition.stop();
    };

    recognition.onerror = (event) => {
        alert('Error occurred in recognition: ' + event.error);
    };
} else {
    alert('Speech Recognition API not supported in this browser.');
    startVoiceButton.disabled = true;
}

function fillFormFields(apiResponse) {
    const lines = Object.keys(apiResponse);

    lines.forEach(field => {
        // Log the field and the corresponding value for debugging
        console.log(`Field: ${field}, Value: "${apiResponse[field]}"`);

        // Check if the value is not null or empty before updating the form field
        if (apiResponse[field] && apiResponse[field].trim() !== "") {
            // Nama field update check
            if (field === "nama") {
                formFields['nama'].value = apiResponse[field];
                console.log("Nama field updated.");
            } 
            // Tempat Lahir field update check
            else if (field === "tempat_lahir") {
                formFields['tempat_lahir'].value = apiResponse[field];
                console.log("Tempat Lahir field updated.");
            } 
            // Tanggal Lahir field update check
            else if (field === "tanggal_lahir") {
                const parts = apiResponse[field].split('/');
                if (parts.length === 3) {
                    const formattedDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
                    formFields['tanggal_lahir'].value = formattedDate;
                    console.log("Tanggal Lahir field updated.");
                }
            } 
            // Tanggungan field update check
            else if (field === "tanggungan") {
                formFields['tanggungan'].value = apiResponse[field];
                console.log("Tanggungan field updated.");
            } 
            // Status field update check
            else if (field === "status") {
                const statusValue = apiResponse[field].toLowerCase();
                formFields['status'].forEach(radio => {
                    if (radio.value.toLowerCase() === statusValue) {
                        radio.checked = true;
                        console.log("Status field updated.");
                    }
                });
            } 
            // Alamat field update check
            else if (field === "alamat") {
                formFields['alamat'].value = apiResponse[field];
                console.log("Alamat field updated.");
            }
        }
    });
}


