import json
import os
import sys
import re

import configparser

from flask import Blueprint, jsonify , redirect , request

from dark import DarkMap, DarkGateway
from shared_utils import MANAGED_NAM_DICT


##
## VARIABLES
##
PROJECT_ROOT='./'

##
## API CONFIGURATIONS
##

manage_api = Blueprint('update_api', __name__)#, url_prefix='/admin')

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

def update_dnmas(dm:DarkMap):
    dnma_list = []
    n = dm.auth_db.caller.count_dnma()
    for i in range(0,n):
        addr = dm.auth_db.caller.get_dnma_by_index(i)
        v = dm.auth_db.caller.get_dnma(addr)
        
        organizaion = v[1]
        contact = v[2]
        nan = v[3]
        payload_schema = v[-1]
        dnma = {
                'organization':organizaion,
                'contact':contact,
                'nan' : nan,
                'payload_schema' : payload_schema
            }
        dnma_list.append(dnma)

    return dnma_list


@manage_api.route('/update/dnmas', methods=['GET'])
def update_managed_nam_dict():
    # data = request.get_json()  # Dados recebidos via POST
    # app.config['MANAGED_NAM_DICT'].update(data)
    lista = update_dnmas(dark_map)
    if len(lista) == 0:
        resp_code = 500
        resp = jsonify({'status' : 'no pids availabel'},)
    else:
        try:
            dict_dnma = {}
            for dnma in lista:
                dict_dnma[dnma['nan']] = True
            
            MANAGED_NAM_DICT.update(dict_dnma)
            resp_code = 200
            resp = jsonify({'status' : 'managed nam update'},{'nam' : lista},)
        except Exception:
            resp_code = 500
            resp = jsonify({'status' : 'unable to connect to blockchain'},)
    
    return resp, resp_code
    # return jsonify({"message": "Variável atualizada com sucesso!"})