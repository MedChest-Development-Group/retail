// Sample tasks
const tasks = [
    { id: 1, text: 'Task 1' },
    { id: 2, text: 'Task 2' },
    { id: 3, text: 'Task 3' }
];

function createTaskElement(task) {
    const taskElement = document.createElement('div');
    taskElement.className = 'task';
    taskElement.textContent = task.text;
    taskElement.draggable = true;
    taskElement.dataset.taskId = task.id;
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
    dropZone.appendChild(taskElement);
}

function dragOver(event) {
    event.preventDefault();
}

const todoColumn = document.getElementById('inProgressColumn');
tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    todoColumn.appendChild(taskElement);
});

const columns = document.querySelectorAll('.column');
columns.forEach(column => {
    column.addEventListener('dragover', dragOver);
    column.addEventListener('drop', drop);
});