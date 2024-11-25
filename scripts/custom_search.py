import requests
import uuid  # Importing uuid to generate unique user IDs

def fetch_linkedin_profiles(api_key, search_engine_id, title, name, quota_user):
    # Construct the search query
    query = f'{title} {name} site:linkedin.com/in/ -inurl:jobs -inurl:posts -inurl:company'
    
    # Set up the API URL with quota_user
    url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&quotaUser={quota_user}'
    
    # Make the request to the Google Custom Search API
    response = requests.get(url)
    
    # Check if the response was successful
    if response.status_code == 200:
        results = response.json()
        profiles = []
        
        # Extract the top three LinkedIn profiles
        for item in results.get('items', [])[:3]:  # Get only top 3 results
            profile_info = {
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            }
            profiles.append(profile_info)
        
        return profiles
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Example usage:
API_KEY = 'AIzaSyDak5k8MES2kWU2snLBhqQRgfkbCRan3oc'  # Replace with your actual API key
SEARCH_ENGINE_ID = '2334c869aa6e448c7'  # Replace with your search engine ID

title_input = 'g sai shyam'  # Example title
name_input = 'ai/ml lead'  # Example name

# Run the fetch_linkedin_profiles function 120 times with unique quota_user IDs
for i in range(120):
    quota_user_id = str(uuid.uuid4())  # Generate a unique user ID for each query
    print(f"Run {i + 1} with Quota User ID: {quota_user_id}:")
    
    profiles = fetch_linkedin_profiles(API_KEY, SEARCH_ENGINE_ID, title_input, name_input, quota_user_id)
    
    for j, profile in enumerate(profiles, start=1):
        print(f"Profile {j}: Link: {profile['link']}")
    
    print("\n")  # Print a newline for better readability between runs