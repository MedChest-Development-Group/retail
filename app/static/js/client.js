const tasks = [];

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

function dragStart(event) {
    event.dataTransfer.setData('text/plain', event.target.dataset.taskId);
}

function drop(event) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData('text/plain');
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    const dropZone = event.target.closest('.column');
    taskElement.dataset.taskColumn = dropZone.id;
    updateCard(taskElement);
    dropZone.appendChild(taskElement);
}

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

function updateTask(taskElement) {
    const newContent = prompt('Enter the Retailer:');
    if(newContent){
        taskElement.textContent = newContent;
        updateCard(taskElement);
    }
}

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

function dragOver(event) {
    event.preventDefault();
}

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

function getNewId(){
    var max = 0;
    for (var i = 0; i < tasks.length; i++) {
        console.log(tasks[i]['id'])
        if(parseInt(tasks[i]['id']) > max){
            max = tasks[i]['id'];
        }
    }
    console.log(max)
    return max+1;
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

const columns = document.querySelectorAll('.column');
columns.forEach(column => {
    column.addEventListener('dragover', dragOver);
    column.addEventListener('drop', drop);
});

document.addEventListener('DOMContentLoaded', function() {
    fetchCards();
});