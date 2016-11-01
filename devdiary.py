#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import logging
import argparse
import pdb
import datetime
import calendar

DEVDIARY_VERSION = 'DevDiary v0.1'

class PathExists(Exception):
    pass

class TF:

    RESET        = '\x1b[m'
    BOLD         = '\x1b[1m'
    RED          = '\x1b[31m'
    GREEN        = '\x1b[32m'
    YELLOW       = '\x1b[33m'
    BLUE         = '\x1b[34m'
    MAGENTA      = '\x1b[35m'
    CYAN         = '\x1b[36m'
    BOLD_RED     = '\x1b[1;31m'
    BOLD_GREEN   = '\x1b[1;32m'
    BOLD_YELLOW  = '\x1b[1;33m'
    BOLD_BLUE    = '\x1b[1;34m'
    BOLD_MAGENTA = '\x1b[1;35m'
    BOLD_CYAN    = '\x1b[1;36m'
    BG_RED       = '\x1b[41m'
    BG_GREEN     = '\x1b[42m'
    BG_YELLOW    = '\x1b[43m'
    BG_BLUE      = '\x1b[44m'
    BG_MAGENTA   = '\x1b[45m'
    BG_CYAN      = '\x1b[46m'

    @classmethod
    def str(cls, color, msg):
        return color + msg + TF.RESET

class DevDiary:

    def __init__(self, devdiary_path, logger):
        self.devdiary_path = devdiary_path if devdiary_path[-1] != '/' else devdiary_path[:-1]
        self.diary_path = '{0}/diaries'.format(self.devdiary_path)
        self.logger = logger

        # Create the settingns_path dir if it doesn't already exist
        if not os.path.exists(self.devdiary_path):
            self.logger.debug('creating directory')
            os.makedirs(self.devdiary_path)

        # Make sure the diary_path exists
        if not os.path.exists(self.diary_path):
            os.makedirs(self.diary_path)
        else:
            if not os.path.isdir(self.diary_path):
                self.logger.fatal('{} is not a directory'.format())

    def query(self):
        """Query whether there is an entry for the day or not
        """
        now = datetime.date.today()
        path = '{0}/{1:04d}/{2:02d}/{3:02d}.md'.format(self.diary_path, now.year, now.month, now.day)
        return os.path.exists(path)

        
    def add(self):
        """Add a new entry for the day. Does nothing if one already exists.
        """
        now = datetime.datetime.now()
        year = '{0}/{1:04d}'.format(self.diary_path, now.year)
        month = '{0}/{1:02d}'.format(year, now.month)
        day = '{0}/{1:02d}.md'.format(month, now.day)

        # Create dir if it doesn't already exist
        def create_dir(path):
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                if not os.path.isdir(path):
                    raise PathExists('{} exists and is not a directory'.format(path))
        
        create_dir(year)
        create_dir(month)

        if os.path.exists(day):
            self.logger.debug('Entry for today already exists'.format(day))
        else:
            with open(day, 'w') as f:
                lines = [
                    '# DevDiary',
                    'Created on {0}'.format(now.strftime('%c')),
                    '',
                    "Don't reformat anything above and including the \"Worked on:\" row below",
                    '',
                    'Worked on:',
                    '',
                    '* '
                ]
                f.writelines([l + '\n' for l in lines])

    def latest(self):
        """Get the full path to the latest diary entry
        """
        y = max(os.listdir(self.diary_path))
        m = max(os.listdir('{0}/{1}'.format(self.diary_path, y)))
        d = max(os.listdir('{0}/{1}/{2}'.format(self.diary_path, y, m)))
        return '{0}/{1}/{2}/{3}'.format(self.diary_path, y, m, d)


    def summarize(self, args):
        """Prints a summary of all diary entries.
        args: a list of years to consider for the summary, default is all years
        """
        summary = [TF.str(TF.BOLD_BLUE, '# Summary\n\n')]

        # Folders to exclude (in case the diaries are under version control)
        exclude = ['.git']

        # Do we need to filter (is args empty or not?)
        _filter = (lambda y: y not in args) if args else (lambda _: False)

        def ordinal_suffix(number):
            # Teens don't follow rules, otherwise it's simply modulo 10: 1st, 2nd, 3rd, Nth
            return 'th' if 4 <= number % 100 <= 20 else { 1: 'st', 2: 'nd', 3: 'rd' }.get(number % 10, 'th')

        for y in os.listdir(self.diary_path):
            if _filter(y) or y in exclude:
                # This directory should be ignored
                continue

            with calendar.TimeEncoding('en_US.UTF-8') as encoding:
                summary.append(TF.str(TF.BOLD_GREEN, '## {0}\n\n'.format(y)))
                for m in os.listdir('{0}/{1}'.format(self.diary_path, y)):
                    summary.append(TF.str(TF.BOLD_MAGENTA, '### {0}\n\n'.format(calendar.month_name[int(m)])))
                    for d in os.listdir('{0}/{1}/{2}'.format(self.diary_path, y, m)):
                        with open('{0}/{1}/{2}/{3}'.format(self.diary_path, y, m, d), 'r') as f:
                            lines = f.readlines()
                            date_str = str(int(d.replace('.md', ''))) # Trick to remove leading zeros
                            date_str = '{0}{1}'.format(date_str, ordinal_suffix(int(date_str)))
                            summary.append(TF.str(TF.BOLD_YELLOW, '#### {0}\n\n'.format(date_str)))

                            # We assume the default template, which means actual text starts at line 7
                            summary += lines[7:]
                            summary.append('\n')

        print ''.join(summary)

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add', action='store_true', help='Add new entry')
    parser.add_argument('-l', '--latest', action='store_true', help='Get the latest entry')
    parser.add_argument('-q', '--query', action='store_true', help="Checks whether there's an entry for today or not")
    parser.add_argument('-s', '--summarize', nargs='*', help='Shows a summary of all diary entries')
    parser.add_argument('-d', '--debug', action='store_true', help='Sets loglevel to DEBUG')
    parser.add_argument('-v', '--version', action='store_true', help='Prints script version and exits')
    args = parser.parse_args()
    
    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.WARNING))
    dd = DevDiary('{0}/.devdiary'.format(os.path.expanduser('~')), logging.getLogger(__file__))
    if args.version:
        print DEVDIARY_VERSION
        exit(0)
    elif args.summarize is not None:
        dd.summarize(args.summarize)
    elif args.query:
        exit(0 if dd.query() else 1)
    else:
        if args.add:
            dd.add()
        if args.latest:
            print dd.latest()

if __name__ == '__main__':
    main()


