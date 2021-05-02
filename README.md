# How to Run in AWS
- git clone repository
- Set server time as Korean Time Zone
```
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
```
- install prerequisites
```
sudo apt install python3-pip
pip3 install pyupbit
pip3 install matplotlib
```
- set your access, secret key in bitcoinAutoTradeSlack.py

- run program as background
```
nohup python3 bitcoinAutoTradeSlack.py > output.log &
```

- check if the program is running by 
```
ps ax | grep .py
```

- if you want to kill your program,
```
kill -9 PID
```