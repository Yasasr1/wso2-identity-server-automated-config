import json
import warnings
import requests
import sys
import os


# export test results of a given test plan
def save_results(plan):
    response = requests.get(url=sys.argv[1] + "/api/plan/exporthtml/" + plan['_id'], stream=True, verify=False)
    with open("./" + plan['planName'] + "_test_results.zip", 'wb') as fileDir:
        for chunk in response.iter_content(chunk_size=128):
            fileDir.write(chunk)


# return names of all failed tests of a given test plan
def get_failed_tests(plan):
    test_fails = []
    test_warnings = []
    test_others = []
    test_log = json.loads(requests.get(url=sys.argv[1] + "/api/log?length=100&search=" + plan['_id'], verify=False).content)
    for test in test_log['data']:
        if "result" in test and test['result'] == "FAILED":
            test_fails.append(test['testName'])
        elif "result" in test and test['result'] == "WARNING":
            test_warnings.append(test['testName'])
        else:
            test_others.append(test['testName'])
    return {
        'fails': test_fails,
        'warnings': test_warnings,
        'others': test_others
    }


failed_plan_details = dict()
contains_fails = False
warnings.filterwarnings("ignore")
plan_list = json.loads(requests.get(url=sys.argv[1] + "/api/plan?length=50", verify=False).content)
print("======================\nExporting test results\n======================")
for test_plan in plan_list['data']:
    save_results(test_plan)
    failed_tests_list = get_failed_tests(test_plan)
    if len(failed_tests_list['fails']) > 0 or len(failed_tests_list['warnings']) > 0:
        failed_plan_details[test_plan['planName']] = failed_tests_list
        if len(failed_tests_list['fails']) > 0:
            contains_fails = True

if failed_plan_details:
    print("Following tests have fails/warnings\n===========================")
    for test_plan in failed_plan_details:
        print("\n"+test_plan+"\n-----------------------------------")
        print("\nFails\n-----")
        print(*failed_plan_details[test_plan]['fails'], sep="\n")
        print("\nWarnings\n--------")
        print(*failed_plan_details[test_plan]['warnings'], sep="\n")
    if contains_fails:
        sys.exit(1)
    else:
        sys.exit(0)
else:
    print("\nAll test plans finished successfully")
    sys.exit(0)
