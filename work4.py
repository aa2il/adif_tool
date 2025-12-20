#!/usr/bin/env -S uv run --script

# Some preliminary database explorations - inserting new data

import os,sys
from fileio import *
import pandas as pd
import sqlite3

#import sqlalchemy as db
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

# Read database
fname=os.path.expanduser('~/AA2IL/AA2IL.db')
print('\nReading SQL file ',fname,'...')
conn = sqlite3.connect(fname)
cursor = conn.cursor()
#engine = db.create_engine('sqlite:///'+fname)
df = pd.read_sql('SELECT * FROM QSOs', conn)
print('Current DB:\n',df)

# Read the new qsos
fname2=os.path.expanduser('New.adif')
print('\nReading New.adif file ',fname2,'...')
QSOS = parse_adif(fname2,verbosity=0)
df2 = pd.DataFrame.from_dict(QSOS)
print('New:\n',df2)

# Concat the two dataframes
print('\nMerging ...')
df3=pd.concat([df,df2],ignore_index=True)
print('Merged:\n',df3)

# Remove dupes
dupes = df3[df3.duplicated()]
print('\nDupes:\n',dupes)
df3.drop_duplicates(inplace=True)
print('\nLess Dupes:\n',df3)

# Export updated DB
df3.to_sql('QSOs', conn, if_exists='replace', index=False)
conn.close()

# Read it back
print('\nReading SQL file ',fname,'...')
conn2 = sqlite3.connect(fname)
df4 = pd.read_sql('SELECT * FROM QSOs', conn2)
print('Read-back:\n',df4)
conn.close()

sys.exit(0)


# Add the new QSOs - this adds them all w/o checking for dupes :-(
print('\nAdding new QSOs to data base ...')
df2.to_sql(
    name='QSOs',          # The name of the table in the database
    con=conn,             # The database connection (Engine or Connection)
    if_exists='append',
    index=False,          # Do not write the DataFrame's index as a column
    method='multi'        #  Use multi-row insertion

)
conn.close()

# Lets see what happend
print('\nRe-reading SQL file ',fname,'...')
conn2 = sqlite3.connect(fname)
cursor2 = conn2.cursor()
df3 = pd.read_sql('SELECT * FROM QSOs', conn2)
print(df3)

# Remove dupes    
dupes = df[df3.duplicated()]
print('\nDupes:\n',dupes)
df3.drop_duplicates(inplace=True)
print('\nLess Dupes:\n',df3)

sys.exit(0)

sql=f"""SELECT * FROM QSOs
WHERE EXISTS (
  SELECT 1 FROM Pets p2 
  WHERE Pets.PetName = p2.PetName
  AND Pets.PetType = p2.PetType
  AND Pets.rowid > p2.rowid
);"""

cursor2.execute(sql)
conn2.close()



sys.exit(0)

qso=QSOS[0]
print(qso,type(qso))

inspector = db.inspect(engine)
print(inspector)
print('\nTABLES:',inspector.get_table_names())

columns = inspector.get_columns('QSOs')
for col in columns:
   print(col['name'])


metadata = db.MetaData()
metadata.reflect(bind=engine)
tab = db.Table("QSOs", metadata, autoload_with=engine)
print( [c.name for c in tab.columns] )
print(type(tab))
print(tab)
print(tab(**qso))

sys.exit(0)

Session = sessionmaker(bind=engine)
session = Session()
session.merge(QSOs(**qso))
session.commit()


# Lets see what happend
print('\nRe-reading SQL file ',fname,'...')
engine2 = db.create_engine('sqlite:///'+fname)
df3 = pd.read_sql('SELECT * FROM QSOs', engine2)
print(df3)


sys.exit(0)

"""
# Add the new QSOs - this adds them all w/o checking for dupes :-(
print('\nAdding new QSOs to data base ...')
df2.to_sql(
    name='QSOs',          # The name of the table in the database
    con=conn,             # The database connection (Engine or Connection)
    if_exists='append',
    index=False,          # Do not write the DataFrame's index as a column
    method='multi'        #  Use multi-row insertion

)
conn.close()
"""

print('Creating temp staging area ...')
temp_table_name = 'staging_area'
df.to_sql(
    name=temp_table_name,
    con=engine,
    if_exists='replace',
    index=False
)

print('Inserting new QSOs ...')
with engine.begin() as conn:
   sql = """INSERT INTO QSOs (Col1, Col2, Col3, ...)
            SELECT t.Col1, t.Col2, t.Col3, ...
            FROM {temp_table_name} t
            WHERE NOT EXISTS 
                (SELECT 1 FROM QSOs f
                 WHERE t.MatchColumn1 = f.MatchColumn1
                 AND t.MatchColumn2 = f.MatchColumn2)"""

   conn.execute(sql)
   
# Lets see what happend
print('\nRe-reading SQL file ',fname,'...')
engine2 = db.create_engine('sqlite:///'+fname)
df3 = pd.read_sql('SELECT * FROM QSOs', engine2)
print(df3)
