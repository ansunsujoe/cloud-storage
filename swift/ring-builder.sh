#!/bin/bash

# Account builder
swift-ring-builder account.builder create 10 1 1
swift-ring-builder account.builder \
  add --region 1 --zone 1 --ip 192.168.1.53 --port 6202 \
  --device sdb --weight 100
swift-ring-builder account.builder rebalance

# Container builder
swift-ring-builder container.builder create 10 1 1
swift-ring-builder container.builder \
  add --region 1 --zone 1 --ip 192.168.1.53 --port 6201 \
  --device sdb --weight 100
swift-ring-builder container.builder rebalance

# Object builder
swift-ring-builder object.builder create 10 1 1
swift-ring-builder object.builder \
  add --region 1 --zone 1 --ip 192.168.1.53 --port 6200 \
  --device sdb --weight 100
swift-ring-builder object.builder rebalance

# Move gz files to correct place
scp account.ring.gz container.ring.gz object.ring.gz root@192.168.1.53:/etc/swift
mv account.ring.gz container.ring.gz object.ring.gz /etc/swift