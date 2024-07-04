#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Command line param parser for adif tool.
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import os
import sys
import argparse
import datetime
import glob 
from settings import CONFIG_PARAMS
from operator import itemgetter

################################################################################

# User params
#DIR_NAME = os.path.expanduser( '~/.fldigi/logs/' )

#######################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument("-i", help="Input ADIF or CSV file(s)",
                              type=str,default=None,nargs='*')
        arg_proc.add_argument("-o", help="Output ADIF or CSV file",
                              type=str,default='New.adif')
        arg_proc.add_argument('-sats', action='store_true',
                              help='Satellite QSOs')
        arg_proc.add_argument('-strict', action='store_true',
                              help='Strict Rules for Calls')
        arg_proc.add_argument('-aca', action='store_true',
                              help='Compare CWops worked vs ACA lists')
        arg_proc.add_argument('-notes', action='store_true',
                              help='Take note of items with question marks')
        arg_proc.add_argument('-prune', action='store_true',
                              help='Prune Fields')
        arg_proc.add_argument('-big_prune', action='store_true',
                              help='Prune Fields Even Harder')
        arg_proc.add_argument('-all', action='store_true',
                              help='Search All Logs in ~/logs')
        arg_proc.add_argument("-days", help="Last N days",
                              type=int,default=0)
        arg_proc.add_argument("-after", help="Starting Date",
                              type=str,default=None)
        arg_proc.add_argument("-before", help="Ending Date",
                              type=str,default=None)
        arg_proc.add_argument("-call", help="Call(s) worked",
                              type=str,default=None,nargs='*')
        arg_proc.add_argument("-qps", help="State QPs",
                              type=str,default=None,nargs='*')
        arg_proc.add_argument("-contest", help="Contest ID",
                              type=str,default=None,nargs='*')
        arg_proc.add_argument("-quiet", help="Quiet Mode",
                               action='store_true')
        arg_proc.add_argument("-comments", help="Include all QSOs with Comments",
                               action='store_true')
        args = arg_proc.parse_args()

        self.COMMENT = args.comments
        self.SATS    = args.sats
        self.STRICT  = args.strict
        self.NOTES   = args.notes
        self.ACA     = args.aca
        self.QUIET     = args.quiet
        
        calls=args.call
        if calls:
            self.CALLS=[]
            for call in calls:
                self.CALLS.append(call.upper())
        else:
            self.CALLS=None

        # Read config file
        S=CONFIG_PARAMS('.keyerrc')
        self.SETTINGS=S.SETTINGS
        #print(self.SETTINGS)

        # Form list of file names
        DIR_NAME = ""
        fname = args.i
        #print(fname)
        if args.all:
            fname=['*.adi','*.adif','fflog/*.adi*']
        if fname==None:

            # Use usual defaults if nothing speficied
            #DIR_NAME = os.path.expanduser( '~/.fldigi/logs/' )
            DIR_NAME = os.path.expanduser( '~/logs/' )
            MY_CALL=self.SETTINGS['MY_CALL']
            fname=[]
            for fn in [MY_CALL+'*.adif','wsjtx_log.adi','wsjtx_log9*.adi','wsjt_contest_log.adif',
                       'sats.adif','sprint.adif']:  # ,'wsjtx_log_991a.adi','wsjtx_log_9700.adi']:
                print('LOG FILE found:',fn)
                fname.append(fn)

        # Expand wildcards if necessary        
        print('fname=',fname,'\t',type(fname),'\nDIR_NAME=',DIR_NAME)
        if type(fname) == list:   
            self.input_files  = []
            for fn in fname:
                if not self.QUIET:
                    print(fn)
                for fn2 in glob.glob(DIR_NAME+fn):
                    self.input_files.append(fn2)
                    if not self.QUIET and False:
                        print(fn2)
        else:
            self.input_files  = [fname]
        if False:
            print(self.input_files)
            sys.exit(0)

        self.output_file = args.o

        after=args.after
        if not after and self.ACA:
            after='1/1'
        ndays=args.days
        if after:
            if len(after.split('/'))==2:
                now = datetime.datetime.utcnow()
                year = now.strftime('%Y').upper()
                #year = 2023
                print('Year=',year)
                after+='/'+str(year)
            self.date0 = datetime.datetime.strptime( after, "%m/%d/%Y")  # Start date

        elif ndays>0:
            now = datetime.datetime.utcnow()
            self.date0 = now-datetime.timedelta(days=ndays) 

        else:
            self.date0 = datetime.datetime.strptime( '01/01/1900', "%m/%d/%Y")  # Start date
    
        before=args.before
        if before:
            if len(before.split('/'))==2:
                now = datetime.datetime.utcnow()
                year = now.strftime('%Y').upper()
                print('Year=',year)
                before+='/'+year
        else:
            before='12/31/2299'
        self.date1 = datetime.datetime.strptime( before, "%m/%d/%Y")  # End date

        self.CONTEST_IDs=args.contest
        self.QPs=args.qps
        if self.QPs:
            if self.CONTEST_IDs==None:
                self.CONTEST_IDs=[]
            for qp in self.QPs:
                self.CONTEST_IDs.append(qp+'-QSO-PARTY')
        
        self.PRUNE=args.prune
        self.BIG_PRUNE=args.big_prune
        
        
