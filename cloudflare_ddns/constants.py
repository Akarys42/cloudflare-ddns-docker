# App defaults
DEFAULT_DELAY = "5 minutes"

# Endpoints
BASE_ENDPOINT = "https://api.cloudflare.com/client/v4/"

VERIFY_TOKEN = BASE_ENDPOINT + "user/tokens/verify"

LIST_ZONES = BASE_ENDPOINT + "zones"
LIST_DNS = BASE_ENDPOINT + "zones/{zone_identifier}/dns_records"

# Utilities
ACCEPTED_RECORDS = ('A', 'AAAA')
