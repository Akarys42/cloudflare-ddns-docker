# App defaults
DEFAULT_DELAY = "5 minutes"

# Endpoints
BASE_ENDPOINT = "https://api.cloudflare.com/client/v4/"

VERIFY_TOKEN = BASE_ENDPOINT + "user/tokens/verify"

LIST_ZONES = BASE_ENDPOINT + "zones"
LIST_DNS = BASE_ENDPOINT + "zones/{zone_identifier}/dns_records"
PATCH_DNS = BASE_ENDPOINT + "zones/{zone_identifier}/dns_records/{identifier}"

# Utilities
ACCEPTED_RECORDS = ('A', 'AAAA')

IP_API_URL_IPV4 = "https://api.ipify.org/"
IP_API_URL_IPV6 = "https://api6.ipify.org/"
