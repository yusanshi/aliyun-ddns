# Aliyun DDNS

```bash
pip3 install aliyun-python-sdk-alidns
cd ~
git clone https://github.com/yusanshi/aliyun-ddns && cd aliyun-ddns
mv config.example.json config.json
# Set authentication info and records updating info
# In "new_record" field, the ("rr", "type", "line") is the primiary key to identify a record,
# and the "value" defines the IP address of the new record,
# currently three types are supported:
# 1. LITERAL: specify the IP address directly, 
#                e.g., "value": "LITERAL#1.1.1.1"
# 2. INTERFACE(currently ipv4 only): get it from local interface, 
#                e.g., "value": "IPV4_INTERFACE#eth0"
#                 Note: if your OS is not Linux based, you may need to modify
#                       the python code for this type.
# 3. ONLINE(currently ipv4 only): get it online, 
#                e.g., "value": "IPV4_ONLINE#"
vim config.json
chmod +x main.py
./main.py --dry-run # test in dry run mode (i.e., read only), check the output to make sure everything is ok
./main.py # a REAL test
crontab -e # add `*/10 * * * * $HOME/aliyun-ddns/main.py`
# check log at $HOME/aliyun-ddns/log.txt
```

