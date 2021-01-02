
# Refer to here for LogLevels....
# https://support.solarwinds.com/SuccessCenter/s/article/Syslog-Severity-levels

import sys
from enum import Enum
import logging

from functions import *
from logger import *
from AddressObject import *

class AuthType(Enum):
	BASIC = 0
	DIGEST = 1

class SonicWall:
	required_prefix = "AUTO"
	def __init__(self, host):
		self.logger = createLogger()
		self.logger.setLevel(logging.DEBUG)
		self.logger.info("Creating new sonic wall object" + "-"*100) #TODO: Identify sonicwall object with unique value
		self.host = host
		self.headers = {}
		self.headers["status"] = {}
		self.log_level = LogLevel.VERBOSE

		self.proxy_host="127.0.0.1"
		self.proxy_port=8888
		self.proxy_enable=False
		self.always_params= ""
		self.text_response = ""
		self.last_curl_command = ""
		if self.proxy_enable:
			self.proxy = {"host" : self.proxy_host, "port" : self.proxy_port}
		else:
			self.proxy = {}

	@staticmethod
	def connectToSonicwall(ip="192.168.71.3"):	#Todo:How to make this function return SonicWall? -> SonicWall does not work
		#Todo:We should accept the name of a CONFIG file that includes an encrypted SW Password and other configuration settings.
		sw = SonicWall("192.168.71.3")
		sw.always_params = "--connect-timeout 5 --insecure --include"
		sw.log_level=LogLevel.DEBUG
		sw.proxy_enable=False
		sw.proxy_host="127.0.0.1"
		sw.proxy_port=8888
		sw.logout(throwErrorOnFailure=False)
		sw.login("admin", "p", authType=AuthType.BASIC, throwErrorOnFailure=True)
		return sw

	def log(self, msg, *args, msgLogLevel=LogLevel.INFO):
		Logger.log(msg, args, msgLogLevel=msgLogLevel)

	def header_function(self, header_line):
		import traceback
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
				raise RuntimeError(f"Getting status from response header. header_line:{header_line}.")
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
		#Todo:Refactor this.  There must be a better way to specify default values, etc.
		if "throwErrorOnFailure" in kargs.keys():
			throwErrorOnFailure=kargs["throwErrorOnFailure"]
			del kargs["throwErrorOnFailure"]
		else:
			throwErrorOnFailure=True
		#The idea behind throwErrorOnFailure=False is that the REQ doesn't have to be successful for the program to continue.
		#For example, for LOGOFF, this is failing sometimes, if called when noone is logged in.		

		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		self.log("Host:", self.host, msgLogLevel=LogLevel.DEBUG)

		curlCommand = "curl " + self.always_params
		
		# set proxy
		if self.proxy_enable:
			self.log("Proxy is enabled:", self.proxy_host, self.proxy_port, msgLogLevel=LogLevel.DEBUG)
			curlCommand += " --proxy " + self.proxy_host + ":" + str(self.proxy_port)  + " "
		else:
			self.log("Proxy is DISABLED.", msgLogLevel=LogLevel.INFO)
		
		extraCommands = ""
		if "params" in kargs.keys():
			extraCommands += " " + kargs["params"] + " "

			if "--data" in kargs["params"]:
				line = kargs["params"].split(" ")
				filename = line[line.index("--data") + 1]
				filename = filename.replace("@", "").replace('"', '')
				with open(filename, "r") as f:
					file_data = f.read()
				self.log(f"Address object: {file_data}")
		
		if "username" in kargs.keys() and "password" in kargs.keys():
			extraCommands += " -u " + kargs["username"] + ":" + kargs["password"]
		curlCommand += extraCommands

		# set headers
		if "headers" in kargs.keys():
			for key in kargs["headers"].keys():
				curlCommand += " --header " + '"' + key + ": " + str(kargs['headers'][key]).strip() + '" '

		curlCommand += " -X " + method.upper() + " " + web

		import json
		kargs_str=json.dumps(kargs, indent=1)
		self.log(f"Detailed Request Info, Method:{method} to Address:{web}\nkargs:\n{kargs_str}\n----------", msgLogLevel=LogLevel.DEBUG)

		self.log("Running CURL:", curlCommand, msgLogLevel=LogLevel.INFO)

		self.logger.info("Running CURL:" + curlCommand)
		if "params" in kargs.keys():
			if "--data" in kargs["params"]:
				line = kargs["params"].split(" ")
				filename = line[line.index("--data") + 1]
				filename = filename.replace("@", "").replace('"', '')
				with open(filename, "r") as f:
					file_data = f.read()
				self.logger.info(f"Address object: {file_data}")

		self.last_curl_command=curlCommand
		process = subprocess.Popen(curlCommand,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE)
		self.text_response = process.stdout.read().decode()
		self.text_error = process.stderr.read().decode()
		with open("stderr.out", "w") as f:
			f.write(self.text_error)
		with open("sonicWall.out", "w") as f:
			f.write(self.text_response)
		self.json_response = ""
		bodies = self.text_response.split("\r\n\r\n")
		self.log(f"Detailed Response Info from Request, Method:{method} to Address:{web}\n-----text_reponse:-----\n{self.text_response}\n-----END OF text_response-----\n-----text_error:-----\n{self.text_error}\n-----END OF text_error-----", msgLogLevel=LogLevel.DEBUG)
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
		#Todo: Need to catch errors here.  If the response doesn't have valid json the prog will crash and it won't be apparent why.
		self.log(f"json Response from parsing text_response:\n{json.dumps(self.json_response, indent=1)}", msgLogLevel=LogLevel.DEBUG)
		try:
			if not self.json_response=="":
				self.dict_response = json.loads(self.json_response)
			else:
				self.dict_response = "{}"
		except:
			jsresponse=self.json_response
			if jsresponse=="":
				jsresponse="---BLANK---"
			exceptionWithTraceback(msg=f"Error loading JSON response from server. json_response is:\n{jsresponse}", blnThrowError=throwErrorOnFailure)
		if self.headers["status"] == {}:
			if throwErrorOnFailure:
				raise RuntimeError("Getting status.  Did not find status in Response Headers.")
			else:
				self.log(f"Error getting status on Sonicwall Logout.  Was there a user logged in?", msgLogLevel=LogLevel.ERROR)
		self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		r=self.text_response
		return r

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
			#Todo:Need to implement DIGEST AuthType.
			raise RuntimeError(f"Auth type {authType.name} not supported.")
		else:
			self.log(f"Auth type {authType.name} is lowest security level.  Consider a higher Level Auth Type like Digest.", msgLogLevel=LogLevel.WARNING)
			req=self.request(web, username=username, password=password, headers = header)
		self.log("Login status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.checkStatus("Login to Sonicwall", web, req, throwErrorOnFailure=throwErrorOnFailure):
			self.log(f"Login successful for username:{username}", msgLogLevel=LogLevel.INFO)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			self.log(f"Failed to login. username:{username}", msgLogLevel=LogLevel.INFO)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return False

	def logout(self, throwErrorOnFailure=False):
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		self.log(f"Logging out of {self.host}...", msgLogLevel=LogLevel.NOTICE)

		headers = {
			"Accept" : "*/*",
			"Expect" : "",	#if this is not set, PyCurl will respond with pycurl.error: (56, ''), unless the server sends what PyCurl is expecting (a corresponding Expect).  See https://gms.tf/when-curl-sends-100-continue.html
			"Content-Type" : "",
			# "Transfer-Encoding" : "",
			# "User-Agent" : "curl/7.50.3"
		}
		web = "https://" + self.host + "/api/sonicos/auth"
		req = self.request(web, proxy=self.proxy, headers = headers, method="delete", timeout=5, throwErrorOnFailure=False)
		self.log("Logout status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.checkStatus("Logout of Sonicwall", web, req, throwErrorOnFailure=throwErrorOnFailure):
			self.log("Logout successful", msgLogLevel=LogLevel.INFO)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to logout. Status:{fullstatus}", msgLogLevel=LogLevel.INFO)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return False

	def getIPv4AddressObjectByName(self, name: str) -> AddressObject:
		from urllib.parse import quote
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		headers = {}
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4/name/" + quote(name)
		req = self.request(web, proxy=self.proxy, headers=headers, method="get")
		self.log("Get address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.checkStatus("Get address object", web, req, throwErrorOnFailure=True):
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			# self.text_response
			#Todo: Need to validate the dict_response.  It should have Zone, IP, Name and be structured correctly.
			addr=AddressObjectWithDict(self.dict_response)
			return addr
		else:
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			raise RuntimeError(f"Failed to get address object from, {web}.")

	def getArrayIPv4AddressObjects(self):
		from urllib.parse import quote
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		headers = {}
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4/"
		req = self.request(web, proxy=self.proxy, headers=headers, method="get")
		self.log("Get address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.checkStatus("Get address object", web, req, throwErrorOnFailure=True):
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			#Todo: Need to validate the dict_response.
			all_objects = []
			self.log("Only custom objects are going to returned.")
			for obj in self.dict_response["address_objects"]: #TODO: confirm that custom objects uuid always start with a '0'
				if obj["ipv4"]["uuid"][0] != '0':
					self.log(f"Custom object {obj} found. Skipping.", msgLogLevel=LogLevel.DEBUG)
					continue
				addr=AddressObjectWithDict({"address_object" : obj})
				all_objects.append(addr)
			return all_objects
		else:
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			raise RuntimeError(f"Failed to get address object from, {web}.")

	def createIPv4AddressObject(self, addressObject: AddressObject, useHiddenName:bool = True, throwErrorOnFailure=True):
		addrName = addressObject.getName()
		if addrName[:4] != self.required_prefix:
			raise RuntimeError(f"Address object {addrName} must start with {self.required_prefix} to be created")

		import shlex
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4"
		# req = self.request(web, method="get", params="--data-ascii " + '"' + (str(addressObject.getJson())).replace('"', '^"') + '"', headers= {"Content-type" : "application/json"})
		filename="x1.dat"
		with open(filename, "w") as f:
			f.write(str(addressObject.getJson(getHiddenName=useHiddenName)))
		req = self.request(web, method="post", params=' -d "@' + filename + '" ', headers= {"Content-type" : "application/json"})

		self.log("Create address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.checkStatus("Create Address Object", web, req, throwErrorOnFailure=throwErrorOnFailure):
			self.log(f"New Address Object created. Name:{addressObject.getName()}", msgLogLevel=LogLevel.NOTICE)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			#Todo: Need to get JSON response when the create fails. For example: status, info, message: "Already exists."
			fullstatus=self.headers["status"]["full"]
			print(f"Failed to create address object.  Text Response:{self.dict_response}")
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to create address object from, {web}, status:{fullstatus}")
			else:
				return False
	
	def checkStatus(self, msg, web, req, functionName="unknown", throwErrorOnFailure=True):
		#Todo:functionName is not necessary here.  Refactor.
		#Todo:This function should be in a TRY: and should report enough info in the exception to troubleshoot.
		self.log(f"Checking API request status, '{msg}'", msgLogLevel=LogLevel.INFO)
		self.log(f"Response 'status' Headers:", self.headers["status"], msgLogLevel=LogLevel.DEBUG)
		self.log("Full HTTP Response from Request:", req, msgLogLevel=LogLevel.VERBOSE)
		statusCode=self.headers["status"]["code"]
		statusFull=self.headers["status"]["full"]
		if self.headers["status"]["code"]=="200":
			self.log(f"'{msg}' successful.  Status:{statusCode}/{statusFull}", msgLogLevel=LogLevel.INFO)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			self.log(f"'{msg}' failed.  Status:{statusCode}/{statusFull}", msgLogLevel=LogLevel.NOTICE)
			self.log("Full HTTP Response from Request:", req, msgLogLevel=LogLevel.ERROR)
			self.log("Exiting function:" + functionName, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to get API request status, '{msg}' from:\nWeb:{web}\nStatus:{statusCode}/{statusFull}\nCurl:{self.last_curl_command}")
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

	def modifyAddressObject(self, addressObject, updateWithHiddenName:bool = True, throwErrorOnFailure=True):
		from urllib.parse import quote
		from datetime import datetime
		existing_addrName=addressObject.hiddenName
		existing_addrName_encoded=quote(existing_addrName)
		addressObject.numOccur+=1
		oldUpdated=addressObject.updated
		addressObject.updated=datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
		# if updateWithHiddenName:
		# 	nm=addressObject.hiddenName
		# else:
		# 	nm=addressObject.getName()
		self.log(f"Updating address object named, {existing_addrName}.\nIncreased numOccur to {addressObject.numOccur}\nChanged updated from {oldUpdated} to {addressObject.updated}.", msgLogLevel=LogLevel.NOTICE)

		web = "https://" + self.host +  f"/api/sonicos/address-objects/ipv4/name/{existing_addrName_encoded}"
		filename = "addressObject.dat"
		with open(filename, "w") as f:
			f.write(str(addressObject.getJson(updateWithHiddenName)))
		req = self.request(web, "put", params=' --data "@' + filename + '" ', headers={"Content-type":"application/json"})
		return self.checkStatus("Modifying address object " + existing_addrName + " ", web, req, sys._getframe().f_code.co_name, throwErrorOnFailure=throwErrorOnFailure)

	def deleteAddressObject(self, addrName: str, succeedIfNotExist=False):
		from urllib.parse import quote
		if addrName[:4] != self.required_prefix:
			raise RuntimeError(f"Address object {addrName} must start with {self.required_prefix} to be deleted")
		if succeedIfNotExist:
			raise RuntimeError("succeedIfNotExists option not yet supported in function:" + sys._getframe().f_code.co_name)
		addrName_encoded=quote(addrName)
		web = "https://" + self.host +  f"/api/sonicos/address-objects/ipv4/name/{addrName_encoded}"
		req = self.request(web, "delete", headers={"Content-type":"application/json"})
		if self.checkStatus("Delete address object " + addrName + " ", web, req, sys._getframe().f_code.co_name):
			self.log(msg=f"Deleted address object, {addrName}.", msgLogLevel=LogLevel.NOTICE)
			return True
		else:
			self.log(f"Unable to delete address object with name:{addrName}\Response from HTTP Request:{req}", msgLogLevel=LogLevel.ERROR)
			raise RuntimeError(f"Unable to delete address object with name:{addrName}")

	def getIPv4AddressGroupByName(self, groupName: str) -> AddressGroup:
		import json
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		web = "https://" + self.host + "/api/sonicos/address-groups/ipv4/name/" + groupName
		req = self.request(web, method="get")
		group = AddressGroup(orig_json=json.dumps(self.dict_response))
		for addrObj in self.dict_response["address_group"]["ipv4"]["address_object"]["ipv4"]:
			addrObj2 = self.getIPv4AddressObjectByName(addrObj["name"])
			group.addAddressObject(addrObj2)
		self.checkStatus("getting address group", web, req, sys._getframe().f_code.co_name)
		return group

	def addAddressOnjectToIPv4AddressGroupWithJson(self, groupName: str, addressObjectName: str, json:str) -> bool:
		from urllib.parse import quote
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		try:
			groupName_encoded=quote(groupName)
			# web = "https://" + self.host + "/api/sonicos/address-groups/ipv4/name/" + groupName_encoded
			web = "https://" + self.host + "/api/sonicos/address-groups/ipv4"
			filename = "addressObject.dat"
			with open(filename, "w") as f:
				f.write(str(json))
			req = self.request(web, "put", params=' --data "@' + filename + '" ', headers={"Content-type":"application/json"})
			return self.checkStatus(f"Adding address object, {addressObjectName}, to Address Group, {groupName}", web, req, sys._getframe().f_code.co_name)
		except:
			exceptionWithTraceback(f"Adding Sonicwall Address Object, {addressObjectName}, to Address Group, {groupName}.", blnThrowError=False)
			return False

	def deleteOldestAddressObjectByLastUpdated(self, addrgrp: AddressGroup, maxGroupSize: int=100):
		#Todo: Currently only deletes one object at a time, if necessary.
		if len(addrgrp.group)>=maxGroupSize:
			Logger.log(f"Max Group Size, {maxGroupSize}, has been reached.  Current Size is, {len(addrgrp.group)}.  Looking for Addr Object to delete.", msgLogLevel=LogLevel.NOTICE)
			oldestAddr=addrgrp.findOldestAddrByLastUpdated()
			oldestAddrName=oldestAddr.getName()
			self.deleteAddressObject(oldestAddrName, succeedIfNotExist=False)
		else:
			Logger.log(f"Max Group Size, {maxGroupSize}, has not been reached.  Current Size is, {len(addrgrp.group)}.", msgLogLevel=LogLevel.NOTICE)
