
import os
import logging as log
from argparse import ArgumentParser

from icarus.parse.parcels.parcels import Parcels
from icarus.util.sqlite import SqliteUtil
from icarus.util.config import ConfigUtil

parser = ArgumentParser()
parser.add_argument('--folder', type=str, dest='folder', default='.')
parser.add_argument('--log', type=str, dest='log', default=None)
parser.add_argument('--level', type=str, dest='level', default='info',
    choices=('notset', 'debug', 'info', 'warning', 'error', 'critical'))
args = parser.parse_args()

handlers = []
handlers.append(log.StreamHandler())
if args.log is not None:
    handlers.append(log.FileHandler(args.log, 'w'))
log.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s',
    level=getattr(log, args.level.upper()),
    handlers=handlers)

path = lambda x: os.path.abspath(os.path.join(args.folder, x))
home = path('')
config = ConfigUtil.load_config(path('config.json'))

log.info('Running maricopa parcel parsing tool.')
log.info(f'Loading run data from {home}.')

database = SqliteUtil(path('database.db'))
parcels = Parcels(database)

residence_file = config['network']['parcels']['residence_file']
commerce_file = config['network']['parcels']['commerce_file']
parcel_file = config['network']['parcels']['parcel_file']

if not parcels.ready(residence_file, commerce_file, parcel_file):
    log.error('Dependent data not parsed or generated; see warnings.')
    exit(1)
elif parcels.complete():
    log.warning('Parcel data already parsed. Would you like to replace it? [Y/n]')
    if input().lower() not in ('y', 'yes', 'yeet'):
        log.info('User chose to keep existing parcel data; exiting parsing tool.')
        exit()

try:
    log.info('Starting parcel parsing.')
    parcels.parse(residence_file, commerce_file, parcel_file)
except:
    log.exception('Critical error while parsing parcels; '
        'terminating process and exiting.')
    exit(1)
