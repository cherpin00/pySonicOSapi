from SonicWall import *

def test_deleteUpdateObject(s: SonicWall):

    addr1 = AddressObjectWithParams("test_delete1", "1.1.1.1")
    try:
        s.deleteAddressObject(addr1.name, succeedIfNotExist=False)
    except:
        print("Cannot delete 'test_delete1' address object in fixture preparation.")
    s.commit()

    s.createIPv4AddressObject(addr1)
    s.commit()

    if s.deleteAddressObject(addr1.name, succeedIfNotExist=False):
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
    
