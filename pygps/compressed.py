# compressed.py -- some nice utilities for compressed files and the sort
import os
import re
import tarfile
import zipfile
import fnmatch
from pymendez import files

EXCLUDED_FILES = [
    '.DS_Store',
]

class Archive(object):
    '''Allows you to walk through the files in a tar file. or
    search for one.'''
    def __init__(self, filename):
        self.filename = filename
        if '.zip' in filename:
            self.archive = zipfile.open(filename)
        elif 'tar' in filename:
            self.archive = tarfile.open(filename)
    
    def __enter__(self):
        '''with constructor'''
        return self
    
    def __exit__(self, type, value, traceback):
        '''Close the tar file'''
        self.archive.close()
    
    def __iter__(self):
        '''By default iterate over names and data'''
        for name, data in self.genfiles():
            yield name, data
    
    def getdata(self, item):
        '''Get the ascii data for a item.  Item can either be a member
        or a file name in the archive.'''
        return self.archive.extractfile(item).read()
    
    def gennames(self):
        '''iterator over the names of files -- ignores directories'''
        for member in self.archive.getmembers():
            name = member.name
            isokfile = any([f not in name for f in EXCLUDED_FILES])
            if member.isfile() and isokfile:
                yield member.name
    
    def genfiles(self):
        '''generator -- get a list of the filenames and file data.  This
        assumes that the files are nice ascii data.  '''
        for name in self.gennames():
            data = self.getdata(name)
            yield name, data
    
    def genbyfilename(self, filestring):
        '''get a filename and data by a given string.  This allows 
        for searching for things by globs and question marks for 
        nice things.  Allows you to search for all files that have
        some string in them.'''
        magic_check = re.compile('[*?[]')
        for file in self.gennames():
            if magic_check.search(filestring) is not None:
                # dirname, basename = os.path.split(file)
                if fnmatch.fnmatch(file, filestring):
                    yield file, self.getdata(file)
            elif filestring in file:
                yield file, self.getdata(file)
                
                

if __name__ == '__main__':
    filename = files.niceFile('~/tmp/python/tar/lastfm_2013.08.29.tar.gz')
    tar = Archive(filename)
    for file,data in tar.genbyfilename('*44066acd99d803f382f7c840eba8cd1*'):
        print file
    
    filename = files.niceFile('~/Dropbox/Personal/_archive/gps_20120416.tar.gz')
    tar = Archive(filename)
    for file, data in tar.genbyfilename('*.csv'):
        print file
    
    # for x in tar.gennames():
    #     print x
    # 
    # for name, data in tar.genfiles():
    #     print name
    #     print data
    #     break
    # 
    
    