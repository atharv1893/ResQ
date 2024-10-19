const form = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const outputArea = document.getElementById('output-area');
function voice(){
    console.log("Voice Button Activated")
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        const outputDiv = document.getElementById('output');
        const startBtn = document.getElementById('start-btn');

        recognition.continuous = false; // Recognize speech as one sentence
        recognition.interimResults = false; // Don't show partial results
        recognition.lang = 'en-US'; // Set language (can be changed to any supported language)

        // Event when speech recognition service returns a result
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            
            userInput.value = transcript;
        };

        // Start recognition when button is clicked
        startBtn.addEventListener('click', () => {
            recognition.start();
            userInput.value = "Listening...";
        });

        // Event for error handling
        recognition.onerror = function(event) {
            outputDiv.innerHTML = `<span style="color: red;">Error: ${event.error}</span>`;
        };
    } else {
        // Speech Recognition API not supported
        document.body.innerHTML = '<h1>Your browser does not support Speech Recognition API.</h1>';
    }
}
form.addEventListener('submit', (e) => {
    e.preventDefault();
    const userInputValue = userInput.value.trim();
    
    if (userInputValue !== '') {
        fetch('/medical', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: userInputValue })
        })
        .then(response => response.json())
        .then((data) => {
            console.log(data);

            let resq = document.getElementById("image-container");
            if (resq) resq.style.display = "none";

            // Clear output area first
            outputArea.innerHTML = "";
            outputArea.style.display = "block";
            outputArea.style.color = "#ffffff";

            const text = data.results;  // Assuming text contains the result text
            const videoId = data.video_id;  // Assuming video_id is from API response

            console.log('Video ID:', videoId);  // Log the video ID to check its value
            
            // If video ID exists, embed the video
            if (videoId) {
                const iframe = document.createElement('iframe');
            
                // Set attributes for the iframe
                // iframe.width = "560";
                // iframe.height = "315";
                iframe.src = `https://www.youtube.com/embed/${videoId}`;
                iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
                iframe.allowFullscreen = true;

                // Append the iframe to the div container
                outputArea.appendChild(iframe);
            } 
            // If results exist, append the formatted text
            else if (text) {
                let formattedText = text.replace(/<\/h2>/g, '</h2><br><br>');
                outputArea.innerHTML += formattedText;
            } else {
                // Handle the case when both videoId and results are missing
                outputArea.innerHTML = "No content available.";
            }
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
            outputArea.innerHTML = "An error occurred while fetching the data.";
        });
    }
});
