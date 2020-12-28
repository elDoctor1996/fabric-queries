import csv
import os
import sys
import traceback
import threading
import subprocess
import time
from classes import PeerOrg1Thread, PeerENV_Org1, DockerThread
import argparse

parser = argparse.ArgumentParser(description='Hyperledger Fabric test-network query test')
parser.add_argument('num_queries', type=int, help='Number of queries (0<n<=250000', const=2, default=2, nargs='?')
args = parser.parse_args()

def done_filter(rows, done):

    tmp = list( filter( lambda x: x[0] in [y[0] for y in done], rows) )
    for k in tmp:
        ind=None
        for i, x in enumerate(rows):
            if k[0]==x[0]:
                ind=i
                break
        if ind:
            del rows[ind]
            ind=None

def save_outputs(PWD, docker, exec_times, done):
    try:
        old_pwd = os.environ['PWD']
        os.chdir(PWD)
        with open("docker-stats_log.txt", "w") as output:
            output.writelines(docker)
        with open("execution-times.csv", "w") as output:
            for i,t in enumerate(exec_times):
                output.write('%d,%.3f\n' % (i,t))
        with open("done.csv", "w") as output:
            csv_writer = csv.writer(output, delimiter=',')
            
            for row in done:
                csv_writer.writerow(row)

        os.chdir(old_pwd)
    except:
        traceback.format_exc()
        sys.exit(1)

def main():
    logger = DockerThread()
    logger.start()
    print("Started Docker logging thread")

    exec_times = []

    done = []

    #Loading committed queries

    try:
        with open('done.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for l in csv_reader:
                done.append(l)
            print("Found committed queries file")

    except FileNotFoundError:
        print("Not found committed queries file")
        pass


    #Load queries file

    try:
        with open('queries.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = []
            for l in csv_reader:
                rows.append(l)

            done_filter(rows, done)
        
            
        if len(rows)==0:
            print("There are no more queries")
            sys.exit(1)


        print("Loaded queries file in memory")
    except :
        traceback.print_exc()
        sys.exit(1)

    home_dir = os.environ['HOME']
    TEST_NETWORK=f'{home_dir}/fabric-samples/test-network'
    OLD_PATH=os.environ['PATH']
    OLD_PWD=os.environ['PWD']


    os.chdir(TEST_NETWORK)
    print(f"Changed directory to TEST_NETWORK: {TEST_NETWORK}")


    #Setting common env variables
    # $PATH=TEST_NETWORK+'/../bin:'+OLD_PATH
    # $FABRIC_CFG_PATH=TEST_NETWORK+'/../config/'

    os.environ['PATH']=TEST_NETWORK+'/../bin:'+OLD_PATH
    print(f"Set PATH: {os.environ['PATH']}")
    os.environ['FABRIC_CFG_PATH']=TEST_NETWORK+'/../config/'
    print(f"Set FABRIC_CFG_PATH: {os.environ['FABRIC_CFG_PATH']}")
    #Setting Peer env variables
    #Test1
    env_org1 = PeerENV_Org1(TEST_NETWORK)

    for k, v in env_org1.__dict__.items():
        os.environ[k]=v
        print(f"Set {k}: {v}")

    count = 0

    try:

        for row in rows[1:]:

            if count >= args.num_queries:
                break

            peer = PeerOrg1Thread(PWD=TEST_NETWORK, query=row)
            peer.start()
            peer.join()
            exec_times.append(peer.execTime)
            print(f'Added {row} to the Ledger')
            print(f'Query n. {count+1}')
            time.sleep(1)
            count += 1

            done.append(row)
    except:
        traceback.format_exc()

    finally:
        logger.stop()
        logger.join()
        print("Stopped Docker logging thread")
        save_outputs(OLD_PWD, logger.outputs, exec_times, done)
        print(f"Saved outputs in: {OLD_PWD}")


if __name__ == "__main__":
    main()
