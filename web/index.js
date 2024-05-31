// index.js

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();

var partialText = "";
var finalText = "";
// Middleware to parse JSON request bodies

// Set the view engine to EJS
app.set('view engine', 'ejs');



app.use(bodyParser.json());
app.use(cors());
// Define a route to handle POST requests
app.post('/api/postPartial', (req, res) => {
  // Access the POST request data from req.body
  const requestData = req.body;

  // You can process the data here
  // For example, you can log it to the console
  console.log('Received POST data:', requestData);
  partialText = requestData;
  // Send a response back to the client
  res.status(200).json({ message: requestData});
});

app.post('/api/postFinal', (req, res) => {
    // Access the POST request data from req.body
    const requestData = req.body;
  
    // You can process the data here
    // For example, you can log it to the console
    console.log('Received POST data:', requestData);
    finalText = requestData;
    // Send a response back to the client
    res.status(200).json({ message: requestData});
  });

app.get('/api/GetPartial', (req, res) => {
    res.send(partialText);
  }) ;
app.get('/api/GetFinal', (req, res) => {
    res.send(finalText);
  }) ;

// Define a route for the webpage
app.get('/', (req, res) => {
    res.render('index', { pageTitle: 'My Webpage'})

});

// Start the server on a specified port (e.g., 3000)
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});
