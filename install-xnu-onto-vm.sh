#!/bin/bash

XNU=$1
MOD=$2
echo "Installing $XNU onto $2..."
EXPECT=$(shasum -a 256 $XNU)
echo "  Expect hash: $EXPECT"
scp $XNU local@$MOD:~/kernel.development
ssh local@$MOD "sudo cp ~/kernel.development /System/Library/Kernels/kernel.development"
ssh local@$MOD "sudo cp ~/kernel.development /System/Library/Kernels/kernel"
ssh local@$MOD "sudo touch /System/Library/Extensions"
ssh local@$MOD "ps -e | grep kextd"
ssh local@$MOD "sudo reboot"

echo "Finished issuing reboot. Sleeping for a while before ssh'ing..."
sleep 25 

ssh local@$MOD "uname -a"
ssh local@$MOD "shasum -a 256 /System/Library/Kernels/kernel"
ssh local@$MOD "shasum -a 256 /System/Library/Kernels/kernel.development"
