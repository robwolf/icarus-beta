
import json

from getpass import getpass
from pkg_resources import resource_filename
from argparse import ArgumentParser

from icarus.input.merger.merger import PlansMerger
from icarus.util.print import Printer as pr

parser = ArgumentParser(prog='PlansMerger',
    description='Merges output plans with vehicular data.')
parser.add_argument('--config', type=str,  dest='config',
    default=resource_filename('icarus', 'input/merger/config.json'),
    help=('Specify a config file location; default is "config.json" in '
        'the current working directory.'))
parser.add_argument('--log', type=str, dest='log',
    help='specify a log file location; by default the log will not be saved',
    default=None)
args = parser.parse_args()

if args.log is not None:
    pr.log(args.log)

with open(args.config) as handle:
    config = json.load(handle)

database = config['database']

database['password'] = getpass(
    f'SQL password for {database["user"]}@localhost: ')

merger = PlansMerger(database)
merger.run(config)
