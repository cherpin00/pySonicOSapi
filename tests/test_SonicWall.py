from inspect import getsourcefile
import os.path as path, sys
current_dir = path.dirname(path.abspath(getsourcefile(lambda:0)))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])
from SonicWall import *  # Replace "my_module" here with the module name.
sys.path.pop(0)

def test_getSimple():
    sw = SonicWall.connectToSonicwall("192.168.71.3")
    # sw.login("admin", "p", authType=AuthType.BASIC, throwErrorOnFailure=False)
    sw.getIPv4AddressObjectByName("t1")
    sw.logout(throwErrorOnFailure=False)