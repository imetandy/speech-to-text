// script.js

document.addEventListener('DOMContentLoaded', () => {
    const resultElement = document.getElementById('result');
  
    // Function to make a POST request to your Node.js server
    const postData = async () => {
      try {
        const response = await fetch('http://localhost:3000/api/GetData', {
          method: 'GET',
          headers: {
            'Access-Control-Allow-Origin' : '*',
            'Content-Type': 'application/json',
          }
        });
  
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
  
        const data = await response.json();
        console.log(data.myText);
        resultText = data.myText
        resultElement.textContent = resultText;
        

      } catch (error) {
        console.error('Error:', error);
        resultElement.textContent = 'An error occurred';
      }
    };
  
    // Call the postData function when a button is clicked or on page load
    postData();
  });
  