from SonicWall import *

names = [
    " AUTO_type1_eventCreated=2020-05-16 15:04:17;country=Singapore;sourceZone=WAN;destinationZone=VPN;ip=54.254.165.111;created=2020-05-31 17:30:02.574251;updated=;numOccur=1;eventSource=97.105.93.2;messageID=1198;descr=;",
]

group = AddressGroup()

sw = SonicWall("192.168.71.3")
obj1 = AddressObjectWithParams()

group.addAddressObject()