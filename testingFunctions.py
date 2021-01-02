from SonicWall import *
from test import *

if __name__ == "__main__":
    sw = SonicWall.connectToSonicwall()
    addr = sw.getIPv4AddressObjectByName("caleb_hello")
    group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    group.addToGroupOnSonicwall("caleb_hello", sw)
    sw.commit()
    sw.logout()

    exit()
    # sw = SonicWall.connectToSonicwall()
    # addr = AddressObjectWithParams("new_test_object", "1.1.1.1")
    # sw.createIPv4AddressObject(addr)
    # group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    # group.addToGroupOnSonicwall("new_test_object", sw)
    # sw.commit()
    # sw.logout()
    # exit()
    sw = SonicWall.connectToSonicwall()
    # sw.addAddressOnjectToIPv4AddressGroupWithJson("my_AUTO_Blacklist", addr.getName(), addr.getJson(True))
    name = "web_test2_1.2.3.4"
    addr = sw.getIPv4AddressObjectByName(name)
    group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    group.addAddressObject(addr)
    group.addToGroupOnSonicwall(name, sw)
    sw.commit()
    sw.logout()
    exit()
    arr = sw.getArrayIPv4AddressObjects()
    sw.deleteAddressObject("t1")
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

