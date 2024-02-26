function Play(player) {
    let computer = Math.floor(Math.random() * 3);
    heading.textContent = Roll(player, computer)
}

let bars = document.querySelectorAll('.bar')
let win = document.querySelector('.win')
let tie = document.querySelector('.tie')
let lose = document.querySelector('.lose')
let score = [0, 0, 0]

function Reset() {
    score = [0, 0, 0]
    win.style.height = '0%'
    tie.style.height = '0%'
    lose.style.height = '0%'
    console.log(score)
}

function Roll(player, computer) {
    if (+player == computer) {
        score[1]++
        tie.style.height = `${score[1]*10}%`
        return "Tie"
    } else if (+player + 1 == computer || (+player + 1 == 3 && computer == 0)) {
        score[0]++
        if (score[0] < 5) {
            lose.style.height = `${score[0]*10}%`
            return "Lose"
        } else {
            Reset()
            return "You lost"
        }
    } else if (+player - 1 == computer || (+player - 1 == -1 && computer == 2)) {
        score[2]++
        if (score[2] < 5) {
            win.style.height = `${score[2]*10}%`
            return "Win"
        } else {
            Reset()
            return "YOU WON"
        }
    } else {
        return `player=${player} comp=${computer}`
    }

}

Reset()

let buttons = document.querySelectorAll('button')
let heading = document.querySelector('h2')


for (button of buttons) {
    button.addEventListener('click', (e) => {
        Play(e.target.id)
    })
}
