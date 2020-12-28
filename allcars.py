import csv
import os
import sys
import traceback
import threading
import subprocess
import time
from classes import PeerOrg1Thread, AllCarsThread, PeerENV_Org1, DockerThread

def main():
    home_dir = os.environ['HOME']
    TEST_NETWORK=f'{home_dir}/fabric-samples/test-network'
    OLD_PATH=os.environ['PATH']
    try:
        os.chdir(TEST_NETWORK)
    except Exception:
        with open("err_file.txt", "w") as err_out:
            err_out.write(traceback.format_exc())
        return

    #Setting common env variables
    # $PATH=TEST_NETWORK+'/../bin:'+OLD_PATH
    # $FABRIC_CFG_PATH=TEST_NETWORK+'/../config/'

    os.environ['PATH']=TEST_NETWORK+'/../bin:'+OLD_PATH
    os.environ['FABRIC_CFG_PATH']=TEST_NETWORK+'/../config/'

    #Setting Peer env variables
    #Test all cars

    env_org1 = PeerENV_Org1(TEST_NETWORK)


    for k, v in env_org1.__dict__.items():
        os.environ[k]=v
    try:
        allcars = AllCarsThread(TEST_NETWORK)
        allcars.start()
        allcars.join()

        if allcars.stdout:
            print(allcars.stdout.decode('utf-8'))
	    print("\nNumber of cars: %d" % (allcars.stdout.decode('utf-8').count('KEY') )
        else:
            print(allcars.stderr.decode('utf-8'))
    except:
        with open("err_file.txt", "w") as err_out:
            err_out.write(traceback.format_exc())
        return

if __name__ == "__main__":
    try:
        main()
    except:
        print("Exception")
