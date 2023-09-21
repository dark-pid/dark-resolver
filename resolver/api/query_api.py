import json
import os
import sys
import configparser

from flask import Blueprint, jsonify , redirect

from dark import DarkMap, DarkGateway

##
## VARIABLES
##
PROJECT_ROOT='./'
SUPORTED_PROTOCOLS = ['ark:','doi:']
try:
    MANAGED_NAM_DICT = json.loads(os.environ['MANAGED_NAM_DICT'])
except:
    print("ERROR: MANAGED_NAM_DICT not set or malformed")
    print("resolver shutdown")
    sys.exit()

##
## API CONFIGURATIONS
##

query_api = Blueprint('queries_api', __name__) # Blueprint('core_api', __name__, url_prefix='/core')

##
## configuring dARK GW
##

bc_config = configparser.ConfigParser()
deployed_contracts_config = configparser.ConfigParser()

# bc configuration
bc_config.read(os.path.join(PROJECT_ROOT,'config.ini'))
# deployed contracts config
deployed_contracts_config.read(os.path.join(PROJECT_ROOT,'deployed_contracts.ini'))

# gw
dark_gw = DarkGateway(bc_config,deployed_contracts_config)
dark_map = DarkMap(dark_gw)

###
### methods 
###

# @query_api.get('/get/<dark_id>')
def get_pid(dark_id):
    resp_code = 200
    try:
        dark_pid = None
        if dark_id.startswith('0x'):
            dark_pid = dark_map.get_pid_by_hash(dark_id)
            # dark_object = dpid_db.caller.get(dark_id)
        else:
            dark_pid = dark_map.get_pid_by_ark(dark_id)
        
        resp_dict = dark_pid.to_dict()
        del resp_dict['pid_hash']
        del resp_dict ['responsible']

        if len(dark_pid.externa_pid_list) == 0:
            del resp_dict['externa_pid_list']

        resp = resp_dict
    except ValueError as e:
        #nao existe na bc
        resp = jsonify({'status' : 'Unable to recovery (' + str(dark_id) + ')', 'ablock_chain_error' : str(e)},)
        resp_code = 404
    except Exception as e:
        resp = jsonify({'status' : 'Unable to recovery (' + str(dark_id) + ')', 'block_chain_error' : str(e)},)
        resp_code = 500 # colocar um erro especifico?
    
    return resp, resp_code

def get_by_doi(doi_id):
    resp_code = 200
    try:
        #TODO NEED TO IMPLEMENT A EXTERNAL PID RECOVERY
        pass
    except Exception as e:
        resp = jsonify({'status' : 'Unable to recovery (' + str(doi_id) + ')', 'block_chain_error' : str(e)},)
        resp_code = 500 # colocar um erro especifico?

def call_external_resolver(globla_resolver_addr,pid_id):
    redirect_url =  globla_resolver_addr + pid_id
    return redirect(redirect_url, code=303)

@query_api.route('/get/<protocol>/<path:pid>', methods=['GET'])
def retrieve_ark(protocol,pid):
    # dark_id = nam + str('/') + shoulder
    protocol = protocol.lower()
    pid_id = str(pid)

    if not protocol in SUPORTED_PROTOCOLS:
        # http://127.0.0.1:8000/get/ccn:/99166/w66d60p2
        resp = jsonify({'status' : 'PID [{}] system not suported. dARK resolver is able to handle {}'.format(protocol,SUPORTED_PROTOCOLS)},)
        return resp, 500
    
    if protocol == 'ark:':
        resp, resp_code = get_pid(pid_id)
        globla_resolver_addr = 'https://n2t.net/ark:/'
    if protocol == 'doi:':
        resp, resp_code = get_pid(pid_id)
        globla_resolver_addr = 'https://dx.doi.org/'

    nam = pid_id.split('/')[0]
    if (resp_code == 500 or resp_code == 404) and (MANAGED_NAM_DICT.get(nam) == None):
        #send to global resolver
        # https://n2t.net/ark:/99166/w66d60p2
        # http://127.0.0.1:8000/ark:/99166/w66d60p2
        #
        # https://dx.doi.org/10.1016/j.datak.2023.102180
        # http://127.0.0.1:8000/get/DOI:/10.1016/j.datak.2023.102180
        return call_external_resolver(globla_resolver_addr, pid_id)
    elif (resp_code == 404) and (MANAGED_NAM_DICT.get(nam) != None):
        return jsonify({'status' : 'Unable to recovery (' + protocol +'/'+ str(pid_id) + ')'}), 404
    else:
        return resp, resp_code


