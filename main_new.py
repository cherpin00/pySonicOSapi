from SonicWall import *
from test import *

def test_getCaleb():
    sw.login("admin", "password", authType=AuthType.BASIC, throwErrorOnFailure=False)
    sw.getIPv4AddressObjectByName("Caleb")
    sw.logout(throwErrorOnFailure=False)

def findAddrByIP(addrgrp:dict, ip, srcZone):
    for key,value in addrgrp.group.items():
        if value.getIP()==ip and value.getZone()==srcZone:
            Logger.log(f"Found IP, {ip}, in Addr: {value.getName()}")
            return value
    return None
def printAddressGroup(addrgrp:dict):
    i=0
    print("Showing Address Group Items:")
    for key,value in addrgrp.group.items():
        i+=1
        print(f"Address Object {i}: {value.getName()}, {value.getIP()}, {value.getZone()}")
        if not value.getName()==value.hiddenName:
            Logger.log(f"hiddenName and getName() are NOT equal.\nhiddenName:{value.hiddenName}\n getName():{value.getName()}")
# tests()

def createAddressObjectFromEventLogText(logEvent:str) -> AddressObject:
    logDict=keyValueStringToDict3(logEvent, fieldSep=" ", keyValueSep="=",quotedIdentifier='"')
    # for key in logDict:
    #     print(key, '=', logDict[key])
    if "m" not in logDict.keys():
        print("Can't create address object.  No sonic wall message(m) found.")
        raise RuntimeError("Can't create address object.  No sonic wall message(m) found.  msg=" + logEvent)
        return

    if logDict["m"] == "1198":
        messageID = logDict["m"]
        numOccur = 1
        eventCreated=logDict["time"]
        eventSource=logDict["fw"]
        sourceZone=logDict["srcZone"]
        destinationZone=logDict["dstZone"]
        country=logDict["msg"].split("Country Name:")[1]
        ip=logDict["src"].split(":")[0]
        descr=""
        # eventCreated, eventSource, sourceZone, destinationZone, country, ip, descr, messageID: int=-1, numOccur: int=1):
        # , eventSource, sourceZone, destinationZone, country, ip, descr, messageID: int=-1, numOccur: int=1
        a=AddressObjectWithDetails(eventCreated, eventSource, sourceZone, destinationZone, country, ip, descr, messageID, numOccur)
        return a
    else:
        print("Sonic wall message ID not handled," + "m = " + logDict["m"])
        raise RuntimeError("Sonic wall message ID not handled," + "m = " + logDict["m"]+", msg=" + logEvent)

def start():
    print("*"*100)
    print("*"*100)
    print("*"*100)
    print()
    print()
    print()
    print()

start()
Logger.LOG_LEVEL=LogLevel.NOTICE
sw=SonicWall.connectToSonicwall()

sw.logout(throwErrorOnFailure=False)
sw.login("admin", "p", authType=AuthType.BASIC, throwErrorOnFailure=True)

addressGroupName="my_AUTO_Blacklist"
addrgrp = sw.getIPv4AddressGroupByName(addressGroupName)
ip="100.1.1.23"
zone="WAN"
printAddressGroup(addrgrp)
maxGroupSize=10
Logger.log(f"# of items in group:{len(addrgrp.group)}. Max Group Size:{maxGroupSize}", msgLogLevel=LogLevel.NOTICE)
addr=findAddrByIP(addrgrp, ip, zone)
#Todo: Important.  What if the oldest Addr Object is the one that we are modifying?
sw.deleteOldestAddressObjectByLastUpdated(addrgrp, maxGroupSize=maxGroupSize+1) #we call this to make sure we don't have too many objects.  This should only happen if the script previously had failed, if the MAX number has been decreased, or if a user has added objects manually.
print("===========================")
if addr is None:
    Logger.log(f"IP Address, {ip}, and ZONE, {zone} not found.  Creating new address object for {addressGroupName}.")
    addr=AddressObjectWithParams(name="", ip=ip, zone=zone)
    if sw.createIPv4AddressObject(addr, useHiddenName=False):
        sw.deleteOldestAddressObjectByLastUpdated(addrgrp, maxGroupSize=maxGroupSize)
        newName=addr.getName()
        addrgrp.addToGroupOnSonicwall(newName, sw)

        #Todo: Still need to add this new address object to the AddressGroup
        sw.commit() #Todo:Confirm that both new addr and addition to Group can be done on same commit
        Logger.log(f"Commited new address object and added to Address Group:{addressGroupName}.", msgLogLevel=LogLevel.NOTICE)
    else:
        Logger.log(f"Cannot create address object for ip:{ip}, zone:{zone}.", msgLogLevel=LogLevel.ERROR)
else:
    #We need to update the addr
    Logger.log(f"IP Address, {ip}, and ZONE, {zone} were found.  Updating the address object.", msgLogLevel=LogLevel.WARNING)
    sw.modifyAddressObject(addr, updateWithHiddenName=False)
    sw.commit()

addrgrp = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist")
printAddressGroup(addrgrp)
print("===========================")



exit()

