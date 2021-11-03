#!/usr/bin/env python3

import json
import pathlib
import os
import copy
import subprocess
import logging
import argparse

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest


def filter_aliyun_record(record):
    return {
        key_aliyun2my[k]: v
        for k, v in record.items() if k in key_aliyun2my
    }


def get_records(client, domain):
    request = DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    response = client.do_action_with_exception(request)
    return json.loads(str(response,
                          encoding='utf-8'))['DomainRecords']['Record']


def update_record(client, domain, current_records, new_record):
    found_records = [
        record for record in current_records
        if all(record[key_my2aliyun[key]] == new_record[key]
               for key in key_my2aliyun.keys() if key != 'value')
    ]
    assert len(found_records) == 1
    found_record = found_records[0]
    print(f'Found record {filter_aliyun_record(found_record)}')

    if found_record[key_my2aliyun['value']] == new_record['value']:
        print('IP address not changed, skip updating')
    else:
        print(f'Updating {filter_aliyun_record(found_record)} to {new_record}')
        if args.dry_run:
            print('Skipped in dry run mode')
        else:
            record_id = found_record['RecordId']
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')

            request.set_RecordId(record_id)
            request.set_RR(new_record['rr'])
            request.set_Type(new_record['type'])
            request.set_Value(new_record['value'])
            request.set_Line(new_record['line'])

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

    key_my2aliyun = {
        'rr': 'RR',
        'type': 'Type',
        'value': 'Value',
        'line': 'Line',
    }

    key_aliyun2my = {v: k for k, v in key_my2aliyun.items()}

    with open(os.path.join(script_directory, 'config.json')) as f:
        config = json.load(f)
        config_copied = copy.deepcopy(config)
        for index, operation in enumerate(config_copied['operations']):
            ip_type, ip_parameter = operation['new_record']['value'].split('#')
            if ip_type == 'LITERAL':
                ip = ip_parameter
            elif ip_type == 'IPV4_INTERFACE':
                ip = subprocess.check_output(
                    f"ip -4 a show {ip_parameter} | grep -Po 'inet \K[0-9.]*'",
                    shell=True,
                    text=True).strip()
            else:
                raise NotImplementedError
            config['operations'][index]['new_record']['value'] = ip

    credentials = AccessKeyCredential(
        config['authentication']['access_key'],
        config['authentication']['access_secret'])

    client = AcsClient(credential=credentials)

    current_records = get_records(client, config['domain'])

    for operation in config['operations']:
        if operation['type'] == 'update':
            update_record(client, config['domain'], current_records,
                          operation['new_record'])
        else:
            raise NotImplementedError(
                f"Operation type {operation['type']} not implemented")
