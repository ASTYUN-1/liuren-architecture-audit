"""Read-only HTTPS probe with a fixed destination and full TLS name validation.

Does not change DNS, proxies, certificate trust, or the user's network settings.
"""
import argparse
import concurrent.futures
import http.client
import json
import socket
import ssl
import time

parser = argparse.ArgumentParser()
parser.add_argument('--ip', default='45.135.119.76')
parser.add_argument('--host', default='wen.qiluhub.com')
args = parser.parse_args()


def probe(path):
    started = time.monotonic()
    try:
        context = ssl.create_default_context()
        with socket.create_connection((args.ip, 443), timeout=10) as tcp:
            connected = time.monotonic()
            with context.wrap_socket(tcp, server_hostname=args.host) as tls:
                secured = time.monotonic()
                tls.sendall((f'GET {path} HTTP/1.1\r\nHost: {args.host}\r\n'
                             'Connection: close\r\nUser-Agent: Wenheng-Readiness-Probe/1\r\n\r\n').encode())
                response = http.client.HTTPResponse(tls)
                response.begin()
                first = time.monotonic()
                content = response.read(2_000_000)
                result = {'path': path, 'ip': tls.getpeername()[0], 'status': response.status,
                          'tls': tls.version(), 'certificateVerified': True,
                          'tcpSeconds': round(connected-started, 3),
                          'tlsSeconds': round(secured-started, 3),
                          'firstByteSeconds': round(first-started, 3),
                          'totalSeconds': round(time.monotonic()-started, 3),
                          'bytes': len(content)}
                if path == '/api/status' and response.status == 200:
                    result['publicService'] = json.loads(content)
                if path == '/':
                    result['hasWenhengTitle'] = '问衡' in content.decode('utf-8', errors='replace')
                return result
    except Exception as error:
        return {'path': path, 'ip': args.ip, 'error': str(error),
                'totalSeconds': round(time.monotonic()-started, 3)}


with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(probe, ['/', '/api/status', '/chart']))
print(json.dumps({'host': args.host, 'results': results}, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(r.get('status') == 200 for r in results) else 1)
