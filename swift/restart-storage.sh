#!/bin/bash

# Rsyncd service
systemctl enable rsyncd.service
systemctl restart rsyncd.service

# Account services
systemctl restart openstack-swift-account.service openstack-swift-account-auditor.service \
  openstack-swift-account-reaper.service openstack-swift-account-replicator.service

# Container services
systemctl restart openstack-swift-container.service \
  openstack-swift-container-auditor.service openstack-swift-container-replicator.service \
  openstack-swift-container-updater.service

# Object services
systemctl restart openstack-swift-object.service openstack-swift-object-auditor.service \
  openstack-swift-object-replicator.service openstack-swift-object-updater.service