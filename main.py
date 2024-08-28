import json
import time
import random
import string
import argparse
import logging

import pandas as pd

from api import AuraAPI

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('tenant_id', type=str, help="Aura Tenant ID")
    parser.add_argument('client_id',  type=str, help="Aura API Client ID")
    parser.add_argument('client_secret', type=str, help="Aura API Client Secret")
    parser.add_argument('task', type=str, help='setup task', choices=['create', 'clone', 'status', 'list', 'pause',
                                                                      'resume', 'delete', 'snapshots'])
    parser.add_argument('--output', default='instances.csv', help="full path to csv file")
    return parser.parse_args()

def clone_instances(api, **kwargs):

    # Get configuration parameters
    params = kwargs.get('params', {})

    source_instance_id = params.get('source_instance_id','')
    if source_instance_id:
        status = api.status(source_instance_id)
        if status not in ['running']:
            logger.info("Source Instance is not running. Not ready to Clone: {} {}".format(instance_id, status))
            return list()
        source_snapshot_date = params.get('source_snapshot_date', '')
        source_snapshot_id =  __get_latest_snapshot(source_instance_id, source_snapshot_date)   
        kwargs['params'].update(
            {
            "source_snapshot_id":  source_snapshot_id
            }
        )
    if not source_instance_id:
        logger.info("Source Instance ID not provided. Source Instance ID: {} {}".format(source_instance_id))
        return list()
    
    instances = create_instances(api, **kwargs)
    return instances

def create_instances(api, **kwargs):
    # Get the list of current instances
    current_instance_list = api.list()
    current_instance_names = [d['name'] for d in current_instance_list]

    # Get configuration parameters
    params = kwargs.get('params')

    # New Instances
    instances = list()
    seqs = __random_sequences(kwargs.get('num_instances'))
    for dbname_suffix in seqs:
        db_name = '_'.join([kwargs.get('dbname_prefix'), dbname_suffix])
        params.update({
            "name": db_name
        })

        # Check if an instance exists with same name
        if db_name in current_instance_names:
            instance_details = [d for d in current_instance_list if d['name'] == db_name][0]
            logger.info("Instance already exists: {}".format(instance_details))

        # Create the new instance
        data = api.create(params=params)
        if not data:
            continue
        instance_details = {k: v for k, v in data.items() if
                            k in ['id', 'connection_url', 'name', 'username', 'password']}
        instances.append(instance_details)
        time.sleep(5)
    return instances

def __random_sequences(num, length=7):
    seqs = [''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) for i in range(num)]
    return seqs

def __get_latest_snapshot(instance_id, snapshot_date=None):
    snapshots = api.snapshots(instance_id, snapshot_date)
    for snapshot in snapshots:
        status = snapshot.get('status', '')
        if status == 'Completed':
            snapshot_id =  snapshot['snapshot_id']
            break
    return snapshot_id

def collect_instance_ids(config):
    prefix = config.get('dbname_prefix', '')
    _list = list()
    if prefix:
        _instances = api.list()  # Get the list of current instances
        _list = [d['id'] for d in _instances if d['name'].startswith(prefix)]
    instance_ids = config.get('instance_ids') + _list

    # Exclude instance IDs specified in the config list
    exclude_instances = config.get('exclude', [])
    if len(exclude_instances) > 0:
        instance_ids = [ins for ins in instance_ids if ins not in exclude_instances]
    return instance_ids

def pause_instances(api, **kwargs):

    # Collect Instance IDs to pause
    instance_ids = collect_instance_ids(kwargs)

    # Check for instance status. Exclude the instances that are not running
    running_instances = list()
    for instance_id in instance_ids:
        status = api.status(instance_id)
        if status == 'running':
            running_instances.append(instance_id)

    paused_instances = list()
    for instance_id in running_instances:
        data = api.pause(instance_id)
        if not data:
            continue
        paused_instances.append(data)
    return paused_instances


def __resume_if_not_running(api, instance_id, wait=True):
    status = api.status(instance_id)
    if status not in ['paused', 'running']:
        logger.info("Source Instance is not ready to start: {} {}".format(instance_id, status))
        return status
    if status == 'paused':
        logger.info("Source Instance is Paused. Resuming now..: {}".format(instance_id))
        start_time = time.time()
        _ = api.resume(instance_id, wait=wait)
        logger.info("Time to status: running from status:paused in secs: {}".format(time.time() - start_time))
        status = api.status(instance_id)
    return status

if __name__ == '__main__':
    start = time.time()
    args = cli()
    tenant_id = args.tenant_id
    output_file = args.output

    with open("config.json", "r") as f:
        config = json.load(f)
    base_url = config.get('endpoint')
    config['auth']['client_id'] = args.client_id
    config['auth']['client_secret'] = args.client_secret

    api = AuraAPI(base_url, tenant_id, **config)
    _ = api.generate_token_if_expired()

    if args.task == 'clone':
        instances = clone_instances(api, **config['clone'])
        df = pd.DataFrame(instances, index=None)
        df.to_csv(output_file, index=False)

    if args.task == 'create':
        instances = create_instances(api, **config['create'])
        df = pd.DataFrame(instances, index=None)
        df.to_csv(output_file, index=False)

    if args.task == 'pause':
        instances = pause_instances(api, **config['pause'])
        df = pd.DataFrame(instances, index=None)
        print(df)

    if args.task == 'resume':
        instance_ids = collect_instance_ids(config['resume'])
        resumed_instances = list()
        for instance_id in instance_ids:
            data = api.resume(instance_id, wait=False)
            resumed_instances.append(data)
        df = pd.DataFrame(resumed_instances, index=None)
        print(df)

    if args.task == 'delete':
        instance_ids = collect_instance_ids(config['delete'])
        deleted_instances = list()
        for instance_id in instance_ids:
            data = api.delete(instance_id)
            deleted_instances.append(data)
        df = pd.DataFrame(deleted_instances, index=None)
        #df.to_csv(output_file, index=False)
        print(df)

    if args.task == 'list':
        instances = api.list()
        df = pd.DataFrame(instances, index=None)
        print(df)
    
    if args.task == 'snapshots':
        instance_id = config['snapshots']['instance_id']
        snapshot_date = config['snapshots'].get('snapshot_date', '')
        snapshots = api.snapshots(instance_id, snapshot_date=snapshot_date)
        for snapshot in snapshots:
            print(json.dumps(snapshot, indent=2))

    if args.task == 'status':
        instance_ids = collect_instance_ids(config['status'])
        instance_status = list()
        for instance_id in instance_ids:
            status = api.status(instance_id)
            instance_status.append({"instance_id": instance_id, "status":status})
        df = pd.DataFrame(instance_status, index=None)
        print(df)
