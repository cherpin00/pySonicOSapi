import requests
import json
import bisect
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# http=127.0.0.1:8888;https=127.0.0.1:8888
proxies = {
    "http" : "127.0.0.1:8888",
    "https" : "127.0.0.1:8888",
}

headers = {
    'Content-type' : "application/json",
    'Accept': '*/*',
    'User-Agent':'PycURL/7.43.0.1 libcurl/7.58.0 WinSSL zlib/1.2.11',
    "Expect": "100-continue",
    "Accept-Encoding" : "*",
}
response = requests.post('https://192.168.71.3:443/api/sonicos/auth', verify=False, auth=('admin', 'password71'), headers=headers, timeout=30, proxies=proxies)
print("type:", response)
print("auth response:", response.text)
print("response reason:", response.reason)
response = requests.delete('https://192.168.71.3:443/api/sonicos/auth', verify=False, auth=('admin', 'password71'), timeout=30, proxies=proxies)
print(response.text)





exit()
response = requests.put('https://192.168.71.3:443/api/sonicos/address-objects/ipv4/name/AUTO_simple', headers=headers, verify=False)
# time.sleep(5)
print("Json:", response.text)
exit()
response1 = {
     "address_object": {
         "ipv4": {
             "name": "Caleb_Simple"
            ,"uuid": "00000000-0000-0003-0100-18b1699ddacc"
            ,"zone": "WAN"

            ,"host": {
                 "ip": "8.8.8.7"
             }
         }
     }
}

response2 = {
     "address_object": {
         "ipv4": {
             "name": "Caleb_Simple"
            ,"uuid": "00000000-0000-0003-0100-18b1699ddacc"
            ,"zone": "WAN"

            ,"host": {
                 "ip": "8.8.8.7"
             }
         }
     }
}


def insert(list, n): 
    bisect.insort(list, n)  
    return list

class AdressObject:
    def __init__(self, resp):
        self.name = resp["address_object"]["ipv4"]["name"]
        self.uuid = resp["address_object"]["ipv4"]["uuid"]
        self.zone = resp["address_object"]["ipv4"]["zone"]
        self.ip = resp["address_object"]["ipv4"]["host"]["ip"]
    
    def __str__(self):
        str = ("name: " + self.name) + "\n" + \
        ("uuid: " + self.uuid) + "\n" + \
        ("zone: " + self.zone) + "\n" + \
        ("ip: " + self.ip) + "\n"
        return str
    
    def __lt__(self, other):
        return self.name < other.name

    

obj1 = AdressObject(response1)
obj2 = AdressObject(response2)

group = []
insert(group, obj2)
insert(group, obj1)
print(group[0])

# for addObj in in group:
#     if addObj.expire == None:
#         log = "no explination"
#     else:
#         if addObj.now > addObj.expire:
#             #delete
        
