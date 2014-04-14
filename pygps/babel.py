# gps file reading using gpsbabel
from pymendez.files import niceFile as nicefile
import numpy as np
import pylab
import tempfile
import pylab

import gpsbabel
import gpxpy
import compressed

def readgpx(infile, outfile):
    gps = gpsbabel.GPSBabel()
    gps.addInputFile(infile, 'mtk-bin')
    gps.addOutputFile(outfile,'unicsv')
    # gps.addFilter('discard','sat=3')
    # gps.addFilter('discard',dict(sat=3))
    # gps.addFilter('position', dict(distance='1f'))
    
    # gps.procRoutes = True
    # gps.procTrack = True
    # gps.procWpts = True
    try:
        gps.execCmd(parseOutput = False)
    except Exception as e:
        print e
        print 'FAILED: ', infile


    
def parsegpx(infile):
    gpx = gpxpy.parse(open(infile,'r').read())
    print 'Tracks: ', len(gpx.tracks)
    print 'Way points: ', len(gpx.waypoints)
    print 'Routes: ', len(gpx.routes)
    return GPX(gpx)

class GPX(object):
    def __init__(self, gpx):
        self.gpx = gpx
    def __getattr__(self, name):
        try:
            return [getattr(w,name) for w in self.gpx.waypoints]
        except Exception as e:
            print e
            return getattr(self.gpx, name)

def plotgpx(gpx):
    pylab.scatter(gpx.longitude, gpx.latitude, c=gpx.elevation, 
                  marker='.', edgecolor='none', alpha=0.5)
    # pylab.hist(gpx.elevation, 100)
    pylab.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    pylab.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    pylab.show()
    
    
def read(filename):
    tmp = tempfile.NamedTemporaryFile()
    readgpx(filename, tmp.name)
    print tmp.read()
    # gpx = parsegpx(tmp.name)
    # plotgpx(gpx)

def getfiles():
    directory = nicefile('~/Dropbox/Personal/_archive/')
    files = ['gpsdata_20110831.tar.gz', 'gps_20120416.tar.gz',  'gpsdata_20140412.tar.gz']

    k = 0
    tmpfile = nicefile('~/Desktop/tmp')
    for filename in files:
        print filename
        with compressed.Archive(directory + '/' + filename) as arch:
            for fname, data in arch.genbyfilename('*.bin'):
                print ' '+fname
                open(tmpfile,'w').write(data)
                readgpx(tmpfile, nicefile('~/Desktop/gpsdata/gpsdata_{:04d}.csv'.format(k)))
                k += 1
                # break
    

    

if __name__ == '__main__':
    # filename = nicefile('~/tmp/gps/BT747log.bin')
    # read(filename)
    getfiles()
    
    