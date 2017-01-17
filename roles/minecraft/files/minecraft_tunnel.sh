#!/bin/zsh

eval `keychain --noask --eval id_ecdsa`

exec ssh -v -N -g -R \*:25565:localhost:25566 prime
