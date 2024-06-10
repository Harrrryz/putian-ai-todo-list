const button = document.getElementById("change-name-button")
button.addEventListener('click', setName)
function setName() {
    const span = document.getElementById("name")
    span.innerHTML = "Charles"
}
const todoButton = document.getElementById("get-todo")
todoButton.addEventListener('click', getTodos)

async function getTodos() {
    try {
        const response = await fetch('http://127.0.0.1:5000/todo-items-json');
        if (!response.ok) {
            throw new Error(`Error fetching todo items: ${response.statusText}`);
        }
        const data = await response.json();
        console.log(data); // This will be the array of todo items
        const todosDiv = document.getElementById('todos')
        todosDiv.innerHTML = ''
        let i = 1
        for (const item of data) {
            const div = document.createElement('div')
            div.innerHTML = `${i}. ${item.item} - ${item.plan_time} created: ${item.created_at}`
            todosDiv.appendChild(div)
            i++
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

const createButton = document.getElementById("create-button")
createButton.addEventListener('click', createItem)
async function createItem() {
    const item = document.getElementById("create-item").value
    const date = document.getElementById("create-item-date").value
    const response = await fetch('http://127.0.0.1:5000/add-todo-json', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item: item, date: date })
    });
    if (!response.ok) {
        throw new Error(`Error fetching todo items: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(data); // This will be the array of todo items
    await getTodos();
}

const deleteButton = document.getElementById("delete-button")
deleteButton.addEventListener('click', deleteItem)
async function deleteItem() {
    const item = document.getElementById("select-delete-item").value
    const response = await fetch('http://127.0.0.1:5000//delete-todo-json', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item: item })
    });
    if (!response.ok) {
        throw new Error(`Error fetching todo items: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(data); // This will be the array of todo items
    await getTodos();
}

const updateButton = document.getElementById("update-button")
updateButton.addEventListener('click', updateItem)
async function updateItem() {
    const item = document.getElementById("select-update-item").value
    const date = document.getElementById("select-update-date").value
    const response = await fetch('http://127.0.0.1:5000//update-todo-json', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item: item, date: date })
    });
    if (!response.ok) {
        throw new Error(`Error fetching todo items: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(data); // This will be the array of todo items
    await getTodos();
}

getTodos()