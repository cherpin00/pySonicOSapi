import sys
import json
import datetime
sys.path.append(".\pySonicOSapi")
from SonicWall import SonicWall
from AddressObject import AddressObjectWithParams
from AddressObject import addressObject2

data = {"ip":"1", "prefixName":"AUTO_test", "name":"testName"}
a = addressObject2(data)
print(a.name)
print(a.ip)
print(a.updated)