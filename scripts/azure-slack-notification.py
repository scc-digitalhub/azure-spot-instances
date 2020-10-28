import json
import re
import os
from slack import WebClient
from slack.errors import SlackApiError

# malformed_json = '{"schemaId":"Microsoft.Insights/activityLogs","data":{"status":"Activated","context":{"activityLog":{"authorization":{"action":"Microsoft.Compute/virtualMachines/start/action","scope":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm"},"channels":"Operation","claims":"{\\"aud\\":\\"https://management.core.windows.net/\\",\\"iss\\":\\"https://sts.windows.net/11d1b7a3-5e92-4744-83dc-831a43e1f967/\\",\\"iat\\":\\"1598515195\\",\\"nbf\\":\\"1598515195\\",\\"exp\\":\\"1598519095\\",\\"http://schemas.microsoft.com/claims/authnclassreference\\":\\"1\\",\\"aio\\":\\"ATQAy/8QAAAAB2VcQhk/xzzxEA32G8oEUrkm3txG5IvOSIxg/HJzwLgjWxsttF8vQetaLfpRMnos\\",\\"http://schemas.microsoft.com/claims/authnmethodsreferences\\":\\"pwd\\",\\"appid\\":\\"c44b4083-3bb0-49c1-b47d-974e53cbdf3c\\",\\"appidacr\\":\\"2\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname\\":\\"Fais\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname\\":\\"Fabio\\",\\"groups\\":\\"f3385808-fe4d-4886-9337-6d8af049de2e,4cd463c1-a5a1-4329-a94d-80292c7cff54,efff3c00-c703-45d0-a823-2032567437c7\\",\\"ipaddr\\":\\"78.14.214.43\\",\\"name\\":\\"Fabio Fais\\",\\"http://schemas.microsoft.com/identity/claims/objectidentifier\\":\\"e311a6da-2a4b-401d-a7ad-86d0d2f1c74e\\",\\"onprem_sid\\":\\"S-1-5-21-2103128890-231609770-29589445-29242\\",\\"puid\\":\\"10030000ACC52F1A\\",\\"http://schemas.microsoft.com/identity/claims/scope\\":\\"user_impersonation\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier\\":\\"KfV9JOTlRucj4c4J1WuWxNBCuWXZjQQVjqfSyCFl8UM\\",\\"http://schemas.microsoft.com/identity/claims/tenantid\\":\\"11d1b7a3-5e92-4744-83dc-831a43e1f967\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name\\":\\"ffais@fbk.eu\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn\\":\\"ffais@fbk.eu\\",\\"uti\\":\\"DCeU-rEkmEexjqW9v9c7AQ\\",\\"ver\\":\\"1.0\\",\\"xms_tcdt\\":\\"1399897334\\"}","caller":"ffais@fbk.eu","correlationId":"a77a37c0-98e7-455f-beb3-334c4dfda474","description":"","eventSource":"Administrative","eventTimestamp":"2020-08-27T08:53:40.3067313+00:00","eventDataId":"f764db3d-77d3-4716-961d-a9e732b4247a","level":"Informational","operationName":"Microsoft.Compute/virtualMachines/start/action","operationId":"da7175c3-af71-4d99-b7bd-50451a893cde","properties":{"eventCategory":"Administrative"},"resourceId":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm","resourceGroupName":"TESTSPOTVM","resourceProviderName":"Microsoft.Compute","status":"Succeeded","subStatus":"","subscriptionId":"f8948095-f2ff-4dbd-aa56-d319a3c81cf1","submissionTimestamp":"2020-08-27T08:54:46.0903412+00:00","resourceType":"Microsoft.Compute/virtualMachines"}},"properties":{}}}'

# malformed_json = '{"schemaId":"Microsoft.Insights/activityLogs","data":{"status":"Activated","context":{"activityLog":{"authorization":{"action":"Microsoft.Compute/virtualMachines/start/action","scope":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm"},"channels":"Operation","claims":"{\\"aud\\":\\"https://management.core.windows.net/\\",\\"iss\\":\\"https://sts.windows.net/11d1b7a3-5e92-4744-83dc-831a43e1f967/\\",\\"iat\\":\\"1598518499\\",\\"nbf\\":\\"1598518499\\",\\"exp\\":\\"1598522399\\",\\"http://schemas.microsoft.com/claims/authnclassreference\\":\\"1\\",\\"aio\\":\\"ATQAy/8QAAAAXSWa/tcDYmdOYQKHYIGaX5cNu50MiRpkeUOwNf1oatP/TrBF1S09AEhT5hnLVqvh\\",\\"http://schemas.microsoft.com/claims/authnmethodsreferences\\":\\"pwd\\",\\"appid\\":\\"c44b4083-3bb0-49c1-b47d-974e53cbdf3c\\",\\"appidacr\\":\\"2\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname\\":\\"Fais\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname\\":\\"Fabio\\",\\"groups\\":\\"f3385808-fe4d-4886-9337-6d8af049de2e,4cd463c1-a5a1-4329-a94d-80292c7cff54,efff3c00-c703-45d0-a823-2032567437c7\\",\\"ipaddr\\":\\"78.14.214.43\\",\\"name\\":\\"Fabio Fais\\",\\"http://schemas.microsoft.com/identity/claims/objectidentifier\\":\\"e311a6da-2a4b-401d-a7ad-86d0d2f1c74e\\",\\"onprem_sid\\":\\"S-1-5-21-2103128890-231609770-29589445-29242\\",\\"puid\\":\\"10030000ACC52F1A\\",\\"http://schemas.microsoft.com/identity/claims/scope\\":\\"user_impersonation\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier\\":\\"KfV9JOTlRucj4c4J1WuWxNBCuWXZjQQVjqfSyCFl8UM\\",\\"http://schemas.microsoft.com/identity/claims/tenantid\\":\\"11d1b7a3-5e92-4744-83dc-831a43e1f967\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name\\":\\"ffais@fbk.eu\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn\\":\\"ffais@fbk.eu\\",\\"uti\\":\\"CP4X1rXAu02_dtQT3QVCAQ\\",\\"ver\\":\\"1.0\\",\\"xms_tcdt\\":\\"1399897334\\"}","caller":"ffais@fbk.eu","correlationId":"6f8b46c5-ef44-47cd-a5b5-f7d25db55835","description":"","eventSource":"Administrative","eventTimestamp":"2020-08-27T09:34:15.9722207+00:00","httpRequest":"{\\"clientRequestId\\":\\"aacaf243-8bf2-4f90-923a-18becf82e26e\\",\\"clientIpAddress\\":\\"78.14.214.43\\",\\"method\\":\\"POST\\"}","eventDataId":"db74f061-aacb-47f0-91e9-daf984467580","level":"Informational","operationName":"Microsoft.Compute/virtualMachines/start/action","operationId":"6f8b46c5-ef44-47cd-a5b5-f7d25db55835","properties":{"statusCode":"Accepted","serviceRequestId":"d06bee28-e70e-4bee-9569-c305bb3d9e02","eventCategory":"Administrative"},"resourceId":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm","resourceGroupName":"TESTSPOTVM","resourceProviderName":"Microsoft.Compute","status":"Accepted","subStatus":"Accepted","subscriptionId":"f8948095-f2ff-4dbd-aa56-d319a3c81cf1","submissionTimestamp":"2020-08-27T09:36:07.133957+00:00","resourceType":"Microsoft.Compute/virtualMachines"}},"properties":{}}}'

