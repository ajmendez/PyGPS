#!/usr/bin/python

# [system]
import os
import sys

# [installed]
import psycopg2
import pymendez

# [Package]
from pygps import gps

import xml.dom.minidom
# from xml.dom.minidom import Node
# from stat import *







class DB(object):
  '''A database object that connects to the locate system'''
  def __init__(self):
    '''setup the database connection for further awesomeness'''
    params = ['user','password','dbname', 'host','port']
    credentials = pymendez.auth('postgres', params)
  
    # Build the string that we connect with
    conn_string = ("{param}='{value}'".format(param=p,value=v) 
                   for p,v in zip(params,credentials))
    conn_string = ' '.join(conn_string)
    # print conn_string
    
    self.db = psycopg2.connect(conn_string)
    self.cursor = self.db.cursor()
  
  def __enter__(self):
    '''Constructor does not need anything besides init'''
    return self
  
  def __exit__(self, type, value, traceback):
    '''Close it all down!'''
    self.cursor.close()
    self.db.close()
  
  def e(self, statement):
    '''e is for execute.  Returns the first fetched result from the cursor'''
    self.cursor.execute(statement)
    return self.cursor.fetchone()
    
  
  def _isfile(self, filename):
    '''returns true if the file is already added'''
    
  
  def add_file(self, filename):
    '''Adds a file '''
    # ensure that we have the full path name
    filename = pymendez.niceFile(filename)
    name = os.path.splitext(os.path.basename(filename))[0]
    cmd = "SELECT * FROM files where filename='{}'".format(filename)
    
    if self.e(cmd):
      pymendez.cprint('Already added file: {}'.format(filename), color='green')
      return
    
    data = gps.load(filename)
    
    
    point = "POINT({} {})".format(lat,lon)
    geom = "Transform( ST_GeomFromText('{}', 4326), 900913)".format(point)
    cmd = """INSERT INTO files (filename, name, geom, timestamp) 
                VALUES ('{}', '{}', '{}') 
                RETURNING id;""".format(filename, name, geom)
    file_id = self.e(cmd)
      
  def parse_files(self):
    '''Load the data from each file and import it to the database'''
    # "SELECT * FROM gpx_files where filename = '" + filename + "' and gps_name = '" + gps_name + "';"
  
def load_gpx(gps_name,filename):
  cursor.execute()
  if cursor.fetchone():
    return

  path = gps_name + "/Traces/" + filename
  os.system("unzip -j " + path)  
  unzipped = filename.replace(".zip","")
  
  doc = xml.dom.minidom.parse(unzipped)
  os.system("rm " + unzipped)
  
  size = str(os.stat(path)[ST_SIZE])
  trkpt = doc.getElementsByTagName("trkpt")[0]
  lat = trkpt.getAttribute("lat")
  lon = trkpt.getAttribute("lon")
  time = trkpt.getElementsByTagName("time")[0].firstChild.data

  cursor.execute("INSERT INTO gpx_files (filename,size,gps_name,geom,timestamp) values ('" + filename + "','" + size + "','" + gps_name + "'," + " Transform( ST_GeomFromText('POINT(" + lon + " " + lat + ")', 4326), 900913)" + ",'" + time + "') RETURNING id;")

  gpx_id = cursor.fetchone()[0]

  trkid = 0
  for trk in doc.getElementsByTagName("trk"):
    trkid += 1
    for trkseg in trk.getElementsByTagName("trkseg"):
      for trkpt in trkseg.getElementsByTagName("trkpt"):
        lat = trkpt.getAttribute("lat")
        lon = trkpt.getAttribute("lon")
        ele = trkpt.getElementsByTagName("ele")[0].firstChild.data
        time = trkpt.getElementsByTagName("time")[0].firstChild.data
        cursor.execute("INSERT INTO gps_points (altitude,trackid,geom,gpx_id,timestamp) values ('" + ele + "','" + str(trkid) + "'," + " Transform( ST_GeomFromText('POINT(" + lon + " " + lat + ")', 4326), 900913)" + ",'"  + str(gpx_id) + "','"  + time + "');")

  conn.commit()
  exit()
  
if __name__ == "__main__":
  filename = pymendez.niceFile('~/tmp/gps/short.gpx')
  
  db = DB()
  db.add_file(filename)
  
  doc = xml.dom.minidom.parse(filename)
  trkpt = doc.getElementsByTagName("trkpt")[0]
  lat = trkpt.getAttribute("lat")
  lon = trkpt.getAttribute("lon")
  time = trkpt.getElementsByTagName("time")[0].firstChild.data
  
  print filename
  print lat
  print lon
  
  # db_connect()
  # 
  # for entry in os.listdir('.'):
  #   if os.path.exists(entry + '/Traces/'):
  #     for filename in os.listdir(entry + '/Traces/'):
  #       if filename.find(".gpx.zip") != -1:
  #         load_gpx(entry, filename)  
  # 
  # db_close()
