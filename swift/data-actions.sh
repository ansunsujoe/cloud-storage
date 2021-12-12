#!/bin/bash

if [ "$1" == "add" ]; then
    swift upload container1 container-data-temp
    rm -rf container-data-temp
elif [ "$1" == "datacount" ]; then
    ssh root@$2 'find /srv/node/sdb/objects -name *.data | wc -l'
fi