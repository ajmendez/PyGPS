#!/usr/bin/env python
import os
import sys
import glob
import pandas as pd
import numpy as np

DIRECTORY = os.path.expanduser('~/data/gps')
EXT = 'csv'

def getfilenames(directory, ext):
    '''Walk a directory searching for specific extensions.  Sorted list returned.'''
    return sorted(glob.glob(os.path.join(directory, '*.{}'.format(ext))))


def getlines(filename):
    '''Wrapper around read_csv(pandas) to read a file and deal with the datestamp'''
    df = pd.read_csv(filename, parse_dates=[['DATE','TIME']])#.set_index('DATE_TIME')
    return df

def walk(directory=DIRECTORY, ext=EXT):
    '''Combine a number of files in a directory de-duping in the process'''
    out = None
    for filename in getfilenames(directory, ext):
        df = getlines(filename)
        if out is None:
            out = df
        else:
            # out = pd.concat([out,df], verify_integrity=True)
            out = pd.merge(out, df, how='outer')
        print filename, len(df), len(out)
    return out


if __name__ == '__main__':
    '''August 7th though Sept 1.'''
    directory = os.path.expanduser('~/tmp/gps/combine/')
    walk(directory)
    
    
    
