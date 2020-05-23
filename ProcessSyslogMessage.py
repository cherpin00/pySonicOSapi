import requests

url = "https://google.com"

r = requests.get(url)

print(r.status_code)
print(r.json)
print(r.text)