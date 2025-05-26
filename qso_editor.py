#! /home/joea/miniconda3/envs/aa2il/bin/python -u
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
################################################################################
#
# qso_editor.py - Rev. 1.0
# Copyright (C) 2024-5 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui for editing QSO data.
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

import sys
import os
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
    import tkinter.messagebox
else:
    from Tkinter import *
    import tkFont
import time
import platform
import argparse
from widgets_tk import StatusBar,SPLASH_SCREEN
from ToolTip import *

################################################################################

OVERWRITE=False
OVERWRITE=True

################################################################################

# GUI for editing QSO data
class QSO_EDITOR():
    def __init__(self,root,P):

        # Inits
        self.P = P
        self.nqsos=0
        self.DISPLAY_FIELDS=['Date','Time','Call','Band','Mode',
                             'Name','QTH','SRX']
        self.FIELDS=['call','band','mode','qso_date','time_off',
                             'name','qth','srx']
        self.nfields=0
        self.QSOs=[]
        self.Dirty=False
        self.fmt=" %8s %8s  %-10.10s  %-4.4s %-4.4s %-8.8s %-12.12s %+5.5s"
 
        # Open main or pop-up window depending on if "root" is given
        if root:
            self.win=Toplevel(root)
            self.Hide()
        else:
            self.win = Tk()
        self.win.title("QSO Editor by AA2IL")
        self.win.geometry('1700x500+100+10')
        self.root=self.win

        # Create spash screen
        #if self.STAND_ALONE:
        #    self.splash  = SPLASH_SCREEN(self.root,'keyer_splash.png')
        #    self.status_bar = self.splash.status_bar
        #    self.status_bar.setText("Howdy Ho!!!!!")
        
        # Load fixed-spaced fonts we want to use
        if platform.system()=='Linux':
            FAMILY="monospace"
        elif platform.system()=='Windows':
            FAMILY="courier"
        else:
            print('GUI INIT: Unknown OS',platform.system())
            sys.exit(0)
        if self.P.SMALL_FONT:
            SIZE=8
        else:
            SIZE=10 
        if sys.version_info[0]==3:
            self.font = tkinter.font.Font(family=FAMILY,size=SIZE,weight="bold")
        else:
            self.font = tkFont.Font(family=FAMILY,size=SIZE,weight="bold")
            
        # Add menu bar
        #self.create_menu_bar()

        # Frame for entry boxes
        self.Frame1 = Frame(self.root)
        self.Frame1.pack(fill=BOTH)

        label = Label(self.root,
                      font=self.font,
                      anchor="w",justify=LEFT,
                      text=self.fmt % tuple(self.DISPLAY_FIELDS) )
        label.pack(fill=BOTH)
        
        # List box with a scroll bar
        self.Frame2 = Frame(self.root)
        self.Frame2.pack(fill=BOTH,expand=1)
        self.scrollbar = Scrollbar(self.Frame2, orient=VERTICAL)

        self.lb   = Listbox(self.Frame2, yscrollcommand=self.scrollbar.set,font=self.font)
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.lb.pack(side=LEFT, fill=BOTH, expand=1)
        self.lb.bind('<<ListboxSelect>>', self.LBLeftClick)
        """
        self.lb.bind('<Button-2>',self.LBCenterClick)
        self.lb.bind('<Button-3>',self.LBRightClick)

        # Trap the mouse wheel pseudo-events so we can handle them properly
        self.lb.bind('<Button-4>',self.scroll_updown)
        self.lb.bind('<Button-5>',self.scroll_updown)          
        self.scrollbar.bind('<Button-4>',self.scroll_updown)   
        self.scrollbar.bind('<Button-5>',self.scroll_updown)   
        """
        
        # Status bar along the bottom
        self.status_bar = StatusBar(self.root)
        self.status_bar.setText("Howdy Ho!")
        self.status_bar.pack(fill=X,side=BOTTOM)
        
        # Make what we have so far visible
        self.root.update_idletasks()
        self.root.update()

        
    # Routine to create entry boxes for editing ADIF fields
    def make_entry_boxes(self):

        self.row=0
        self.col=0
        self.boxes={}
        for field in self.FIELDS:
            label = Label(self.Frame1,text=' '+field+':',font=self.font)
            label.grid(row=self.row,column=self.col,columnspan=1)
            box    = Entry( self.Frame1,
                            font=self.font,
                            selectbackground='lightgreen',
                            validate='key',            # all?
                            validatecommand=(self.root.register(self.QSO_Changed), '%W','%P') )
            box.grid(row=self.row,column=self.col+1,columnspan=1)
            self.boxes[field]=box
            self.col+=2
            if self.col>10:
                self.row+=1
                self.col=0


    # Callback to note if any box has changes
    def QSO_Changed(self,widget,txt):
        #idx=list(map(int, widget.replace('.!Cell','').split('_') ))
        #gprint(widget,'\t')
        
        self.Dirty=True
        return True
                
        
    # Routine to add a single qso to the scroll box
    def insert_qso(self,qso,idx):

        try:
            call     = qso['call']
            date     = qso['qso_date']
            time_off = qso['time_off']
            band     = qso['band']
            mode     = qso['mode']
            if 'name' in qso:
                name  = qso['name']
            else:
                name=''
            if 'qth' in qso:
                qth  = qso['qth']
            else:
                qth=''
            if 'srx' in qso:
                srx  = qso['srx']
            else:
                srx=''
        except:
            print('INSERT QSO ERROR')
            print(qso)
            sys.exit(0)
            
        self.lb.insert(idx,self.fmt % (date,time_off,call,band,mode,name,qth,srx))
            
        if idx==END:
            idx=self.nqsos-1
        if idx % 2:
            c='bisque'
        else:
            c='lemon chiffon'
        self.lb.itemconfigure(idx, background=c)

        
    # Routine to add qsos to the scroll box
    def add_qsos(self,qsos):

        for qso in qsos:
            
            for field in qso.keys():
                if field not in self.FIELDS:
                    self.FIELDS.append(field)
        
            self.nqsos+=1
            self.QSOs.append(qso)
            self.insert_qso(qso,END)
            
        print('FIELDS=',self.FIELDS)

        # Make sure we have all an entry box for each field
        self.make_entry_boxes()

        # Make latest (last) qso visible
        sb=self.scrollbar.get()
        print('sb=',sb)
        self.root.update_idletasks()
        self.lb.yview_moveto(sb[1])

        
    # Handler for when an entry is selected
    def LBLeftClick(self,event):
        print('LBLeftClick ...')

        # Check if we need to save any changes
        if self.Dirty:
            msg='Save changes?'
            lab="QSO Editor"
            if sys.version_info[0]==3:
                result=tkinter.messagebox.askyesno(lab,msg)
            else:
                result=tkMessageBox.askyesno(lab,msg)
                
            if result:
                
                qso=self.QSOs[self.qso_index]
                for field in self.FIELDS:
                    val=self.boxes[field].get()            # .upper()
                    if len(val)>0 or field in qso:
                        qso[field]=val
                self.QSOs[self.qso_index]=qso

                self.lb.delete(self.qso_index,self.qso_index)
                self.insert_qso(qso,self.qso_index)
                
            else:
                print('Changes Discarded.')

        w=event.widget
        if len( w.curselection() ) > 0:
            self.qso_index = int(w.curselection()[0])
            value = w.get(self.qso_index)
            print('You selected item %d: "%s"' % (self.qso_index, value))

            qso=self.QSOs[self.qso_index]
            print('qso=',qso)

            for field in self.boxes.keys():
                box=self.boxes[field]
                box.delete(0,END)
                if field in qso:
                    box.insert(0,qso[field])
                
        self.Dirty=False
        
