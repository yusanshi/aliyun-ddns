# Aliyun DDNS

Yet another DDNS script for Aliyun.

## Get started

### Install package and clone

```bash
pip3 install aliyun-python-sdk-alidns
cd ~
git clone https://github.com/yusanshi/aliyun-ddns && cd aliyun-ddns
```

### Set authentication info and records updating info

```
cp config.example.json config.json
vim config.json
```

In `authentication` part, input the access key pair you get from Aliyun console website.

The `updates` list defines the records to update. In each record, the `("RR", "Type", "Line")` in `record_key` is the primiary key to identify a record (see [Aliyun Document](https://next.api.aliyun.com/document/Alidns/2015-01-09/UpdateDomainRecord) for the detail), and the new IP address is obtained from the output of `ip_address_command`. Basic your have two options to set the command:

- To get it online, try `curl -s ifconfig.me`, `curl -s ipinfo.io/ip`, etc.

- To get it from local interface, try something like `ip -4 a show eth0 | grep -Po 'inet \\K[0-9.]*'` (and check [Stack Overflow](https://stackoverflow.com/questions/8529181/which-terminal-command-to-get-just-ip-address-and-nothing-else) for more ways).

  > Note the `\\` in `inet \\K...`. If you directly run the command in terminal, it should be `inet \K...`. But in the JSON file, the backslash must be escaped by another backslash. So in the `config.json`, you should write `inet \\K...`.



### Test

```bash
chmod +x main.py
# Test in dry run mode (i.e., read only), check the output to make sure everything is ok
./main.py --dry-run
./main.py # A REAL test
```

### Run periodically with cron

```bash
crontab -e
```

To run the script every 10 minutes, append `*/10 * * * * $HOME/aliyun-ddns/main.py` in the opened file.

### Check log

Check log at `$HOME/aliyun-ddns/log.txt`

