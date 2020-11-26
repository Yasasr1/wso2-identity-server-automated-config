import requests
import json
from urllib.parse import urlencode
from datetime import datetime

dcr_url = "https://localhost:9443/api/identity/oauth2/dcr/v1.1/register"
token_url = "https://localhost:9443/oauth2/token"
dcr_client_id = "oidc_test_clientid001"
dcr_client_secret = "oidc_test_client_secret001"
applications_url = "https://localhost:9443/api/server/v1/applications"
scopes = "internal_user_mgt_update internal_application_mgt_create internal_application_mgt_view internal_login " \
         "internal_claim_meta_update internal_application_mgt_update"

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
    return {"clientId": response['clientId'], "clientSecret": response['clientSecret'], "applicationId": application_id}


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
    if json.loads(response.content)['code'] == "APP-65001":
        print("Application already registered, getting details")
    else:
        print("Service provider " + name + " registered")
    response = requests.get(url=applications_url + "?filter=name+eq+" + name, headers=headers, verify=False)
    print(response.status_code)
    response_map = json.loads(response.content)
    print(response_map)
    if response_map['count'] == 0:
        print("error application not found")
    else:
        return get_service_provider_details(response_map['applications'][0]['id'])


def set_user_claim_values():
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }

    # can't update these values -
    #   telephone - updated claim mapping
    #   middle name

    body = {
        "Operations": [
            {
                "op": "replace",
                "value": {
                    "profileUrl": "newUrl"
                }
            },
            {
                "op": "replace",
                "value": {
                    "locale": "locale"
                }
            },
            {
                "op": "replace",
                "value": {
                    "photos": [
                        "photos",
                        {
                            "type": "photo",
                            "value": "photourl"
                        }
                    ]
                }
            },
            {
                "op": "replace",
                "value": {
                    "addresses": [
                        "address"
                    ]
                }
            },
            {
                "op": "replace",
                "value": {
                    "timezone": "+5:30"
                }
            },
            {
                "op": "replace",
                "value": {
                    "displayName": "displayu name"
                }
            },
            {
                "op": "replace",
                "value": {
                    "nickName": "nicj name"
                }
            },
            {
                "op": "replace",
                "value": {
                    "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
                        "emailVerified": "true",
                        "manager": {
                            "value": "female"
                        },
                        "phoneVerified": "true",
                        "dateOfBirth": "1997-11-26T05:09:15.680889Z"
                    }
                }
            },
            {
                "op": "replace",
                "value": {
                    "name": {
                        "givenName": "yasas"
                    }
                }
            },
            {
                "op": "replace",
                "value": {
                    "name": {
                        "familyName": "Administrator"
                    }
                }
            },
            {
                "op": "replace",
                "value": {
                    "emails": [
                        "admin@wso2.com"
                    ]
                }
            },
            {
                "op": "replace",
                "value": {
                    "phoneNumbers": [
                        {
                            "type": "mobile",
                            "value": "07178394922"
                        },
                        {
                            "type": "home",
                            "value": "011571"
                        }
                    ]
                }
            },
        ],
        "schemas": [
            "urn:ietf:params:scim:api:messages:2.0:PatchOp"
        ]
    }

    json_body = json.dumps(body)
    response = requests.patch(url="https://localhost:9443/scim2/Me", headers=headers, data=json_body, verify=False)
    print(response.status_code)
    print(response.text)


def change_local_claim_mapping(body, url):
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }

    json_body = json.dumps(body)
    response = requests.put(url=url, headers=headers, data=json_body, verify=False)
    print(response.status_code)
    print(response.text)


def add_claim_service_provider(application_id):
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }

    body = {
        "claimConfiguration": {
            "dialect": "LOCAL",
            "requestedClaims": [
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/emailaddress"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/identity/emailVerified"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/mobile"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/identity/phoneVerified"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/addresses"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/fullname"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/givenname"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/lastname"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/middleName"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/nickname"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/url"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/photourl"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/url"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/gender"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/dob"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/timeZone"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/local"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/displayName"
                    },
                    "mandatory": True
                },
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/modified"
                    },
                    "mandatory": True
                }
            ],
            "role": {
                "claim": {
                    "uri": "http://wso2.org/claims/role"
                },
                "includeUserDomain": True
            },
            "subject": {
                "claim": {
                    "uri": "http://wso2.org/claims/username"
                },
                "includeTenantDomain": False,
                "includeUserDomain": False,
                "useMappedLocalSubject": False
            }
        }
    }

    json_body = json.dumps(body)
    response = requests.patch(url=applications_url + "/" + application_id, headers=headers, data=json_body,
                              verify=False)
    print(response.status_code)
    print(response.text)


def configure_acr(application_id):
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Authorization': 'Bearer ' + access_token
    }

    body = {
        "authenticationSequence": {
            "attributeStepId": 1,
            "steps": [
                {
                    "id": 1,
                    "options": [
                        {
                            "authenticator": "BasicAuthenticator",
                            "idp": "LOCAL"
                        }
                    ]
                },
                {
                    "id": 2,
                    "options": [
                        {
                            "authenticator": "BasicAuthenticator",
                            "idp": "LOCAL"
                        }
                    ]
                },
                {
                    "id": 3,
                    "options": [
                        {
                            "authenticator": "BasicAuthenticator",
                            "idp": "LOCAL"
                        }
                    ]
                }
            ],
            "subjectStepId": 1,
            "type": "USER_DEFINED",
            "script": "// Define conditional authentication by passing one or many Authentication Context Class "
                      "References \n// as comma separated values.\n\n// Specify the ordered list of ACR "
                      "here.\nvar supportedAcrValues = ['acr1', 'acr2', 'acr3'];\n\nvar onLoginRequest = function("
                      "context) {\n    var selectedAcr = selectAcrFrom(context, supportedAcrValues);\n    Log.info("
                      "'--------------- ACR selected: ' + selectedAcr);\n    context.selectedAcr = selectedAcr;\n   "
                      " switch (selectedAcr) {\n        case supportedAcrValues[0] :\n            executeStep("
                      "1);\n            break;\n        case supportedAcrValues[1] :\n            executeStep("
                      "1);\n            executeStep(2);\n            break;\n        case supportedAcrValues[2] "
                      ":\n            executeStep(1);\n            executeStep(3);\n            break;\n        "
                      "default :\n            executeStep(1);\n            executeStep(2);\n            "
                      "executeStep(3);\n    }\n};"
        }
    }
    json_body = json.dumps(body)
    response = requests.patch(url=applications_url + "/" + application_id, headers=headers, data=json_body,
                              verify=False)
    print(response.status_code)
    print(response.text)


dcr(dcr_headers, json.dumps(dcr_body), dcr_url)

access_token = get_access_token(dcr_client_id, dcr_client_secret, scopes, token_url)

service_provider = register_service_provider("conformance", "https://localhost.emobix.co.uk:8443/test/a/yasas/callback")

print(service_provider)

set_user_claim_values()

# change phone number to mobile
change_local_claim_mapping({
    "claimURI": "phone_number",
    "mappedLocalClaimURI": "http://wso2.org/claims/mobile"
}, "https://localhost:9443/api/server/v1/claim-dialects/aHR0cDovL3dzbzIub3JnL29pZGMvY2xhaW0/claims/cGhvbmVfbnVtYmVy")

add_claim_service_provider(service_provider['applicationId'])

configure_acr(service_provider['applicationId'])
