#!/usr/bin/env -S uv run --script
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
############################################################################################
#
# adif_tool.py - Rev 1.1
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Program to manipulate adif files.
# Rev 1.1 - Use Pandas instead of dicts
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
import numpy as np
from params import *
from fileio import *
from pprint import pprint
from dx import ChallengeData
from load_history import load_history
from counties import *
from qso_editor import QSO_INSPECTOR
from copy import copy
from utilities import error_trap
import pytz

############################################################################################

def check_id(qso):
    ok=True
    if 'qth' in qso:
        qth=qso['qth'].split('/')[0]
    else:
        print('\nHELP! No qth!')
        print('qso=',qso)
        print('--- Giving up ---')
        qth='??'
        ok=False
        #sys.exit(0)
        return qso,ok
    id=qso['contest_id'][:2]
    if id in ['W1','W7','DE','IN']:
        state=qth[:2]
        if len(qth)<5:
            print('\nCHECK ID: Unable to confirm state - id=',id)
            print('qso=',qso)
            print('qth=',qth,'\tstate=',state,'\tid=',id)
            id2=id
            if id=='W7':
                id9='7QP'
            else:
                id9=id
            print('counties=',COUNTIES[id9])
            if (qth in COUNTIES[id9]) or (id+qth in COUNTIES[id9]):
                print('Its Probably OK!')
            ok=True
            #sys.exit(0)
        elif (state in W7_STATES) or (state+'7QP' in W7_STATES):
            #print(W7_STATES)
            id2='W7'
        elif state in W1_STATES:
            #print(W1_STATES)
            id2='W1'
        else:
            id2=state
    else:
        if qth in COUNTIES[id]:
            id2=id
        else:
            print('\nCHECK ID: Unable to confirm state - id=',id)
            print('qso=',qso)
            print('qth=',qth)
            state=qth[:2]
            if id in ['IN','DE']:
                if state==id:
                    print('Its Probably OK!')
                    id2=id
                elif state=='WA':
                    id2='W7'
            else:
                print('counties=',COUNTIES[id])
                print('--- Giving up ---')
                sys.exit(0)

    qso2=qso
    if id!=id2:
        ok=False
        print('\nCHECK ID: Contest ID fixup - ',id,' --> ',id2)
        print('qso=',qso)
        print('qth=',qth,'\tstate=',state,'\tid=',id)
        #sys.exit(0)
        qso2['contest_id']=id2+qso['contest_id'][2:]

    return qso2,ok

############################################################################################

def qso_compare(qso1,qso2):
    
    #keys=list( set( qso1.keys() ) | set( qso2.keys() ) )
    keys=qso2.keys()
    #print('keys=',keys)

    same=True
    ndiff=0
    qso3=copy(qso1)
    for key in keys:
        if key in ['file_name','flagged']:
            continue
        elif key in qso2:
            if key in qso1:
                if qso1[key]==qso2[key]:
                    pass
                else:
                    print('QSO COMPARE: key=',key,'\tValues:',qso1[key],qso2[key])
                    same=False
                    qso3[key]=qso2[key]
                    ndiff+=1
            else:
                print('Missing key',key,'in qso1')
                val2 = qso2[key]
                if len(val2)==0:
                    pass
                else:
                    if False:
                        print('qso1=',qso1)
                        print('qso2=',qso2)
                        print('val2=',val2,len(val2))
                        print('HELP!!!!')
                        same=False
                        sys.exit(0)
                    else:
                        qso3[key]=val2
                        same=False
                        ndiff+=1
                        
        else:
            if key in qso1:
                #print('Missing key',key,'in qso2')
                #same=False
                pass
            else:
                print('Missing key',key,'in both qsos','\tHELP!')
                same=False
                sys.exit(0)

    if not same:
        print('Difference found: ndiff=',ndiff)
        print('\tcall=',qso1['call'],qso2['call'],qso3['call'])
        print('\tqso1=',qso1)
        print('\tqso2=',qso2)
        print('\tqso3=',qso3)
        print(' ')
        #sys.exit(0)

    return same,ndiff,qso3

############################################################################################

# Start of main
print('\n****************************************************************************')
print('\nADIF Tool beginning ...\n')
P=PARAMS()
if not P.QUIET:
    print("P=")
    pprint(vars(P))

# Init
istart  = -1

