from SonicWall import *
from test import *

if __name__ == "__main__":
    sw = SonicWall.connectToSonicwall()
    addr = sw.getIPv4AddressObjectByName("test_create1_")
    sw.addAddressOnjectToIPv4AddressGroupWithJson("my_AUTO_Blacklist", addr.getName(), addr.getJson(True))
    exit()
    arr = sw.getArrayIPv4AddressObjects()
    sw.deleteAddressObject("test_create1_")
    sw.createIPv4AddressObject()
    a = AddressObjectWithFullName("hello")
    a.getJson
    sw.getIPv4AddressObjectByName
    for addr in arr:
        print(addr)
    exit()
    sw.deleteAddressObject("test111")
    sw.commit()
    exit()
    group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    print("="*100)
    printAddressGroup(group)

