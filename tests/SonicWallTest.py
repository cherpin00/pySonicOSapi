from SonicWall import *

def test_getCaleb():
    sw = SonicWall("192,168.71.3")
    sw.login("admin", "password71", authType=AuthType.BASIC, throwErrorOnFailure=False)
    sw.getIPv4AddressObjectByName("Caleb")
    sw.logout(throwErrorOnFailure=False)    