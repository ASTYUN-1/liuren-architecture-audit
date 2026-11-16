"""Small SSH helper for the explicitly authorized domestic entry deployment."""
import argparse
import shlex
import subprocess
from pathlib import Path

home=Path.home()
targets={
    'old':['-F','NUL','-i',str(home/'.ssh/old-server-control'),'-p','22223','-o',f'UserKnownHostsFile={home}/Documents/OldServerControl/linux_known_hosts','slope@192.168.100.8'],
    'cn':['aliyun-vps'],
}
parser=argparse.ArgumentParser()
parser.add_argument('target',choices=targets)
parser.add_argument('action',choices=['run','upload','script'])
parser.add_argument('value')
parser.add_argument('destination',nargs='?')
args=parser.parse_args()
ssh=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=12']+targets[args.target]
if args.action=='run':
    result=subprocess.run(ssh+[args.value])
elif args.action=='script':
    result=subprocess.run(ssh+['sudo bash -s'],input=Path(args.value).read_bytes())
else:
    assert args.destination and args.destination.startswith('/tmp/'), 'Stage only to /tmp'
    result=subprocess.run(ssh+['umask 077; cat > '+shlex.quote(args.destination)],input=Path(args.value).read_bytes())
raise SystemExit(result.returncode)
