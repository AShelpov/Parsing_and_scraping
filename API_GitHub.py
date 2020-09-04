import requests
import random as rnd
import json
from pprint import pprint

# generate random user id, consists within 6 numbers
user_id = rnd.randint(100000, 999999)
main_link = f"https://api.github.com/user/{user_id}"
response = requests.get(main_link)
if response.status_code == 403:
    print(response.json()["message"])
else:
    output = response.json()
    try:
        login = output["login"]
    except KeyError:
        print(f"Sorry there is no user with id {user_id} on Github, try again!")
    else:
        print(f'Name of GitHub user: {output.get("name")}')
        response = requests.get(output["repos_url"])
        response = response.json()

        with open(f"{output['name']}.json", "w") as file:
            file.write(json.dumps(response))

        for i in range(len(response)):
            print(f'Name of repo: {response[i]["full_name"].split("/")[1]}', end="\t")
            print(f'repo link: {response[i]["html_url"]}')
