import subprocess
import time
while(True):
    time.sleep(5)
    o1 = subprocess.check_output(['sudo','python3', '2callDownloadToText.py'])
    o2 = subprocess.check_output(['sudo','python3', '3summarizerSample.py'])

    print(str(o1))
    print(str(o2))
