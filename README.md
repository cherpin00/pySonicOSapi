# pySonicOSapi

Fiddler must be open and listening on port 8888

Remember to commit


Steps to add to a group
    sw = SonicWall.connectToSonicwall()
    addr = sw.getIPv4AddressObjectByName("caleb_hello")
    group = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
    group.addToGroupOnSonicwall("caleb_hello", sw)
    sw.commit()
    sw.logout()