import json

# Read the original items_with_images.json file
with open('items_with_images.json', 'r') as json_file:
    items_with_images = json.load(json_file)

# Sort the items based on the length of item names from shortest to longest
sorted_items = sorted(items_with_images.items(), key=lambda x: len(x[0]))

# Create a new dictionary with the sorted items and their image URLs
sorted_items_dict = {item[0]: item[1] for item in sorted_items}

# Write the sorted items back to the JSON file
with open('sorted_items_with_images.json', 'w') as json_file:
    json.dump(sorted_items_dict, json_file, indent=4)

print("Items sorted and saved to sorted_items_with_images.json")
