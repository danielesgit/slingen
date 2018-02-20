'''
Created on Oct 31, 2013

@author: nikos
'''

from __future__ import absolute_import
import requests
import json
import time
import traceback
import os
from base64 import b64encode

MEDIATOR_API_VERSION = '1.0'
# maximmum  number of retries to connect to Mediator
MAX_RETRIES = 6


class Client(object):
    MAX_POLL_TRIES = 1200
    POLL_SLEEP_TIME = 6
    
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
    
    def run_experiments(self, experiments):
        payload = {
            "apiVersion": MEDIATOR_API_VERSION,
            "experiments": [exp.to_dict() for exp in experiments],
            "async": "True"
        }
        response = self._send_job_request(payload)
        try:
            response = response.json()
            return response
        except ValueError:
            print 'Cannot parse response as json: %s' % response.text
            raise Exception('BadResponse')
    
    def _send_job_request(self, payload):
        ''' Send the payload to /job and return the job results (if async=True, handle the polling). '''
        response = self._send_request(payload)
        if payload.get('async', 'True') == 'True':
            try:
                response = response.json()
                job_id = response['jobID']
                job_state = response['jobState']
                if job_state != 'SUBMITTED':
                    raise Exception('Failed to submit job. Returned jobState: %s' % job_state)
                
                results_payload = {
                    'jobID': job_id,
                    'apiVersion': MEDIATOR_API_VERSION
                }
                tries = 0
                while tries < self.MAX_POLL_TRIES:
#                     print 'Polling /results for the %d time...' % tries
                    tries += 1
                    response = self._send_request(results_payload, '%s:%d/results' % (self.hostname, self.port))
                    try:
                        response_contents = response.json()
                        job_state = response_contents.get('jobState', 'FINISHED')
                        if job_state != 'PENDING':
                            break
                        time.sleep(self.POLL_SLEEP_TIME)
                    except ValueError:
                        print traceback.format_exc()
                        raise Exception('Cannot json-parse response from /results: %s' % response.text)
                
                if job_state == 'PENDING':
                    raise Exception('Reached max tries of polling and job is still in PENDING state')
                elif job_state != 'FINISHED':
                    raise Exception('Job processing did not finish successfully (jobState: %s)' % job_state)
            except ValueError:
                print traceback.format_exc()
                raise Exception('Cannot json-parse response from /results: %s' % response.text)
        return response      
    
    def _send_request(self, payload, url=None):
        ''' Send the payload to url and return the response object. '''
        if url is None:
            url = '%s:%d/job' % (self.hostname, self.port)
        data=json.dumps(payload)
        headers = {'Content-type': 'application/json'}
        for i in range(MAX_RETRIES):
            try:
                response = requests.post(url, data=data, headers=headers)
                break
            except Exception as e:
                print 'Exception while sending request to Mediator for %d-time:' % (i+1)
                print e
                time.sleep(10)
        return response
    

class Experiment(object):
    def __init__(self, device, config):
        self.device = device
        self.config = config
        self.files = []
    
    def add_file_from_filesystem(self, local_filename, remote_filename=None, is_executable=False):
        if remote_filename is None:
            remote_filename = os.path.split(local_filename)[1]
        file_contents = _get_file_contents(local_filename, is_binary=is_executable)
        if is_executable:
            file_entry = {
                "path": remote_filename,
                "contents": b64encode(file_contents),
                "encoding": "base64",
                "binary": "True",
                "executable": "True"
            }
        else:
            file_entry = {
                "path": remote_filename,
                "contents": file_contents
            }
        self.files.append(file_entry)
    
    def add_folder_from_filesystem(self, folder, prefix_path=None):
        for f in os.listdir(folder):
            full_f = os.path.join(folder, f)
            remote_full_f = f if prefix_path is None else self.device.os.path_join(prefix_path, f)
            if os.path.isfile(full_f):
                self.add_file_from_filesystem(full_f, remote_full_f)
            else:
                self.add_folder_from_filesystem(full_f, remote_full_f)
    
    def add_file_from_string(self, file_contents, remote_filename):
        self.files.append({
            "path": remote_filename,
            "contents": file_contents
        })
        
    def to_dict(self):
        res = { 
            "files": self.files,
            "device": self.device.to_dict(),
        }
        res.update(self.config)
        return res
    

class Device(object):
    def __init__(self, hostname, username, password=None, rsa_key_file=None, rsa_pass='', 
                 port=22, exp_root_folder='/', os='LINUX', affinity=None, devtype='SSH_DEVICE'):
        if password is None and rsa_key_file is None:
            raise ValueError('We need a password or an RSA key to connect to the device through ssh.')
        if affinity is None: affinity = [0] 
        self.hostname = hostname
        self.username = username
        self.password = password
        self.rsa_key = _get_file_contents(rsa_key_file) if rsa_key_file is not None else None
        self.rsa_pass = rsa_pass
        self.port = port
        self.exp_root_folder = exp_root_folder
        self.os = get_os(os)
        self.affinity = affinity
        self.type = devtype
    
    def to_dict(self):
        res = { 
            "type": "SSH_DEVICE",
            "hostname": self.hostname,
            "username": self.username,
            "port": self.port,                                   
            "experimentRootFolder": self.exp_root_folder,       
            "os": self.os.name,
            "affinity": self.affinity
        }
        if self.rsa_key is not None:
            res["rsaKey"] = self.rsa_key
            if self.rsa_pass is not None:
                res["rsaKeyPass"] = self.rsa_pass
        else:
            res["password"] = self.password
        return res    
  
  
class OS(object):
    def __init__(self, name):
        self.name = name
    
    @staticmethod
    def path_join(*args):
        raise NotImplementedError('Should have implemented this!')
        

class Linux(OS):
    separator = '/'
    
    @staticmethod
    def path_join(*args):
        return Linux.separator.join([arg.rstrip(Linux.separator) for arg in args])
       
       
_OS = {
    'LINUX': Linux
}

def get_os(os_name):
    try:
        return _OS[os_name](os_name)
    except KeyError:
        raise ValueError('OS %s not supported!' % os_name)



def _get_file_contents(filename, is_binary=False):
    readmode = 'rb' if is_binary else 'r'
    with open(filename, readmode) as f:
        return f.read()
