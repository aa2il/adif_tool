#! /usr/bin/python3
############################################################################################
#
# adif_tool.py - Rev 1.0
# Copyright (C) 2021-2 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Program to manipulate adif files.
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

import sys
import os
import datetime
import argparse
import numpy as np
from params import *
from fileio import parse_file_name,parse_adif,write_adif_log
from pprint import pprint

#######################################################################################

# Start of main
print('\n****************************************************************************')
print('\nADIF Tool beginning ...\n')
P=PARAMS()
print("P=")
pprint(vars(P))

# Init
istart  = -1

# Read adif input file(s)
QSOs=[]
for f in P.input_files:
    fname=os.path.expanduser( f )
    print('Input file:',fname)

    p,n,ext=parse_file_name(fname)
    if ext=='.csv':
        print('Reading CSV file ...')
        qsos1,hdr=read_csv_file(fname)
    else:
        qsos1 = parse_adif(fname)

    for qso in qsos1:
        qso['file_name']=f

    QSOs = QSOs + qsos1
    
print("\nThere are ",len(QSOs)," input QSOs ...")

# Sift through the qsos and select those that meet the criteria
QSOs_out=[]
KEYS=[]
for qso in QSOs:
    for key in qso.keys():
        if key not in KEYS:
            #print('Adding key',key)
            KEYS.append(key)

    if False:
        print(qso)
        keys=qso.keys()
        print('\n Keys=',keys)
        print('\n Keys=',set(keys))
        print(' ')
        sys.exit(0)

    # Flag "TEST" qsos
    if qso['call'].upper()=='TEST':
        print('\nNeed to purge TEST qso from',qso['file_name'])
        print(qso)
        sys,exit(0)
    
    
    # Get qso date
    if 'qso_date_off' in qso and len(qso['qso_date_off'])>0:
        date_off = datetime.datetime.strptime( qso['qso_date_off'], "%Y%m%d")
    elif 'qso_date' in qso:
        date_off = datetime.datetime.strptime( qso['qso_date'], "%Y%m%d")
    else:
        print('\nHmmmmmmmmmm - cant figure out date!')
        print(rec)
        print(keys)
        sys.exit(0)

    # Is the qso date in our window?
    if date_off>=P.date0 and date_off<=P.date1:
        save_qso=True
    else:
        save_qso=False

    # Are we looking for satellite qsos?
    if P.SATS:
        if 'sat_name' in qso:
            if 'gridsquare' in qso:
                qth=qso['gridsquare'][:4]
            elif 'srx_string' in qso:
                #print(qso)
                exch=qso['srx_string']
                a=exch.split(',')
                if len(a[0])==4:
                    qth=a[0]
                elif len(a)>1 and len(a[1])==4:
                    qth=a[1]
                else:
                    qth=''
            if (not 'qth' in qso) or (len(qso['qth'])==0):
                qso['qth']=qth
        else:
            save_qso=False

    # Are we looking for a specific call?
    if P.CALL!=None:
        if qso['call'].upper()!=P.CALL:
            save_qso=False

    # If we passed all the criteria, add this qso to our list
    if save_qso:
        QSOs_out.append(qso)
        #print(qso)

print("There are ",len(QSOs_out)," QSOs meeting criteria ...")
        
# Write out new adif or csv file
#KEYS2=sort_keys(KEYS)
KEYS2=KEYS
print('fname=',P.output_file)
print('\nKEYS2=',KEYS2)

# Sort list of Q's by date & time
QSOs_out2 = sorted(QSOs_out, key=itemgetter('qso_date','time_on'))
#print('rec0=',QSOs_out2[0])

# Merge the same Q's
QSOs_out3=[]
valid=len(QSOs_out2)*[True]
for i in range(len(QSOs_out2)):
    qso1=QSOs_out2[i]
    keys1=qso1.keys()
    #print(i,valid[i])
    if valid[i]:
        for j in range(i+1,len(QSOs_out2)):
            qso2=QSOs_out2[j]
            match=True
            for field in ['call','qso_date','time_on']:
                match = match and (qso1[field]==qso2[field])
            if match:
                #print('\nMatch!!!',i,j,valid[j])
                keys2=qso2.keys()
                #print(qso1)
                #print(qso2)
                valid[j]=False
                for key in keys2:
                    if key!='unique' and (key not in keys1 or len(qso1[key])==0):
                        qso1[key]=qso2[key]
        QSOs_out3.append(qso1)

#print(valid)        
#print(len(QSOs_out2),len(QSOs_out3))
        
# Finally write out list of Q's
p,n,ext=parse_file_name(P.output_file)
if ext=='.csv':
    print('Writing output CSV file with',len(QSOs_out3),' QSOs ...')
    write_csv_file(P.output_file,KEYS2,QSOs_out3)
else:
    print('Writing output adif file with',len(QSOs_out2),' QSOs ...')
    P.contest_name=''
    write_adif_log(QSOs_out2,P.output_file,P,SORT_KEYS=False)

# Show a list of QSOs for a specified call
if P.CALL!=None:
    print('\nCall\tMode\tDate\t\tUTC\tBand\tRST Out\tRST In')
    for qso in QSOs_out2:
        if 'rst_rcvd' in qso:
            rst_in=qso['rst_rcvd']
        else:
            rst_in='?'
        if 'rst_sent' in qso:
            rst_out=qso['rst_sent']
        else:
            rst_out='?'
        d=qso['qso_date_off']
        date=d[4:6]+'-'+d[6:]+'-'+d[0:4]
        t=qso['time_off']
        time=t[0:2]+':'+t[2:4]
        if 'band' in qso:
            band=qso['band']
        else:
            band='?'
        fname=qso['file_name']
        print(qso['call'],'\t',qso['mode'],'\t',
              date,'\t',time,'\t',
              band,'\t',rst_out,'\t',rst_in,'\t\t',fname)
              
print("\nThat's all folks!")

    
