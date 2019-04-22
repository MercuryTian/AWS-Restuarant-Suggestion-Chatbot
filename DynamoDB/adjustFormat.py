import json

with open("yelp1.json", 'r') as data_file:
    data = json.load(data_file)

new_file = []
for cuisine, rest_info in data.items():
    tmp = rest_info
    for rest in tmp:
        rest["cuisine"] = cuisine
    new_file.append(tmp)
    
with open("data.json", 'w') as data_file:
    data = json.dump(new_file, data_file)


with open("data.json", "r+") as data_file:
    data = json.load(data_file)

new_file = []
for ele in data:
    new_file.append(ele[0])

with open("yelp1.json", "w") as data_file:
    json.dump(new_file, data_file)