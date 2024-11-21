// document.getElementById('login-form').addEventListener('submit', async function(event) {
//     event.preventDefault();
    
//     const email = document.getElementById('email').value;
//     const password = document.getElementById('password').value;
    
//     const response = await fetch('/api/auth/login', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ email, password })
//     });
    
//     const data = await response.json();
    
//     if (response.ok) {
//         document.getElementById('message').textContent = `Login successful! Welcome, ${data.user.email}`;
//     } else {
//         document.getElementById('message').textContent = `Error: ${data.message}`;
//     }
// });
// document.getElementById('login-form').addEventListener('submit', async function(event) {
//     event.preventDefault();
    
//     console.log("Form submitted");  // Add this line to confirm event listener works

//     const email = document.getElementById('email').value;
//     const password = document.getElementById('password').value;

//     try {
//         const response = await fetch('/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ email, password })});

//         const data = await response.json();
//         console.log("Response data:", data);  // Check response data

//         if (response.ok) {
//             document.getElementById('message').textContent = `Login successful! Welcome, ${data.user.email}`;
//             // Redirect or render next page
//             window.location.href = "/upload";  // Replace "/home" with your target route
//         } else {
//             document.getElementById('message').textContent = `Error: ${data.message}`;
//         }
//     } catch (error) {
//         console.error("Error:", error);
//         document.getElementById('message').textContent = "An error occurred.";
//     }
// });
document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    console.log("Form submitted");

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        // Ensure the response is JSON and handle accordingly
        if (response.headers.get("content-type").includes("application/json")) {
            const data = await response.json();
            console.log("Response data:", data);

            if (response.ok) {
                // Redirect to upload page if login is successful
                window.location.href = "/upload"; 
            } else {
                // Display error message returned from server
                // document.getElementById('message').textContent = `Error: ${data.message}`;
                document.getElementById("error-message").textContent = data.message;
            }
        } else {
            throw new Error("Received non-JSON response");
        }
    } catch (error) {
        console.error("Error in fetch:", error);
        document.getElementById('error-message').textContent = "Invalid User Password.";
    }
});

// for login in signup page---------------------

  

document.getElementById('signup-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const response = await fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        document.getElementById('message').textContent = `Signup successful! Welcome, ${data.user.email}`;
    } else {
        document.getElementById('message').textContent = `Error: ${data.message}`;
    }
});
// eye togglle-------------------
window.onload = function () {
    // Get the password input and the eye icon
    const togglePassword = document.getElementById("togglePassword");
    const password = document.getElementById("password");
  
    togglePassword.addEventListener("click", function () {
      // Toggle the type attribute between password and text
      const type = password.type === "password" ? "text" : "password";
      password.type = type;
  
      // Toggle the icon (change between 'bxs-show' and 'bxs-hide')
      if (password.type === "password") {
        togglePassword.classList.remove("bxs-hide");
        togglePassword.classList.add("bxs-show");
      } else {
        togglePassword.classList.remove("bxs-show");
        togglePassword.classList.add("bxs-hide");
      }
    });
  };
  






// OCR Functionality
document.getElementById('ocrButton').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput').files[0];
    if (!fileInput) {
        alert("Please upload a file first.");
        return;
    }

    const outputText = document.getElementById('outputText');

    if (fileInput.type.startsWith("image/")) {
        // OCR for image files
        Tesseract.recognize(
            URL.createObjectURL(fileInput),
            'eng'
        ).then(({ data: { text } }) => {
            outputText.value = text;
        }).catch(err => console.error(err));
    } else if (fileInput.type === "application/pdf") {
        // Placeholder: OCR for PDFs would require additional handling
        outputText.value = "OCR for PDF is not implemented in this example.";
    } else if (fileInput.name.endsWith(".docx")) {
        // Placeholder: OCR for DOCX requires additional handling
        outputText.value = "OCR for DOCX is not implemented in this example.";
    } else {
        alert("Unsupported file type.");
    }
});

// Save as Text File
document.getElementById('saveTextButton').addEventListener('click', () => {
    const text = document.getElementById('outputText').value;
    const blob = new Blob([text], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'extracted_text.txt';
    link.click();
});

// Entity Extraction Placeholder
document.getElementById('entityButton').addEventListener('click', () => {
    const extractedText = document.getElementById('outputText').value;
    if (!extractedText) {
        alert("Please extract text first.");
        return;
    }

    // Placeholder for entity extraction functionality
    alert("Entity extraction is not implemented in this example.");
});
