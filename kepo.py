import requests

BOT_TOKEN = "8439339382:AAE4YyfgsylrfvM9xB5Urh0s51FQOFL7c48"
USER_ID = 1426697934  # ganti dengan user ID target

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
params = {"chat_id": USER_ID}

res = requests.get(url, params=params).json()
print(res)
