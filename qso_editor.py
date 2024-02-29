#! /usr/bin/python3 -u
################################################################################
#
# qso_editor.py - Rev. 1.0
# Copyright (C) 2024 by Joseph B. Attili, aa2il AT arrl DOT net
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
else:
    from Tkinter import *
    import tkFont
import time
import platform
from widgets_tk import StatusBar,SPLASH_SCREEN

################################################################################

# GUI for editing QSO data
class QSO_EDITOR():
    def __init__(self,root,P):

        # Inits
        self.P = P
        self.nqsos=0
        self.KEYS=['call','band','mode','qso_date','time_off']
        self.nkeys=0
        self.QSOs=[]

        # Open main or pop-up window depending on if "root" is given
        if root:
            self.win=Toplevel(root)
            self.hide()
        else:
            self.win = Tk()
        self.win.title("QSO Editor by AA2IL")
        self.win.geometry('1700x240+100+10')
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

        # Entry boxes for editing
        self.row=0
        self.col=0
        self.Frame1 = Frame(self.root)
        self.Frame1.pack(fill=BOTH)
        self.boxes={}
        for key in self.KEYS:
            label = Label(self.Frame1,text=' '+key+':',font=self.font)
            label.grid(row=self.row,column=self.col,columnspan=1)
            box    = Entry(self.Frame1,font=self.font,selectbackground='lightgreen')
            box.grid(row=self.row,column=self.col+1,columnspan=1)
            self.boxes[key]=box
            self.col+=2
            if self.col>10:
                self.row+=1
                self.col=0
        
        # List box with a scrool bar
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
        
        
    # Routine to add qsos to the scroll box
    def add_qsos(self,qsos):

        for qso in qsos:
            
            for key in qso.keys():
                if key not in self.KEYS:
                    self.KEYS.append(key)
        
            try:
                call     = qso['call']
                date     = qso['qso_date']
                time_off = qso['time_off']
                band     = qso['band']
                mode     = qso['mode']
            except:
                print(qso)
                sys.exit(0)
            
            self.nqsos+=1
            self.QSOs.append(qso)
            
            self.lb.insert(END, " %8s %8s  %-10.10s  %4s %4s" % \
                           (date,time_off,call,band,mode))
            if self.nqsos % 2:
                c='bisque'
            else:
                c='lemon chiffon'
            self.lb.itemconfigure(END, background=c)

            # Make latest (last) qso visible
            sb=self.scrollbar.get()
            self.lb.yview_moveto(sb[1])
        
        print('KEYS=',self.KEYS)

    # Handler for when an entry is selected
    def LBLeftClick(self,event):
        print('LBLeftClick ...')
        w=event.widget
        if len( w.curselection() ) > 0:
            index = int(w.curselection()[0])
            value = w.get(index)
            print('You selected item %d: "%s"' % (index, value))

            qso=self.QSOs[index]
            print('qso=',qso)

            for key in self.boxes.keys():
                box=self.boxes[key]
                box.delete(0,END)
                box.insert(0,qso[key])
                
        
################################################################################

# If this file is called as main, run as independent exe
# Not quite there yet ...
if __name__ == '__main__':

    from settings import read_settings
    from fileio import parse_adif
    
    print('Howdy Ho!')
    
    # Structure to contain processing params
    class EDITOR_PARAMS:
        def __init__(self):

            # Init
            self.SMALL_FONT=False
            
            # Read config file
            self.SETTINGS,RCFILE = read_settings('.keyerrc')

            
    # Set basic run-time params
    P=EDITOR_PARAMS()

    # Create GUI
    P.Editor = QSO_EDITOR(None,P)
    
    # Read ADIF log
    DIR_NAME = os.path.expanduser( '~/.fldigi/logs/' )
    MY_CALL=P.SETTINGS['MY_CALL']
    #fname=DIR_NAME+MY_CALL+'.adif'
    fname=MY_CALL+'.adif'
    print('Input file:',fname)
    qsos = parse_adif(fname)
    print("\nThere are ",len(qsos)," input QSOs ...")
    print('Last qso=',qsos[-1])

    # Populate editor
    P.Editor.add_qsos(qsos)
    
    # And away we go!
    #P.Editor.status_bar.setText("Let's Rock!")
    mainloop()

    print("Y'all come on back now ya hear!")

    
