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
            "targets": [host.ip_address],
            "labels": host.tags
        }
        output.append(x)
    return output


def complete_run(hostname, port, notls, username, password, output, filter):
    connection = VMConnection(hostname, port, notls,
                              username, password, filter)
    connection.build_tag_library()
    hlist = connection.build_list()
    promoutput = prometheus_output(hlist)
    tmppath = "{}/tmp.out".format(os.path.dirname(output))
    if os.path.exists(tmppath):
        os.remove(tmppath)
    with open(tmppath, 'w') as f:
        json.dump(promoutput, f)
    os.rename(tmppath, output)
    print('Run finished: {}'.format(time.ctime()))


@click.command()
@click.option('--hostname', '-h', help='Hostname of the vSphere Server.')
@click.option('--port', '-po', help='Port of the vSphere Server.', default="443")
@click.option('--notls', '-nt', help='Disable TLS Verification.', is_flag=True)
@click.option('--username', '-u', help='Username to connect to the vSphere Server.')
@click.option('--password', '-p', help='Password to connect to the vSphere Server.')
@click.option('--output', '-o', help='Output filename.')
@click.option('--loop', '-l', help='Set this flag to loop indefinitely.', is_flag=True)
@click.option('--interval', '-i', help='How much time you want between runs', default=300)
@click.option('--filter', '-f', help='Filter using tags, examples: "{\"environment\": \"production\"}"')
def collect(hostname, port, notls, username, password, output, loop, interval, filter):
    """Collect from a vSphere Server an inventory of systems with tags for consumption by prometheus file discovery."""
    while True:
        print('Run starting: {}'.format(time.ctime()))
        complete_run(hostname, port, notls, username, password, output, filter)
        if loop is True:
            time.sleep(interval)
        else:
            break


if __name__ == '__main__':
    collect()
