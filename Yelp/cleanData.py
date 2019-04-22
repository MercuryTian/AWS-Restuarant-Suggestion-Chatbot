import json

with open("steakhouse.json", 'r') as data_file:
    data = json.load(data_file)

for element in data['businesses']:
    element.pop("rating")
    element.pop("alias")
    element.pop("url")
    element.pop("is_closed")
    element.pop("review_count")
    element.pop("image_url")
    element.pop("phone")
    element.pop("display_phone")
    element.pop("distance")
    element.pop("transactions")

# new_file = {"chinese": []}
# new_file["chinese"] = data["businesses"]

with open("yelp_restaurant.json", 'r') as data_file:
    yelp = json.load(data_file)
yelp["steakhouse"] = data["businesses"]
with open("yelp_restaurant.json", 'w') as data_file:
    data = json.dump(yelp, data_file)