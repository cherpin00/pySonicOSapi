from datetime import datetime
from functions import *
from logger import *

		


class AddressObject:
	def __init__(self, ip, hiddenName="", zone="WAN", eventCreated="", eventSource="pySonicOSapi", sourceZone="", destinationZone="", country="", descr="", messageID: int=-1, numOccur: int=1, updated: str="", created: str=""):
		from datetime import datetime
			# AddressObject: represents a Sonicwall AddressObject
			# jsonSonicWall: this is the JSON returned by the SonicwallAPI
			#     It contains IP address, Zone, and Name
			# The NAME field from the jsonSonicWall is a KeyValue LOV.

			# createAddressObject from 
			#     NAME LOV.
			#     Details (each of the details are passed in)
		self.keys = {"eventCreated":"evtCreated", "country":"", "sourceZone":"srcZone", "destinationZone":"dstZone", "ip":"", "created":"", "updated":"", "numOccur":"", "eventSource":"", "messageID":"msgID", "descr":""}
		self.hiddenName = hiddenName  #this is what was used to create the object.  getName() will equal this if nothing has been changed since creation
		self.prefixName="AUTO_type1_" #All object names will begin with this
		self.sourceZone = zone  #For GeoIP Blocked, this would be WAN - (we would not want to block LAN SourceZones)
		self.zone = zone
		self.ip = ip
		self.country=country
		self.descr=descr
		self.eventCreated=eventCreated #Date of event (may be different from created date)
		if created=="":
			self.created=datetime.now().strftime("%Y-%m-%d_%H:%M:%S")	#this is date Addr Object was created
		else:
			self.created=created
		self.updated=updated #this is date the AddrObject was last updated
		self.numOccur=numOccur #this is number of times the AddrObject was modified (to count # of times this IP has hit the firewall)
		self.eventSource=eventSource  #this is usually the IP Address of the device that generated the Event
		self.messageID=messageID	#this is the eventID from the device (1198=Geo IP Blocked)
		self.destinationZone=destinationZone  #For GeoIP Blocked, this would be, for example, LAN
		for key in self.__dict__.keys():
			if "/" in str(self.__dict__[key]):
				Logger.log(f"TODO: Log this.  There is a slash(/) in the key, {key}.  This is being changed to a dash(-).  New value is, {self.__dict__[key]}", msgLogLevel=LogLevel.ALERT)
				self.__dict__[key]=self.__dict__[key].replace("/", "-")
	
	def getLastUpdated(self):
		#if updated has a date/time, use it
		#if updated doesn't have a date/time, use created
		#if created doesn't have a date/time, use now()
		#if any of the needed fields don't have a valid value, use the oldest value or NoW()
		#myNow=now()
		#updated=isnull(self.updated, oldest)
		#created=isnull(self.created, updated)
		#return case when self.updated=="" and self.created="" then now else max(updated,created)
		#NOW=2/5
		#1. updated=""-oldest, created=1/5  ---> return 1/5
		#2. updated="1/5", created=""-oldest --> return 1/5
		#3. updated="", created=""   ---> return 2/5
		from datetime import datetime
		oldest=datetime.min
		myUpdated=getDateTime(self.updated, None, logger=Logger) if not self.updated=="" else oldest
		myCreated=getDateTime(self.created, None, logger=Logger) if not self.created=="" else myUpdated
		if myUpdated==None or myCreated==None:
			raise RuntimeError(f"Cannot interpret Updated and/or Created to a valid date & time. updated:{self.updated}, created:{self.created}")
		if self.updated=="" and self.created=="":
			Logger.log(f"Both updated and created are missing.  Using NOW()")
			return datetime.now()
		else:
			r=max(myUpdated, myCreated)
		Logger.log(f"In getLastUpdated\nupdated:{self.updated}\ncreated:{self.created}\nChosen:{r}", msgLogLevel=LogLevel.CRITICAL)
		return r

	def getName(self):
		rvalue = self.__dict__["prefixName"] + ";"
		keys = self.keys
		for key,value in keys.items():
			if value=="":
				value=key
			# rvalue += value + "=" + str(self.__dict__[str(key)]) + ";"
			# print("key", key, value)
			# print("rvalue", rvalue)
			rvalue += value + "=" + str(self.__dict__.get(str(key), "")) + ";"
		#Todo:Test removal of trailing semicolon(;)
		if rvalue[-1]==";":
			rvalue=rvalue[:-1]
		if len(rvalue)>200:
			raise RuntimeError(f"invalid length of Name.  Sonicwall only supports up to 200 characters.  Name:{rvalue}") 
		return rvalue
		# return f"{self.prefixName};eventCreated={self.eventCreated}Country={self.country};sourceZone={self.sourceZone};destZone={self.destinationZone}"
	
	# def getName2(self):
	# 	rvalue = self.__dict__["prefixName"] + ";"
	# 	# keys = ["eventCreated", "country", "sourceZone", "destinationZone", "ip", "created", "updated", "numOccur", "eventSource", "messageID", "descr"]
	# 	keys = {"eventCreated":"evtCreated", "country":"", "sourceZone":"srcZone", "destinationZone":"dstZone", "ip":"", "created":"", "updated":"", "numOccur":"", "eventSource":"", "messageID":"msgID", "descr":""}
	# 	keys = {"ip":"", "lastThreat":"", "updated":"", "lastProt":"", "created":"", "numOccur":""}
	# 	for key,value in keys.items():
	# 		if value=="":
	# 			value=key
	# 		rvalue += value + "=" + str(self.__dict__[str(key)]) + ";"
	# 	#Todo:Test removal of trailing semicolon(;)
	# 	if rvalue[-1]==";":
	# 		rvalue=rvalue[:-1]
	# 	if len(rvalue)>200:
	# 		raise RuntimeError(f"invalid length of Name.  Sonicwall only supports up to 200 characters.  Name:{rvalue}") 
	# 	return rvalue
	# 	# return f"{self.prefixName};eventCreated={self.eventCreated}Country={self.country};sourceZone={self.sourceZone};destZone={self.destinationZone}"

	def __str__(self):
		str = ("name: " + self.hiddenName) + "\n" + \
		("zone: " + self.zone) + "\n" + \
		("ip: " + self.ip) + "\n"
		return str
	
	def __lt__(self, other):
		return self.hiddenName < other.hiddenName

	def getZone(self):
		return self.sourceZone
	def getIP(self):
		return self.ip
	def getJson(self, getHiddenName:bool = False):  #Todo: this jSon is specific to what the SonicOSApi is expecting when calling it's API.
		import json
		rvalue = {
			"address_object" : {
				"ipv4" : {
					"name" : self.getName() if not getHiddenName else self.hiddenName,
					"zone" : self.getZone(),
					"host" : {
						"ip" : self.getIP(),
					},
				},
			},
		}
		return json.dumps(rvalue)


	def compareFromDict(self, testDict, dontCares=[]):
		from datetime import datetime
		for key in testDict.keys():
			if key in dontCares:
				continue
			if not self.__dict__[key] == testDict[key]:
				print("NOT EQUAL", key, self.__dict__[key])
				print("NOT EQUAL", key, testDict[key])
				return False
		return True

	def __eq__(self, other):
		dontCares = ["created"]
		return self.compareFromDict(other.__dict__, dontCares)

