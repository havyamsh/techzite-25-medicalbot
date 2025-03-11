document.getElementById("send-message-btn").addEventListener("click", sendMessage);

function sendMessage() {
  const inputElement = document.getElementById("chat-input");
  const userMessage = inputElement.value.trim();

  if (userMessage) {
    displayMessage(userMessage, 'user');
    inputElement.value = ""; // Clear the input field

    // Send the message to the backend
    fetch("http://localhost:5000/chat", {  // Replace with your server URL
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userMessage })
    })
      .then(response => response.json())
      .then(data => {
        displayMessage(data.response, 'bot');
      })
      .catch(error => {
        console.error("Error:", error);
      });
  }
}

function displayMessage(message, sender) {
  const chatbox = document.getElementById("chatbox");
  const messageElement = document.createElement("div");
  messageElement.classList.add(sender);
  messageElement.textContent = message;
  chatbox.appendChild(messageElement);

  // Scroll chatbox to the bottom
  chatbox.scrollTop = chatbox.scrollHeight;
}
