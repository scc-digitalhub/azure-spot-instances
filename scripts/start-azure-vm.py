#!/usr/bin/env python2
"""
Starts Azure resource manager virtual machines in a subscription.

This Azure Automation runbook runs on Azure to start Azure vms in a subscription.
If no arguments are specified, then all VMs that are currently stopped are started.
If a resource group is specified, then all VMs in the resource group are started.
If a resource group and VM are specified, then that specific VM is started.

Args:
    groupname (-g) - Resource group name.
    vmname (-v) - virtual machine name

    Starts the virtual machines
    Example 1:
            start_azure_vm.py -g <resourcegroupname> -v <vmname>
            start_azure_vm.py -g <resourcegroupname>
            start_azure_vm.py

Changelog:
    2017-09-11 AutomationTeam:
    -initial script

"""
import threading
import getopt
import sys
import azure.mgmt.resource
import azure.mgmt.storage
import azure.mgmt.compute
import automationassets
from slackclient import SlackClient

# Max number of VMs to process at a time
_MAX_THREADS = 20

# Send notification to slack channel
def send_message_slack(msg, apikey, channel):
    slack_token = apikey
    sc = SlackClient(slack_token)

    sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=msg
    )

# Returns a credential based on an Azure Automation RunAs connection dictionary
def get_automation_runas_credential(runas_connection):
    """ Returs a credential that can be used to authenticate against Azure resources """
    from OpenSSL import crypto
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    sp_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM, sp_cert.get_privatekey())

    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    resource = "https://management.core.windows.net/"
    authority_url = ("https://login.microsoftonline.com/" + tenant_id)
    context = adal.AuthenticationContext(authority_url)
    return azure_active_directory.AdalAuthentication(
        lambda: context.acquire_token_with_client_certificate(
            resource,
            application_id,
            pem_pkey,
            thumbprint)
    )

class StartVMThread(threading.Thread):
    """ Thread class to start Azure VM """
    def __init__(self, resource_group, vm_name):
        threading.Thread.__init__(self)
        self.resource_group = resource_group
        self.vm_name = vm_name
    def run(self):
        print "Starting " + self.vm_name + " in resource group " + self.resource_group
        sys.stdout.flush()
        start_vm(self.resource_group, self.vm_name)
        print "Started " + self.vm_name + " in resource group " + self.resource_group
        sys.stdout.flush()

def start_vm(resource_group, vm_name):
    """ Starts a vm in the specified resource group """
    # Start the VM
    vm_start = compute_client.virtual_machines.start(resource_group, vm_name)
    vm_start.wait()

# Process any arguments sent in
resource_group_name = None
vm_name = None

opts, args = getopt.getopt(sys.argv[1:], "g:v:a:c:")
for o, a in opts:
    print o
    print a
    if o == '-g':  # if resource group name is passed with -g option, then use it.
        resource_group_name = a
    elif o == '-v':  # if vm name is passed in with the -v option, then use it.
        vm_name = a
    elif o == '-a':
        apikey = a
    elif o == '-c':
        ch = a

# Check for correct arguments passed in
if vm_name is not None and resource_group_name is None:
    raise ValueError("VM name argument passed in without a resource group specified")

# Authenticate to Azure using the Azure Automation RunAs service principal
automation_runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
azure_credential = get_automation_runas_credential(automation_runas_connection)
subscription_id = str(automation_runas_connection["SubscriptionId"])

resource_client = azure.mgmt.resource.ResourceManagementClient(
    azure_credential,
    subscription_id)

compute_client = azure.mgmt.compute.ComputeManagementClient(
    azure_credential, subscription_id)

# Get list of resource groups
groups = []
if resource_group_name is None and vm_name is None:
    # Get all resource groups
    groups = resource_client.resource_groups.list()
elif resource_group_name is not None and vm_name is None:
    # Get specific resource group
    resource_group = resource_client.resource_groups.get(resource_group_name)
    groups.append(resource_group)
elif resource_group_name is not None and vm_name is not None:
    # Specific resource group and VM name passed in so start the VM
    vm_detail = compute_client.virtual_machines.get(resource_group_name, vm_name, expand='instanceView')
    if vm_detail.instance_view.statuses[1].code == 'PowerState/deallocated' and vm_detail.tags['restart'] == 'true':
        msg = 'Starting VM %s' % vm_name
        print msg
        print apikey
        print ch
        send_message_slack(msg, apikey, ch)
        start_vm(resource_group_name, vm_name)

# List of threads that are used to start VMs in parallel
vm_threads_list = []

# Process any VMs that are in a group
for group in groups:
    vms = compute_client.virtual_machines.list(group.name)
    for vm in vms:
        vm_detail = compute_client.virtual_machines.get(group.name, vm.name, expand='instanceView')
        if vm_detail.instance_view.statuses[1].code == 'PowerState/deallocated' and vm_detail.tags['restart'] == 'true':
            msg = 'Starting VM %s' % vm.name
            print msg
            print apikey
            print ch
            send_message_slack(msg, apikey, ch)
            start_vm_thread = StartVMThread(group.name, vm.name)
            start_vm_thread.start()
            vm_threads_list.append(start_vm_thread)

            if len(vm_threads_list) > _MAX_THREADS:
                for thread in vm_threads_list:
                    thread.join()
                del vm_threads_list[:]

# Wait for all threads to complete
for thread in vm_threads_list:
    thread.join()
print "Finished starting all VMs"
