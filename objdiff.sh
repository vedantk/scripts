#!/bin/bash

function normalize() {
	sed '/file format elf64-x86-64/d'
}

objdump -d $1 | normalize > /tmp/lhs
objdump -d $2 | normalize > /tmp/rhs
diff /tmp/{l,r}hs
