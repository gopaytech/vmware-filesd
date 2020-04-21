import os
import click
import pprint
import json
import time
from vmconnection import VMConnection

def prometheus_output(hlist):
        output = []
        for host in hlist:
            x = {
                "targets": [host.hostname],
                "labels": host.tags
            }
            output.append(x)
        return output

def complete_run(hostname, port, notls, username, password, file):
    connection = VMConnection(hostname, port, notls, username, password)
    connection.build_tag_library()
    hlist = connection.build_list()
    output = prometheus_output(hlist)    
    tmppath = "{}/tmp.out".format(os.path.dirname(file))
    if os.path.exists(tmppath):
            os.remove(tmppath)
    with open(tmppath, 'w') as f:
        json.dump(output, f)
    os.rename(tmppath, file)
    print('Run finished: {}'.format(time.ctime()))


@click.command()
@click.option('--hostname', '-h', help='Hostname of the vSphere Server.')
@click.option('--port', '-po', help='Port of the vSphere Server.', default="443")
@click.option('--notls', '-nt', help='Disable TLS Verification.', is_flag=True)
@click.option('--username', '-u', help='Username to connect to the vSphere Server.')
@click.option('--password', '-p', help='Password to connect to the vSphere Server.')
@click.option('--file', '-f', help='The filename to output.')
@click.option('--loop', '-l', help='Set this flag to loop indefinitely.', is_flag=True)
@click.option('--pausetime', '-t', help='How much time you want between runs', default=300)
def collect(hostname, port, notls, username, password, file, loop, pausetime):
    """Collect from a vSphere Server an inventory of systems with tags for consumption by prometheus file discovery."""
    while True:
        print('Run starting: {}'.format(time.ctime()))
        complete_run(hostname, port, notls, username, password, file)
        if loop is True:
            time.sleep(pausetime)
        else:
            break

if __name__ == '__main__':
    collect()