class addressObjectWithDict2(AddressObject):
	def __init__(self, dataDict:dict):
		if "ip" not in dataDict:
			raise RuntimeError("IP is a required field.")
		# if "prefixName" not in dataDict:
		# 	raise RuntimeError("prefixName is a required field.")
		# if dataDict["prefixName"][:4]!="AUTO":
		# 	raise RuntimeError("prefixName must begin with AUTO.")
		for k, v in dataDict.items():
			setattr(self, k, v)

		self.keys = {"eventCreated":"evtCreated", "country":"", "sourceZone":"srcZone", "destinationZone":"dstZone", "ip":"", "created":"", "updated":"", "numOccur":"", "eventSource":"", "messageID":"msgID", "descr":""}
		self.created=datetime.now().strftime("%Y-%m-%d_%H:%M:%S") #this is date Addr Object was created
		self.updated=self.created #this is date the AddrObject was last updated
		self.numOccur=1 #this is number of times the AddrObject was modified (to count # of times this IP has hit the firewall)

		eventCreated=AddressObjectWithDict.getValue(dataDict, "eventCreated", "")
		eventSource=AddressObjectWithDict.getValue(dataDict, "eventSource", "")
		sourceZone=AddressObjectWithDict.getValue(dataDict, "sourceZone", "")
		destinationZone=AddressObjectWithDict.getValue(dataDict, "destinationZone", "")
		country=AddressObjectWithDict.getValue(dataDict, "country", "")
		descr=AddressObjectWithDict.getValue(dataDict, "descr", "")
		messageID=AddressObjectWithDict.getValue(dataDict, "messageID", "-1")
		numOccur=int(AddressObjectWithDict.getValue(dataDict, "numOccur", 1))
		updated=AddressObjectWithDict.getValue(dataDict, "updated", "")
		created=AddressObjectWithDict.getValue(dataDict, "created", "")

		#TODO: HiddenName, zone, and ip should not be requeried to be passed into the dictinary in this case they are?
		super().__init__(self.ip, hiddenName = self.hiddenName, zone = self.zone, eventCreated=eventCreated, eventSource=eventSource\
				, sourceZone=sourceZone, destinationZone=destinationZone, country=country, descr=descr\
				, messageID=messageID, numOccur=numOccur, updated=updated, created=created)

		self.prefixName=dataDict.get("prefixName", "AUTO_unknown")	#set this here in case the parent class changes it

		# super().__init__(self.ip)

