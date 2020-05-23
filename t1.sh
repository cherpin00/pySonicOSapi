USER=admin
PASSWORD=password71
set -x
# IP Addr and HTTPS Web management port of the SonicWall.
URL=192.168.71.3:443

# Login using Digest Auth
#curl -k -i -u $USER:$PASSWORD --digest -X HEAD https://$URL/api/sonicos/auth
# If you're using basic auth, use this instead:

PROXY=127.0.0.1:8888
params="--proxy $PROXY"
curl $params --insecure -i -u $USER:$PASSWORD -X POST https://$URL/api/sonicos/auth

# Query the SSL VPN Sessions

URL2="api/sonicos/reporting/ssl-vpn/sessions"
URL2="api/sonicos/address-objects/ipv4"
URL2="api/sonicos/address-groups/ipv4/name/my_AUTO_Blacklist"
URL2="api/sonicos/address-objects/ipv4/name/AUTO_type1_00001_added=2020/05/21_14:20:48;Description=GoogleDNSServer;expires=1000"
URL2="api/sonicos/address-objects/ipv4/name/AUTO_simple"
#curl --data-urlencode -k -i -X GET "https://$URL/$URL2" -H  "accept: application/json"
curl $params -k -i -X GET "https://$URL/$URL2" -H  "accept: application/json"

# "Logout" by deleting the auth info.
curl $params -k -i -X DELETE "https://$URL/api/sonicos/auth"
