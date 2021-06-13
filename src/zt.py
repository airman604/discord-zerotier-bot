#!/usr/bin/env python3
import requests
import logging
import string

from requests import status_codes

ZT_BASE_URL = "https://my.zerotier.com/api"

def _validate_hex(input: str):
    return all(c in string.hexdigits for c in input)

class ZeroTier:
    def __init__(self, zt_network, zt_token):
        self.zt_network = zt_network
        self.api_token = zt_token

        self._get_network()

    def _get_network(self):
        if not _validate_hex(self.zt_network):
            raise Exception(f"Invalid network ID format")

        # https://my.zerotier.com/api/network/{networkID}
        url = f"{ZT_BASE_URL}/network/{self.zt_network}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception(f"Could not initialize ZeroTier client: [{r.status_code}] {r.text}")

        return r.json()

    def get_member(self, member_id):
        if not _validate_hex(member_id):
            return None

        # https://my.zerotier.com/api/network/{networkID}/member/{memberID}
        url = f"{ZT_BASE_URL}/network/{self.zt_network}/member/{member_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        r = requests.get(url, headers=headers)
        if not r.ok:
            return None
            
        return r.json()

    def authorize_member(self, member_id, name):
        if not _validate_hex(member_id):
            return False
            
        url = f"{ZT_BASE_URL}/network/{self.zt_network}/member/{member_id}"
        # url = f"http://68.183.205.119/{ZT_BASE_URL}/network/{self.zt_network}/member/{member_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        data = {
            "name": name,
            "config": {
                "authorized": True
            }
        }
        
        r = requests.post(url, headers=headers, json=data)
        if r.ok:
            return True
        else:
            logging.error(f"Cannot authorize a ZeroTier member: [{r.status_code}] {r.text}")
        
        return False
