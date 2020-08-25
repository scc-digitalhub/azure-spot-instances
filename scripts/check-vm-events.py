import requests
import json
import time

import os
from slack import WebClient
from slack.errors import SlackApiError

def send_message_slack(msg):
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    try:
        response = client.chat_postMessage(
            channel='#spotvm',
            text=msg)
        assert response["message"]["text"] == msg
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

if __name__ == '__main__':
    send_mes = True
    headers = {'Metadata': 'true'}
    event_url = 'http://169.254.169.254/metadata/scheduledevents?api-version=2019-01-01'
    instance_url = 'http://169.254.169.254/metadata/instance?api-version=2019-06-01'
    try:
        inst_r = requests.get(instance_url, headers=headers, timeout=60)
        inst_r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    inst_metadata = json.loads(inst_r.text)
    vm_name = inst_metadata['compute']['name']
    send_message_slack(f"VM {vm_name} Started")
    while True:
        r = requests.get(event_url, headers=headers)
        events = json.loads(r.text)
        for event in events['Events']:
            print (event)
            if 'Reboot' in event['EventType']:
                print (f"VM {vm_name} will be rebooted in 5m")
                if send_mes:
                    send_mes = False
                    send_message_slack(f"VM {vm_name} will be rebooted in 5m")
            if 'Preempt' in event['EventType']:
                print (f"VM {vm_name} will be evicted in 30s")
                if send_mes:
                    send_mes = False
                    send_message_slack(f"VM {vm_name} will be evicted in 30s")
        time.sleep(1)
        print (time.ctime())
