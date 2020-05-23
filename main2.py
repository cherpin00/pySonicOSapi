import pycurl
from io import BytesIO
import json
from datetime import datetime
def log(*args):
    myStr = ""
    for a in args:
        myStr += "," + a
    print(datetime.now(), myStr)

global headers
headers = {}
headers["status"] = {}
def header_function(header_line):
    log("Header_function:", header_line.decode())
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
                headers["status"]["full"] = header_line
                headers["status"]["version"] = temp[0]
                headers["status"]["code"] = temp[1].strip()
                headers["status"]["msg"] = temp[2] .strip()
        except:
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
    headers[name] = value

class curlWrapper:
    relations = {
    str(pycurl.PROXY) : "proxy",
    str(pycurl.PROXYPORT) : "proxy port",
    str(pycurl.PROXYTYPE) : "proxy type",
    str(pycurl.PROXYTYPE_HTTP) : "HTTP",
    str(pycurl.URL) :  "url",
    str(pycurl.POST) : "POST",
    str(pycurl.HTTPHEADER) : "HTTP header",
    str(pycurl.USERPWD) : "username and password",
    str(pycurl.HTTPAUTH) : "HTTP auth",
    str(pycurl.HTTPAUTH_BASIC) : "HTTP auth basic",
    str(pycurl.SSL_VERIFYHOST) : "Verify host",
    str(pycurl.SSL_VERIFYPEER) : "Verify peer",
    }

    @classmethod
    def getRel(self, arg):
        return curlWrapper.relations[str(arg)] if str(arg) in curlWrapper.relations.keys() else arg

    def __init__(self):
        self.c = pycurl.Curl()
        pass
    def setopt(self, *args):
        print(curlWrapper.getRel(args[0]), ":" ,curlWrapper.getRel(args[1]))
        self.c.setopt(args[0], args[1])
    
    def perform(self):
        self.c.perform()
        
    def close(self):
        self.c.close()

def sonicWallLogin(host, username, password, throwErrorOnFailure=True):
    proxy = {"host" : "127.0.0.1", "port" : 8888}
    header = {
        "Accept" : "*/*",
    }
    web = "https://" + host + "/api/sonicos/auth"
    req=request(web, username=username, password=password, proxy=proxy, headers = header)
    if headers["status"]["code"]=="200":
        return True
    else:
        fullstatus=headers["status"]["full"]
        if throwErrorOnFailure:
            raise RuntimeError(f"Failed to login to host, {web}, status:{fullstatus}")
        else:
            print(f"Failed to login.  Status:{fullstatus}")
            return False
    return req
def sonicWallLogout(host):
    proxy = {"host" : "127.0.0.1", "port" : 8888}
    headers = {
        "Accept" : "*/*",
    }
    web = "https://" + host + "/api/sonicos/auth"
    return request(web, username=username, password=password, proxy=proxy, headers = headers, method="delete")

# def sonicWall

def request(web, method="post", **kargs):
    buffer = BytesIO()
    c = pycurl.Curl()
    # c = curlWrapper()
    
    # set proxy
    # c.setopt(pycurl.PROXY, kargs["proxy"]["host"])
    # c.setopt(pycurl.PROXYPORT, kargs["proxy"]["port"])
    # c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)

    c.setopt(pycurl.URL, web)
    
    #turn verify off
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)

    #set to auth basic
    c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    
    #username and password
    c.setopt(pycurl.USERPWD, kargs["username"] + ':' + kargs["password"])

    # set headers
    headersList = []
    for key in kargs["headers"].keys():
        headersList.append(key + ": " + kargs['headers'][key])
    c.setopt(pycurl.HTTPHEADER, headersList)

    #set to post
    if method == "delete":
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
    elif method == "post":
        c.setopt(pycurl.POST, 1)
    else:
        raise RuntimeError("Method " + method +" not accpeted.")

    #Set header function
    c.setopt(c.HEADERFUNCTION, header_function)
    c.perform()
    if headers["status"] == {}:
        raise RuntimeError("Getting status.  Did not find status in Response Headers.")

    c.close()
    body = buffer.getvalue()
    return body.decode('iso-8859-1')


sw=new sonicwall(192.168.71.3)
sw.login(username, password)
sw.logout()
sonicwall_url = 'https://192.168.71.3:443/api/sonicos/auth'
username = 'admin'
password = 'password71'

host = "192.168.71.3"
sonicWallLogin(host, "admin", "password71", throwErrorOnFailure=False)
exit()
print(headers)
sonicWallLogout(host)

exit()
# buffer = BytesIO()
# c = pycurl.Curl()
# c.setopt(pycurl.PROXY, "127.0.0.1")
# c.setopt(pycurl.PROXYPORT, 8888)
# c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
# c.setopt(pycurl.URL, sonicwall_url)
# c.setopt(pycurl.SSL_VERIFYPEER, 0)
# c.setopt(pycurl.SSL_VERIFYHOST, 0)
# c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
# c.setopt(pycurl.USERPWD, username + ':' + password)
# c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json','Accept: application/json'])
# c.setopt(pycurl.POST, 1)
# c.perform()
# c.close()
# body = buffer.getvalue()
# Body is a byte string.
# We have to know the encoding in order to print it to a text file
# such as standard output.
# print("Body is:")
# print(body.decode('iso-8859-1'))

