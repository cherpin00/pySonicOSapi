
# Refer to here for LogLevels....
# https://support.solarwinds.com/SuccessCenter/s/article/Syslog-Severity-levels

import sys
from enum import Enum
class LogLevel(Enum):
	EMERGENCY = 0
	ALERT = 1
	CRITICAL = 2
	ERROR = 3
	WARNING = 4
	NOTICE = 5
	INFO = 6
	DEBUG = 7
	VERBOSE = 8
	def __ge__(self, other):
		return self.value >= other.value

class AuthType(Enum):
	BASIC = 0
	DIGEST = 1

class AddressObject:
	def __init__(self, ip, hiddenName="", zone="WAN", eventCreated="", eventSource="pySonicOSAPI", sourceZone="", destinationZone="", country="", descr="", messageID: int=-1, numOccur: int=1):
		from datetime import datetime
		self.name = hiddenName
		self.prefixName="AUTO_type1_" #All object names will begin with this
		self.zone = zone
		self.ip = ip
		self.country=country
		self.descr=descr
		self.eventCreated=eventCreated #Date of event (may be different from created date)
		self.created=datetime.now()	#this is date Addr Object was created
		self.updated="" #this is date the AddrObject was last updated
		self.numOccur=numOccur #this is number of times the AddrObject was modified (to count # of times this IP has hit the firewall)
		self.eventSource=eventSource  #this is usually the IP Address of the device that generated the Event
		self.messageID=messageID	#this is the eventID from the device (1198=Geo IP Blocked)
		self.destinationZone=destinationZone  #For GeoIP Blocked, this would be, for example, LAN
		self.sourceZone=sourceZone  #For GeoIP Blocked, this would be WAN - (we would not want to block LAN SourceZones)

	
	def getName(self):
		return f"{self.prefixName};eventCreated={self.eventCreated}Country={self.country};sourceZone={self.sourceZone};destZone={self.destinationZone}"

	def __str__(self):
		str = ("name: " + self.name) + "\n" + \
		("zone: " + self.zone) + "\n" + \
		("ip: " + self.ip) + "\n"
		return str
	
	def __lt__(self, other):
		return self.name < other.name

	def __eq__(self, other):
		return self.getJson() == other.getJson()

	def getJson(self):
		import json
		rvalue = {
			"address_object" : {
				"ipv4" : {
					"name" : self.name,
					"zone" : self.zone,
					"host" : {
						"ip" : self.ip,
					},
				},
			},
		}
		return json.dumps(rvalue)

class AddressObjectWithParams(AddressObject):
	def __init__(self, name: str, ip: str, zone: str="WAN"):
		super().__init__(ip, hiddenName=name, zone=zone)

class AddressObjectWithDict(AddressObject):
	def __init__(self, myDict: dict):
		super().__init__(myDict["address_object"]["ipv4"]["host"]["ip"], name = myDict["address_object"]["ipv4"]["name"], zone = myDict["address_object"]["ipv4"]["zone"])


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
	def __init__(self):
		self.group = {}
	
	def __str__(self):
		rvalue = str(self.group)
		return rvalue		
	
	def get(self, idx):
		for index, key in enumerate(self.group.keys()):
			if index == idx:
				return self.group[key]

	def addAddressObject(self, addressObject: AddressObject):
		self.group[addressObject.name] = addressObject #.getJson()["address_object"]

