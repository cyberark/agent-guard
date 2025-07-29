import os

CYBERARK_ENV = os.getenv('CYBERARK_ENV', '').upper()
if CYBERARK_ENV in ('DEV', 'INT'):
    CYBERARK_DOMAIN = 'integration-cyberark.cloud'
else:
    CYBERARK_DOMAIN = 'cyberark.cloud'