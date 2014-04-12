# gps file reading using gpsbabel
from pymendez.files import niceFile as nicefile
import numpy as np
import pylab

import gpsbabel


def read(filename):
    gps = gpsbabel.GPSBabel()
    gps.addInputFile(filename, 'mtk-bin')
    gps.addOutputFile('test.gpx')
    # gps.procRoutes = True
    # gps.procTrack = True
    # gps.procWpts = True
    print gps.execCmd(parseOutput = False)
    print 'done'



if __name__ == '__main__':
    filename = nicefile('~/tmp/gps/BT747log.bin')
    read(filename)
    