class AddressObjectWithParams(AddressObject):
	def __init__(self, name: str, ip: str, zone: str="WAN"):
		super().__init__(ip, hiddenName=name, zone=zone)

class AddressObjectWithDict(addressObjectWithDict2):
	labels = {"eventCreated":"evtCreated", "country":"", "sourceZone":"srcZone", "destinationZone":"dstZone", "ip":"", "created":"", "updated":"", "numOccur":"", "eventSource":"", "messageID":"msgID", "descr":""}
	@staticmethod
	def getValue(dict, keyToGet, default):
		key=AddressObjectWithDict.labels[keyToGet]
		if key=="":
			key=keyToGet
		r=dict[key] if key in dict.keys() else default
		return r
	
	def __init__(self, ipv4Dict: dict):
		#Todo: Need to validate the dict_response.  It should have Zone, IP, Name and be structured correctly.
		#AUTO_type1_eventCreated=;country=;sourceZone=WAN;destinationZone=;ip=2.1.1.1;created=2020-05-31 20:22:35.957445;updated=;numOccur=1;eventSource=pySonicOSapi;messageID=-1;descr=;"

		try:
			name=ipv4Dict["address_object"]["ipv4"]["name"]
			ip=ipv4Dict["address_object"]["ipv4"]["host"]["ip"]
			zone=ipv4Dict["address_object"]["ipv4"]["zone"]
			obj=keyValueStringToDict3(name, fieldSep=";", keyValueSep="=", quotedIdentifier='"')
			#Todo: We should get the labels for fields from a centralized place.  e.g. sourceZone=srcZone.
			if "ip" in obj.keys():
				if not obj["ip"]==ip:
					#Todo:Test obj.ip.
					ip2=obj["ip"]
					Logger.log(f"Warning: IP Address changing from: {ip2}, to: {ip}", msgLogLevel=LogLevel.WARNING)
			else:
				obj["ip"] = ip
			if "srcZone" in obj.keys():
				if not obj["srcZone"]==zone:
					#Todo:Test obj.sourceZone.
					srcZone2=obj["srcZone"]
					Logger.log(f"Warning: sourceZone changing from: {srcZone2}, to: {zone}", msgLogLevel=LogLevel.WARNING)
	
			# eventCreated=AddressObjectWithDict.getValue(obj, "eventCreated", "")
			# eventSource=AddressObjectWithDict.getValue(obj, "eventSource", "")
			# sourceZone=AddressObjectWithDict.getValue(obj, "sourceZone", "")
			# destinationZone=AddressObjectWithDict.getValue(obj, "destinationZone", "")
			# country=AddressObjectWithDict.getValue(obj, "country", "")
			# descr=AddressObjectWithDict.getValue(obj, "descr", "")
			# messageID=AddressObjectWithDict.getValue(obj, "messageID", "-1")
			# numOccur=int(AddressObjectWithDict.getValue(obj, "numOccur", 1))
			# updated=AddressObjectWithDict.getValue(obj, "updated", "")
			# created=AddressObjectWithDict.getValue(obj, "created", "")

			# #If obj didn't have an eventCreated, then make sure it does.
			# obj["eventCreated"] = eventCreated
			# obj["eventSource"]=eventSource
			# obj["sourceZone"]=sourceZone
			# obj["destinationZone"]=destinationZone
			# obj["country"]=country
			# obj["descr"]=descr
			# obj["messageID"]=messageID
			# obj["numOccur"]=numOccur
			# obj["updated"]=updated
			# obj["created"]=created

			if "hiddenName" in obj:
				raise RuntimeError(f"hiddenName cannot be a field in the Name of an AddressObject.  Name={name}")

			obj["prefixName"]=list(obj.keys())[0]	#the prefixName doesn't have a key/value pair.  The first item should always be the prefixName.

			obj["hiddenName"]=name
			obj["zone"]=zone

			super().__init__(obj)

			# eventSource=obj["evtSource"] if "evtSource" in obj.keys() else "pySonicOSapi"
			# sourceZone=obj["sourceZone"] if "sourceZone" in obj.keys() else ""
			# destinationZone=obj["dstZone"] if "destinationZone" in obj.keys() else ""
			# country=obj["country"] if "country" in obj.keys() else ""
			# descr=obj["descr"] if "descr" in obj.keys() else ""
			# messageID=obj["messageID"] if "messageID" in obj.keys() else -1
			# numOccur=int(obj["numOccur"]) if "numOccur" in obj.keys() else 1
			# updated=obj["updated"] if "updated" in obj.keys() else ""
			# created=obj["created"] if "created" in obj.keys() else ""
			# super().__init__(ip, hiddenName = name, zone = zone, eventCreated=eventCreated, eventSource=eventSource\
			# 	, sourceZone=sourceZone, destinationZone=destinationZone, country=country, descr=descr\
			# 	, messageID=messageID, numOccur=numOccur, updated=updated, created=created)
		except:
			exceptionWithTraceback(f"Error creating Address Object with dictionary.\nIPv4 Dict:{ipv4Dict}")

