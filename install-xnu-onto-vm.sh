#!/bin/bash

XNU=$1
MOD=$2
echo "Installing $XNU onto $2..."
scp $XNU local@$MOD:~/kernel.development
ssh local@$MOD "sudo cp ~/kernel.development /System/Library/Kernels/"
ssh local@$MOD "sudo touch /System/Library/Extensions"
ssh local@$MOD "sudo touch /tmp/rebooting"
ssh local@$MOD "sudo reboot"

echo "Finished issuing reboot. Sleeping for a while before ssh'ing..."
sleep 25 

ssh local@$MOD "cat /tmp/rebooting"