# Read adif input file(s)
QList=[]
nfiles=0
for f in P.input_files:
    nfiles+=1
    fname=os.path.expanduser( f )
    if not P.QUIET:
        print('Input file:',fname)

    p,n,ext=parse_file_name(fname)
    #print(p,n,ext)

    if ext=='.csv':
        print('Reading CSV file ...')
        print('ADIF_TOOL - Need to update this pathway for Pandas!!!!!')
        sys.exit(0)
        qsos1,hdr=read_csv_file(fname)
        print('hdr=',hdr)

        # Check freq - must be MHz
        #print(qsos1[0])
        for i in range(len(qsos1)):
            frq=float( qsos1[i]['freq'] )
            if frq>=1400.:               # The highest band I can op is 23cm
                frq *= 1e-3              # Assume KHz and convert to MHz
                qsos1[i]['freq'] = str(frq)
        #print(qsos1[0])
        #sys.exit(0)
        
    else:
        qsos1 = parse_adif(fname,DF=True)

    # Add field with filename for these QSOs
    nrows=qsos1.shape[0]
    print('nrows=',nrows)
    qsos1['file_name'] = nrows*[f]

    # Make a list qso dataframes
    if P.DIFF and nfiles==2:
        QSOs2 = qsos1
        found_start=False
    else:
        QList.append(qsos1)
        #if nfiles>2:
        #    break
        
# Merge QSOs from various files together
#print('QList=',QList)
QSOs=pd.concat(QList,ignore_index=True)
#print(QSOs)

# Remove dupes    
#dupes = QSOs[QSOs.duplicated()]
#print('\nDupes:\n',dupes)
QSOs.drop_duplicates(inplace=True,ignore_index=True)
print('\nDropped Dupes:\n',QSOs)

# Fixups
nqsos=QSOs.shape[0]
UTC = pytz.utc
ts=[]
for i in range(nqsos):
    qso=QSOs.loc[i]
    date_off = qso["qso_date_off"]
    time_off = qso["time_off"]
    time_stamp = datetime.datetime.strptime( date_off +" "+ time_off , "%Y%m%d %H%M%S") \
                                      .replace(tzinfo=UTC)
    d=qso['qso_date']
    if type(d)==float and np.isnan(d):
        #qso['qso_date']=date_off
        QSOs.loc[i,'qso_date']=qso['qso_date_off']
    t=qso['time_on']
    if type(t)==float and np.isnan(t):
        #qso['time_on']=qso['time_off']
        QSOs.loc[i,'time_on']=qso['time_off']
    ts.append(time_stamp)
    
QSOs['time_stamp'] = ts
print('\nDropped Dupes:\n',QSOs)
#print('row 0=',QSOs.iloc[0])
    
if not P.QUIET:
    print("\nThere are ",nqsos," input QSOs ...")

# Open script file for questionable lines
if P.NOTES:
    fname77='snippets.txt'
    fp = open(fname77,"w")
    fp.write('%s\n' % ('#/bin/tcsh -f') )
    fp.write('%s\n' % (' ') )
    fp.write('%s\n' % ('set fname="capture_*.wav"') )
    fp.write('%s\n' % (' ') )

# Read CWops lists
if P.ACA:
    naca=0
    maybe=[]

    # Member list
    fname88 = os.path.expanduser('~/Python/history/data/Shareable CWops data.xlsx')
    HIST,fname2 = load_history(fname88)
    cwops_members=list( set( HIST.keys() ) )

    print('No. CW Ops Members:',len(cwops_members))
    #print(cwops_members)

    # List worked for ACA credit
    CHALLENGE_FNAME = os.path.expanduser('~/AA2IL/states.xls')
    P.data = ChallengeData(CHALLENGE_FNAME)
    aca  = list(set(P.data.cwops_worked))
    nums = list(set(P.data.cwops_nums))
    print('\nNo. CWops members worked for ACA:',len(aca),len(nums))
    print('\n    No.\t Call\t\tMem Num\tStatus')

    #sys.exit(0)

