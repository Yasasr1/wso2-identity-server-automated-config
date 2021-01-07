import json
import warnings
import requests
import sys


# export test results of a given test plan
def save_results(plan):
    print("======================\nExporting test results\n======================")
    response = requests.get(url=sys.argv[1] + "/api/plan/exporthtml/" + plan['_id'], stream=True, verify=False)
    with open("./" + plan['_id'] + "_test_results.zip", 'wb') as fileDir:
        for chunk in response.iter_content(chunk_size=128):
            fileDir.write(chunk)


# return names of all failed tests of a given test plan
def get_failed_tests(plan):
    failed_tests = []
    test_log = json.loads(requests.get(url=sys.argv[1] + "/api/log?search=" + plan['_id'], verify=False).content)
    for test in test_log['data']:
        if "result" in test and test['result'] == "FAILED":
            failed_tests.append(test['testName'])
    return failed_tests


failed_plan_details = dict()
warnings.filterwarnings("ignore")
plan_list = json.loads(requests.get(url=sys.argv[1] + "/api/plan?length=15", verify=False).content)

for test_plan in plan_list['data']:
    # save_results(test_plan)
    failed_tests_list = get_failed_tests(test_plan)
    if len(failed_tests_list) > 0:
        failed_plan_details[test_plan['planName']] = failed_tests_list

if failed_plan_details:
    print("Following tests failed\n===========================")
    for test_plan in failed_plan_details:
        print("\n"+test_plan+"\n-----------------------------------")
        print(*failed_plan_details[test_plan], sep="\n")
    sys.exit(1)
else:
    print("\nAll test plans finished successfully")
    sys.exit(0)

