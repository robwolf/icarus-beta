
import os
import logging as log
from argparse import ArgumentParser
from icarus.output.parse import Parsing
from icarus.util.sqlite import SqliteUtil
from icarus.util.config import ConfigUtil

def run(database):
    parsing = Parsing(database)
    # if not parsing.complete():
    parsing.parse('output/output_plans.xml.gz', 'output/output_events.xml.gz')


parser = ArgumentParser()
parser.add_argument('--folder', type=str, dest='folder', default='.')
parser.add_argument('--log', type=str, dest='log', default=None)
parser.add_argument('--level', type=str, dest='level', default='info',
    choices=('notset', 'debug', 'info', 'warning', 'error', 'critical'))
# TODO add argument parsing
args = parser.parse_args()

handlers = []
handlers.append(log.StreamHandler())
if args.log is not None:
    handlers.append(log.FileHandler(args.log, 'w'))
log.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s',
    level=getattr(log, args.level.upper()),
    handlers=handlers)

path = lambda x: os.path.join(args.folder, x)
config = ConfigUtil.load_config(path('config.json'))
database = SqliteUtil(path('database.db'))

run(database)