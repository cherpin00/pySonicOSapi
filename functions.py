from enum import Enum

from logger import Logger

def keyValueStringToDict3(keyValueString: str, fieldSep=";", keyValueSep="=", quotedIdentifier="'"):
    #Adapted from https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
    #Also, there are many more options in the above s.o. q&a.  A Google search for: python parse string quoted
    from tssplit import tssplit
    import csv
    # print("String is", keyValueString)
    # print("===================================================")
    fields=tssplit(keyValueString, quote=quotedIdentifier, delimiter=fieldSep)
    for index,item in enumerate(fields):
        if keyValueSep not in item:
            fields[index]=item+keyValueSep
        #     print("Adding keyValueSep", keyValueSep)
        # print("index, item", index, item)
    r=dict(next(csv.reader([item], delimiter=keyValueSep)) 
        for item in fields)
    return r

def checkIsEqual(val, expected, msg: str, throwError: bool=True) -> bool:
    if val==expected:
        print("Passed test: Val", val, "EQUALS Expected", expected, msg)
        return True
    else:
        print("Failed test: Val\n", val, "EQUALS Expected\n", expected, msg)
        if throwError:
            raise RuntimeError("checkIsEqual failed test: " + msg)
        else:
            return False

def exceptionWithTraceback(msg:str, blnThrowError=True):
    import traceback, sys
    #Todo:Consider passing in a LogLevel and defaulting to ERROR.  If logLevel not met, then just LOG simple info.  This maynot be a good idea.
    print("Exception in user code:")
    print('-'*60)
    #Todo: Need to consider other options.  Does this print the entire stack?
    traceback.print_exc(file=sys.stdout)
    print('-'*20)
    print(f"Error occurred.  MSG is:\n{msg}\n")
    print('-'*60)
    if blnThrowError:
        raise RuntimeError(f"Error occurred.  See above for message details.")

def getDateTime(s:str, default=None, throwOnError=True, logger=None):
    from dateutil.parser import parse
    from datetime import datetime
    try:
        s=s.replace("_", " ")   #we see underscores in the datetime and dateutil.parser doesn't handle the underscores.
        r=parse(s)
        return r
    except:
        if throwOnError:
            if not logger==None:
                logger.log(msg=f"Error parsing string, '{s}' to date.  raising Exception.")
                raise RuntimeError(f"Error parsing string, '{s}' to date.")
        else:
            if not logger==None:
                logger.log(msg=f"Error parsing string, '{s}' to date.  Using default value, {default}.")
                r=default
                return r

def printAddressGroup(addrgrp:dict):
    i=0
    print("Showing Address Group Items:")
    for key,value in addrgrp.group.items():
        i+=1
        print(f"Address Object {i}: {value.getName()}, {value.getIP()}, {value.getZone()}")
        if not value.getName()==value.hiddenName:
            Logger.log(f"hiddenName and getName() are NOT equal.\nhiddenName:{value.hiddenName}\n getName():{value.getName()}")