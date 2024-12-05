import json
import httpx
import asyncio

# URL to send the POST request
url = "https://www.signalhire.com/api/v1/candidate/search"

# Headers with the API key
headers = {'apikey': '202.hWGz10GhKUH4yB1Ki1U2mCB50rmn', 'Content-Type': 'application/json'}

# Data to send in the POST request
# data = {
#     "items": [
#         "https://www.linkedin.com/in/prashanth-gundla-b4ab5a5/",
#     ],
#     "callbackUrl": "https://www.hi.com/callbackUrl"
# }

payload = {'items': ['https://www.linkedin.com/in/prashanth-gundla-b4ab5a5'], 'callbackUrl': 'https://api-hiring-bot-g5hdguataybybne9.centralindia-01.azurewebsites.net/profile-search/call-back/org_2ow5pexgsO0avtK5892cjr1yUry'}
# Async function to send POST request
async def search_profiles_signalhire():
    """
    Search profiles based on the search query
    """
    # payload = {
    #     "items": [
    #         "https://www.linkedin.com/in/prashanth-gundla-b4ab5a5/",
    #     ],
    #     "callbackUrl": "https://www.hi.com/callbackUrl"
    # }

    async with httpx.AsyncClient() as client:
        # Send POST request asynchronously
        response = await client.post(url, headers=headers, json=payload)

    # Check the response status and handle accordingly
    if response.status_code != 201:
        print("Error: ", response.status_code)
        print(response.text)  # print error details
        return None  # or handle accordingly

    return response.json()  # Return the response JSON if status is 200

# To run the async function
async def main():
    result = await search_profiles_signalhire()
    if result:
        print(result)  # Handle the result as needed

# Start the async event loop
if __name__ == "__main__":
    asyncio.run(main())
