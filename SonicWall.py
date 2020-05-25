
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

class SonicWall:	
	def __init__(self, host):
		self.host = host
		self.headers = {}
		self.headers["status"] = {}
		self.log_level = LogLevel.INFO

		self.proxy_host=""
		self.proxy_port=-1
		self.proxy_enable=False

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
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		import pycurl
		from io import BytesIO

		self.log("Host:", self.host, msgLogLevel=LogLevel.DEBUG)

		buffer = BytesIO()
		c = pycurl.Curl()
		# c = curlWrapper()

		# set verify off
		c.setopt(pycurl.SSL_VERIFYPEER, 0)
		c.setopt(pycurl.SSL_VERIFYHOST, 0)

		# set proxy
		if self.proxy_enable:
			self.log("Proxy is enabled:", self.proxy_host, self.proxy_port, msgLogLevel=LogLevel.NOTICE)
			c.setopt(pycurl.PROXY, self.proxy_host)
			c.setopt(pycurl.PROXYPORT, self.proxy_port)
			c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
		else:
			self.log("Proxy is DISABLED.", msgLogLevel=LogLevel.NOTICE)
			c.setopt(pycurl.PROXY, "")	#this effectively disables the proxy
			c.setopt(pycurl.PROXYPORT, 0)	#according to https://curl.haxx.se/libcurl/c/CURLOPT_PROXYPORT.html, this is the default, which causes it to use 443 or 1080
			c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)	#should be the default
			

		# set URL
		c.setopt(pycurl.URL, web)
		
		# set standard out off
		c.setopt(pycurl.WRITEFUNCTION, lambda x : None)



		
		#username and password
		if "username" in kargs.keys() and "password" in kargs.keys():
			#set to auth basic
			c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
			c.setopt(pycurl.USERPWD, kargs["username"] + ':' + kargs["password"])

		# set headers
		headersList = []
		for key in kargs["headers"].keys():
			headersList.append(key + ": " + kargs['headers'][key])
		c.setopt(pycurl.HTTPHEADER, headersList)

		#set to post
		if method == "delete":
			# c.setopt(pycurl.POST, 0)
			c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
		elif method == "post":
			c.setopt(pycurl.POST, 1)
		elif method == "get":
			# c.setopt(pycurl.POST, 1)
			c.setopt(pycurl.CUSTOMREQUEST, "GET")
			c.setopt(pycurl.HTTPGET, 1)
		else:
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			raise RuntimeError("Method " + method +" not accpeted.")

		#Set header function
		c.setopt(c.HEADERFUNCTION, self.header_function)
		c.perform()
		if self.headers["status"] == {}:
			raise RuntimeError("Getting status.  Did not find status in Response Headers.")

		c.close()
		body = buffer.getvalue()
		self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		return body.decode('iso-8859-1')

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

	def getIPv4AddressObjectByName(self, name, throwErrorOnFailure=True):
		self.log("Starting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
		proxy = {"host" : "127.0.0.1", "port" : 8888}
		headers = {}
		web = "https://" + self.host + "/api/sonicos/address-objects/ipv4/name/AUTO_simple"
		req = self.request(web, proxy=proxy, headers=headers, method="get")

		self.log("Get address object status", self.headers["status"], msgLogLevel=LogLevel.INFO)
		if self.headers["status"]["code"]=="200":
			self.log("Get address object successful", msgLogLevel=LogLevel.NOTICE)
			self.log("Response", req, msgLogLevel=LogLevel.ALERT)
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			return True
		else:
			fullstatus=self.headers["status"]["full"]
			self.log(f"Failed to get address object.  Status:{fullstatus}")
			self.log("Exiting function:" + sys._getframe().f_code.co_name, msgLogLevel=LogLevel.VERBOSE)
			if throwErrorOnFailure:
				raise RuntimeError(f"Failed to get address object from, {web}, status:{fullstatus}")
			else:
				return False