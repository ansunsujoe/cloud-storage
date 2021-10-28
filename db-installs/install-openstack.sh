#!/bin/bash

# STEP 1
# Disable firewall and network manager service
# Source: https://www.rdoproject.org/install/packstack/
systemctl disable firewalld
systemctl stop firewalld
systemctl disable NetworkManager
systemctl stop NetworkManager
systemctl enable network
systemctl start network

# STEP 2
# Network configurations (defining controller, compute, block/storage)
# This must be done in all nodes
# Source: https://docs.openstack.org/mitaka/install-guide-ubuntu/environment-networking-controller.html

# STEP 3
# Openstack packages for RHEL and CentOS
# This step should be done for controller, compute, and block storage nodes
# Source: https://docs.openstack.org/install-guide/environment-packages-rdo.html#finalize-the-installation

# Enable openstack repository
yum install -y centos-release-openstack-train
yum upgrade -y

# Install openstack client for OpenStack services (do NOT install SELinux)
yum install -y python-openstackclient

# Install python3 and pip packages
yum install -y python3 python3-devel
pip3 install --upgrade pip
pip3 install setuptools_rust
pip3 install python3-openstackclient

# STEP 4
# Identity service (Keystone) installation
# Source: https://docs.openstack.org/keystone/train/install/keystone-install-rdo.html

# Configure the database (after installing MariaDB)
yum install -y mariadb-server
systemctl enable mariadb
systemctl start mariadb

# Install components
yum install -y openstack-keystone httpd mod_wsgi