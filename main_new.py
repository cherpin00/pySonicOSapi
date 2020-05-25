from SonicWall import SonicWall, LogLevel, AuthType

sw = SonicWall("192.168.71.3")

sw.log_level=LogLevel.VERBOSE
sw.proxy_enable=False
sw.proxy_host="127.0.0.1"
sw.proxy_port=8888
sw.login("admin", "password71", authType=AuthType.BASIC, throwErrorOnFailure=False)
# sw.getIPv4AddressObjectByName("AUTO_simple")
sw.logout(throwErrorOnFailure=False)    
