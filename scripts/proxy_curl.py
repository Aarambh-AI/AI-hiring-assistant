import requests
import json

# URL to send the POST request
url = "https://www.signalhire.com/api/v1/candidate/search"

# Headers with the API key
headers = {
    "apikey": "DTRQBj4rYHRHuS6demdH4nY8xUcCMpJ3",
    "Content-Type": "application/json"  # Ensure the data is sent as JSON
}

# Data to send in the POST request
data = {
    "items": [
        "https://www.linkedin.com/in/sai-shyam-g-009690112",
    ],
    "callbackUrl": "https://www.hi.com/callbackUrl"
}

# Send the POST request with the data and headers
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response from the server
print(response.status_code)
print(response.text)
