import json
import re
import os
from slack import WebClient
from slack.errors import SlackApiError

def send_message_slack(msg, ch):
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    try:
        response = client.chat_postMessage(
            channel=ch,
            text=msg)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def fix_json (malformed_json):
    to_delete = ['("claims".*)"caller"', '("httpRequest".*)"resourceId"' ]
    malformed_json = str(malformed_json).strip("b").strip("'")

    for to_del in to_delete:
        result = re.search(to_del, malformed_json)
        if result:
            malformed_json = malformed_json.replace(result.group(1), '')
    valid_json = malformed_json
    return valid_json

def handler(context, event):
    if (event.method == 'POST'):
        context.logger.info(event.body)
        valid_json = fix_json(event.body)
        context.logger.info(valid_json)
        body = json.loads(valid_json)
        operation_name = re.search('virtualMachines/(.*)/action', body['data']['context']['activityLog']['authorization']['action']).group(1)
        print(operation_name)
        if operation_name == "start":
            operation_type = "Started"
        elif operation_name == "deallocate":
            operation_type = "Stopped"
        user_mail = body['data']['context']['activityLog']['caller']
        print (user_mail)
        vm_name = re.search('virtualMachines/(.*)', body['data']['context']['activityLog']['resourceId']).group(1)
        print (vm_name)
        if body['data']['context']['activityLog']['status'] == "Accepted":
            if body['data']['context']['activityLog']['resourceGroupName'] == "MobS":
                send_message_slack(f"VM {vm_name} was {operation_type} by {user_mail}", "#spotvm")
            elif body['data']['context']['activityLog']['resourceGroupName'] == "DH":
                send_message_slack(f"VM {vm_name} was {operation_type} by {user_mail}", "#dhspotvm")
            elif body['data']['context']['activityLog']['resourceGroupName'] == "NPL":
                send_message_slack(f"VM {vm_name} was {operation_type} by {user_mail}", "#nplspotvm")
    else:
        context.logger.info("error not supported")
        return context.Response(body='Error not supported',
                headers={},
                content_type='text/plain',
                status_code=405)
