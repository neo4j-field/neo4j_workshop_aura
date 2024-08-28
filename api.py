import os
import json
import time
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')

class AuraAPI:
    def __init__(self, url, tenant_id, token=None, **kwargs):
        self.url = url
        self.token = token
        self.tenant_id = tenant_id
        self.config = kwargs

    def list(self):
        headers = {"Authorization": self.token}
        params = {'tenantId': self.tenant_id}
        response = requests.get(self.url, headers=headers, params=params)
        res = json.loads(response.content)
        instance_list = res.get('data', [])
        if not instance_list:
            logger.info("No instances found: {}".format(instance_list))
        return instance_list

    def snapshots(self, instance_id, snapshot_date=None):
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        _url = os.path.join(self.url, instance_id)
        if snapshot_date:
            _url = os.path.join(_url, 'snapshots?date=' + snapshot_date)
        response = requests.get(_url, headers=headers)
        res = json.loads(response.content)
        if not res.get('data', {}): 
            logger.info("No snapshots, make sure instance is on")
            return 'Unknown'
        logger.info(_url)
        snapshots = res.get('data')
        return snapshots

    def status(self, instance_id):
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        _url = os.path.join(self.url, instance_id)
        response = requests.get(_url, headers=headers)
        res = json.loads(response.content)
        if not res.get('data'):
            logger.info("Unable to retrieve instance Status : {}".format(instance_id))
            return 'Unknown'
        status = res.get('data').get('status')
        return status

    def create(self, params):
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        params.update({
            'tenant_id': self.tenant_id
        })
        response = requests.post(self.url, headers=headers, json=params)
        res = json.loads(response.content)
        instance_details = res.get('data', {})
        errors = res.get('errors', {})
        if not instance_details:
            logger.info("Instance creation not successful: {}".format(errors))
        return instance_details

    def clone(self, source_instance_id, target_instance_id, wait=True, time_out=360, snapshot_id=None):
        params = {
            "source_instance_id": source_instance_id
        }
        if snapshot_id:
            params.update({
                "source_snapshot_id": snapshot_id
            })
        _url = os.path.join(self.url, target_instance_id, 'overwrite')
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        response = requests.post(_url, headers=headers, json=params)
        res = json.loads(response.content)
        instance_details = res.get('data', {})
        if wait:
            status = self.__wait(target_instance_id, status='running', time_out=time_out)
            if status != 'running':
                logger.info("Instance is not cloned yet: {} {}".format(target_instance_id, status))
        return instance_details

    def pause(self, instance_id, wait=False):
        _url = os.path.join(self.url, instance_id, 'pause')
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        response = requests.post(_url, headers=headers)
        res = json.loads(response.content)
        instance_details = res.get('data', {})
        errors = res.get('errors', {})
        if not instance_details:
            logger.info("Pause not successful: {}".format(errors))
        if wait:
            status = self.__wait(instance_id, status='paused')
            if status != 'paused':
                logger.info("Instance is not paused yet: {} {}".format(instance_id, status))
                return dict()
        return instance_details

    def resume(self, instance_id, wait=True):
        _url = os.path.join(self.url, instance_id, 'resume')
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        response = requests.post(_url, headers=headers)
        res = json.loads(response.content)
        instance_details = res.get('data', {})
        if wait:
            status = self.__wait(instance_id, status='running')
            if status != 'running':
                logger.info("Instance is not ready yet: {} {}".format(instance_id, status))
                return dict()
        return instance_details

    def delete(self, instance_id):
        _url = os.path.join(self.url, instance_id)
        headers = {"Content-Type": "application/json", "Authorization": self.token}
        response = requests.delete(_url, headers=headers)
        res = json.loads(response.content)
        instance_details = res.get('data', {})
        errors = res.get('errors', {})
        if not instance_details:
            logger.info("Instance not found or unable to delete: {}".format(errors))
            return dict()
        return instance_details

    def __generate_token(self, url, client_id, client_secret):
        body = {
            "grant_type": "client_credentials"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, auth=(client_id, client_secret), headers=headers, data=body)
        data = json.loads(response.content)
        token = data['access_token']
        return token

    def generate_token_if_expired(self):
        auth_config = self.config['auth']
        auth_url = auth_config.get('endpoint')
        client_id = auth_config.get('client_id')
        client_secret = auth_config.get('client_secret')
        if time.time() - auth_config.get('token_ttl') >= 3599:
            self.token = self.__generate_token(auth_url, client_id, client_secret)
            self.config['auth']['access_token'] = self.token
            self.config['auth']['token_ttl'] = time.time()
            logger.info("Token Generation Successful: {}".format(time.ctime()))
            return True
        logger.info("Token is Valid")
        return False

    def __wait(self, instance_id, status=None, time_out=300):
        start = time.time()
        current_status = self.status(instance_id)
        while current_status != status and time.time() - start <= time_out:
            time.sleep(60)
            current_status = self.status(instance_id)
            logger.info("Waiting: {} {}".format(instance_id, status))
        return current_status
