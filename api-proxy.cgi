#!/usr/bin/python3
"""
CGI proxy for XCRI API
Forwards requests from /iz/xcri/api/* to FastAPI backend on localhost:8001
"""

import sys
import os
import urllib.request
import urllib.parse
from http import client as http_client

# FastAPI backend
API_HOST = "127.0.0.1"
API_PORT = 8001

def main():
    # Get the path after /iz/xcri/api/
    path_info = os.environ.get('PATH_INFO', '')
    query_string = os.environ.get('QUERY_STRING', '')
    request_method = os.environ.get('REQUEST_METHOD', 'GET')
    
    # Build backend URL
    backend_url = f"http://{API_HOST}:{API_PORT}{path_info}"
    if query_string:
        backend_url += f"?{query_string}"
    
    try:
        # Forward request to backend
        if request_method == 'POST':
            content_length = int(os.environ.get('CONTENT_LENGTH', 0))
            post_data = sys.stdin.buffer.read(content_length) if content_length > 0 else None
            req = urllib.request.Request(backend_url, data=post_data, method='POST')
        else:
            req = urllib.request.Request(backend_url, method=request_method)
        
        # Add Content-Type header explicitly (CGI provides this as CONTENT_TYPE, not HTTP_CONTENT_TYPE)
        content_type = os.environ.get('CONTENT_TYPE')
        if content_type:
            req.add_header('Content-Type', content_type)
        
        # Add other HTTP headers
        for key, value in os.environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                if header_name not in ['Host', 'Connection']:
                    req.add_header(header_name, value)
        
        # Make request
        with urllib.request.urlopen(req) as response:
            # Output headers (with immediate flush)
            print(f"Status: {response.status}", flush=True)
            for header, value in response.getheaders():
                if header.lower() not in ['server', 'date', 'connection']:
                    print(f"{header}: {value}", flush=True)
            print(flush=True)  # End headers
            
            # Flush text stdout before binary write
            sys.stdout.flush()
            
            # Output body
            sys.stdout.buffer.write(response.read())
            sys.stdout.buffer.flush()
            
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}", flush=True)
        print("Content-Type: application/json", flush=True)
        print(flush=True)
        sys.stdout.flush()
        sys.stdout.buffer.write(e.read())
        sys.stdout.buffer.flush()
    except Exception as e:
        print("Status: 500", flush=True)
        print("Content-Type: application/json", flush=True)
        print(flush=True)
        sys.stdout.flush()
        error_msg = f'{{"error": "Proxy error: {str(e)}"}}'
        sys.stdout.buffer.write(error_msg.encode('utf-8'))
        sys.stdout.buffer.flush()

if __name__ == '__main__':
    main()
