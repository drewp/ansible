#!/bin/sh
# ok to run this at startup; it waits for b2g to launch
while ! echo 'window.resizeTo(702,480)' | nc localhost 9999; do sleep 2; done
