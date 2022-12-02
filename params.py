#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021-2 by Joseph B. Attili, aa2il AT arrl DOT net
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
import argparse
import datetime
import glob 
from settings import CONFIG_PARAMS
from operator import itemgetter

################################################################################

# User params
DIR_NAME = os.path.expanduser( '~/.fldigi/logs/' )

#######################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument("-i", help="Input ADIF or CSV file",
                              type=str,default=None,nargs='*')
        arg_proc.add_argument("-o", help="Output ADIF or CSV file",
                              type=str,default='New.adif')
        arg_proc.add_argument('-sats', action='store_true',help='Satellite QSOs')
        arg_proc.add_argument("-days", help="Last N days",
                              type=int,default=0)
        arg_proc.add_argument("-after", help="Starting Date",
                              type=str,default=None)
        arg_proc.add_argument("-before", help="Ending Date",
                              type=str,default=None)
        arg_proc.add_argument("-call", help="Call worked",
                              type=str,default=None)
        args = arg_proc.parse_args()
        
        self.SATS=args.sats
        if args.call:
            self.CALL=args.call.upper()
        else:
            self.CALL=None

        # Read config file
        S=CONFIG_PARAMS('.keyerrc')
        self.SETTINGS=S.SETTINGS
        #print(self.SETTINGS)

        # Form list of file names
        fname = args.i
        if fname==None:

            # Use usual defaults if nothing speficied
            MY_CALL=self.SETTINGS['MY_CALL']
            fname=[]
            for fn in [MY_CALL+'*.adif','wsjtx_log.adi','sats.adif']:  # ,'wsjtx_log_FT991a.adi','wsjtx_log_IC9700.adi']:
                fname.append(fn)

        # Expand wildcards if necessary        
        if type(fname) == list:   
            self.input_files  = []
            for fn in fname:
                for fn2 in glob.glob(DIR_NAME+fn):
                    self.input_files.append(fn2)
        else:
            self.input_files  = [fname]

        self.output_file = args.o

        after=args.after
        ndays=args.days
        if after:
            if len(after.split('/'))==2:
                after+='/2022'
            self.date0 = datetime.datetime.strptime( after, "%m/%d/%Y")  # Start date

        elif ndays>0:
            now = datetime.datetime.utcnow()
            self.date0 = now-datetime.timedelta(days=ndays) 

        else:
            self.date0 = datetime.datetime.strptime( '01/01/1900', "%m/%d/%Y")  # Start date
    
        before=args.before
        if before:
            if len(before.split('/'))==2:
                before+='/2022'
        else:
            before='12/31/2299'
        self.date1 = datetime.datetime.strptime( before, "%m/%d/%Y")  # End date
