#sort the ItemList.txt file from fewest to most characters
#this is to make the search for the item name more efficient

#open the file
with open("ItemList.txt", "r") as f:
    #read the file
    lines = f.readlines()
    #sort the file
    lines.sort(key=len)
    #write the file
    with open("ItemList.txt", "w") as f:
        f.writelines(lines)

