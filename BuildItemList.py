import requests
import time
import json

# Set the base URL for the Grand Exchange API
base_url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?"

# Define a function to query the API for information about a specific item
def get_item_info(item_id):
    # Build the API request URL
    request_url = base_url + "item=" + str(item_id)

    # Send the request and retrieve the response
    response = requests.get(request_url)

    # Check if the request was successful
    if response.status_code == 200:
        # If the request was successful, return the data from the response as a Python dictionary
        return response.json()
    else:
        # If the request was unsuccessful, return None
        return None

# Initialize an empty list to store the responses
responses = []

# Iterate over a range of item IDs
for item_id in range(55000, 56000):
    # Add a 3-second delay between requests to avoid exceeding the rate limit
    time.sleep(4)

    # Print the item ID being queried
    print(f"Querying item ID {item_id}...")

    # Query the API for information about the current item
    item_info = get_item_info(item_id)

    # Check if the item information was successfully retrieved
    if item_info is not None:
        # If the item information was successfully retrieved, check if the item has a name
        if "name" in item_info["item"]:
            # If the item has a name, add the item ID and name to the list of responses
            responses.append({
                "item_id": item_id,
                "name": item_info["item"]["name"]
            })
            #append the item id and name to ItemList.txt
            with open("ItemList.txt", "a") as f:
                f.write(str(item_id) + " " + item_info["item"]["name"] + "\n")
        else:
            # If the item does not have a name, print an error message
            print(f"Error: No name found for item ID {item_id}")
    else:
        # If the item information was not successfully retrieved, print an error message
        print(f"Error: Failed to retrieve information for item ID {item_id}")



# Print the list of responses
print(responses)
