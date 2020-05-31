from SonicWall import *
from test import *

def test_getCaleb():
    sw.login("admin", "password", authType=AuthType.BASIC, throwErrorOnFailure=False)
    sw.getIPv4AddressObjectByName("Caleb")
    sw.logout(throwErrorOnFailure=False)


def x1(str, quotechar='"'):
    print(f"keyValueString:{str}")
    for item in next(csv.reader([str], delimiter=";", quotechar=quotechar, quoting=csv.QUOTE_ALL)):
        print("Item", item)
        for item2 in next(csv.reader([item], delimiter="=", quotechar=quotechar)):
            print("Item2", item2)

    print("--------------")

test_createAddressObject2("")
exit()
test_parseLogEvent()
exit()
test_keyValueStringToDict()

test_createAddressObject2("")

exit()

sw = SonicWall("192.168.71.3")
sw.always_params = "--connect-timeout 5 --insecure --include"
sw.log_level=LogLevel.DEBUG
sw.proxy_enable=True
sw.proxy_host="127.0.0.1"
sw.proxy_port=8888

sw.login("admin", "p", authType=AuthType.BASIC, throwErrorOnFailure=True)

test_createAddressObject(sw,"David Herpin")
obj1 = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist").get(0)
print(obj1.getName())

exit(1)
test_deleteUpdateObject(sw)
test_updateAddressObject(sw)
sw.logout()
exit()


# test_getCaleb()
# exit()
sw.login("admin", "password71", authType=AuthType.BASIC, throwErrorOnFailure=False)
sw.getIPv4AddressObjectByName("Caleb")

# addrObj = AddressObjectWithParams("Caleb", "1.1.1.1")
# sw.createIPv4AddressObject(addrObj)
# newAddrObj = AddressObjectWithParams("Caleb", "1.1.1.2")
# sw.modifyAddressObject(newAddrObj)
# sw.commit()
# sw.getPendingChanges()

sw.logout(throwErrorOnFailure=False)    

