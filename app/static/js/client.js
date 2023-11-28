////////////////////////
// Progress Board Logic
////////////////////////

const tasks = [];

function createTaskElement(task) {
    const taskElement = document.createElement('div');
    taskElement.className = 'task';
    taskElement.textContent = task.text;
    taskElement.draggable = true;
    taskElement.dataset.taskId = task.id;
    taskElement.dataset.taskColumn = task.column;

    return taskElement;
}


function fetchCards(){
    fetch("http://127.0.0.1:5000/get_cards", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        //console.log(data)
        for(var i = 0; i < data['cards'].length; i++) {
            const task = {id: data['cards'][i]['id'], text: data['cards'][i]['content'], column: data['cards'][i]['column']}
            tasks.push(task);
            const taskElement = createTaskElement(task);
            document.getElementById(taskElement.dataset.taskColumn).appendChild(taskElement);
        }

        // Update card count after fetching cards
        updateCardCount('inProgressColumn');
        updateCardCount('wonColumn');
        updateCardCount('lostColumn');
    })
    .catch(error => {
        // Handle any errors that occur during the fetch.
        console.error('Error:', error);
    });
}

function updateCardCount(columnId) {
    const column = document.getElementById(columnId);
    const cardCount = column.querySelectorAll('.task').length;
    const cardCountSpan = column.querySelector('.card-count');

    if (cardCountSpan) {
        cardCountSpan.textContent = cardCount;
    }
}

tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    document.getElementById(taskElement.dataset.taskColumn).appendChild(taskElement);
});











/////////////////////////
// Messaging Board Logic
/////////////////////////
const messages = [];

function createMessageElement(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.textContent = message.content;
    messageElement.dataset.id = message.id;
    messageElement.dataset.author = message.author;
    messageElement.dataset.timestamp = message.timestamp;

    // Message Info
    const messageElementInfo = document.createElement('div');
    messageElementInfo.className = 'message-context';
    messageElementInfo.textContent = "Posted By "+message.author+" On "+new Date(message.timestamp*1000).toString()
    messageElement.appendChild(messageElementInfo)

    return messageElement;
}

function getNewMessageId(){
    var max = 0;
    for (var i = 0; i < messages.length; i++) {
        if(parseInt(messages[i]['id']) > max){
            max = messages[i]['id'];
        }
    }
    return max+1;
}

function fetchMessages(){
    fetch("http://127.0.0.1:5000/get_messages", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        for(var i = 0; i < data['messages'].length; i++) {
            const message = { id: data['messages'][i]['id'], content: data['messages'][i]['content'], author: data['messages'][i]['author'], timestamp: data['messages'][i]['timestamp']}
            messages.push(message);
            const messageElement = createMessageElement(message);
            document.getElementById("messaging-section").appendChild(messageElement);
        }
    })
    .catch(error => {
        // Handle any errors that occur during the fetch.
        console.error('Error:', error);
    });
}

$('.message-form button').on('click', function(event) {
    event.preventDefault();
    const newId = getNewMessageId();
    const content = document.getElementById('message').value;
    const author = currentAuthor;
    document.getElementById('message').value = "";
    if(content){
        const message = { id: newId, content: content, author: author, timestamp: Math.floor(new Date().getTime() / 1000)};
        const messageElement = createMessageElement(message);
        document.getElementById("messaging-section").appendChild(messageElement);
        fetch("http://127.0.0.1:5000/add_message", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(message)
        })
        .then(response => response.json())
        .then(data => {
            //console.log(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
        messages.push(message);
    }
});

messages.forEach(message => {
    document.getElementById("messaging-section").appendChild(createMessageElement(message))
});

/////////////////////////
// "On Load" Stuff
/////////////////////////
document.addEventListener('DOMContentLoaded', function() {
    fetchCards();
    fetchMessages();
});