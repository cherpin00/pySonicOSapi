from SonicWall import *
from test import *

def test_getCaleb():
    sw.login("admin", "password71", authType=AuthType.BASIC, throwErrorOnFailure=False)
    sw.getIPv4AddressObjectByName("Caleb")
    sw.logout(throwErrorOnFailure=False)    

sw = SonicWall("192.168.71.3")
sw.always_params = "--connect-timeout 5 --insecure --include"
sw.log_level=LogLevel.DEBUG
sw.proxy_enable=True
sw.proxy_host="127.0.0.1"
sw.proxy_port=8888

sw.login("admin", "password71", authType=AuthType.BASIC, throwErrorOnFailure=False)

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

