#!/usr/bin/env python3

import json
import pathlib
import os
import subprocess
import logging
import argparse

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest


def get_records(client, domain):
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    response = client.do_action_with_exception(request)
    return json.loads(str(response,
                          encoding='utf-8'))['DomainRecords']['Record']


def update_record(client, current_records, update):
    found_records = [
        record for record in current_records
        if all(record[key] == update['record_key'][key]
               for key in update['record_key'].keys())
    ]
    assert len(found_records) == 1
    found_record = found_records[0]
    print(f'Found record {found_record}')

    new_ip_address = subprocess.check_output(update['ip_address_command'],
                                             shell=True,
                                             text=True).strip()

    if found_record['Value'] == new_ip_address:
        print('IP address not changed, skip updating')
    else:
        print(
            f"Updating record {tuple(found_record[key] for key in update['record_key'].keys())}'s address from {found_record['Value']} to {new_ip_address}"
        )
        if args.dry_run:
            print('Skipped in dry run mode')
        else:
            record_id = found_record['RecordId']
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')

            request.set_RecordId(record_id)
            request.set_RR(update['record_key']['RR'])
            request.set_Type(update['record_key']['Type'])
            request.set_Line(update['record_key']['Line'])
            request.set_Value(new_ip_address)

            client.do_action_with_exception(request)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    script_directory = pathlib.Path(__file__).parent.resolve()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[
                            logging.FileHandler(
                                os.path.join(script_directory, 'log.txt')),
                            logging.StreamHandler()
                        ])
    print = logging.info

    with open(os.path.join(script_directory, 'config.json')) as f:
        config = json.load(f)

    credentials = AccessKeyCredential(
        config['authentication']['access_key'],
        config['authentication']['access_secret'])

    client = AcsClient(credential=credentials)

    current_records = get_records(client, config['domain'])

    for update in config['updates']:
        update_record(client, current_records, update)