class AddressObjectWithDetails(AddressObject):
	def __init__(self, eventCreated, eventSource, sourceZone, destinationZone, country, ip, descr, messageID: int=-1, numOccur: int=1):
		super().__init__(ip, eventCreated=eventCreated, eventSource=eventSource, sourceZone=sourceZone, destinationZone=destinationZone, country=country, descr=descr, messageID = messageID, numOccur=numOccur)

class AddressObjectWithFullName(AddressObject):
	def __init__(self, name):
		arr = name.split(";")
		myDict = {}
		for keyValue in arr:
			myDict[keyValue.split("=")[0]]=keyValue.split("=")[1]
		super().__init__(myDict["ip"],  zone=myDict["zone"], eventCreated=myDict["eventCreated"], sourceZone=myDict["sourceZone"], destinationZone=myDict["destinationZone"], country=myDict["country"], descr=myDict["descr"], messageID=myDict["messageID"], numOccur=myDict["numOccur"])

class AddressGroup:
	def __init__(self, orig_json:str = ""):
		#orig_json: this is the json that was retrieved from the Sonicwall
		self.group = {}
		self.orig_json=orig_json
	
	def __str__(self):
		rvalue = str(self.group)
		return rvalue		
	
	def get(self, idx):
		for index, key in enumerate(self.group.keys()):
			if index == idx:
				return self.group[key]

	def addAddressObject(self, addressObject: AddressObject):
		self.group[addressObject.hiddenName] = addressObject #.getJson()["address_object"]

	def addToGroupOnSonicwall(self, addressObjectName:str, objSonicwall):
		import json
		#Todo:This really belongs directly in the Sonicwall Class, just like other AddressObject logic.  Consider moving it.
		if self.orig_json=="":
			raise RuntimeError("Missing original json in addToGroupOnSonicwall")
		mydict=json.loads(self.orig_json)
		addrGroupName=mydict["address_group"]["ipv4"]["name"]
		mydict["address_group"]["ipv4"]["address_object"]["ipv4"] = []
		addr={"name":addressObjectName}
		mydict["address_group"]["ipv4"]["address_object"]["ipv4"].append(addr)
		newJson=json.dumps(mydict)
		return objSonicwall.addAddressOnjectToIPv4AddressGroupWithJson(addrGroupName, addressObjectName, newJson)

	def findOldestAddrByLastUpdated(self):
		from datetime import datetime
		oldest=None
		oldestAddr=None
		for index, key in enumerate(self.group.keys()):
			addr=self.group[key]
			lastUpdated=addr.getLastUpdated()
			# if not addr.updated is None:
			# 	updatedDatetime=datetime.strptime(addr.updated, '%Y-%m-%d_%H:%M:%S')
			# else:
			# 	updatedDatetime=None
			if oldest is None or lastUpdated < oldest:
				#Todo:What happens if the updated time doesn't exactly match the string format given?
				oldest=lastUpdated
				oldestAddr=addr
		if oldestAddr is None:
			Logger.log(f"Cannot find oldest addrObject.  Size is {len(self.group)}", msgLogLevel=LogLevel.NOTICE)
		else:
			Logger.log(f"Found oldest addrobject.  Name:{oldestAddr.getName()}", msgLogLevel=LogLevel.NOTICE)
		return oldestAddr
