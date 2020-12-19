from SonicWall import *
from functions import *

logEvent1='<105>1 2020-05-16T15:04:17.504337-05:00 192.168.1.1  - - -  '+\
    'id=firewall sn=C0EAE48632A0 time="2020-05-16 15:04:17" '+\
    'fw=97.105.93.2 pri=1 c=0 gcat=3 m=1198 srcMac=00:d0:02:0a:5c:00 '+\
    'src=54.254.165.111:51898:X1 srcZone=WAN dstMac=c2:ea:e4:86:32:a1 dst=10.10.2.17:443:X3 '+\
    'dstZone=VPN proto=tcp/https rcvd=60 vpnpolicyDst="Vultr IPSec Gateway via PFSense" '+\
    'app=49177 appName="General HTTPS" '+\
    'msg="Initiator from country blocked: Initiator IP:54.254.165.111 Country Name:Singapore" n=2100544'
expected1={'<105>1': '', '2020-05-16T15:04:17.504337-05:00': '', '192.168.1.1': '', '': '', '-': '', 'id': 'firewall', 'sn': 'C0EAE48632A0', 'time': '2020-05-16 15:04:17', 'fw': '97.105.93.2', 'pri': '1', 'c': '0', 'gcat': '3', 'm': '1198', 'srcMac': '00:d0:02:0a:5c:00', 'src': '54.254.165.111:51898:X1', 'srcZone': 'WAN', 'dstMac': 'c2:ea:e4:86:32:a1', 'dst': '10.10.2.17:443:X3', 'dstZone': 'VPN', 'proto': 'tcphttps', 'rcvd': '60', 'vpnpolicyDst': 'Vultr IPSec Gateway via PFSense', 'app': '49177', 'appName': 'General HTTPS', 'msg': 'Initiator from country blocked: Initiator IP:54.254.165.111 Country Name:Singapore', 'n': '2100544'}

def tests():
    sw=SonicWall.connectToSonicwall()

    sw.logout(throwErrorOnFailure=False)
    sw.login("admin", "p", authType=AuthType.BASIC, throwErrorOnFailure=True)
    test_createAddressObject(sw)

    test_createAddressObject3_SlashInName(sw)
    test_createAddressObject2(sw)
    test_parseLogEvent()
    # exit()
    test_keyValueStringToDict()

    test_createAddressObject2(sw)

    # exit()

    test_createAddressObject(sw,"David Herpin")

    obj1 = sw.getIPv4AddressGroupByName("my_AUTO_Blacklist").get(0)
    print(obj1.getName())

    test_deleteUpdateObject(sw)
    test_updateAddressObject(sw)
    # sw.logout()
    # exit()

    sw.logout(throwErrorOnFailure=False)    

def test_createAddressObject3_SlashInName(s: SonicWall):
    countryToReplace="Singapore"
    country="Hong Kong/China"
    countryExpected=country.replace("/","-")
    logEvent=logEvent1.replace(countryToReplace, country)
    
    logDict=keyValueStringToDict3(logEvent, fieldSep=" ", keyValueSep="=",quotedIdentifier='"')
    # for key in logDict:
    #     print(key, '=', logDict[key])
    if "m" not in logDict.keys():
        print("Can't create address object.  No sonic wall message(m) found.")
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
    else:
        print("Sonic wall message ID not handled," + "m = " + logDict["m"])
    import datetime
    testDict = {'hiddenName': '', 'prefixName': 'AUTO_type1_', 'zone': 'WAN', 'ip': '54.254.165.111', 'country': 'Hong Kong-China', 'descr': '', 'eventCreated': '2020-05-16 15:04:17', 'created': datetime.datetime(2020, 5, 31, 15, 18, 53, 256122), 'updated': '', 'numOccur': 1, 'eventSource': '97.105.93.2', 'messageID': '1198', 'destinationZone': 'VPN', 'sourceZone': 'WAN'}
    checkIsEqual(a.compareFromDict(testDict, dontCares=["created"]), True, "Adress object creation from logEvent")
    checkIsEqual(a.country, countryExpected, "Replace slashes with dashes in Country")


