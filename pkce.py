import base64
import hashlib
import secrets
import socket
import string
import sys
import time

import requests

alphabet = string.ascii_letters + string.digits + '-._~'
code_verifier = ''.join(secrets.choice(alphabet) for _ in range(128))
hashed = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(hashed).rstrip(b'=')

host = '172.16.10.3'

requests.packages.urllib3.disable_warnings()

resp = requests.get(f'https://{host}:8443/v1/oauth/authorize', {
    'audience': 'homesmart.local',
    'response_type': 'code',
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
}, verify=False)
content = resp.json()

if resp.status_code != 200:
    print(content)
    sys.exit(1)

authorization_code = content['code']
while True:
    resp = requests.post(f'https://{host}:8443/v1/oauth/token', data={
        'code': authorization_code,
        'name': socket.gethostname(),
        'grant_type': 'authorization_code',
        'code_verifier': code_verifier,
    }, verify=False)
    content = resp.json()

    if resp.status_code == 403 and content['error'] == 'Button not pressed or presence time stamp timed out.':
        print('waiting for button press')
        time.sleep(1)
    else:
        print(content)
        break
