#!/usr/bin/env -S uv run --script

# Some preliminary database explorations - using sqlalchemy
# This is a dead-end for now - use sqlite3 instead

import os,sys
from fileio import *
import pandas as pd 
import sqlalchemy as db

# Read the ADIF file
fname=os.path.expanduser('~/AA2IL/AA2IL.adif')
print('\nReading adif file ',fname,'...')
QSOS = parse_adif(fname,verbosity=0)
print(len(QSOS))
print(QSOS[0])

print('\nResulting Pandas data frame:')
df = pd.DataFrame.from_dict(QSOS)
print(df)

# Open database
fname3='sqlite:///'+fname.replace('.adif','.db')
print(fname3)
engine = db.create_engine(fname3)

# Export to SQL
df.to_sql('QSOs', engine, if_exists='replace', index=False)

# Close up database
#engine.commit()
#engine.close()


# Read it back
print('Reading SQL file ',fname3,'...')
engine2 = db.create_engine(fname3)
df3 = pd.read_sql('SELECT * FROM QSOs', engine2)
print(df3)

