#!/usr/bin/env -S uv run --script

# Some preliminary database explorations - using pandas

import os,sys
from fileio import *
import pandas as pd 
import sqlite3

# Read the ADIF file
fname=os.path.expanduser('~/AA2IL/AA2IL.adif')
print('\nReading adif file ',fname,'...')
if False:
    QSOS = parse_adif(fname,verbosity=0)
    print(len(QSOS))
    print(QSOS[0])
    df = pd.DataFrame.from_dict(QSOS)
    print('\nResulting Pandas data frame:\n',df)
else:
    df = parse_adif(fname,DF=True)
    print(df)

CALL='AA3B'
print('Query for QSOs with ',CALL,'...')
df2 = df.query('call=="'+CALL+'"')
print(df2)

#sys.exit(0)

# Create SQLite connection
fname3=fname.replace('.adif','.db')
print('Writing SQL file ',fname3,'...')
conn = sqlite3.connect(fname3)

# Export to SQL
df.to_sql('QSOs', conn, if_exists='replace', index=False)

# Close connection
conn.close()

# Read it back
print('Reading SQL file ',fname3,'...')
conn = sqlite3.connect(fname3)
df3 = pd.read_sql('SELECT * FROM QSOs', conn)
print(df3)
conn.close()

sys.exit(0)

