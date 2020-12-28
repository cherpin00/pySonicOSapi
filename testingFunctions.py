from SonicWall import *
from test import *

if __name__ == "__main__":
    sw = SonicWall.connectToSonicwall()
    # sw.getIPv4AddressObjectByName("test_create1_")
    arr = sw.getArrayIPv4AddressObjects()
    sw.deleteAddressObject("test_create1_")
    for addr in arr:
        print(addr)
    exit()
    sw.deleteAddressObject("test111")
    sw.commit()
    exit()
    group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    print("="*100)
    printAddressGroup(group)

