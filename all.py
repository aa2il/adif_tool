#! /usr/bin/python3
############################################################################################
#
# all.py - Rev 1.0
# Copyright (C) 2023 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Program to sift through ALL.TXT file
#
############################################################################################
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
############################################################################################

#import sys
#import os
#import datetime
#import numpy as np
#from params import *
from fileio import *
#from pprint import pprint

############################################################################################

# Start of main
print('\n****************************************************************************')
print('\nALL tool beginning ...\n')

# Init
MY_CALL='AA2IL'

# Read the log file
qsos=read_csv_file('FT8.csv')[0]
print('\nLOG:')
for qso in qsos:
    #print(qso)
    #print(qso['call'])
    print(qso['call'],'\t',qso['qso_date_off'],'\t',qso['time_off'],'\t')

print(' ')
n=0
#sys.exit(0)    

# Read the ALL.TXT file
lines=read_text_file('ALL2.TXT')
last_call=''
for line in lines:

    # Only look at lines pertaining to me - ignore my CQ's
    if MY_CALL in line and "CQ TEST "+MY_CALL not in line:
        #print(line)
        if MY_CALL+" 73" in line or MY_CALL+" RR73" in line:

#0         1         2         3         4         5         6         6 
#01234567890123456789012345678901234567890123456789012345678901234567890123456789
#230610_191445    50.313 Tx FT8      0  0.0  364 NA6MG AA2IL RR73
            
            a=line.split()
            dt=a[0].split('_')
            d=dt[0]
            t=dt[1]
            f=a[1]
            m=a[3]
            df=a[6]
            call=a[7]

            #print(a)
            print('\n',line)
            print(d,t,call)
            print(n,qsos[n])

            if call==last_call:
                print('Skipping extra confirmation ...')
                continue
            
            found=False
            if call==qsos[n]['call']:
                dt = int(t)-int(qsos[n]['time_off'])
                if abs(dt)<120:
                    found=True
                    n+=1
                    last_call=call
                else:
                    print('Big time gap - dt=',dt)
                    sys.exit(0)    
            if not found:
                print('Missing QSO!!!')
                sys.exit(0)    
            

print("\nThat's all folks!")

    
