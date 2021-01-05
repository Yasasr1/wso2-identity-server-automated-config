#!/bin/bash +x
CONFORMANCE_SUITE_URL=https://localhost:8443
declare -a failed_test_plans
IS_FAILED=false
echo "========================"
echo "Running Tests"
echo "========================"
echo
echo "Basic certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-basic-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee basic-certification-test-plan-log.txt
then
	IS_FAILED=true
    failed_test_plans+=("Basic certification test plan")
fi
echo
echo "Implicit certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-implicit-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee implicit-certification-test-plan-log.txt
then
	IS_FAILED=true
    failed_test_plans+=("Implicit certification test plan")
fi
echo
echo "Hybrid certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-hybrid-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee hybrid-certification-test-plan-log.txt
then

	IS_FAILED=true
    failed_test_plans+=("Hybrid certification test plan")
fi
echo
echo "Formpost basic certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-formpost-basic-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee formpost-basic-certification-test-plan-log.txt
then

	IS_FAILED=true
    failed_test_plans+=("Formpost basic certification test plan")
fi
echo
echo "Formpost implicit certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-formpost-implicit-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee formpost-implicit-certification-test-plan-log.txt
then

	IS_FAILED=true
    failed_test_plans+=("Formpost implicit certification test plan")
fi
echo
echo "Formpost hybrid certification test plan"
echo "-----------------------------"
echo
if sudo python3 ./conformance-suite/scripts/run-test-plan.py oidcc-formpost-hybrid-certification-test-plan[server_metadata=static][client_registration=static_client] ./IS_config.json 2>&1 | tee formpost-hybrid-certification-test-plan-log.txt
then

	IS_FAILED=true
    failed_test_plans+=("Formpost hybrid certification test plan")
fi
echo
echo "Exporting results"
echo "-----------------------------"
echo
sudo python3 ./wso2-identity-server-automated-config/export_results.py $CONFORMANCE_SUITE_URL

if $IS_FAILED
then
	echo
    echo "Following test plans finished with failures/warnings"
    echo "----------------------------------------------------"
   	printf '%s\n' "${failed_test_plans[@]}"
    exit 1
else
	echo
    echo "All test plans finished successfully"
    echo "------------------------------------"
	exit 0
fi