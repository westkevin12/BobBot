import csv
import json

# Open the CSV file
with open('ecc_item_list.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header row

    # Initialize a dictionary to store item data
    items_data = {}

    # Loop through the CSV rows and extract data
    for row in csv_reader:
        item_name = row[0]
        image_url = row[1]
        items_data[item_name] = image_url

# Save the data as a JSON file
with open('items_with_images.json', 'w') as json_file:
    json.dump(items_data, json_file, indent=4)
