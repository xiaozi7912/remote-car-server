#!/bin/bash

killall python3

cd /home/igwadmin/remote-car-server

python3 ./python/car_http.py >/dev/null 2>&1 &
python3 ./python/car_bt.py >/dev/null 2>&1 &