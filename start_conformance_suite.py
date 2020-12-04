import subprocess
import os
import sys


def start(file):
    try:
        os.chmod(file, 0o777)
        process = subprocess.Popen("sudo -E docker-compose -f " + file + " up", shell=True, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if b'Starting application' in output:
                print("Server Started")
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc
    except FileNotFoundError:
        print(file + " not found")
        raise


start(sys.argv[1])
