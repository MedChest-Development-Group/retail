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

    const buttons = document.createElement('div');

    // Create a delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger button-with-padding';
    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
    deleteButton.addEventListener('click', () => deleteTask(taskElement));
    

    // Create a update button
    const updatebutton = document.createElement('button');
    updatebutton.className = `btn btn-primary button-with-padding`;
    updatebutton.innerHTML = `<i class="fas fa-pencil-alt"></i>`;
    updatebutton.addEventListener('click', () => updateTask(taskElement));


    buttons.appendChild(updatebutton);
    buttons.appendChild(deleteButton);

    taskElement.appendChild(buttons);


    taskElement.addEventListener('dragstart', dragStart);
    return taskElement;
}



/**
 * Handle the dragstart event for a task element.
 * @param {Event} event - Drag start event.
 */
function dragStart(event) {
    event.dataTransfer.setData('text/plain', event.target.dataset.taskId);
}



/**
 * Handle the drop event for a task element.
 * @param {Event} event - Drop event.
 */
function drop(event) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData('text/plain');
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    const dropZone = event.target.closest('.column');
    taskElement.dataset.taskColumn = dropZone.id;
    updateCard(taskElement);
    dropZone.appendChild(taskElement);
}



/**
 * Delete a task and send a request to the server to delete the corresponding card.
 * @param {HTMLDivElement} taskElement - Task element to be deleted.
 */
function deleteTask(taskElement) {
    fetch("http://127.0.0.1:5000/delete_card", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: taskElement.dataset.taskId,
            text: taskElement.textContent,
            column: taskElement.dataset.taskColumn
        })
    })
    .then(response => response.json())
    .then(data => {
        //console.log(data)
    })
    .catch(error => {
        console.error('Error:', error);
    });
    taskElement.remove();
}




/**
 * Update the content of a task by taking user input and send a request to the server to update the corresponding card.
 * @param {HTMLDivElement} taskElement - Task element to be updated.
 */
function updateTask(taskElement) {
    const newContent = prompt('Enter the Retailer:');
    if(newContent){
        taskElement.textContent = newContent;
        const buttons = document.createElement('div');

        // Create a delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger button-with-padding';
        deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
        deleteButton.addEventListener('click', () => deleteTask(taskElement));
        
    
        // Create a update button
        const updatebutton = document.createElement('button');
        updatebutton.className = `btn btn-primary button-with-padding`;
        updatebutton.innerHTML = `<i class="fas fa-pencil-alt"></i>`;
        updatebutton.addEventListener('click', () => updateTask(taskElement));
    
    
        buttons.appendChild(updatebutton);
        buttons.appendChild(deleteButton);
    
        taskElement.appendChild(buttons);
        updateCard(taskElement);
    }
}



/**
 * Update the corresponding card on the server when a task is updated.
 * @param {HTMLDivElement} taskElement - Task element to be updated.
 */
function updateCard(taskElement){
    fetch("http://127.0.0.1:5000/update_card", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: taskElement.dataset.taskId,
            text: taskElement.textContent,
            column: taskElement.dataset.taskColumn
        })
    })
    .then(response => response.json())
    .then(data => {
        //console.log(data)
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


/**
 * Handle the dragover event for a column.
 * @param {Event} event - Drag over event.
 */
function dragOver(event) {
    event.preventDefault();
}




// Event listener for adding a new task
$('.column-header button').on('click', function() {
    const columnId = $(this).closest('.column').attr('id');
    const newId = getNewId();
    const cardContent = prompt('Enter the Retailer:');
    if(cardContent){
        const task = { id: newId, text: cardContent, column: columnId };
        const taskElement = createTaskElement(task);
        document.getElementById(taskElement.dataset.taskColumn).appendChild(taskElement);
        fetch("http://127.0.0.1:5000/add_card", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: newId,
                text: cardContent,
                column: columnId
            })
        })
        .then(response => response.json())
        .then(data => {
            //console.log(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
        tasks.push(task);
    }
});



/**
 * Get a new task ID by finding the maximum existing ID and adding 1.
 * @returns {number} - New task ID.
 */
function getNewId(){
    var max = 0;
    for (var i = 0; i < tasks.length; i++) {
        if(parseInt(tasks[i]['id']) > max){
            max = tasks[i]['id'];
        }
    }
    return max+1;
}




/**
 * Fetch tasks from the server and update the task list.
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
    })
    .catch(error => {
        // Handle any errors that occur during the fetch.
        console.error('Error:', error);
    });
}

tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    document.getElementById(taskElement.dataset.taskColumn).appendChild(taskElement);
});


// Add event listeners for drag-and-drop functionality
const columns = document.querySelectorAll('.column');
columns.forEach(column => {
    column.addEventListener('dragover', dragOver);
    column.addEventListener('drop', drop);
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

    const buttons = document.createElement('div');

    // Create a delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-danger button-with-padding';
    deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
    deleteButton.addEventListener('click', () => deleteTask(taskElement));
    

    // Create a update button
    const updatebutton = document.createElement('button');
    updatebutton.className = `btn btn-primary button-with-padding`;
    updatebutton.innerHTML = `<i class="fas fa-pencil-alt"></i>`;
    updatebutton.addEventListener('click', () => updateTask(taskElement));


    buttons.appendChild(updatebutton);
    buttons.appendChild(deleteButton);

    messageElementInfo.appendChild(buttons);
    messageElement.appendChild(messageElementInfo)

    return messageElement;
}




/**
 * Get a new unique message ID by finding the maximum ID in the existing messages and incrementing it.
 * @returns {number} - New unique message ID.
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
 * Fetches messages from the server, processes the response data, and appends message elements to the messaging section.
 * @returns {void}
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



/**
 * Event handler for the click event on buttons inside elements with the class 'message-form'.
 * Prevents the default behavior of the event, retrieves the message content, and sends a request to add the message.
 * @param {Event} event - The click event object.
 * @returns {void}
 */
$('.message-form button').on('click', function(event) {
    event.preventDefault();
    console.log('here')
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