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
    test_log = json.loads(requests.get(url=sys.argv[1] + "/api/log?length=100&search=" + plan['_id'], verify=False).content)
    for test in test_log['data']:
        if "result" in test and test['result'] == "FAILED":
            test_fails.append(test['testName'])
        elif "result" in test and test['result'] == "WARNING":
            test_warnings.append(test['testName'])
    return {
        'fails': test_fails,
        'warnings': test_warnings
    }


failed_plan_details = dict()
failed_count = 0
warnings_count = 0
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
            failed_count += len(failed_tests_list['fails'])
        elif len(failed_tests_list['warnings']) > 0:
            warnings_count += len(failed_tests_list['warnings'])

# send google chat notification
request_body = {
    'text': 'Hi all, OIDC conformance test run #' + sys.argv[2] + ' completed with status: '+sys.argv[3] +
            ' \n Total test cases: ' + (failed_count+warnings_count) +
            ' \n Failed test cases: ' + failed_count +
            ' \n Test cases with warnings: ' + warnings_count +
            ' \n https://github.com/'+sys.argv[4]+'/actions/runs/' + sys.argv[5]
}
response = requests.post(sys.argv[6], json=request_body)
print(response.text)


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
