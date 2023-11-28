////////////////////////
// Progress Board Logic
////////////////////////

const tasks = [];



/**
 * Create a task element based on task data.
 * @param {Object} task - Task object with properties: id, text, column.
 * @returns {HTMLDivElement} - Created task element.
 */
function createTaskElement(task) {
    const taskElement = document.createElement('div');
    taskElement.className = 'task';
    taskElement.textContent = task.text;
    taskElement.draggable = true;
    taskElement.dataset.taskId = task.id;
    taskElement.dataset.taskColumn = task.column;

    return taskElement;
}




/**
 * Fetch cards from the server and update the task list.
 */
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



/**
 * Update the card count display for a specific column.
 * @param {string} columnId - ID of the column to update.
 */
function updateCardCount(columnId) {
    const column = document.getElementById(columnId);
    const cardCount = column.querySelectorAll('.task').length;
    const cardCountSpan = column.querySelector('.card-count');

    if (cardCountSpan) {
        cardCountSpan.textContent = cardCount;
    }
}

// Iterate through existing tasks and update the task list
tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    document.getElementById(taskElement.dataset.taskColumn).appendChild(taskElement);
});











/////////////////////////
// Messaging Board Logic
/////////////////////////
const messages = [];


/**
 * Create a message element based on message data.
 * @param {Object} message - Message object with properties: id, content, author, timestamp.
 * @returns {HTMLDivElement} - Created message element.
 */
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


/**
 * Get a new message ID by finding the maximum existing ID and adding 1.
 * @returns {number} - New message ID.
 */
function getNewMessageId(){
    var max = 0;
    for (var i = 0; i < messages.length; i++) {
        if(parseInt(messages[i]['id']) > max){
            max = messages[i]['id'];
        }
    }
    return max+1;
}



/**
 * Fetch messages from the server and update the message list.
 */
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


// Event listener for submitting a new message
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


// Iterate through existing messages and update the message list
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