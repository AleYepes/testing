// CREATE CANVAS
function createCanvas() {
    let cells = document.querySelectorAll('.flex-auto');
    cells.forEach((cell) => cell.remove());
    let columns = document.createElement('div');
    for (let i = 0; i < resolution; i++){
        let cell = document.createElement('div');
        cell.classList.add('flex-auto');
        cell.classList.add('cell');
        columns.appendChild(cell);
    };

    for (let i = 0; i < resolution; i++){
        let clone = columns.cloneNode(true);
        clone.classList.add('flex-auto');
        container.appendChild(clone);
    };
    
    activatePencil();
}

function activatePencil() {
    // SET MOUSE EVENT INTERACTIONS
    let mouseDown = false;
    document.addEventListener('mousedown', () => mouseDown = true);
    document.addEventListener('mouseup', () => mouseDown = false);
    
    // ADD PENCIL INTERACTION
    let color = 'grey'
    let cells = document.querySelectorAll('.cell');
    cells.forEach((cell) => {
        cell.addEventListener('mousemove', (e) => {
            if (mouseDown){
                e.target.style.backgroundColor = color};
            })
        cell.addEventListener('mousedown', (e) => {
                e.target.style.backgroundColor = color;
            })
    });
    
}

const container = document.querySelector('.container');
let resolution = 16;
const clearButton = document.querySelector("#clear");
const resolutionButton = document.querySelector("#resolution");

clearButton.addEventListener('click', () => createCanvas());

function promptResolution() {
    resolution = +prompt("Set resolution between 0 - 100");
    if (resolution == 0 || isNaN(resolution)) {
        alert('Not a number')
        promptResolution();
    } else if (resolution > 100){
        alert("Too large")
        promptResolution();
    }
}

resolutionButton.addEventListener('click', () => {
    promptResolution()
    createCanvas();
})

createCanvas();