################################################################################

# If this file is called as main, run as independent exe
# Not quite there yet ...
if __name__ == '__main__':

    from settings import read_settings
    from fileio import parse_adif,write_adif_log
    
    print('Howdy Ho!')
    
    # Structure to contain processing params
    class EDITOR_PARAMS:
        def __init__(self):

            # Init
            self.SMALL_FONT=False
            
            # Read config file
            self.SETTINGS,RCFILE = read_settings('.keyerrc')

            # Process command line args
            arg_proc = argparse.ArgumentParser()
            arg_proc.add_argument('Fname', metavar='Fname',
                                  type=str, default=None,
                                  help='ADIF Input File Name')
            args = arg_proc.parse_args()
            
            if args.Fname==None:
                DIR_NAME = os.path.expanduser( '~/.fldigi/logs/' )
                MY_CALL=P.SETTINGS['MY_CALL']
                self.fname=DIR_NAME+MY_CALL+'.adif'
                #fname=MY_CALL+'.adif'
            else:
                DIR_NAME = os.path.expanduser('')
                self.fname=DIR_NAME+args.Fname

            if False:
                print('Input file:',self.fname)
                sys.exit(0)
            

            
    # Set basic run-time params
    P=EDITOR_PARAMS()

    # Create GUI
    P.Editor = QSO_EDITOR(None,P)
    
    # Read ADIF log
    print('Input file:',P.fname)
    qsos = parse_adif(P.fname)
    print("\nThere are ",len(qsos)," input QSOs ...")
    print('Last qso=',qsos[-1])

    # Populate editor
    P.Editor.add_qsos(qsos)
    
    # And away we go!
    #P.Editor.status_bar.setText("Let's Rock!")
    mainloop()

    # Save adif file
    if OVERWRITE:
        fname2=P.fname
    else:
        fname2=P.fname+'2'
    write_adif_log(qsos,fname2,P,SORT_KEYS=False)

    print("Y'all come on back now ya hear!")

