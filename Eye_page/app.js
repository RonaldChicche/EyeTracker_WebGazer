const {SerialPort} = require('serialport')
const {ReadlineParser} = require('@serialport/parser-readline')
const path = require('path')
const express = require('express')
const app = express()

// Web application port settings
app.set('port', process.env.PORT || 3030)

// Static files
app.use(express.static(path.join(__dirname, 'public')))

// Start server 
const server = app.listen(app.get('port'), () => {
    console.log('server on port', app.get('port'));
})

// Websockets settings 
const SocketIO = require('socket.io')
const io = SocketIO(server)

// var msg = ''

io.on('connection', (socket) => {
    console.log('new connection', socket.id);
    socket.on('coor:msg', (data) => {
        //console.log(data.dataX + '/' + data.dataY);
        x = Math.round(data.dataX);
        y = Math.round(data.dataY);
        // Crear un objeto JSON
        let msg = { 'x': x, 'y': y };
        //msg = x + '/' + y + '//';
        //sendData(msg);
        // Emitir datos a todos los clientes conectados
        io.emit('data', msg);
    })
})


//Serial port settings
// const serialport = new SerialPort({ path: 'COM4', baudRate: 115200 })
// const parser = serialport.pipe(new ReadlineParser({delimiter: '\r\n'}))

// serialport.on('open', () => {
//     console.log('Conexión serial abierta.');
//   });
  
// serialport.on('error', (err) => {
//     console.error('Error en la conexión serial:', err.message);
// });

// parser.on('data', function(data) {
//     console.log('Arduino ->' + data)
//     //serialport.write('Respuesta de servidor')
// })

 
// function sendData(data) {
//     serialport.write(data, (error) => {
//         if (error) {
//             console.error('Error al enviar los datos:', error);
//         }
//     });
// }
