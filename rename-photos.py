#!/usr/bin/python3

import os
import datetime
import logging
import sys
import subprocess
import time
import argparse

# From Hitchhiker's Guide to Python
try:
    from logging import NullHandler
except ImportError:
    class NullHandler (logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(NullHandler())
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def fix_file_creation_time(filepath):
    """ If the file's creation time is after its modified time,
    the creation time will be set back to the modified time."""
    mtime = os.path.getmtime(filepath)
    mtime_datetime = datetime.datetime.fromtimestamp(mtime)
    created_time = os.stat(filepath).st_birthtime
    created_time_datetime = datetime.datetime.fromtimestamp(created_time)

    # TODO: Figure out how to update the macOS creation times to be the same as the modified times
    # Can be done with `SetFile -d "$(GetFileInfo -m test.foo)" test.foo`
    if mtime_datetime < created_time_datetime:
        logger.debug('%s had a creation date of %s and modification date of %s, updating creation date to %s',
                     filepath, created_time_datetime, mtime_datetime, mtime_datetime)
        # os.utime(filepath, (mtime, mtime))
    else:
        logger.debug('%s looks okay.', filepath)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Foo bar baz')

    parser.add_argument("file", help="The file to be renamed")

    parser.add_argument('--no-preserve-filenames', dest='preserve_filenames', action='store_false')
    parser.add_argument('--preserve-filenames', dest='preserve_filenames', action='store_true')
    parser.set_defaults(preserve_filenames=True)

    args = parser.parse_args()
    # print(args)
    # sys.exit(0)

    file = args.file # sys.argv[1]
    if os.access(file, os.R_OK):
        fix_file_creation_time(file)
        if os.access(file, os.W_OK):
            path, filename = os.path.split(file)
            try:
                name, ext = filename.rsplit(".", 1)
            except ValueError:
                name = filename
                ext = False
            date_string = datetime.datetime.utcfromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H.%M.%S')
            if args.preserve_filenames:

                new_name = ' '.join([date_string, name])
            else:
                new_name = date_string
            if ext:
                new_name = '.'.join([new_name, ext])
            logger.debug('Renaming %s to %s', filename, new_name)
            os.rename(file, os.path.join(path, new_name))

    else:
        print('Unable to access file: %s' % file)
        sys.exit(2)