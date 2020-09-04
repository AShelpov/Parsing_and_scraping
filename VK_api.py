import requests
import json

token = "####"

link = "https://api.vk.com/method/groups.get?v=5.52&access_token="
parametrs = {"v": "5.52", "access_token": token, "extended": "1"}
response = requests.get(link, parametrs)

with open("vk_groups.json", "w") as file:
    file.write(json.dumps(response.json()))