malformed_json = '{"schemaId":"Microsoft.Insights/activityLogs","data":{"status":"Activated","context":{"activityLog":{"authorization":{"action":"Microsoft.Compute/virtualMachines/deallocate/action","scope":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm"},"channels":"Operation","claims":"{\\"aud\\":\\"https://management.core.windows.net/\\",\\"iss\\":\\"https://sts.windows.net/11d1b7a3-5e92-4744-83dc-831a43e1f967/\\",\\"iat\\":\\"1598525111\\",\\"nbf\\":\\"1598525111\\",\\"exp\\":\\"1598529011\\",\\"http://schemas.microsoft.com/claims/authnclassreference\\":\\"1\\",\\"aio\\":\\"ATQAy/8QAAAAVYc23Ysftw5ZyPj8SzZzedtJDMxHiuyXeD7Qh1XGLEzy3fEMlzY3zxmGYA01VSL7\\",\\"http://schemas.microsoft.com/claims/authnmethodsreferences\\":\\"pwd\\",\\"appid\\":\\"c44b4083-3bb0-49c1-b47d-974e53cbdf3c\\",\\"appidacr\\":\\"2\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname\\":\\"Fais\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname\\":\\"Fabio\\",\\"groups\\":\\"f3385808-fe4d-4886-9337-6d8af049de2e,4cd463c1-a5a1-4329-a94d-80292c7cff54,efff3c00-c703-45d0-a823-2032567437c7\\",\\"ipaddr\\":\\"78.14.214.43\\",\\"name\\":\\"Fabio Fais\\",\\"http://schemas.microsoft.com/identity/claims/objectidentifier\\":\\"e311a6da-2a4b-401d-a7ad-86d0d2f1c74e\\",\\"onprem_sid\\":\\"S-1-5-21-2103128890-231609770-29589445-29242\\",\\"puid\\":\\"10030000ACC52F1A\\",\\"http://schemas.microsoft.com/identity/claims/scope\\":\\"user_impersonation\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier\\":\\"KfV9JOTlRucj4c4J1WuWxNBCuWXZjQQVjqfSyCFl8UM\\",\\"http://schemas.microsoft.com/identity/claims/tenantid\\":\\"11d1b7a3-5e92-4744-83dc-831a43e1f967\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name\\":\\"ffais@fbk.eu\\",\\"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn\\":\\"ffais@fbk.eu\\",\\"uti\\":\\"vBLmN5Z890CkCvtxQfpEAQ\\",\\"ver\\":\\"1.0\\",\\"xms_tcdt\\":\\"1399897334\\"}","caller":"ffais@fbk.eu","correlationId":"2e3e926d-d132-4918-bd6f-b535752977b7","description":"","eventSource":"Administrative","eventTimestamp":"2020-08-27T11:05:45.1135072+00:00","eventDataId":"1c9d3f17-eddb-4edf-9f70-446470fbab47","level":"Informational","operationName":"Microsoft.Compute/virtualMachines/deallocate/action","operationId":"8a3f45b8-eee8-40b0-a554-9e280e6b3fdc","properties":{"eventCategory":"Administrative"},"resourceId":"/subscriptions/f8948095-f2ff-4dbd-aa56-d319a3c81cf1/resourceGroups/TESTSPOTVM/providers/Microsoft.Compute/virtualMachines/TESTSPOTVM-vm","resourceGroupName":"TESTSPOTVM","resourceProviderName":"Microsoft.Compute","status":"Succeeded","subStatus":"","subscriptionId":"f8948095-f2ff-4dbd-aa56-d319a3c81cf1","submissionTimestamp":"2020-08-27T11:06:43.1002166+00:00","resourceType":"Microsoft.Compute/virtualMachines"}},"properties":{}}}'

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
    else:
        context.logger.info("error not supported")
        return context.Response(body='Error not supported',
                headers={},
                content_type='text/plain',
                status_code=405)
