document.getElementById('weekSlider').addEventListener('input', function() {
    const weekValue = this.value;
    document.getElementById('weekLabel').innerText = weekValue;
    const estimatedDate = calculateEstimatedDate(weekValue);
    document.getElementById('estimatedDate').innerText = estimatedDate;
});

function calculateEstimatedDate(week) {
    const startDate = new Date('2024-01-01'); // Example start date
    const estimatedDate = new Date(startDate);
    estimatedDate.setDate(estimatedDate.getDate() + (week * 7));
    return estimatedDate.toISOString().split('T')[0];
}

function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const week = document.getElementById('weekSlider').value;
    const current_date = calculateEstimatedDate(week);

    if (userInput.trim() !== "") {
        const chatBox = document.getElementById('chatBox');

        // Create user message
        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.innerText = userInput;
        chatBox.appendChild(userMessage);

        // Clear the input field
        document.getElementById('userInput').value = "";

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;

        // Send the message to the server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput, week: week , current_date: current_date})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Create bot message
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');
            botMessage.innerText = data.message;
            chatBox.appendChild(botMessage);

            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function displayWeekData(data) {
    // Display the data on the page as needed.
    // Assuming the JSON data has keys like "feeling", "symptoms", "highlights", "goal", "toDoList", and "notes".
    document.getElementById('feeling').value = data["I am feeling"] || '';
    document.getElementById('symptoms').value = data["Symptoms"] || '';
    document.getElementById('highlights').value = data["Highlights of the Week"] || '';
    document.getElementById('goal').value = data["Your goal"] || '';
    document.getElementById('toDoList').value = data["To Do List"] || '';
    document.getElementById('notes').value = data["Notes"] || '';
}
