#!/bin/bash

if [ "$1" == "dataloc" ]; then
    ssh root@$2 'find /srv/node/sdb/objects -name *.data | xargs head -n3' | grep oid
elif [ "$1" == "datacount" ]; then
    ssh root@$2 'find /srv/node/sdb/objects -name *.data | wc -l'
elif [ "$1" == "object-requests" ]; then
    ssh root@$2 "journalctl -u openstack-swift-object | grep $3"
elif [ "$1" == "virsh-nodes" ]; then
    ssh generic@$2 "sudo virsh list"
fi