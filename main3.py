from http.client import HTTPSConnection
from base64 import b64encode
import ssl
#This sets up the https connection
# c = HTTPSConnection("192.168.71.3", 443, context=ssl._create_unverified_context(), timeout=10)
# c.set_tunnel("127.0.0.1", port=8888)
c = HTTPSConnection("127.0.0.1", port=8888, context=ssl._create_unverified_context())
c.set_tunnel("192.168.71.3", 443)
#we need to base 64 encode it 
#and then decode it to acsii as python 3 stores it as a byte string
userAndPass = b64encode(b"admin:password71").decode("ascii")
headers = { 'Authorization' : 'Basic %s' %  userAndPass }
#then connect
c.request('GET', '/api/sonicos/auth', headers=headers)
#get the response back
res = c.getresponse()
# at this point you could check the status etc
# this gets the page text
data = res.read()  
print(data)
