#!/usr/bin/env python2
"""
Generates a simple docker compose file for devmode
"""
import os
import sys

GEN_PATH = os.environ["GEN_PATH"]

# Parse args
if len(sys.argv) != 4:
    sys.stderr.write("Usage: create_dev_docker_compose.py org peer admin")
    exit(1)
ORG = sys.argv[1]
PEER = sys.argv[2]
ADMIN = sys.argv[3]

with open(GEN_PATH + '/devmode/docker-compose-simple.yaml', 'w') as stream:
    stream.write("""version: '2'
# This file is auto-generated

services:
  orderer:
    container_name: orderer
    image: hyperledger/fabric-orderer
    environment:
      - ORDERER_GENERAL_LOGLEVEL=debug
      - ORDERER_GENERAL_LISTENADDRESS=orderer
      - ORDERER_GENERAL_GENESISMETHOD=file
      - ORDERER_GENERAL_GENESISFILE=orderer.block
      - ORDERER_GENERAL_LOCALMSPID={0}
      - ORDERER_GENERAL_LOCALMSPDIR=/etc/hyperledger/msp
      - GRPC_TRACE=all=true,
      - GRPC_VERBOSITY=debug
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric
    command: orderer
    volumes:
      - ../crypto-config/{1}/orderers/orderer.{1}/msp:/etc/hyperledger/msp
      - ./channel/orderer.genesis.block:/etc/hyperledger/fabric/orderer.block
    ports:
      - 7050:7050

  peer:
    container_name: peer
    image: hyperledger/fabric-peer
    environment:
      - CORE_PEER_ID=peer
      - CORE_PEER_ADDRESS=peer:7051
      - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer:7051
      - CORE_PEER_LOCALMSPID={0}
      - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
      - CORE_LOGGING_LEVEL=DEBUG
      - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp
      - CORE_LEDGER_STATE_STATEDATABASE=CouchDB
      - CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=admin
      - CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD=password
      - CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS=couchdb:5984
    volumes:
        - /var/run/:/host/var/run/
        - ../crypto-config/{1}/peers/{2}.{1}/msp:/etc/hyperledger/msp
    working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
    command: peer node start --peer-chaincodedev=true -o orderer:7050
    ports:
      - 7051:7051
      - 7053:7053
    depends_on:
      - orderer
      - couchdb

  cli:
    container_name: cli
    image: hyperledger/fabric-tools
    tty: true
    environment:
      - GOPATH=/opt/gopath
      - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
      - CORE_LOGGING_LEVEL=DEBUG
      - CORE_PEER_ID=cli
      - CORE_PEER_ADDRESS=peer:7051
      - CORE_PEER_LOCALMSPID={0}
      - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp
    working_dir: /opt/gopath/src/chaincodedev
    command: /bin/bash -c 'sleep 5; ./script.sh;'
    volumes:
        - /var/run/:/host/var/run/
        - ../crypto-config/{1}/users/{3}.{1}/msp:/etc/hyperledger/msp
        - ./:/opt/gopath/src/chaincodedev/
        - ./channel:/opt/gopath/src/chaincodedev/channel
    depends_on:
      - orderer
      - peer

  chaincode:
    container_name: chaincode
    image: hyperledger/fabric-ccenv
    tty: true
    environment:
      - GOPATH=/opt/gopath
      - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
      - CORE_LOGGING_LEVEL=DEBUG
      - CORE_PEER_ID=example02
      - CORE_PEER_ADDRESS=peer:7051
      - CORE_PEER_LOCALMSPID={0}
      - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp
    working_dir: /opt/gopath/src/chaincode
    command: /bin/bash -c 'sleep 6000000'
    volumes:
        - /var/run/:/host/var/run/
        - ../crypto-config/{1}/peers/{2}.{1}/msp:/etc/hyperledger/msp
        - ./chaincode:/opt/gopath/src/chaincode
    depends_on:
      - orderer
      - peer

  couchdb:
    container_name: couchdb
    image: yeasy/hyperledger-fabric-couchdb
    # Populate the COUCHDB_USER and COUCHDB_PASSWORD to set an admin user and password
    # for CouchDB.  This will prevent CouchDB from operating in an "Admin Party" mode.
    environment:
      - COUCHDB_USER=admin
      - COUCHDB_PASSWORD=password
    # Comment/Uncomment the port mapping if you want to hide/expose the CouchDB service,
    # for example map it to utilize Fauxton User Interface in dev environments.
    ports:
      - "5984:5984"
""".format(
    ORG.replace('.', '-') + '-MSP',
    ORG,
    PEER,
    ADMIN
))
