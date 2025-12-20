#!/usr/bin/env -S uv run --script

# adifttols is suppose to read into a pandas data frame but is a garbage library - Doesn't work

import os
import adiftools.adiftools as adiftools

fname=os.path.expanduser('~/AA2IL/AA2IL.adif')
print(fname)

adi = adiftools.ADIFParser()
df_adi = adi.read_adi(fname) 
print(df)
