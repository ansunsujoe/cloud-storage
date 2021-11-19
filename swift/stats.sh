#!/bin/bash

if [ "$1" == "dataloc" ]; then
    ssh root@$2 'find /srv/node/sdb/objects -name *.data | xargs head -n3' | grep oid
elif [ "$1" == "datacount" ]; then
    ssh root@$2 'find /srv/node/sdb/objects -name *.data | wc -l'
elif [ "$1" == "data-delete" ]; then
    ssh root@$2 'rm -r /srv/node/sdb/objects/* /srv/node/sdb/containers/* /srv/node/sdb/accounts/*'
elif [ "$1" == "object-requests" ]; then
    if [ "$4" == "None" ]; then
        ssh root@$2 "journalctl -u openstack-swift-object | grep $3"
    else
        ssh root@$2 "journalctl -u openstack-swift-object --since "$4" | grep $3"
    fi
elif [ "$1" == "virsh-running-nodes" ]; then
    ssh generic@$2 "sudo virsh list"
elif [ "$1" == "virsh-shutoff-nodes" ]; then
    ssh generic@$2 "sudo virsh list --state-shutoff"
elif [ "$1" == "virsh-shutdown" ]; then
    ssh generic@$2 "sudo virsh shutdown $3"
elif [ "$1" == "virsh-startup" ]; then
    ssh generic@$2 "sudo virsh start $3"
elif [ "$1" == "initconfig" ]; then
    ssh root@$2 "timedatectl set-timezone America/Chicago"
fi 