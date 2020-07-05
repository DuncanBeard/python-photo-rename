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
    parser.add_argument('--dirs', dest='put_in_directories', action='store_true', help="Whether to put the renamed photos in directories.")
    parser.add_argument('--no-dirs', dest='put_in_directories', action='store_false', help="Whether to put the renamed photos in directories.")
    parser.set_defaults(put_in_directories=False)
    parser.add_argument('--root-dir', dest='root_dir', help="Where to store the renamed photos")

    args = parser.parse_args()
    # print(args)
    # sys.exit(0)

    file = args.file # sys.argv[1]
    if os.access(file, os.R_OK):
        # Disabled while broken
        # fix_file_creation_time(file)
        if os.access(file, os.W_OK):
            path, filename = os.path.split(file)
            if args.root_dir:
                # Create the provided root directory if it does not exist
                if not os.path.isdir(args.root_dir):
                    os.mkdir(args.root_dir)
                path = args.root_dir
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
            if args.put_in_directories:
                # Get when the file was modified
                mtime = os.path.getmtime(file)
                mtime_datetime = datetime.datetime.fromtimestamp(mtime)
                year = str(mtime_datetime.year)
                month = str(mtime_datetime.month).zfill(2)
                day = str(mtime_datetime.day)

                # Check if the year directory exists
                if not os.path.isdir(os.path.join(path, year)):
                    os.mkdir(os.path.join(path, year))
                if not os.path.isdir(os.path.join(path, year, month)):
                    os.mkdir(os.path.join(path, year, month))
                # logger.debug('%s/%s/%s', year, month, new_name)
                new_name = os.path.join(year, month, new_name)

            new_path = os.path.join(path, new_name)
            dup_count = 0
            path_found = False
            while not path_found:
                try:
                    file_and_path, ext = new_path.rsplit('.', 1)
                except ValueError:
                    logger.debug('Found a file with no extension: %s', new_path)
                    file_and_path = new_path
                    ext = False
                if ext:
                    if dup_count > 0:
                        potential_path = file_and_path + '_' + str(dup_count) + '.' + ext
                    else:
                        potential_path = file_and_path + '.' + ext
                else:
                    if dup_count > 0:
                        potential_path = file_and_path + '_' + str(dup_count)
                    else:
                        potential_path = file_and_path
                logger.debug('Trying %s...', potential_path)
                if os.path.isfile(potential_path):
                    dup_count = dup_count + 1
                    logger.warning('%s already exists, incrementing...', new_path)
                else:
                    logger.debug('Found a good path: %s', potential_path)
                    path_found = True
            logger.debug('Renaming %s to %s', file, potential_path)
            os.rename(file, potential_path)

    else:
        print('Unable to access file: %s' % file)
        sys.exit(2)