# Sift through the qsos and select those that meet the criteria
print('\nSifting ...')
Saved_QSO_List=[]
KEYS=[]
nflagged=0
nflagged2=0
nqsos1=0
nqsos2=0
for i in range(nqsos):
    qso=QSOs.loc[i]
    nqsos1+=1

    # Is the qso date in our window?
    date_off = qso['time_stamp']
    #print('date_off=',date_off,'\tdate0=',P.date0,'\tdate1=',P.date1)
    #sys.exit(0)
    if date_off>=P.date0 and date_off<=P.date1:
        save_qso=True
    else:
        save_qso=False
        continue

    # Has this QSO been flagged
    noted=False
    if P.NOTES and 'flagged' in qso and qso['flagged']:
        noted=True
        nflagged+=1
        print('\nOp flagged this qso:\n',qso)
        note=qso['call']+' FLAGGED '+str(nflagged)

    #sys.exit(0)
        
    for key in qso.keys():
        
        if key not in KEYS:
            #print('Adding key',key)
            #if not P.PRUNE or key not in ['band_rx','freq_rx','my_city']:
            if P.BIG_PRUNE and key in ['my_gridsquare','rst_rcvd','rst_sent',
                                       'station_callsign','skcc','file_name',
                                       'sat_name','prop_mode','my_rig','running',
                                       'band_rx','freq_rx','my_city']:
                pass
            elif P.PRUNE and key in ['band_rx','freq_rx','my_city','my_rig']:
                pass
            elif key=='qth' and False:
                print('key=',key)
                print('keys=',list(qso.keys()))
                print('KEYS=',KEYS)
                KEYS.append(key)
                print('KEYS=',KEYS)
                sys.exit(0)
            else:
                KEYS.append(key)

        # Is there a question about any field?
        if P.NOTES and type(qso[key])==str and '?' in qso[key] and not noted:
            noted=True
            print('\nQuestionable field:',key,qso[key],'\n',qso)
            note=qso['call']+' '+key+' '+qso[key]
            #sys.exit(0)
            
    if False:
        print(qso)
        keys=qso.keys()
        print('\n Keys=',keys)
        print('\n Keys=',set(keys))
        print(' ')
        sys.exit(0)

    # Flag "TEST" qsos
    #print(qso)
    if qso['call'].upper()=='TEST':
        print('\nNeed to purge TEST qso from',qso['file_name'])
        print(qso)
        sys,exit(0)

    # Are we looking for a specific contest?
    #print(P.CONTEST_IDs)
    if P.CONTEST_IDs!=None:
        if 'contest_id' in qso:
            contest_id=qso['contest_id'].upper()
            #print(P.CONTEST_IDs,contest_id)
            if contest_id not in P.CONTEST_IDs:
                save_qso=False
            #print(P.CONTEST_IDs,contest_id,len(P.CONTEST_IDs[0]),len(contest_id),contest_id in P.CONTEST_IDs,save_qso)
        else:
            save_qso=False

    # Reconcile differences
    if save_qso and P.DIFF:
        if nqsos2>=len(QSOs2):
            print('\nWhoops!\tnqsos2=',nqsos2,len(QSOs2))
            print('qso=',qso)
            print('QSOs2[-1]=',QSOs2[-1])
            print('Did you delete a QSO somewhere along the way?')
        qso2=QSOs2[nqsos2]
        nqsos2+=1
        same,ndiff,qso3=qso_compare(qso,qso2)
        if not same:
            qso=qso3
            #print('qso=',qso)
            #sys.exit(0)
        else:
            #save_qso=False
            pass
        if 'flagged' in qso3 and False:
            print('\nqso  =',qso)
            print(qso.keys())
            print('\nqso2 =',qso2)
            print(qso2.keys())
            print('\nqso3 =',qso3)
            print(qso3.keys())
            sys.exit(0)

    # Is there a question about the call sign
    if '?' in qso['call'] and P.STRICT:
        print('Skipping QSO with questionable call', qso['call'])
        save_qso=False
        if True:
            print('YOU NEED TO FIX THIS!!!')
            sys.exit(0)

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

    # Are we looking for a specific call(s)?
    if P.CALLS!=None:
        if qso['call'].upper() not in P.CALLS:
            save_qso=False

    # Do we want all qso's with comments?
    cwo=None
    if 'comment' in qso:
        comment = qso['comment']
        if type(comment)==str and comment[0:4]=='CWO:':
            cwo=comment[4:]
            #print('cwo=',cwo)
            #if ')' in comment:
            #    print(qso)
            #    sys.exit(0)
        if P.COMMENT:
            save_qso = True

    # Are we looking for 1x1 callsigns?
    if P.THREE and save_qso:
        call = qso['call'].upper()
        if len(call)==3:
            pass
        else:
            save_qso = False
        #print(call,save_qso)
        #sys.exit(0)
        
    # Are we looking for potentially over-looked ACA contacts?
    if P.ACA and save_qso:
        call = qso['call'].upper()
        mode = qso['mode'].upper()
        try:
            num = float( HIST[call]['cwops'] )
        except:
            num = -1
        try:
            status = HIST[call]['status']
        except:
            status = 'n/a'
        if cwo:
            try:
                num2 = float( HIST[cwo]['cwops'] )
            except:
                num2 = -1
            try:
                status2 = HIST[cwo]['status']
            except:
                status2 = 'n/a'
        if (mode=='CW') and (call in cwops_members) and \
           (call not in aca) and (num not in nums):
            naca+=1
            print('ACA:',naca,' \t',call,'  \t',int(num),'\t',status)
            maybe.append(call)
        elif (mode=='CW') and (cwo in cwops_members) and \
           (cwo not in aca) and (num2 not in nums):
            naca+=1
            print('ACA2:',naca,' \t',cwo,'  \t',int(num),'\t',status)
            maybe.append(cwo)
        else:
            save_qso = False

    # If we passed all the criteria, add this qso to our list
    #print('HEY!',save_qso)
    if save_qso:
        #print('Save QSO ...',noted,P.RunInspector)

        # Check State QSO Contest IDs
        if P.QPs!=None:
            contest_id=qso['contest_id'].upper()
            if 'QSO-PARTY' in contest_id and True:
                qso3,ok=check_id(qso)
                noted = noted or not ok
                note = 'State QP contest ID change'

        if noted and P.RunInspector:
            nflagged2+=1
            print('\nInspecting flagged QSO',nflagged2,'of',nflagged)
            try:
                inspector=QSO_INSPECTOR(qso)
                print(inspector.qso2)
                print('Burp!',inspector.Changed,inspector.SkipRemaining)
                if inspector.Changed:
                    qso=inspector.qso2
                P.RunInspector = not inspector.SkipRemaining
                #sys.exit()
            except:
                error_trap('ADIF_TOOL - Saving QSO: I dont know what I am doing here?!')
            
        Saved_QSO_List.append(i)
        #print('qso=',qso)
        #sys.exit(0)
        if noted:
            cmd='split_wave $fname -snip ' + qso['time_off'] + \
                  ' ; audacity SNIPPIT.wav >& /dev/null'
            print('\n#',note)
            print(cmd,'\n')
            fp.write('\n# %s\n' % (note) )
            fp.write('%s\n' % (cmd) )
            fp.flush()
            #sys.exit(0)

