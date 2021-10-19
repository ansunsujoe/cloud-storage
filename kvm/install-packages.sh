#!/bin/bash
yum groupinstall "Development Tools" -y
yum install openssl-devel libffi-devel bzip2-devel -y
yum install wget -y