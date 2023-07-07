const socket = io()

let dataX = 0
let dataY = 0

window.saveDataAccrossSessions = true

webgazer.setGazeListener((data, timestamp) => {
        console.log(data, timestamp)
        socket.emit('coor:msg', {
            dataX: data.x,
            dataY: data.y
        })
    })
    .begin()

