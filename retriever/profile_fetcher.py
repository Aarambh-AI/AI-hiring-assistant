from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import uuid

# Function to fetch LinkedIn profiles based on the user's details
def fetch_profile(name, title):
    try:
        # Initialize the Custom Search API service
        service = build(
            "customsearch", "v1", developerKey=os.environ['DEVELOPER_KEY']
        )
        
        # Formulate a refined search query targeting LinkedIn URLs
        search_query = f'{title} {name}  site:linkedin.com/in/ -inurl:jobs -inurl:posts -inurl:company'

        quota_user_id = str(uuid.uuid4())  # Generate a unique user ID for each query

        # Perform the search request
        res = service.cse().list(
            q=search_query,
            cx=os.environ['CX_KEY'],
            num=3,  # Get the top 3 results
            quotaUser= quota_user_id
        ).execute()

        # Check if there are any results
        if 'items' in res:
            # Extract LinkedIn URLs from the results
            linkedin_urls = [item['link'] for item in res['items'] if 'linkedin.com/in/' in item['link']]

            # Return the top 3 LinkedIn URLs
            return linkedin_urls[:3]
        else:
            return []
        
    except HttpError as e:
        print(f"An error occurred: {e}")
        return []

# # Example usage
# name = "g sai shyam"
# title = "ai lead"
# location = "hyderabad"
# company = "nalanda"
# college = "iit kharagpur"

# # Fetch and print the top 3 LinkedIn profiles
# profiles = fetch_profile(name, title, location, company, college)
# pprint.pprint(profiles)