class SonicWall:	
	def __init__(self, host):
		self.host = host
		self.headers = {}
		self.headers["status"] = {}
		self.log_level = LogLevel.INFO

		self.proxy_host=""
		self.proxy_port=-1
		self.proxy_enable=False
		self.always_params= ""
		self.text_response = ""

	def log(self, *args, msgLogLevel=LogLevel.INFO):
		from datetime import datetime
		if self.log_level >= msgLogLevel:
			myStr = ""
			for a in args:
				myStr += ", " + str(a)
			print(datetime.now(), msgLogLevel.name, msgLogLevel.value, myStr)

	def header_function(self, header_line):
		self.log("Starting " + sys._getframe().f_code.co_name + ":", header_line.decode(), msgLogLevel=LogLevel.VERBOSE)
		# HTTP standard specifies that headers are encoded in iso-8859-1.
		# On Python 2, decoding step can be skipped.
		# On Python 3, decoding step is required.
		header_line = header_line.decode('iso-8859-1')

		# Header lines include the first status line (HTTP/1.x ...).
		# We are going to ignore all lines that don't have a colon in them.
		# This will botch headers that are split on multiple lines...
		if ':' not in header_line:
			try: 
				if header_line[:5] == "HTTP/":
					temp = header_line.split(" ")
					self.headers["status"]["full"] = header_line
					self.headers["status"]["version"] = temp[0]
					self.headers["status"]["code"] = temp[1].strip()
					self.headers["status"]["msg"] = temp[2] .strip()
			except:
				self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
				raise RuntimeError("Getting status from response header")
			return
			

		# Break the header line into header name and value.
		name, value = header_line.split(':', 1)

		# Remove whitespace that may be present.
		# Header lines include the trailing newline, and there may be whitespace
		# around the colon.
		name = name.strip()
		value = value.strip()

		# Header names are case insensitive.
		# Lowercase name here.
		name = name.lower()

		# Now we can actually record the header name and value.
		# Note: this only works when headers are not duplicated, see below.
		self.headers[name] = value
		self.log("Exiting " + sys._getframe().f_code.co_name + ".", msgLogLevel=LogLevel.VERBOSE)
	
	def request(self, web, method="post", **kargs):
		import subprocess

		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		self.log("Host:", self.host, msgLogLevel=LogLevel.DEBUG)

		curlCommand = "curl " + self.always_params
		
		# set proxy
		if self.proxy_enable:
			self.log("Proxy is enabled:", self.proxy_host, self.proxy_port, msgLogLevel=LogLevel.NOTICE)
			curlCommand += " --proxy " + self.proxy_host + ":" + str(self.proxy_port)  + " "
		else:
			self.log("Proxy is DISABLED.", msgLogLevel=LogLevel.NOTICE)
		
		extraCommands = ""
		if "params" in kargs.keys():
			extraCommands += " " + kargs["params"] + " "
		
		if "username" in kargs.keys() and "password" in kargs.keys():
			extraCommands += " -u " + kargs["username"] + ":" + kargs["password"]
		curlCommand += extraCommands

		# set headers
		if "headers" in kargs.keys():
			for key in kargs["headers"].keys():
				curlCommand += " --header " + '"' + key + ": " + str(kargs['headers'][key]).strip() + '" '

		curlCommand += " -X " + method.upper() + " " + web
		self.log("Running", curlCommand)
		process = subprocess.Popen(curlCommand,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE)
		self.text_response = process.stdout.read()
		self.text_error = process.stderr.read().decode()
		self.log("x1:", self.text_error, msgLogLevel=LogLevel.VERBOSE)
		with open("stderr.out", "w") as f:
			f.write(self.text_error)
		with open("sonicWall.out", "w") as f:
			f.write(self.text_response.decode())
		self.json_response = ""
		bodies = self.text_response.decode().split("\r\n\r\n")
		for headNumber, head in enumerate(bodies):
			isHeader = False
			isJson = False
			if headNumber == 0 and self.proxy_enable: #This skips the proxy headers.  Later we may not want to skip them and use them for something else
				continue
			for lineNumber, line in enumerate(head.split("\n")):
				if lineNumber == 0 and line[:5] == "HTTP/":
					isHeader = True
				elif lineNumber == 0 and line == "{": #I am assuming that this is the start of the json
					isJson = True
				if isHeader:
					self.header_function(line.encode())
				elif isJson:
					self.json_response += line
		import json
		self.dict_response = json.loads(self.json_response)
		if self.headers["status"] == {}:
			raise RuntimeError("Getting status.  Did not find status in Response Headers.")

		self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		return self.text_response.decode()

	def login(self, username, password, authType = AuthType.DIGEST, throwErrorOnFailure=True):
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		self.log(f"Logging into {self.host}...", msgLogLevel=LogLevel.NOTICE)
		header = {
			"Accept" : "*/*",
			"Expect" : "",	#if this is not set, PyCurl will respond with pycurl.error: (56, ''), unless the server sends what PyCurl is expecting (a corresponding Expect).  See https://gms.tf/when-curl-sends-100-continue.html
			"Content-Type" : "",
		}
		web = "https://" + self.host + "/api/sonicos/auth"
		if authType.value != AuthType.BASIC.value:
			raise RuntimeError(f"Auth type {authType.name} not supported.")
		else:
			self.log(f"Auth type {authType.name} is lowest security level.  Consider a higher Level Auth Type like Digest.", msgLogLevel=LogLevel.WARNING)
			req=self.request(web, username=username, password=password, headers = header)
		self.log("Login status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log("Login successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to login.  Status:{fullstatus}", msgLogLevel=LogLevel.NOTICE)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to login to host, {web}, status:{fullstatus}")
			else:
				return False

	def logout(self, throwErrorOnFailure=True):
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		self.log(f"Logging out of {self.host}...", msgLogLevel=LogLevel.NOTICE)

		proxy = {"host" : "127.0.0.1", "port" : 8888}
		headers = {
			"Accept" : "*/*",
			"Expect" : "",	#if this is not set, PyCurl will respond with pycurl.error: (56, ''), unless the server sends what PyCurl is expecting (a corresponding Expect).  See https://gms.tf/when-curl-sends-100-continue.html
			"Content-Type" : "",
			# "Transfer-Encoding" : "",
			# "User-Agent" : "curl/7.50.3"
		}
		web = "https://" + self.host + "/api/sonicos/auth"
		req = self.request(web, proxy=proxy, headers = headers, method="delete", timeout=5)
		self.log("Logout status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log("Logout successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to logout.  Status:{fullstatus}")
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to logout of host, {web}, status:{fullstatus}")
			else:
				return False
		return req

	def getIPv4AddressObjectByName(self, name: str) -> AddressObject:
		from urllib.parse import quote
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		proxy = {"host" : "127.0.0.1", "port" : 8888}
		headers = {}
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4/name/" + quote(name)
		req = self.request(web, proxy=proxy, headers=headers, method="get")
		self.log("Get address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log("Get address object successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Response", req, msgLogLevel=LogLevel.ALERT)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			self.text_response
			return AddressObjectWithDict(self.dict_response)
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to get address object.  Status:{fullstatus}")
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			raise RuntimeError(f"Failed to get address object from, {web}, status:{fullstatus}")

	def createIPv4AddressObject(self, addressObject: AddressObject, throwErrorOnFailure=True):
		import shlex
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4"
		# req = self.request(web, method="get", params="--data-ascii " + '"' + (str(addressObject.getJson())).replace('"', '^"') + '"', headers= {"Content-type" : "application/json"})
		filename="x1.dat"
		with open(filename, "w") as f:
			f.write(str(addressObject.getJson()))
		req = self.request(web, method="post", params=' -d "@' + filename + '" ', headers= {"Content-type" : "application/json"})

		self.log("Create address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log("Create address object successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Response", req, msgLogLevel=LogLevel.ALERT)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			#Todo: Need to get JSON response when the create fails. For example: status, info, message: "Already exists."
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to create address object.  Status:{fullstatus}")
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to create address object from, {web}, status:{fullstatus}")
			else:
				return False
	

	def checkStatus(self, msg, web, req, functionName="unknown", throwErrorOnFailure=True):
		self.log(msg + " status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log(msg + " successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Response", req, msgLogLevel=LogLevel.ALERT)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to {msg}.  Status:{fullstatus}")
			self.log("Exiting function:" + functionName, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to {msg} from, {web}, status:{fullstatus}")
			else:
				return False

	def commit(self):
		web = "https://" + self.host + "/api/sonicos/config/pending"
		req = self.request(web, "post")
		self.checkStatus("commit", web, req, sys._getframe().f_code.co_name)
	
	def getPendingChanges(self):
		web = "https://" + self.host + "/api/sonicos/config/pending"
		req = self.request(web, "get")
		self.checkStatus("Get pending changes", web, req, sys._getframe().f_code.co_name)

	def modifyAddressObject(self, addressObject, throwErrorOnFailure=True):
		web = "https://" + self.host +  f"/api/sonicos/address-objects/ipv4/name/{addressObject.name}"
		filename = "addressObject.dat"
		with open(filename, "w") as f:
			f.write(str(addressObject.getJson()))
		req = self.request(web, "put", params=' --data "@' + filename + '" ', headers={"Content-type":"application/json"})
		return self.checkStatus("Modyify address object " + addressObject.name + " ", web, req, sys._getframe().f_code.co_name, throwErrorOnFailure=throwErrorOnFailure)

	def deleteAddressObject(self, addrName: str, succeedIfNotExist=False):
		if succeedIfNotExist:
			raise RuntimeError("succeedIfNotExists option not yet supported in function:" + sys._getframe().f_code.co_name)
		web = "https://" + self.host +  f"/api/sonicos/address-objects/ipv4/name/{addrName}"
		req = self.request(web, "delete", headers={"Content-type":"application/json"})
		self.checkStatus("Delete address object " + addrName + " ", web, req, sys._getframe().f_code.co_name)
		return True

	def getIPv4AddressGroupByName(self, groupName: str) -> AddressGroup:
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		web = "https://" + self.host + "/api/sonicos/address-groups/ipv4/name/" + groupName
		req = self.request(web, method="get")
		group = AddressGroup()
		for addrObj in self.dict_response["address_group"]["ipv4"]["address_object"]["ipv4"]:
			addrObj2 = self.getIPv4AddressObjectByName(addrObj["name"])
			group.addAddressObject(addrObj2)
		self.checkStatus("getting address group", web, req, sys._getframe().f_code.co_name)
		return group
