from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

from com.vmware.vapi.std_client import DynamicID
from vmware.vapi.vsphere.client import create_vsphere_client
import pprint
import requests
import urllib3

def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    # tag_svc = self.client.tagging.Tag
    # tag_association = self.client.tagging.TagAssociation
    # cat_svc = self.rest_content.tagging.Category
    # cat_info = dict()
    # tags_info = dict()
    # tags = tag_svc.list()
    # cats = cat_svc.list()
    # for tag in tags:
    #         tag_obj = tag_svc.get(tag)
    #         tags_info[tag_obj.id] = dict(
    #             name=tag_obj.name, category=cat_info[tag_obj.category_id])
    summary = virtual_machine._GetMoId()
    pprint.pprint(summary)
    # print("Name       : ", summary.config.name)
    # print("Template   : ", summary.config.template)
    # print("Path       : ", summary.config.vmPathName)
    # print("Guest      : ", summary.config.guestFullName)
    # print("Instance UUID : ", summary.config.instanceUuid)
    # print("Bios UUID     : ", summary.config.uuid)
    # annotation = summary.config.annotation
    # if annotation:
    #     print("Annotation : ", annotation)
    # print("State      : ", summary.runtime.powerState)
    # if summary.guest is not None:
    #     ip_address = summary.guest.ipAddress
    #     tools_version = summary.guest.toolsStatus
    #     if tools_version is not None:
    #         print("VMware-tools: ", tools_version)
    #     else:
    #         print("Vmware-tools: None")
    #     if ip_address:
    #         print("IP         : ", ip_address)
    #     else:
    #         print("IP         : None")
    # if summary.runtime.question is not None:
    #     print("Question  : ", summary.runtime.question.text)
    # print("")


class Host:
    def __init__(self, uuid, hostname, ip_address):
        self.hostname = hostname
        self.ip_address = ip_address
        self.uuid = uuid
        self.tags = {}
        self.tags["address"] = ip_address
        self.tags["uuid"] = uuid

    def add_values(self, key, value):
        print(f"Tag definiton found for {self.hostname}. Key: {key} Value: {value}")
        self.tags[key] = value

    def get_hostname(self):
        return self.hostname

class VMConnection:
    def __init__(self, h, po, nt, u, p):
        try:
            if nt:
                session = requests.session()
                session.verify = False
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                self.connection = connect.SmartConnectNoSSL(host=h,
                                                            user=u,
                                                            pwd=p,
                                                            port=int(po))
                self.client = create_vsphere_client(server=h, username=u, password=p, session=session)
            else:
                session = requests.session()
                self.connection = connect.SmartConnect(host=h,
                                                        user=u,
                                                        pwd=p,
                                                        port=int(po))
                self.client = create_vsphere_client(server=h, username=u, password=p, session=session)
            self.content = self.connection.RetrieveContent()
            self.tag_association = self.client.tagging.TagAssociation
            self.tag_svc = self.client.tagging.Tag
            self.cat_svc = self.client.tagging.Category
            print('Connection Success')
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            return -1
    
    def build_tag_library(self):
        cat_info = dict()
        tags_info = dict()
        tags = self.tag_svc.list()
        cats = self.cat_svc.list()
        for cat in cats:
            cat_obj = self.cat_svc.get(cat)
            cat_info[cat_obj.id] = cat_obj.name
        for tag in tags:
                tag_obj = self.tag_svc.get(tag)
                tags_info[tag_obj.id] = dict(
                    name=tag_obj.name, category=cat_info[tag_obj.category_id])
        self.tags_info = tags_info
        # pprint.pprint(tags_info)
    
    def build_list(self):
        host_list = []
        container = self.content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = self.content.viewManager.CreateContainerView(
            container, viewType, recursive)
        children = containerView.view
        for child in children:
            print('Building definition for host: {}, UUID: {}'.format(child.summary.config.name, child.summary.config.uuid))
            vm_dynamic_id = DynamicID(type='VirtualMachine', id=child._GetMoId())
            if child.summary.guest is not None:
                host = Host(child.summary.config.uuid, child.summary.config.name, child.summary.guest.ipAddress)
                for tag in self.tag_association.list_attached_tags(vm_dynamic_id):
                    host.add_values(self.tags_info[tag]['category'], self.tags_info[tag]['name'])
                host_list.append(host)
            else:
                print('Host is not valid or booted: {}'.format(child.summary.config.name))
        return host_list