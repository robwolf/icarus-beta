
import os
import logging as log
from argparse import ArgumentParser

from icarus.export.routes.routes import export_routes
from icarus.util.config import ConfigUtil
from icarus.util.sqlite import SqliteUtil

parser = ArgumentParser()
parser.add_argument('file', type=str,
    help='file path to save the exported routes to')
parser.add_argument('--modes', type=str, nargs='+', dest='modes',
    help='list of modes to export routes for; defualt is all modes',
    default=('walk', 'pt', 'car', 'bike'),
    choices=('walk', 'pt', 'car', 'bike'))
parser.add_argument('--skip-empty', dest='skip', action='store_true', default=False,
    help='skip all legs that do not have routes')

parser.add_argument('--folder', type=str, dest='folder', default='.',
    help='file path to the directory containing Icarus run data; default is the working directory')
parser.add_argument('--log', type=str, dest='log', default=None,
    help='file path to save the process log; by default the log is not saved')
parser.add_argument('--level', type=str, dest='level', default='info',
    help='verbosity level of the process log; default is "info"',
    choices=('notset', 'debug', 'info', 'warning', 'error', 'critical'))
parser.add_argument('--replace', dest='replace', action='store_true', default=False,
    help='automatically replace existing data; do not prompt the user')
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

log.info('Running route export tool.')
log.info(f'Loading run data from {home}.')

database = SqliteUtil(path('database.db'), readonly=True)

try:
    export_routes(database, args.modes, args.file, args.skip)
except:
    log.exception('Critical error while exporting routes:')
    exit(1)

database.close()
