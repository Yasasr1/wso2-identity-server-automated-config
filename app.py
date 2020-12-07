import warnings
import psutil
import requests
import json
from urllib.parse import urlencode
from zipfile import ZipFile
import subprocess
import os
import sys

ALIAS = "test"
DCR_ENDPOINT = "https://localhost:9443/api/identity/oauth2/dcr/v1.1/register"
TOKEN_ENDPOINT = "https://localhost:9443/oauth2/token"
DCR_CLIENT_ID = "oidc_test_clientid001"
DCR_CLIENT_SECRET = "oidc_test_client_secret001"
APPLICATION_ENDPOINT = "https://localhost:9443/api/server/v1/applications"
SCOPES = "internal_user_mgt_update internal_application_mgt_create internal_application_mgt_view internal_login " \
         "internal_claim_meta_update internal_application_mgt_update internal_scope_mgt_create"

DCR_HEADERS = {'Content-Type': 'application/json', 'Connection': 'keep-alive',
               'Authorization': 'Basic YWRtaW46YWRtaW4='}
DCR_BODY = {
    'client_name': 'python_script',
    "grant_types": ["password"],
    "ext_param_client_id": DCR_CLIENT_ID,
    "ext_param_client_secret": DCR_CLIENT_SECRET
}

headers = {
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'Authorization': 'Bearer '
}


def dcr():
    print("DCR")
    response = requests.post(url=DCR_ENDPOINT, headers=DCR_HEADERS, data=json.dumps(DCR_BODY), verify=False)
    print(response.status_code)


def get_access_token(client_id, client_secret, scope, url):
    body = {
        'grant_type': 'password',
        'username': 'admin',
        'password': 'admin',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }

    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
    }
    print("Getting access token")
    response_map = json.loads(requests.post(url=url, headers=token_headers, data=urlencode(body), verify=False).content)
    print(response_map)
    if response_map['access_token']:
        return response_map['access_token']
    else:
        print("Error: No access token found")


def get_service_provider_details(application_id):
    response = json.loads(requests.get(url=APPLICATION_ENDPOINT + "/" + application_id + "/inbound-protocols/oidc",
                                       headers=headers, verify=False).content)
    return {"clientId": response['clientId'], "clientSecret": response['clientSecret'], "applicationId": application_id}


