#!/bin/bash

# Disable firewall and network manager service
systemctl disable firewalld
systemctl stop firewalld
systemctl disable NetworkManager
systemctl stop NetworkManager
systemctl enable network
systemctl start network

# Install packstack-openstack
yum install -y centos-release-openstack-train
yum install -y openstack-packstack
packstack --allinone