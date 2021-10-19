#!/bin/bash
qemu-img create \
-o preallocation=off \
-f qcow2 /var/lib/libvirt/images/centos7.qcow2 4G