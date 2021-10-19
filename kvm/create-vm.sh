#!/bin/bash
qemu-img create \
-o preallocation=off \
-f qcow2 /var/lib/libvirt/images/$1.qcow2 4G

virt-install \
--virt-type=kvm \
--name $1 \
--ram 2048 \
--vcpus=1 \
--os-variant=centos7.0 \
--cdrom=/var/lib/libvirt/boot/CentOS-7-x86_64-Minimal-2009.iso \
--network=bridge=br0,model=virtio \
--graphics vnc \
--disk path=/var/lib/libvirt/images/centos7.qcow2,bus=virtio,format=qcow2