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
    os.chdir(TEST_NETWORK)

    #Setting common env variables
    # $PATH=TEST_NETWORK+'/../bin:'+OLD_PATH
    # $FABRIC_CFG_PATH=TEST_NETWORK+'/../config/'

    os.environ['PATH']=TEST_NETWORK+'/../bin:'+OLD_PATH
    print(f"Set PATH: {os.environ['PATH']}")
    os.environ['FABRIC_CFG_PATH']=TEST_NETWORK+'/../config/'
    print(f"Set FABRIC_CFG_PATH: {os.environ['FABRIC_CFG_PATH']}")

    #Setting Peer env variables
    #Test all cars

    env_org1 = PeerENV_Org1(TEST_NETWORK)


    for k, v in env_org1.__dict__.items():
        os.environ[k]=v
        print(f"Set {k}: {v}")

    allcars = AllCarsThread(TEST_NETWORK)
    print("Starting allCars query")
    allcars.start()
    allcars.join()

    if allcars.stdout:
        print(allcars.stdout.decode('utf-8'))
        print("\nNumber of cars: %d" % (allcars.stdout.decode('utf-8').count('Key') ) )
    else:
        print(allcars.stderr.decode('utf-8'))

if __name__ == "__main__":
    main()
