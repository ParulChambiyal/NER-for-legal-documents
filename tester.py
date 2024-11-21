import requests
import json

# API URL
url = "http://127.0.0.1:5000/extract-entities"

# Hindi text to send to the API
data = {
    "text": "यह एक अदालत का मामला है जिसमें याचिकाकर्ता ने 2024 में याचिका दायर की।"
}

# Send a POST request to the API
response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

# Print the response from the API
if response.status_code == 200:
    print("Entities extracted successfully:")
    print(response.json())
else:
    print(f"Failed to extract entities. Status code: {response.status_code}")
    print(response.json())
