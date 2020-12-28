import threading
import subprocess
import time

# class _PeerENV_Org2:
    
#     def __init__(self, PWD):
#         self.CORE_PEER_TLS_ENABLED='true'
#         self.CORE_PEER_LOCALMSPID="Org2MSP"
#         self.CORE_PEER_TLS_ROOTCERT_FILE='%s/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt' % (PWD)
#         self.CORE_PEER_MSPCONFIGPATH='%s/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp' % (PWD)
#         self.CORE_PEER_ADDRESS='localhost:9051'

class PeerENV_Org1:
    
    def __init__(self, PWD):
        self.CORE_PEER_TLS_ENABLED='true'
        self.CORE_PEER_LOCALMSPID="Org1MSP"
        self.CORE_PEER_TLS_ROOTCERT_FILE='%s/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt' % (PWD)
        self.CORE_PEER_MSPCONFIGPATH='%s/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp' % (PWD)
        self.CORE_PEER_ADDRESS='localhost:7051'

class _TestThread(threading.Thread):
    
    def __init__(self):
        self.stdout = None
        self.stderr = None
        
        threading.Thread.__init__(self)

class DockerThread(threading.Thread):
    def __init__(self):
        _TestThread.__init__(self)
        self._condition=True
        self.outputs = []

    def stop(self):
        self._condition=False
        
    def run(self):
        while self._condition:
            p = subprocess.Popen('docker stats --no-stream'.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.stdout, _ = p.communicate()
            self.outputs.append(self.stdout.decode('utf-8')+'\n\n')
            time.sleep(1)

class PeerOrg1Thread(_TestThread):
    def __init__(self, PWD, query):
        
        _TestThread.__init__(self)
        
        # Execution time
        self.execTime=None
        
        # query is a list of attributes (ergo without csv separator) from a row of csv file (avoided to install libraries like Pandas)
        self.query = query

    def run(self):
        z=f'{{"function": "createCar", "Args":["{self.query[0]}", "{self.query[1]}", "{self.query[2]}", "{self.query[3]}", "{self.query[4]}"]}}'
        query='peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls true --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n fabcar --peerAddresses localhost:7051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c \'%s\''
        start = time.perf_counter()
        p = subprocess.Popen(query % z , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
        end = time.perf_counter()
        self.execTime = round(end-start, 3)

class AllCarsThread(_TestThread):
    def __init__(self, PWD):
        
        _TestThread.__init__(self)

    def run(self):
        query='peer chaincode query -C mychannel -n fabcar -c \'{"Args":["queryAllCars"]}\''
        p = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
