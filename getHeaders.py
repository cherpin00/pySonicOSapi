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
    headers = []
    for key in kargs["headers"].keys():
        headers.append(key + ": " + kargs['headers'][key])
    c.setopt(pycurl.HTTPHEADER, headers)

    #set to post
    if method == "delete":
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
    elif method == "post":
        c.setopt(pycurl.POST, 1)
    else:
        raise RuntimeError("Method " + method +" not accpeted.")


    print(c.perform())
    c.getinfo()
    c.close()
    body = buffer.getvalue()
    return body.decode('iso-8859-1')



import pycurl
import re
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

headers = {}
def header_function(header_line):
    # HTTP standard specifies that headers are encoded in iso-8859-1.
    # On Python 2, decoding step can be skipped.
    # On Python 3, decoding step is required.
    header_line = header_line.decode('iso-8859-1')

    # Header lines include the first status line (HTTP/1.x ...).
    # We are going to ignore all lines that don't have a colon in them.
    # This will botch headers that are split on multiple lines...
    if ':' not in header_line:
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

buffer = BytesIO()
c = pycurl.Curl()

c.setopt(c.URL, 'http://pycurl.io')
c.setopt(c.WRITEFUNCTION, buffer.write)
# Set our header function.
c.setopt(c.HEADERFUNCTION, header_function)
c.perform()
c.close()

# Figure out what encoding was sent with the response, if any.
# Check against lowercased header name.
encoding = None
if 'content-type' in headers:
    content_type = headers['content-type'].lower()
    match = re.search('charset=(\S+)', content_type)
    if match:
        encoding = match.group(1)
        print('Decoding using %s' % encoding)
if encoding is None:
    # Default encoding for HTML is iso-8859-1.
    # Other content types may have different default encoding,
    # or in case of binary data, may have no encoding at all.
    encoding = 'iso-8859-1'
    print('Assuming encoding is %s' % encoding)

body = buffer.getvalue()
# Decode using the encoding we figured out.
# print(body.decode(encoding))
print(headers)