#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import logging
import argparse
import pdb
import datetime

class PathExists(Exception):
    pass


class DevDiary:

    def __init__(self, devdiary_path, logger):
        self.devdiary_path = devdiary_path if devdiary_path[-1] != '/' else devdiary_path[:-1]
        self.diary_path = '{0}/diaries'.format(self.devdiary_path)
        self.logger = logger

        # Create the settingns_path dir if it doesn't already exist
        if not os.path.exists(self.devdiary_path):
            print 'creating directory'
            os.makedirs(self.devdiary_path)

        # Make sure the diary_path exists
        if not os.path.exists(self.diary_path):
            os.makedirs(self.diary_path)
        else:
            if not os.path.isdir(self.diary_path):
                self.logger.fatal('{} is not a directory'.format())

    def query(self):
        now = datetime.date.today()
        path = '{0}/{1:04d}/{2:02d}/{3:02d}.md'.format(self.diary_path, now.year, now.month, now.day)
        return os.path.exists(path)

        
    def add(self):
        now = datetime.datetime.now()
        year = '{0}/{1:04d}'.format(self.diary_path, now.year)
        month = '{0}/{1:02d}'.format(year, now.month)
        day = '{0}/{1:02d}.md'.format(month, now.day)

        def create_dir(path):
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                if not os.path.isdir(path):
                    raise PathExists('{} exists and is not a directory'.format(path))
        
        create_dir(year)
        create_dir(month)
        if os.path.exists(day):
            self.logger.info('Entry for today already exists'.format(day))
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
        y = max(os.listdir(self.diary_path))
        m = max(os.listdir('{0}/{1}'.format(self.diary_path, y)))
        d = max(os.listdir('{0}/{1}/{2}'.format(self.diary_path, y, m)))
        return '{0}/{1}/{2}/{3}'.format(self.diary_path, y, m, d)

    def list(self):
        for y in os.listdir(self.diary_path):
            print y
            for m in os.listdir('{0}/{1}'.format(self.diary_path, y)):
                print '  |--> {0}'.format(m)
                for d in os.listdir('{0}/{1}/{2}'.format(self.diary_path, y, m)):
                    print '  |    |--> {0}'.format(d)

    def summarize(self, args):
        summary = ['# Summary\n\n']

        exclude = ['.git']
        _filter = (lambda y: y not in args) if args else (lambda _: False)

        for y in os.listdir(self.diary_path):
            if _filter(y) or y in exclude:
                continue
            summary.append('## {0}\n\n'.format(y))
            for m in os.listdir('{0}/{1}'.format(self.diary_path, y)):
                summary.append('### {0}\n\n'.format(datetime.date(2016, int(m), 1).strftime('%B')))
                for d in os.listdir('{0}/{1}/{2}'.format(self.diary_path, y, m)):
                    with open('{0}/{1}/{2}/{3}'.format(self.diary_path, y, m, d), 'r') as f:
                        lines = f.readlines()
                        summary.append('#### {0}\n\n'.format(d.replace('.md', '')))
                        summary += lines[7:]
                        summary.append('\n')

        print ''.join(summary)

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', action='store_true', help='Add new entry')
    parser.add_argument('--latest', action='store_true', help='Get the latest entry')
    parser.add_argument('--list', action='store_true', help='List all entries')
    parser.add_argument('--query', action='store_true', help="Checks whether there's an entry for today or not")
    parser.add_argument('--summarize', nargs='*', help='Shows a summary of all diary entries')
    parser.add_argument('--debug', action='store_true', help='Sets loglevel to DEBUG')
    args = parser.parse_args()
    
    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.WARNING))
    dd = DevDiary('{0}/.devdiary'.format(os.path.expanduser('~')), logging.getLogger(__file__))
    if args.list:
        dd.list()
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


