import json
import warnings
import requests
import sys


def save_results(plan_id):
    response = requests.get(url=sys.argv[1] + "/api/plan/exporthtml/" + plan_id, stream=True, verify=False)
    with open("./" + plan_id + "_test_results.zip", 'wb') as fileDir:
        for chunk in response.iter_content(chunk_size=128):
            fileDir.write(chunk)


warnings.filterwarnings("ignore")
plan_list = json.loads(requests.get(url=sys.argv[1] + "/api/plan", verify=False).content)
for plan in plan_list['data']:
    save_results(plan['_id'])
