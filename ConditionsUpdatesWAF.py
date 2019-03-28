import boto3
import optparse
import re
import sys

def get_parameters():
    p = optparse.OptionParser()
    p.add_option('--filename', '-f', default="waf_stage_whitelisted_ips.txt",help="file name from which updations are done")
    p.add_option('--action', '-a', default="INSERT",help="action to take for waf --options [INSERT(default) / DELETE]")
    p.add_option('--name','-n', default="Kong",help="which group you want to update")
    p.add_option('--type','-t',default="IP",help="operations to perform --options [IP(default) / URI / Test]")
    options, arguments = p.parse_args()
    arguments_dictionary ={ "filename":options.filename,
                            "action":options.action,
                            "name":options.name,
                            "type":options.type
                        }
    return arguments_dictionary

def get_waf_client():
    client = boto3.client('waf-regional', region_name='us-east-1')
    return client

def get_values_from_file(filename):
    value_list = [line.rstrip() for line in open(filename)]
    updated_value_list = []
    for line in value_list:
        pattern = re.compile("#")
        status = pattern.search(str(line))
        if status == None:
            updated_value_list.append(str(line))
    return updated_value_list

def get_waf_change_token(waf_client):
    response = waf_client.get_change_token()
    return response.get("ChangeToken")


def get_all_ip_set_id(waf_client):
    response = waf_client.list_ip_sets()
    return response.get('IPSets')

def get_all_uri_set_id(waf_client):
    response = waf_client.list_byte_match_sets()
    return response.get('ByteMatchSets')


def get_desired_ip_set_group_id(ip_set_list,name):
    for ip_set in ip_set_list:
        pattern = re.compile(name+"*",re.IGNORECASE)
        result = pattern.match(ip_set.get("Name").strip())
        if result!=None:
            return ip_set.get("IPSetId")


def get_desired_uri_set_group_id(uri_set_list,name):
    for uri_set in uri_set_list:
        pattern = re.compile(name+"*",re.IGNORECASE)
        result = pattern.match(uri_set.get("Name").strip())
        if result!=None:
            return uri_set.get("ByteMatchSetId")

def check_existing_ip_address(ip_list,ip_set_id,waf_client):
    response = waf_client.get_ip_set(IPSetId=str(ip_set_id))
    ip_addrss_object_list = response.get("IPSet").get("IPSetDescriptors")
    current_ip_list = []
    for ip_address_object in ip_addrss_object_list:
        current_ip_list.append(str(ip_address_object.get("Value")))
    updated_ip_list = list (set(ip_list) - set(current_ip_list))
    return updated_ip_list


def check_existing_uri_address(uri_list,uri_set_id,waf_client):
    response = waf_client.get_byte_match_set(ByteMatchSetId=str(uri_set_id))
    #print(response)
    uri_addrss_object_list = response.get("ByteMatchSet").get("ByteMatchTuples")
    current_uri_list = []
    for uri_addrss_object in uri_addrss_object_list:
        a = str(uri_addrss_object.get("TargetString"))
        p = a.replace("b'","").replace("'","")
        current_uri_list.append(p)
    updated_uri_list = list (set(uri_list) - set(current_uri_list))
    return updated_uri_list



def format_ip_list_for_update(ip_list,action):
    update_list = []
    for ip in ip_list:
        data = { "Action":str(action).upper(),"IPSetDescriptor":{"Type":"IPV4","Value":str(ip)}}
        update_list.append(data)
    return update_list


def format_uri_list_for_update(uri_list,action):
    update_list = []
    for uri in uri_list:
        data = {
                'Action':str(action).upper(),
                    'ByteMatchTuple': {
                        'FieldToMatch': {
                            'Type': 'URI'
                        },
                    'TargetString': str(uri),
                    'TextTransformation': 'NONE',
                    'PositionalConstraint': 'STARTS_WITH'
                    }
            }
        update_list.append(data)
    return update_list




def update_ip_set(updates_object,waf_client,ip_set_id,token):
    try:
        response = waf_client.update_ip_set(IPSetId=str(ip_set_id),ChangeToken=str(token),Updates=updates_object)
        print ("updated successfully")
    except:
        print ("Nothing to Update")
        print ("Unexpected error:", sys.exc_info()[0])
        pass

def update_uri_set(updates_object,waf_client,uri_set_id,token):
    try:
        response = waf_client.update_byte_match_set(ByteMatchSetId=str(uri_set_id),ChangeToken=str(token),Updates=updates_object)
        print ("updated successfully")
    except:
        print ("Nothing to Update")
        print ("Unexpected error:", sys.exc_info()[0])
        pass



#-------------------------------------------------------------------------------------------------------------------



def main():
    parameters = get_parameters()
    if parameters.get("type") == "IP":
        waf_client = get_waf_client()
        ip_list = get_values_from_file(parameters.get("filename"))
        print(ip_list)
        IpSetsList = get_all_ip_set_id(waf_client)
        print(IpSetsList)
        ip_set_id = get_desired_ip_set_group_id(IpSetsList,parameters.get("name"))
        print(ip_set_id)
        ips_to_update = check_existing_ip_address(ip_list,ip_set_id,waf_client)
        print ("Updateing following Ip's "+str(ips_to_update))
        updates_object = format_ip_list_for_update(ips_to_update,parameters.get("action"))
        #print(updates_object)
        token = get_waf_change_token(waf_client)
        update_ip_set(updates_object,waf_client,ip_set_id,token)

    if parameters.get("type") == "URI":
        waf_client = get_waf_client()
        uri_list = get_values_from_file(parameters.get("filename"))
        print(uri_list)
        URISetsList = get_all_uri_set_id(waf_client)
        print(URISetsList)
        uri_set_id = get_desired_uri_set_group_id(URISetsList,parameters.get("name"))
        print(uri_set_id)
        uris_to_update = check_existing_uri_address(uri_list,uri_set_id,waf_client)
        print ("Updateing following Uris's "+str(uris_to_update))
        updates_object = format_uri_list_for_update(uris_to_update,parameters.get("action"))
        print(updates_object)
        token = get_waf_change_token(waf_client)
        update_uri_set(updates_object,waf_client,uri_set_id,token)



if __name__ == '__main__':
    main()