def test_createAddressObject2(s: SonicWall):
    x1=AddressObjectWithParams("name1", "1.1.1.1", "WAN")
    # x2=AddressObjectWithDict(AddressObject):
    # x3=AddressObjectWithDetails(AddressObject):
    # x4=AddressObjectWithFullName():

    logEvent=logEvent1
    logDict=keyValueStringToDict3(logEvent, fieldSep=" ", keyValueSep="=",quotedIdentifier='"')
    # for key in logDict:
    #     print(key, '=', logDict[key])
    if "m" not in logDict.keys():
        print("Can't create address object.  No sonic wall message(m) found" )
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
    else:
        print("Sonic wall message ID not handled," + "m = " + logDict["m"])
    import datetime
    testDict = {'hiddenName': '', 'prefixName': 'AUTO_type1_', 'zone': 'WAN', 'ip': '54.254.165.111', 'country': 'Singapore', 'descr': '', 'eventCreated': '2020-05-16 15:04:17', 'created': datetime.datetime(2020, 5, 31, 15, 18, 53, 256122), 'updated': '', 'numOccur': 1, 'eventSource': '97.105.93.2', 'messageID': '1198', 'destinationZone': 'VPN', 'sourceZone': 'WAN'}
    checkIsEqual(a.compareFromDict(testDict, dontCares=["created"]), True, "Adress object creation from logEvent")
    print("printed name:" , a.getName())
    expectedName="AUTO_type1_;evtCreated=2020-05-16 15:04:17;country=Singapore;srcZone=WAN;dstZone=VPN;ip=54.254.165.111;created=2020-05-31 16:35:18.303117;updated=;numOccur=1;eventSource=97.105.93.2;msgID=1198;descr=;".replace("created=2020-05-31 16:35:18.303117;", "created=x;")
    checkIsEqual(a.getName().replace("created=" + str(a.created) + ";", "created=x;"), expectedName, "Test getName() function")

    test_createAddressObjectOnSonicwall(s, a.getName(), a.ip, a.sourceZone)


def test_parseLogEvent():
    logEvent=logEvent1
    d=keyValueStringToDict3(logEvent, fieldSep=" ", keyValueSep="=", quotedIdentifier='"')
    expected=expected1
    checkIsEqual(d, expected, "Parsed logEvent string into Dictionary.  Log event string was:" + logEvent)
def logToJson(logEvent: str):
    newStr=logEvent.split(" ")

def keyValueStringToDict(keyValue: str, fieldSep=";", keyValueSep="="):
    r=dict(item.split("=") for item in keyValue.split(";"))
    return r

def keyValueStringToDict2(keyValueString: str, fieldSep: str=";", keyValueSep: str="=", quotedIdentifier: str='"'):
    import csv

    # print(f"keyValueString:{keyValueString}")
    # for item in next(csv.reader([keyValueString], delimiter=";", quotechar=quotedIdentifier, quoting=csv.QUOTE_ALL)):
    #     print("Item", item)

    #The following adapted from: https://stackoverflow.com/questions/186857/splitting-a-semicolon-separated-string-to-a-dictionary-in-python
    r=dict(next(csv.reader([item], delimiter=keyValueSep)) 
         for item in next(csv.reader([keyValueString], delimiter=fieldSep, quotechar=quotedIdentifier)))
    return r

    # str='a=1;b="now is=; the timea";c=3'

def test_keyValueStringToDict():
    str="a=1;b=2;c=3"
    val=keyValueStringToDict2(str)
    expected={"a":"1", "b":"2", "c":"3"}
    checkIsEqual(val, expected, msg="simple keyValueStringToDict2 test for: " + str, throwError=True)

    val=keyValueStringToDict(str)
    checkIsEqual(val, expected, msg="simple keyValueStringToDict test for: " + str, throwError=True)


    str="a=1;b='now is the time';c=3"
    val=keyValueStringToDict(str)
    expected={"a":"1", "b":"'now is the time'", "c":"3"}
    checkIsEqual(val, expected, msg="keyValueStringToDict test #2 for: " + str, throwError=True)

    val=keyValueStringToDict2(str, quotedIdentifier="'")
    expected={"a":"1", "b":"'now is the time'", "c":"3"}
    checkIsEqual(val, expected, msg="keyValueStringToDict test #2 for: " + str + ". Notice quotes are missing in val.", throwError=True)

    str='a=1;b="now is=; the timea";c=3'
    try:
        val=keyValueStringToDict3(str, quotedIdentifier='"')
    except:
        val={}
    expected={"a":"1", "b":"now is: the; time", "c":"3"}
    checkIsEqual(val, expected, msg="keyValueStringToDict test #2 for: " + str + ". Notice quotes are missing in val.", throwError=False)

