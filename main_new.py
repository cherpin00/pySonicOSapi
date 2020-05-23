from SonicWall import SonicWall, LogLevel, AuthType

sw = SonicWall("192.168.71.3")

sw.log_level=LogLevel.INFO
sw.login("admin", "password71", authType=AuthType.BASIC,throwErrorOnFailure=False)
sw.logout(throwErrorOnFailure=False)