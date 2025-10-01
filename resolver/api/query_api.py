"""
API for querying PIDs (Persistent Identifiers) in the dARK resolver system.

This module provides endpoints for resolving ARK and DOI identifiers,
including metadata retrieval and redirection to external URLs.
"""

import configparser
import os
import re
from typing import Tuple, Dict, Any, Optional

from flask import Blueprint, jsonify, redirect, request

from dark import DarkMap, DarkGateway
from shared_utils import MANAGED_NAM_DICT


class QueryAPIConfig:
    """Configuration constants for the Query API."""
    
    PROJECT_ROOT = './'
    SUPPORTED_PROTOCOLS = ['ark', 'doi']
    GLOBAL_RESOLVERS = {
        'ark': 'https://n2t.net/ark:/',
        'doi': 'https://dx.doi.org/'
    }
    
    # HTTP Status Codes
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    SEE_OTHER = 303


class PIDResolver:
    """Handler for PID resolution operations."""
    
    def __init__(self):
        """Initialize the PID resolver with blockchain configuration."""
        self.dark_gw = self._initialize_gateway()
        self.dark_map = DarkMap(self.dark_gw)
    
    def _initialize_gateway(self) -> DarkGateway:
        """Initialize and configure the dARK Gateway."""
        bc_config = configparser.ConfigParser()
        deployed_contracts_config = configparser.ConfigParser()
        
        bc_config.read(os.path.join(QueryAPIConfig.PROJECT_ROOT, 'config.ini'))
        deployed_contracts_config.read(
            os.path.join(QueryAPIConfig.PROJECT_ROOT, 'deployed_contracts.ini')
        )
        
        return DarkGateway(bc_config, deployed_contracts_config)
    
    def get_pid_data(self, dark_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Retrieve PID data from the blockchain.
        
        Args:
            dark_id: The PID identifier (hash or ARK format)
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            dark_pid = self._fetch_pid(dark_id)
            resp_dict = self._format_pid_response(dark_pid)
            
            if self._is_draft_pid(dark_pid):
                return self._create_error_response(
                    dark_id, 'PID is a draft', QueryAPIConfig.NOT_FOUND
                )
            
            return resp_dict, QueryAPIConfig.OK
            
        except ValueError as e:
            return self._create_error_response(
                dark_id, f'Blockchain error: {str(e)}', QueryAPIConfig.NOT_FOUND
            )
        except Exception as e:
            return self._create_error_response(
                dark_id, f'Internal error: {str(e)}', QueryAPIConfig.INTERNAL_ERROR
            )
    
    def _fetch_pid(self, dark_id: str):
        """Fetch PID from blockchain by hash or ARK."""
        if dark_id.startswith('0x'):
            return self.dark_map.get_pid_by_hash(dark_id)
        return self.dark_map.get_pid_by_ark(dark_id)
    
    def _format_pid_response(self, dark_pid) -> Dict[str, Any]:
        """Format PID object for API response."""
        resp_dict = dark_pid.to_dict()
        
        # Remove sensitive/unnecessary fields
        resp_dict.pop('pid_hash', None)
        
        # Clean up empty external PID list
        if hasattr(dark_pid, 'external_pid_list') and len(dark_pid.external_pid_list) == 0:
            resp_dict.pop('external_pid_list', None)
        
        return resp_dict
    
    def _is_draft_pid(self, dark_pid) -> bool:
        """Check if PID is a draft (has no external URL)."""
        return len(getattr(dark_pid, 'external_url', '')) == 0
    
    def _create_error_response(self, pid_id: str, reason: str, status_code: int) -> Tuple[Dict[str, Any], int]:
        """Create standardized error response."""
        return {
            'status': f'Unable to recover ({pid_id})',
            'reason': reason
        }, status_code


class ProtocolHandler:
    """Handler for protocol-specific operations."""
    
    def __init__(self, resolver: PIDResolver):
        self.resolver = resolver
    
    def is_protocol_supported(self, protocol: str) -> bool:
        """Check if protocol is supported."""
        return protocol.lower() in QueryAPIConfig.SUPPORTED_PROTOCOLS
    
    def validate_protocol(self, protocol: str) -> Tuple[Optional[Dict[str, Any]], Optional[int]]:
        """Validate protocol support."""
        if not self.is_protocol_supported(protocol):
            error_msg = (
                f'PID [{protocol}] system not supported. '
                f'dARK resolver supports {QueryAPIConfig.SUPPORTED_PROTOCOLS}'
            )
            return {'status': error_msg}, QueryAPIConfig.INTERNAL_ERROR
        return None, None
    
    def should_forward_to_global_resolver(self, status_code: int, nam: str) -> bool:
        """Determine if request should be forwarded to global resolver."""
        return (
            status_code in [QueryAPIConfig.INTERNAL_ERROR, QueryAPIConfig.NOT_FOUND] 
            and MANAGED_NAM_DICT.get(nam) is None
        )
    
    def create_redirect_response(self, url: str, pid_id: str = '') -> Tuple[Any, int]:
        """Create redirect response."""
        redirect_url = url + pid_id
        return redirect(redirect_url, code=QueryAPIConfig.SEE_OTHER), QueryAPIConfig.SEE_OTHER


# Initialize components
resolver = PIDResolver()
protocol_handler = ProtocolHandler(resolver)

# Create Flask Blueprint
query_api = Blueprint('queries_api', __name__)


def extract_nam_from_pid(pid_id: str) -> str:
    """Extract NAM (Name Authority Module) from PID."""
    return pid_id.split('/')[0]


def handle_pid_resolution(protocol: str, pid: str, return_metadata: bool = False) -> Tuple[Any, int]:
    """
    Handle PID resolution with protocol validation and routing.
    
    Args:
        protocol: The protocol (ark, doi)
        pid: The PID identifier
        return_metadata: If True, return metadata instead of redirecting
        
    Returns:
        Tuple of (response, status_code)
    """
    protocol = protocol.lower()
    
    # Validate protocol
    error_response, error_code = protocol_handler.validate_protocol(protocol)
    if error_response:
        return jsonify(error_response), error_code
    
    # Get PID data
    resp, resp_code = resolver.get_pid_data(pid)
    nam = extract_nam_from_pid(pid)
    
    # Handle routing logic
    if protocol_handler.should_forward_to_global_resolver(resp_code, nam):
        global_resolver = QueryAPIConfig.GLOBAL_RESOLVERS[protocol]
        return protocol_handler.create_redirect_response(global_resolver, pid)
    
    elif resp_code == QueryAPIConfig.NOT_FOUND and MANAGED_NAM_DICT.get(nam) is not None:
        error_msg = f'Unable to recover ({protocol}/{pid})'
        return jsonify({'status': error_msg}), QueryAPIConfig.NOT_FOUND
    
    else:
        if return_metadata:
            return jsonify(resp) if isinstance(resp, dict) else resp, resp_code
        else:
            # Redirect to external URL
            external_url = resp.get('external_url', '') if isinstance(resp, dict) else ''
            return protocol_handler.create_redirect_response(external_url)



def _handle_route_logic(protocol: str, pid: str) -> Tuple[Any, int]:
    """
    Common logic for handling PID route requests.
    
    Args:
        protocol: The protocol (ark, doi)
        pid: The PID identifier
        
    Returns:
        Tuple of (response, status_code)
    """
    if request.full_path.endswith('?info'):
        return handle_pid_resolution(protocol, pid, return_metadata=True)
    
    elif re.search(r'\?[a-zA-Z0-9]', request.full_path):
        cmd = request.full_path.split('?')[-1]
        error_msg = f'Operation [{cmd}] not implemented'
        return jsonify({'status': 'error', 'detail': error_msg}), QueryAPIConfig.INTERNAL_ERROR
    
    else:
        return handle_pid_resolution(protocol, pid, return_metadata=False)


@query_api.route('/<protocol>:/<path:pid>', methods=['GET'])
def handle_route_query(protocol: str, pid: str) -> Tuple[Any, int]:
    """
    Main route handler for PID queries using slash format (e.g., ark:/87559/0013000004w09).
    
    Supports:
    - Direct resolution: /<protocol>/<pid>
    - Metadata query: /<protocol>/<pid>?info
    - Other commands: /<protocol>/<pid>?<command>
    """
    return _handle_route_logic(protocol, pid)


@query_api.route('/<protocol>:<path:pid>', methods=['GET'])
def handle_route_query_new_protocol_format(protocol: str, pid: str) -> Tuple[Any, int]:
    """
    Main route handler for PID queries using slash format (e.g., ark:/87559/0013000004w09).
    
    Supports:
    - Direct resolution: /<protocol>/<pid>
    - Metadata query: /<protocol>/<pid>?info
    - Other commands: /<protocol>/<pid>?<command>
    """
    return _handle_route_logic(protocol, pid)