def register_service_provider(name, callback_url):
    body = {
        "name": name,
        "inboundProtocolConfiguration": {
            "oidc": {
                "state": "ACTIVE",
                "grantTypes": [
                    "authorization_code",
                    "implicit"
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

    print("Registering service provider " + name)
    json_body = json.dumps(body)
    response = requests.post(url=APPLICATION_ENDPOINT, headers=headers, data=json_body, verify=False)
    if response.content and json.loads(response.content)['code'] == "APP-65001":
        print("Application already registered, getting details")
    else:
        print("Service provider " + name + " registered")
    response = requests.get(url=APPLICATION_ENDPOINT + "?filter=name+eq+" + name, headers=headers, verify=False)
    print(response.status_code)
    response_map = json.loads(response.content)
    print(response_map)
    if response_map['count'] == 0:
        print("error application not found")
    else:
        return get_service_provider_details(response_map['applications'][0]['id'])


def set_user_claim_values():
    # can't update these values -
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
                        "dateOfBirth": "1997-11-26T05:09:15.680889Z",
                        "organization": "organization2"
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

    print("Setting user claim values")
    json_body = json.dumps(body)
    response = requests.patch(url="https://localhost:9443/scim2/Me", headers=headers, data=json_body, verify=False)
    print(response.status_code)
    print(response.text)


def change_local_claim_mapping(body, url):
    print("changing local claim mapping for " + body['claimURI'])
    json_body = json.dumps(body)
    response = requests.put(url=url, headers=headers, data=json_body, verify=False)
    print(response.status_code)
    print(response.text)


def add_claim_service_provider(application_id):
    body = {
        "claimConfiguration": {
            "dialect": "LOCAL",
            "requestedClaims": [
                {
                    "claim": {
                        "uri": "http://wso2.org/claims/organization"
                    },
                    "mandatory": True
                },
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

    print("Adding claims to service provider")
    json_body = json.dumps(body)
    response = requests.patch(url=APPLICATION_ENDPOINT + "/" + application_id, headers=headers, data=json_body,
                              verify=False)
    print(response.status_code)
    print(response.text)


def configure_acr(application_id):
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
                }
            ],
            "subjectStepId": 1,
            "type": "USER_DEFINED",
            "script": "// Define conditional authentication by passing one or many Authentication Context Class "
                      "References \n// as comma separated values.\n\n// Specify the ordered list of ACR "
                      "here.\nvar supportedAcrValues = ['acr1'];\n\nvar onLoginRequest = function("
                      "context) {\n    var selectedAcr = selectAcrFrom(context, supportedAcrValues);\n    Log.info("
                      "'--------------- ACR selected: ' + selectedAcr);\n    context.selectedAcr = selectedAcr;\n   "
                      " switch (selectedAcr) {\n        case supportedAcrValues[0] :\n            executeStep("
                      "1);\n            break;\n        "
                      "default :\n            executeStep(1);\n    }\n};"
        }
    }
    print("Setup advanced authentication scripts")
    json_body = json.dumps(body)
    response = requests.patch(url=APPLICATION_ENDPOINT + "/" + application_id, headers=headers, data=json_body,
                              verify=False)
    print(response.status_code)
    print(response.text)


def edit_scope(scope_id, body):
    print("Changing scope: " + scope_id)
    json_body = json.dumps(body)
    response = requests.put(url="https://localhost:9443/api/server/v1/oidc/scopes/" + scope_id, headers=headers,
                            data=json_body, verify=False)
    print(response.status_code)
    print(response.text)


def unpack_and_run(zip_file_name, is_directory_name):
    try:
        # extract IS zip
        if os.path.exists(is_directory_name) is not True:
            with ZipFile(zip_file_name, 'r') as zip_file:
                print("Extracting " + zip_file_name)
                zip_file.extractall()

        # start identity server
        print("Starting Server")
        os.chmod("./" + is_directory_name + "/bin/wso2server.sh", 0o777)
        process = subprocess.Popen("./wso2is-5.11.0/bin/wso2server.sh", stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if b'..................................' in output:
                print("Server Started")
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc
    except FileNotFoundError:
        print("File " + zip_file_name + " not found")
        raise


def json_config_builder(service_provider_1, service_provider_2):
    config = {
        "alias": ALIAS,
        "server": {
            "issuer": "https://localhost:9443/oauth2/token",
            "jwks_uri": "https://localhost:9443/oauth2/jwks",
            "authorization_endpoint": "https://localhost:9443/oauth2/authorize",
            "token_endpoint": "https://localhost:9443/oauth2/token",
            "userinfo_endpoint": "https://localhost:9443/oauth2/userinfo",
            "acr_values": "acr1 acr2 acr3"
        },
        "client": {
            "client_id": service_provider_1['clientId'],
            "client_secret": service_provider_1['clientSecret']
        },
        "client2": {
            "client_id": service_provider_2['clientId'],
            "client_secret": service_provider_2['clientSecret']
        },
        "client_secret_post": {
            "client_id": service_provider_1['clientId'],
            "client_secret": service_provider_1['clientSecret']
        },
        "browser": [
            {
                "match": "https://localhost:9443/oauth2/authorize*",
                "tasks": [
                    {
                        "task": "Login",
                        "match": "https://localhost:9443/authenticationendpoint/login*",
                        "optional": True,
                        "commands": [
                            [
                                "text",
                                "id",
                                "usernameUserInput",
                                "admin"
                            ],
                            [
                                "text",
                                "id",
                                "password",
                                "admin"
                            ],
                            [
                                "click",
                                "xpath",
                                "/html/body/main/div/div[2]/div/form/div[9]/div[2]/button"
                            ],
                            [
                                "wait",
                                "contains",
                                "test/callback",
                                10
                            ]
                        ]
                    },
                    {
                        "task": "Consent",
                        "match": "https://localhost:9443/authenticationendpoint/oauth2_consent*",
                        "optional": True,
                        "commands": [
                            [
                                "wait",
                                "id",
                                "approve",
                                10
                            ],
                            [
                                "click",
                                "id",
                                "rememberApproval",
                                "optional"
                            ],
                            [
                                "click",
                                "id",
                                "approve"
                            ],
                            [
                                "wait",
                                "contains",
                                "callback",
                                10
                            ]
                        ]
                    },
                    {
                        "task": "Verify",
                        "match": "https://localhost.emobix.co.uk:8443/test/a/test/callback*"
                    }
                ]
            }
        ],
        "override": {
            "oidcc-server": {
                "browser": [
                    {
                        "match": "https://localhost:9443/oauth2/authorize*",
                        "tasks": [
                            {
                                "task": "Login",
                                "match": "https://localhost:9443/authenticationendpoint/login*",
                                "optional": True,
                                "commands": [
                                    [
                                        "text",
                                        "id",
                                        "usernameUserInput",
                                        "admin"
                                    ],
                                    [
                                        "text",
                                        "id",
                                        "password",
                                        "admin"
                                    ],
                                    [
                                        "click",
                                        "xpath",
                                        "/html/body/main/div/div[2]/div/form/div[9]/div[2]/button"
                                    ],
                                    [
                                        "wait",
                                        "contains",
                                        "oauth2_consent",
                                        10
                                    ]
                                ]
                            },
                            {
                                "task": "Consent",
                                "match": "https://localhost:9443/authenticationendpoint/oauth2_consent*",
                                "optional": True,
                                "commands": [
                                    [
                                        "wait",
                                        "id",
                                        "approve",
                                        10
                                    ],
                                    [
                                        "click",
                                        "id",
                                        "rememberApproval",
                                        "optional"
                                    ],
                                    [
                                        "click",
                                        "id",
                                        "approve"
                                    ],
                                    [
                                        "wait",
                                        "contains",
                                        "callback",
                                        10
                                    ]
                                ]
                            },
                            {
                                "task": "Verify",
                                "match": "https://localhost.emobix.co.uk:8443/test/a/test/callback*"
                            }
                        ]
                    }
                ]
            },
            "oidcc-refresh-token": {
                "browser": [
                    {
                        "match": "https://localhost:9443/oauth2/authorize*",
                        "tasks": [
                            {
                                "task": "Login",
                                "match": "https://localhost:9443/authenticationendpoint/login*",
                                "optional": True,
                                "commands": [
                                    [
                                        "text",
                                        "id",
                                        "usernameUserInput",
                                        "admin"
                                    ],
                                    [
                                        "text",
                                        "id",
                                        "password",
                                        "admin"
                                    ],
                                    [
                                        "click",
                                        "xpath",
                                        "/html/body/main/div/div[2]/div/form/div[9]/div[2]/button"
                                    ],
                                    [
                                        "wait",
                                        "contains",
                                        "oauth2_consent",
                                        10
                                    ]
                                ]
                            },
                            {
                                "task": "Consent",
                                "match": "https://localhost:9443/authenticationendpoint/oauth2_consent*",
                                "optional": True,
                                "commands": [
                                    [
                                        "wait",
                                        "id",
                                        "approve",
                                        10
                                    ],
                                    [
                                        "click",
                                        "id",
                                        "rememberApproval",
                                        "optional"
                                    ],
                                    [
                                        "click",
                                        "id",
                                        "approve"
                                    ],
                                    [
                                        "wait",
                                        "contains",
                                        "callback",
                                        10
                                    ]
                                ]
                            },
                            {
                                "task": "Verify",
                                "match": "https://localhost.emobix.co.uk:8443/test/a/test/callback*"
                            }
                        ]
                    }
                ]
            }
        }
    }
    json_config = json.dumps(config, indent=4)
    f = open("IS_config.json", "w")
    f.write(json_config)
    f.close()


def is_process_running(processName):
    process_list = []

    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo['name'].lower():
                process_list.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if len(process_list) > 0:
        return True
    else:
        return False


warnings.filterwarnings("ignore")

if not is_process_running("wso2server"):
    unpack_and_run(str(sys.argv[1]), "wso2is-5.11.0")
else:
    print("IS already running")

dcr()

access_token = get_access_token(DCR_CLIENT_ID, DCR_CLIENT_SECRET, SCOPES, TOKEN_ENDPOINT)
headers['Authorization'] = "Bearer " + access_token

service_provider_1 = register_service_provider("okfinal1",
                                               "https://localhost.emobix.co.uk:8443/test/a/" + ALIAS + "/callback")
print(service_provider_1)
service_provider_2 = register_service_provider("okfinal2",
                                               "https://localhost.emobix.co.uk:8443/test/a/" + ALIAS + "/callback")
print(service_provider_2)

set_user_claim_values()

# change phone number to mobile
change_local_claim_mapping(
    {
        "claimURI": "phone_number",
        "mappedLocalClaimURI": "http://wso2.org/claims/mobile"
    },
    "https://localhost:9443/api/server/v1/claim-dialects/aHR0cDovL3dzbzIub3JnL29pZGMvY2xhaW0/claims/cGhvbmVfbnVtYmVy")

# change website from url to organization
change_local_claim_mapping(
    {
        "claimURI": "website",
        "mappedLocalClaimURI": "http://wso2.org/claims/organization"
    },
    "https://localhost:9443/api/server/v1/claim-dialects/aHR0cDovL3dzbzIub3JnL29pZGMvY2xhaW0/claims/d2Vic2l0ZQ")

add_claim_service_provider(service_provider_1['applicationId'])
add_claim_service_provider(service_provider_2['applicationId'])

configure_acr(service_provider_1['applicationId'])
configure_acr(service_provider_2['applicationId'])

edit_scope("openid", {
    "claims": [
        "sub"
    ],
    "description": "",
    "displayName": "openid"
})

json_config_builder(service_provider_1, service_provider_2)