def test_createAddressObjectOnSonicwall(s: SonicWall, objName:str, ip:str, zone:str="WAN"):
    addr1 = AddressObjectWithParams(objName, ip, zone)
    try:
        s.deleteAddressObject(addr1.hiddenName, succeedIfNotExist=False)
        s.commit()
    except:
        print(f"Cannot delete address object, {objName}, address object in fixture preparation.")

    try:
        s.createIPv4AddressObject(addr1, useHiddenName=True)
    except:
        e = sys.exc_info()[0]
        print(f"Error: {e}")
        print(f"Cannot create new address object, {objName}, address object in fixture preparation.")
        s.log("Failed test: " + sys._getframe().f_code.co_name)

    # try:
    s.commit()
    addr2=s.getIPv4AddressObjectByName(addr1.hiddenName)
    if addr1.getIP()==addr2.getIP() and addr1.getZone()==addr2.getZone():
        s.log("Passed test: " + sys._getframe().f_code.co_name)
    else:
        print(f"After creating, {addr1.hiddenName}, the value retrieved does not match.")
        print("Expecting:", addr1)
        print("Got:", addr2)
        s.log("Failed test: " + sys._getframe().f_code.co_name)        
    # except:
    #     Logger.log("Error occurred.", sys.exc_info()[0], msgLogLevel=LogLevel.ERROR)
    #     print(f"Cannot commit new address object, {objName}, address object in fixture preparation.")
    #     print("AddrObj:", addr1)
    #     s.log("Failed test: " + sys._getframe().f_code.co_name)

def test_createAddressObject(s: SonicWall, appendName: str=""):
    test_createAddressObjectOnSonicwall(s, "test_create1_"+appendName, "2.1.1.1")

def test_deleteUpdateObject(s: SonicWall):

    addr1 = AddressObjectWithParams("test_delete1", "1.1.1.1")
    try:
        s.deleteAddressObject(addr1.hiddenName, succeedIfNotExist=False)
    except:
        print("Cannot delete 'test_delete1' address object in fixture preparation.")
    s.commit()

    s.createIPv4AddressObject(addr1, useHiddenName=False)
    s.commit()

    if s.deleteAddressObject(addr1.getName(), succeedIfNotExist=False):
        s.commit()
        #Todo: Need to test COMMIT and ROLLBACK.
        s.log("Pass test: " + sys._getframe().f_code.co_name)
    else:
        s.log("Failed test: " + sys._getframe().f_code.co_name)

def test_updateAddressObject(s: SonicWall):
    #Assume that test_update1 object can be deleted if it exists.
    #Todo: All tests should check if anything is waiting to be committed before continuingpygame.examples.aliens.main()
    #Todo: Need to be able to specify option to only commit if ONE change is pending.
    try:
        s.deleteAddressObject("test_update1", succeedIfNotExist=False)
    except:
        e = sys.exc_info()[0]
        print(f"Cannot delete 'test_update1' address object in fixture preparation.  \nError was:{e}")
    s.commit()

    addr1 = AddressObjectWithParams("test_update1", "1.1.1.1")
    s.createIPv4AddressObject(addr1)
    s.commit()

    addr2=AddressObjectWithParams("test_update1", "1.1.1.2")
    s.modifyAddressObject(addr2, throwErrorOnFailure=True)
    s.commit()
    addr3=s.getIPv4AddressObjectByName("test_update1")
    if addr2==addr3:
        s.log("Pass test: " + sys._getframe().f_code.co_name)
    else:
        s.log("Failed test: " + sys._getframe().f_code.co_name)
    
