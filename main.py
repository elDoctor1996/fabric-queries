import csv
import os
import sys
import traceback
import threading
import subprocess
import time
from classes import PeerOrg1Thread, AllCarsThread, PeerENV_Org1, DockerThread

def main():
    logger = DockerThread()
    logger.start()
    
    exec_times = []
    
    try:
        with open('queries.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = []
            for l in csv_reader:
                rows.append(l)
            
    except:
        with open("err_file.txt", "w") as err_out:
            err_out.write(traceback.format_exc())
        return

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
    #Test1
    env_org1 = PeerENV_Org1(TEST_NETWORK)

    for k, v in env_org1.__dict__.items():
        os.environ[k]=v
    count = 0
    for row in rows:
        if count >= 10:
            break
        try:
            peer = PeerOrg1Thread(PWD=TEST_NETWORK, query=row)
            peer.start()
            peer.join()
            exec_times.append(peer.execTime)
            time.sleep(1)
        except:
            with open("err_file.txt", "w") as err_out:
                err_out.write(traceback.format_exc())
            return
        finally:
            count += 1
    logger.stop()
    logger.join()
    with open("docker-stats_log.txt", "w") as output:
        output.writelines(logger.outputs)
    with open("execution-times.csv", "w") as output:
        for i,t in enumerate(exec_times):
            output.write('%d,%.3f\n' % (i,t))

if __name__ == "__main__":
    try:
        main()
    except:
        print("Exception")
