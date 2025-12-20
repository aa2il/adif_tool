#!/usr/bin/env -S uv run --script

# Some preliminary database explorations - using sqlite
# The SQL scripting lang seems combersome - try using pandas data frame instead

import os
import adif_io
import sqlite3

# Read the ADIF file
fname='~/AA2IL/AA2IL.adif'
fname2=os.path.expanduser(fname)
print(fname2)
qsos_raw, adif_header = adif_io.read_from_file(fname2)

print(adif_header)
print(len(qsos_raw))
print(qsos_raw[0])
print(type(qsos_raw[0]))
print(dict(qsos_raw[0]).keys())
print(dict(qsos_raw[0]))
print(qsos_raw[0]['CALL'])

# Open database
fname3=fname2.replace('.adif','.db')
print(fname3)

conn = sqlite3.connect(fname3)
cursor = conn.cursor()

# Create it if necessary
cursor.execute("""
    CREATE TABLE IF NOT EXISTS qsos (
        callsign TEXT,
        qso_date TEXT,
        time_on TEXT,
        freq REAL,
        mode TEXT,
        PRIMARY KEY (callsign, qso_date, time_on)
    );
""")

# Insert qsos into database
for qso in qsos_raw:
    cursor.execute("""
       INSERT INTO qsos (callsign, qso_date, time_on, freq, mode)
       VALUES (?, ?, ?, ?, ?)
       ON CONFLICT(callsign, qso_date, time_on) DO UPDATE SET
           freq = EXCLUDED.freq,
           mode = EXCLUDED.mode;
     """, (qso.get('CALL'), qso.get('QSO_DATE'), qso.get('TIME_ON'),
           qso.get('FREQ'), qso.get('MODE')))

# Close up database
conn.commit()
conn.close()
