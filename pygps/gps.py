# parse the individual gps files
import os
import csv
import collections
import fnmatch
import xml.dom.minidom
import datetime

from pymendez import files

GPSITEM = collections.namedtuple('GPSITEM', ['lat','lon','height','time'])


class CSV(object):
    def __init__(self, filename, data=None):
        self.filename = filename
        
        if data is None:
            self.data = open(filename, 'r')
        elif isinstance(data, str):
            self.data = data.splitlines()
        else:
            self.data = data
        
        self.csv = csv.reader(self.data)
        self.header = [x.lower() for x in self.csv.next()]
    
    def __iter__(self):
        '''by default iterate over some nice items that gps items generally
         needed by the system'''
        items = ['date','time',
                 'lat*','n/s', 'lon*','e/w', 
                 'height*', 'distance*']
        tmp = [item.replace('*','').replace('/','') for item in items]
        out = collections.namedtuple('gpsitems', tmp)
        for args in self.genbyitems(items):
            # yield out(*args)
            tmp = out(*args)
            yield self.convert(tmp)
    
    def genbyitems(self, items):
        '''for each item in the csv grab some list of items 
        matches the header by glob and the sort.  Case insensitive.'''
        names = [fnmatch.filter(self.header, item)[0] for item in items]
        index = [self.header.index(name) for name in names]
        
        try:
            for row in self.csv:
                yield [row[i] for i in index]
        finally:
            self.data.seek(0)
            self.csv.next()
    
    def convert(self, gpsitem):
        '''Convert into a nice (x,y,z,t) tuple
        lat, lon are in degrees
        height is in meters
        time is a datetime object at gmt
        # 2013-08-31T03:06:27.000Z
        # '2012/10/24', '07:11:47.000'
        '''
        return GPSITEM( float(gpsitem.lat),
                        float(gpsitem.lon),
                        float(gpsitem.height),
                        datetime.datetime.strptime(
                            '{} {}'.format(gpsitem.date, gpsitem.time),
                            '%Y/%m/%d %H:%M:%S.000'), )
        
            
            






class GPX(object):
    def __init__(self, filename, data=None):
        self.filename = filename
        self.doc = xml.dom.minidom.parse(filename)
    
    # @profile
    def __iter__(self):
        '''Default get the basics'''
        items = ['time', 'lat','lon', 'ele']
        out = collections.namedtuple('gpsitems', items)
        for args in self.genbyitems(items):
            # yield out(*args)
            tmp = out(*args)
            yield self.convert(tmp)
    
    
    def genbyitems(self, items):
        '''Generate the data from the document.'''
        
        def _get(tree, tag):
            '''Simplify the dom traversal'''
            return tree.getElementsByTagName(tag)
        
        def _attr(tree, tag):
            '''Get an attribute from the dom -- lat, lon'''
            return tree.getAttribute(tag)
        
        def _tag(tree, tag):
            return tree.getElementsByTagName(tag)[0].firstChild.data
        
        def _map(tag):
            '''Map the nice tag names into gpx'''
            M = {
                'LATITUDE':    'lat',
                'LONGITUDE':   'lon',
                'HEIGHT(m)':   'ele', # seems to be meters
                'SPEED(km/h)': 'speed',
            }
            return M.get(tag, tag)
        
        def _fmap(tag):
            if tag in ('lat', 'lon'):
                return _attr
            else:
                return _tag
        
        names = map(_map, items)
        fcns = map (_fmap, names)
        
        for track in _get(self.doc, 'trk'):
            for segment in _get(track, 'trkseg'):
                for point in _get(segment, 'trkpt'):
                    yield [fcn(point,name) for fcn,name in zip(fcns, names)]
    
    
    def convert(self, gpsitem):
        '''convert into a nice tuple
        # 2013-08-31T03:06:27.000Z
        
        '''
        return GPSITEM(float(gpsitem.lat),
                       float(gpsitem.lat),
                       float(gpsitem.ele),
                       datetime.datetime.strptime(
                           gpsitem.time,
                           '%Y-%m-%dT%H:%M:%S.000Z'),
                )



class GPSFile(object):
    def __init__(self, filename):
        '''GPSFile is a wrapper around either GPX or CSV to allow agnostic importing
        of things.'''
        if '.gpx' in filename:
            self.data = GPX(filename)
        elif '.cvs' in filename:
            self.data = CSV(filename)
    



# @profile
def test():
    from pysurvey import util
    util.setup_stop()
    
    # filename = files.niceFile('~/tmp/gps/short.csv')
    # csv = CSV(filename)
    # for x in csv:
    #     print x
    #     break
    # for x in csv:
    #     print x
    #     break
        
    
    filename = files.niceFile('~/tmp/gps/short.gpx')
    gpx = GPX(filename)
    for x in gpx:
        print x
        break

# http://wiki.openstreetmap.org/wiki/Mercator
import math
def y2lat(a):
    return 180.0/math.pi*(2.0*math.atan(math.exp(a*math.pi/180.0))-math.pi/2.0)
def lat2y(a):
    return 180.0/math.pi*math.log(math.tan(math.pi/4.0+a*(math.pi/180.0)/2.0))

def merc_x(lon):
    r_major = 6378137.000
    return r_major*math.radians(lon)
 
def merc_y(lat):
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5
    r_major = 6378137.000
    r_minor = 6356752.3142
    
    temp = r_minor/r_major
    eccent = math.sqrt(1-temp**2)
    phi = math.radians(lat)
    sinphi = math.sin(phi)
    con = eccent*sinphi
    com = eccent/2
    con = ((1.0-con)/(1.0+con))**com
    ts = math.tan((math.pi/2-phi)/2)/con
    y = 0-r_major*math.log(ts)
    return y

def getbounds(location):
    '''http://download.geofabrik.de/north-america.html
    http://boundingbox.klokantech.com/
    '''
    bounds = dict(
        sandiego=[-117.4773385039,32.5719017933,-116.3670803398,33.2681644656,],
        world=[-180,-90,180,90],
    )
    xmin,ymin,xmax,ymax = bounds[location]
    mercbounds = merc_x(xmin), merc_y(ymin), merc_x(xmax), merc_y(ymax)
    print '{0} {1[0]:0.2f} {1[1]:0.2f} {1[2]:0.2f} {1[3]:0.2f}'.format(location, mercbounds)
    return mercbounds
    


if __name__ == '__main__':
    # test()
    getbounds('world')
    getbounds('sandiego')