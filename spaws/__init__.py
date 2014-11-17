import click
import collections
import os
import socket
import subprocess
import sys

from boto import ec2
from spaws.spark_ec2 import stringify_command, ssh_command, get_existing_cluster, wait_for_cluster_state


class Spaws(object):

    def __init__(self, cluster_name, region="us-east-1", user="root", identity_file=None):
        conn = ec2.connect_to_region(region)
        self.opts = collections.namedtuple("Opts", ["user", "identity_file"])(
            user=user,
            identity_file=identity_file
        )
        self.master_nodes, self.slave_nodes = get_existing_cluster(conn, self.opts, cluster_name, die_on_error=False)

    def start(self):
        # cfr. spark_ec2.py
        print "Starting slaves..."
        for inst in self.slave_nodes:
            if inst.state not in ["shutting-down", "terminated"]:
                inst.start()
        print "Starting master..."
        for inst in self.master_nodes:
            if inst.state not in ["shutting-down", "terminated"]:
                inst.start()
        wait_for_cluster_state(
            cluster_instances=(self.master_nodes + self.slave_nodes),
            cluster_state='ssh-ready',
            opts=self.opts
        )

    def stop(self):
        # cfr. spark_ec2.py
        print "Stopping master..."
        for inst in self.master_nodes:
            if inst.state not in ["shutting-down", "terminated"]:
                inst.stop()
        print "Stopping slaves..."
        for inst in self.slave_nodes:
            if inst.state not in ["shutting-down", "terminated"]:
                if inst.spot_instance_request_id:
                    inst.terminate()
                else:
                    inst.stop()

    def run(self, command, directory=None):
        active_master = self.master_nodes[0]
        source_dir = directory or os.getcwd()
        destination_dir = os.path.join("~", "spawsings", socket.gethostname()) + source_dir

        print "Source dir:", source_dir
        print "Destination dir:", destination_dir

        subprocess.check_call(ssh_command(self.opts) + [
            "{0}@{1}".format(self.opts.user, active_master),
            "mkdir", "-p", destination_dir
        ])

        subprocess.check_call([
            'rsync', '-rv',
            '-e', stringify_command(ssh_command(self.opts)),
            "{0}/".format(source_dir),
            "{0}@{1}:{2}".format(self.opts.user, active_master, destination_dir)
        ])

        subprocess.check_call(command)


@click.command()
@click.option("--region", "-r", default="us-east-1", help='EC2 region.')
@click.option("--user", "-u", default="root", help='SSH user.')
@click.option("--identity-file", "-i", default=None, help="SSH identity file.")
@click.option("--directory", "-d", default=None, help='SSH host.')
@click.option("--start-and-stop", "-s", default=False, is_flag=True, help="Start cluster first and stop it afterwards.")
@click.argument("cluster_name", nargs=1)
@click.argument("command", nargs=-1)
def main(region, user, identity_file, directory, start_and_stop, cluster_name, command):
    try:
        spaws = Spaws(cluster_name, region=region, user=user, identity_file=identity_file)
    except Exception as e:
        print >>sys.stderr, e
        sys.exit(1)
    else:
        if start_and_stop:
            spaws.start()
        try:
            spaws.run(command, directory=directory)
        finally:
            if start_and_stop:
                spaws.stop()
