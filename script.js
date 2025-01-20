// Array to store previous commands and responses
let previousCommands = [];

// Variable to track if the user is playing the guess game
let isGuessGameActive = false;

// Create a speech synthesis queue
const speechSynthesisQueue = [];

// Add a speech synthesis task to the queue
function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  speechSynthesisQueue.push(utterance);
  speakNext();
}

// Speak the next task in the queue
function speakNext() {
  if (speechSynthesisQueue.length > 0) {
    const utterance = speechSynthesisQueue.shift();
    utterance.onend = function() {
      speakNext();
    };
    utterance.onerror = function() {
      speakNext();
    };
    window.speechSynthesis.speak(utterance);
  }
}

// Function to update the response display
function updateResponseDisplay(response) {
  const responseDiv = document.getElementById('response');
  responseDiv.innerHTML = ''; // Clear previous content

  // Display previous commands and responses
  previousCommands.forEach(item => {
    responseDiv.innerHTML += `<strong>You Said:</strong> ${item.command}<br><strong>Sirius:</strong> ${item.response}<br><br>`;
  });

  // Add the current command and response
  if (response) {
    responseDiv.innerHTML += `<strong>You Said:</strong> ${currentCommand}<br><strong>Sirius:</strong> ${response}<br><br>`;
    previousCommands.push({ command: currentCommand, response: response });
  }

  // Limit the array to the last 5 commands
  if (previousCommands.length > 5) {
    previousCommands.shift(); // Remove the oldest command
  }
}

// Function to speak the response
function speakResponse(text) {
  speak(text);
}

// Variable to store the current command
let currentCommand = '';

// Variable to track if the assistant is listening
let isListening = false;

// Create a new instance of SpeechRecognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// Disable interim results for better command recognition
recognition.interimResults = false;

// Set the language
recognition.lang = 'en-US';

// Event listener for the recognition result
recognition.onresult = function (event) {
  const transcript = Array.from(event.results)
    .map(result => result[0])
    .map(result => result.transcript)
    .join('');

  console.log("Transcript:", transcript);

  // Store the current command
  currentCommand = transcript;

  // Process the command
  fetch('/api/voice-command', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ command: transcript })
  })
    .then(response => response.json())
    .then(data => {
      console.log("Response from server:", data.response);
      updateResponseDisplay(data.response);
      speakResponse(data.response); // Speak the response

      // Check if the guess game is active
      if (data.response.includes("Congratulations") || data.response.includes("Try again")) {
        isGuessGameActive = true;
      } else if (data.response.includes("I have chosen a number")) {
        isGuessGameActive = true;
      } else {
        isGuessGameActive = false;
      }
    })
    .catch(error => console.error("Error:", error));
};

// Event listener for the recognition end
recognition.onend = function () {
  isListening = false; // Reset listening state
  console.log("Stopped listening.");
  document.getElementById('listening-indicator').style.display = 'none'; // Hide the animation
};

// Function to start listening
function startListening() {
  if (!isListening) {
    isListening = true; // Set listening state to true
    console.log("Listening for commands...");
    recognition.start(); // Start speech recognition
    document.getElementById('listening-indicator').style.display = 'block'; // Show the animation
  }
}

// Function to stop listening
function stopListening() {
  if (isListening) {
    isListening = false; // Set listening state to false
    recognition.stop(); // Stop the recognition
    console.log("Stopped listening.");
    document.getElementById('listening-indicator').style.display = 'none'; // Hide the animation
  
  }
}

// Add event listeners for start and stop buttons
document.getElementById('start-button').addEventListener('click', startListening);
document.getElementById('stop-button').addEventListener('click', stopListening);