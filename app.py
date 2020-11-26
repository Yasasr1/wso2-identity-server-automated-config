import requests
import json
from urllib.parse import urlencode

dcr_url = "https://localhost:9443/api/identity/oauth2/dcr/v1.1/register"
token_url = "https://localhost:9443/oauth2/token"
dcr_client_id = "oidc_test_clientid001"
dcr_client_secret = "oidc_test_client_secret001"
applications_url = "https://localhost:9443/api/server/v1/applications"
scopes = "internal_user_mgt_update internal_application_mgt_create internal_application_mgt_view"

dcr_headers = {'Content-Type': 'application/json', 'Connection': 'keep-alive',
               'Authorization': 'Basic YWRtaW46YWRtaW4='}
dcr_body = {
    'client_name': 'python_script',
    "grant_types": ["password"],
    "ext_param_client_id": dcr_client_id,
    "ext_param_client_secret": dcr_client_secret
}


def dcr(headers, body, url):
    response = requests.post(url=url, headers=headers, data=body, verify=False)
    # response_map = json.loads(response.content)
    print(response.text)


def get_access_token(client_id, client_secret, scope, url):
    body = {
        'grant_type': 'password',
        'username': 'admin',
        'password': 'admin',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    body_encoded = urlencode(body)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
    }

    response = requests.post(url=url, headers=headers, data=body_encoded, verify=False)
    response_map = json.loads(response.content)
    print(response_map)
    if response_map['access_token']:
        return response_map['access_token']
    else:
        print("Error: No access token found")


def get_service_provider_details(application_id):
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }
    response = json.loads(requests.get(url=applications_url + "/" + application_id + "/inbound-protocols/oidc",
                                       headers=headers, verify=False).content)
    return {"clientId": response['clientId'], "clientSecret": response['clientSecret']}


def register_service_provider(name, callback_url):
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }

    body = {
        "name": name,
        "inboundProtocolConfiguration": {
            "oidc": {
                "state": "ACTIVE",
                "grantTypes": [
                    "authorization_code"
                ],
                "publicClient": False,
                "validateRequestObjectSignature": False,
                "callbackURLs": [
                    callback_url
                ],
                "allowedOrigins": []
            }
        },
        "authenticationSequence": {
            "type": "DEFAULT",
            "steps": [
                {
                    "id": 1,
                    "options": [
                        {
                            "idp": "LOCAL",
                            "authenticator": "basic"
                        }
                    ]
                }
            ],
            "subjectStepId": 1,
            "attributeStepId": 1
        },
        "advancedConfigurations": {
            "discoverableByEndUsers": False
        },
        "description": "client to be used by OIDC conformance suite.",
        "templateId": "b9c5e11e-fc78-484b-9bec-015d247561b8"
    }

    json_body = json.dumps(body)
    response = requests.post(url=applications_url, headers=headers, data=json_body, verify=False)
    if response.status_code == 201:
        print("Service provider " + name + " registered")
        response = requests.get(url=applications_url + "?filter=name+eq+" + name, headers=headers, verify=False)
        print(response.status_code)
        response_map = json.loads(response.content)
        print(response_map)
        if response_map['count'] == 0:
            print("error application not found")
        else:
            return get_service_provider_details(response_map['applications'][0]['id'])
    else:
        print(response.text)


dcr(dcr_headers, json.dumps(dcr_body), dcr_url)
access_token = get_access_token(dcr_client_id, dcr_client_secret, scopes, token_url)
service_provider = register_service_provider("test28", "https://localhost.emobix.co.uk:8443/test/a/yasas/callback")
print(service_provider)
