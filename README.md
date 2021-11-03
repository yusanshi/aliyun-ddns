# Aliyun DDNS

```
pip3 install aliyun-python-sdk-alidns
cd ~
git clone https://github.com/yusanshi/aliyun-ddns && cd aliyun-ddns
mv config.example.json config.json
vim config.json # set authentication info and records updating info
chmod +x main.py
./main.py --dry-run # test in dry run mode (i.e., read only), check the output to make sure everything is ok
./main.py # a REAL test
crontab -e # add `*/10 * * * * $HOME/aliyun-ddns/main.py`
# check log at $HOME/aliyun-ddns/log.txt
```