QSOs_out=QSOs.iloc[Saved_QSO_List]

if not P.QUIET:
    print("There are ",len(QSOs_out)," QSOs meeting criteria ...")
    #sys.exit(0)
        
# Write out new adif or csv file
#if 'qso_date' not in KEYS:
#    KEYS.append('qso_date')
#if 'time_on' not in KEYS:
#    KEYS.append('time_on')
KEYS2=KEYS
if not P.QUIET:
    print('fname=',P.output_file)
    #print('\nKEYS2=',KEYS2)

# Sort list of Q's by date & time
if not P.QUIET:
    print('Sorting ...')
QSOs_out2 = QSOs_out.sort_values(by='time_stamp',ignore_index=True)
print('Sorted:\n',QSOs)
#print('rec0=',QSOs_out2[0])

# Finally write out list of Q's
p,n,ext=parse_file_name(P.output_file)
if P.DIFF:
    IGNORE_KEYS=['flagged']
else:
    IGNORE_KEYS=[]

if ext=='.db':
    if not P.QUIET:
        print('Writing output SQL file with',len(QSOs_out2),' QSOs ...')
    write_sql_file(P.output_file,KEYS2,QSOs_out2)
elif ext=='.csv':
    if not P.QUIET:
        print('Writing output CSV file with',len(QSOs_out2),' QSOs ...')
    write_csv_file(P.output_file,KEYS2,QSOs_out2)
else:
    if not P.QUIET:
        print('Writing output adif file with',len(QSOs_out2),' QSOs ...')
    P.contest_name=''
    write_adif_log(QSOs_out2,P.output_file,P,SORT_KEYS=1,IGNORE=IGNORE_KEYS,VERBOSITY=0)

# Show a list of QSOs for specified call(s)
if P.CALLS or P.ACA:
    print('\nCall\tMode\t   Date\t\t  UTC\tBand\tRST Out\tRST In\t Contest Id\t\t Log File')
    
    nqsos2=QSOs_out2.shape[0]
    for i in range(nqsos2):
        qso=QSOs_out2.loc[i]

        if 'rst_rcvd' in qso:
            rst_in=qso['rst_rcvd']
        else:
            rst_in='?'
        if 'rst_sent' in qso:
            rst_out=qso['rst_sent']
        else:
            rst_out='?'
        if 'contest_id' in qso:
            contest_id=qso['contest_id']
        else:
            contest_id=''
        d=qso['qso_date_off']
        #date=d[4:6]+'-'+d[6:]+'-'+d[0:4]
        date=d[0:4]+'-'+d[4:6]+'-'+d[6:]
        t=qso['time_off']
        time=t[0:2]+':'+t[2:4]
        if 'band' in qso:
            band=qso['band']
        else:
            band='?'
        fname=qso['file_name']
        print(qso['call'],'\t',qso['mode'],'\t',
              date,'\t',time,'\t',
              band,'\t ',rst_out,'\t',rst_in,'\t',contest_id,
              '\t\t',fname)
              
if P.NOTES:
    fp.close()

if P.ACA:
    maybe=list(set(maybe))
    print('\nPotential ACA oversights:',len(maybe))
    for call in maybe:
        num = int( HIST[call]['cwops'] )
        try:
            status = HIST[call]['status']
        except:
            print('Unknown status for call=',call,',\tnum=',num)
        print(call,'\t',int(num),'\t',status)
    
print("\nThat's all folks!")

    
