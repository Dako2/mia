document.getElementById('weekSlider').addEventListener('input', function() {
    const weekValue = this.value;
    document.getElementById('weekLabel').innerText = weekValue;
    const estimatedDate = calculateEstimatedDate(weekValue);
    document.getElementById('estimatedDate').innerText = estimatedDate;
    changeBackgroundImage(weekValue);
    loadWeekData(weekValue);
});

function calculateEstimatedDate(week) {
    const startDate = new Date('2024-01-01'); // Example start date
    const estimatedDate = new Date(startDate);
    estimatedDate.setDate(estimatedDate.getDate() + (week * 7));
    return estimatedDate.toISOString().split('T')[0];
}

function changeBackgroundImage(week) {
    let imagePath = '';
    if (week >= 1 && week <= 8) {
        imagePath = 'static/img/week_1-8.jpeg';
    } else if (week >= 9 && week <= 12) {
        imagePath = 'static/img/week_9-12.jpeg';
    } else if (week >= 13 && week <= 16) {
        imagePath = 'static/img/week_13-16.jpeg';
    } else if (week >= 17 && week <= 20) {
        imagePath = 'static/img/week_17-20.jpeg';
    } else if (week >= 21 && week <= 24) {
        imagePath = 'static/img/week_21-24.jpeg';
    } else if (week >= 25 && week <= 28) {
        imagePath = 'static/img/week_25-28.jpeg';
    } else if (week >= 29 && week <= 32) {
        imagePath = 'static/img/week_29-32.jpeg';
    } else if (week >= 33 && week <= 36) {
        imagePath = 'static/img/week_33-36.jpeg';
    } else if (week >= 37 && week <= 40) {
        imagePath = 'static/img/week_37-40.jpeg';
    }
    const imageContainer = document.getElementById('imageContainer');
    if (imageContainer) {
        imageContainer.style.backgroundImage = `url(${imagePath})`;
    } else {
        console.error('Error: imageContainer element not found.');
    }
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

function loadWeekData(week) {
    fetch(`static/data/week_${week}.json`)
        .then(response => response.json())
        .then(data => displayWeekData(data[`Week ${week}`]))
        .catch(error => console.error('Error loading week data:', error));
}

function displayWeekData(data) {
    // Display the data on the page as needed.
    // Assuming the JSON data has keys like "I am feeling", "Symptoms", "Highlights of the Week", "My Goal", "To Do List", and "Notes".
    document.getElementById('feeling').value = data["I am feeling"] || '';
    document.getElementById('symptoms').value = data["Symptoms"] || '';
    document.getElementById('highlights').value = data["Highlights of the Week"] || '';
    document.getElementById('goal').value = data["My Goal"] || '';
    document.getElementById('toDoList').value = data["To Do List"].join('\n') || '';
    document.getElementById('notes').value = data["Notes"] || '';
}