################################################################################
    
class QSO_INSPECTOR():
    def __init__(self,qso,root=None):

        # Init
        print('QSO INSPECTOR: Init ...')
        self.root=root
        self.qso=qso
        self.qso2={}
        self.Changed=False
        self.SkipRemaining=False
        
        if root:
            self.win=Toplevel(root)
            self.Hide()
            #print('Top-level')
        else:
            self.win = Tk()
            #print('Root')
        self.win.title("QSO Inspector")

        row=-1
        self.boxes=[]
        self.keys=qso.keys()
        for key in self.keys:
            row+=1
            Label(self.win, text=key+':').grid(row=row, column=0)
            box = Entry(self.win)
            box.grid(row=row,column=1,sticky=E+W)
            #box.delete(0, END)  
            self.boxes.append(box)
            try:
                box.insert(0,qso[key])
            except:
                pass
        
        row+=1
        col=0
        button = Button(self.win, text="OK",command=self.Dismiss)
        button.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(button, ' Done with this entry ' )

        col+=1
        button = Button(self.win, text="Snip",command=self.Snip)
        button.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(button, ' Snip Audio for this entry ' )

        col+=1
        button = Button(self.root, text='QRZ ?',command=self.Call_LookUp,\
                         takefocus=0 ) 
        button.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(button, ' Query QRZ.com ' )
        
        col+=1
        button = Button(self.win, text="Cancel",command=self.Hide)
        button.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(button, ' Skip this entry ' )

        col+=1
        button = Button(self.win, text="Skip Rest",command=self.SkipRest)
        button.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(button, ' Skip remaining entries ' )

        self.win.protocol("WM_DELETE_WINDOW", self.Hide)        
        self.Show()

        print('Spinning ...')
        self.Done=False
        mainloop()
        print('... Thats all Folks!')


    def Dismiss(self):
        print('DISMISSED ... ')
        for key,box in zip(self.keys,self.boxes):
            val=box.get()
            self.qso2[key] = val
            self.Changed |= val != self.qso[key]

        self.Hide()
        self.Done=True

    def Show(self):
        print('Showing Window ...')
        self.win.update()
        self.win.deiconify()
        
    def Hide(self):
        print('Hide Window ...',self.root)
        if self.root:
            self.win.withdraw()
        else:
            print('Bye Bye')
            self.win.destroy()
            self.win=None
        self.Done=True

    def Snip(self):
        print('\n********************************** Snip Snip ...')
        t=self.qso['time_off']
        d=self.qso['qso_date_off'][-2:]
        cmd='~/Python/split_wave/split_wave.py capture_*'+d+'*.wav -snip ' + t + \
            ' && audacity SNIPPIT.wav > /dev/null 2>&1 &'
        print('\ncmd=\n',cmd,'\n')
        os.system(cmd)

    def Call_LookUp(self):
        call = self.qso['call']
        if len(call)>=3:
            print('CALL_LOOKUP: Looking up '+call+' on QRZ.com')
            link = 'https://www.qrz.com/db/' + call
            webbrowser.open(link, new=2)

    def SkipRest(self):
        print('SkipRest ...')
        self.SkipRemaining=True
        self.Dismiss()
        
        
