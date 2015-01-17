import json
import io
import re
import os
import math
from operator import itemgetter



def PlusCircle(x):
    if(x < 0):
        return 360 + round(x,5)
    else:
        return round(x,5)

def addLzero(s):
    if(s<10):
        return '0'+str(s)
    else:
        return str(s)

def pol(mas,j):
    if(len(mas[j]) > 1):
        return "MultiPolygon"
    else:
        return "Polygon"

def hlen(x,y,z):#length of altitude from middle point
    chisl = math.fabs((x[1]-z[1])*y[0] + (z[0]-x[0])*y[1] + (x[0]*z[1] - z[0]*x[1]))
    znam = math.sqrt(math.pow(x[1]-z[1],2) + math.pow(z[0]-x[0],2))
    if(math.fabs(znam) < 0.000001):
        znam = 0.000001
    return chisl/znam

def preobr(lon, lat):# convert to pixels from lon/ lat
    c = 5000 # const. Lenght of Russia is about 32k pixels given c = 11k
    p = math.pi
    rlat = lat * p / 180
    rlon = lon * p / 180
    a = 6378137
    b = 6356752.3142
    f = (a-b)/a
    e = math.sqrt(2*f - f*f)
    x = c * rlon
    try:
        if(math.fabs(math.fabs(lat) - 90) < 0.0001):
            rlat = (lat + 0.0002) * p / 180
        y = c * math.log(math.fabs(math.tan(rlat/2 + p/4))*math.pow((1-e*math.sin(rlat))/(1+e*math.sin(rlat)),e/2))
    except(ValueError):
        print(lat)
        print(math.tan(rlat/2 + p/4))
    return [x,y]

def anti_preobr(x, y):#covert to lon/ lat from pixels
    c = 5000
    p = math.pi
    a = 6378137
    b = 6356752.3142
    f = (a-b)/a
    e = math.sqrt(2*f - f*f)
    phi = p/2 - 2*math.atan(math.exp(-y/c))
    dphi = 1
    i = 0
    while ((math.fabs(dphi) > 0.0000001) and i < 15):
        i = i + 1
        con = e * math.sin(phi)
        dphi = p/2 - 2*math.atan(math.exp(-y/c) * math.pow((1-con)/(1+con),e)) - phi
        phi = phi + dphi
    rlon = x/c
    lon = 180*rlon/p
    rlat = phi
    lat = 180*rlat/p
    return [lon,lat]


def find_center(rawdata):#Finding polygon center and appropriate zoom level for it
    for x in range(len(rawdata['features'])):
        rawdata['features'][x]['properties']['Center_Opt'] = {}
        if(rawdata['features'][x]['geometry']['type'] == 'Polygon'):
            px = []
            py = []
            for y in rawdata['features'][x]['geometry']['coordinates']:
                for z in y:
                    p = preobr(z[0],z[1])
                    px.append(p[0])
                    py.append(p[1])
            zoom_const = max(max(px) - min(px),max(py) - min(py))
            if zoom_const > 5000:
                c = [0.5*(max(px) + min(px)),0.45*(max(py) + min(py))]
            else:
                c = [0.5*(max(px) + min(px)),0.5*(max(py) + min(py))]
            center = anti_preobr(c[0],c[1])
            zoom_const = max(max(px) - min(px),max(py) - min(py))
            if zoom_const > 4000:
                zoomLevel = 4
            elif zoom_const > 1500 and zoom_const <= 4000:
                zoomLevel = 5
            else:
                zoomLevel = 6
            rawdata['features'][x]['properties']['Center_Opt']['coordinates'] = center
            rawdata['features'][x]['properties']['Center_Opt']['zoom_level'] = zoomLevel
        if(rawdata['features'][x]['geometry']['type'] == 'MultiPolygon'):
            px = []
            py = []
            for y in rawdata['features'][x]['geometry']['coordinates']:
                for t in y:
                    for z in t:
                        p = preobr(z[0],z[1])
                        px.append(p[0])
                        py.append(p[1])
            zoom_const = max(max(px) - min(px),max(py) - min(py))
            if zoom_const > 5000:
                c = [0.5*(max(px) + min(px)),0.45*(max(py) + min(py))]
            else:
                c = [0.5*(max(px) + min(px)),0.5*(max(py) + min(py))]
            center = anti_preobr(c[0],c[1])
            if zoom_const > 4000:
                zoomLevel = 4
            elif zoom_const > 1500 and zoom_const <= 4000:
                zoomLevel = 5
            else:
                zoomLevel = 6
            rawdata['features'][x]['properties']['Center_Opt']['coordinates'] = center
            rawdata['features'][x]['properties']['Center_Opt']['zoom_level'] = zoomLevel


def deletenodes(rawdata):#Function to simplify polygons by deleting nodes
    k = 1
    i = 0
    while k > 0:
        k = 0
        i = i + 1
        #print('iter number: ' + str(i))
        for x in range(len(rawdata['features'])):
            if(rawdata['features'][x]['geometry']['type'] == 'Polygon'):
                for y in range(len(rawdata['features'][x]['geometry']['coordinates'])):
                    for z in range(len(rawdata['features'][x]['geometry']['coordinates'][y])):
                        if (len(rawdata['features'][x]['geometry']['coordinates'][y]) < 4):
                            continue
                        if(z < len(rawdata['features'][x]['geometry']['coordinates'][y])-2):#Simplify regular polygons
                            c0 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][z][0],rawdata['features'][x]['geometry']['coordinates'][y][z][1])
                            c1 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][z+1][0],rawdata['features'][x]['geometry']['coordinates'][y][z+1][1])
                            c2 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][z+2][0],rawdata['features'][x]['geometry']['coordinates'][y][z+2][1])
                            if(hlen(c0,c1,c2) < math.sqrt(2)):#sqrt(2) is such constant that human eye won't notice a difference
                                del(rawdata['features'][x]['geometry']['coordinates'][y][z+1])
                                k = k + 1
            if(rawdata['features'][x]['geometry']['type'] == 'MultiPolygon'):
                for y in range(len(rawdata['features'][x]['geometry']['coordinates'])):
                    for t in range(len(rawdata['features'][x]['geometry']['coordinates'][y])):
                        for z in range(len(rawdata['features'][x]['geometry']['coordinates'][y][t])):
                            if (len(rawdata['features'][x]['geometry']['coordinates'][y][t]) < 4):
                                continue
                            if(z < len(rawdata['features'][x]['geometry']['coordinates'][y][t])-2):#Simplify multipolygons
                                c0 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][t][z][0],rawdata['features'][x]['geometry']['coordinates'][y][t][z][1])
                                c1 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][t][z+1][0],rawdata['features'][x]['geometry']['coordinates'][y][t][z+1][1])
                                c2 = preobr(rawdata['features'][x]['geometry']['coordinates'][y][t][z+2][0],rawdata['features'][x]['geometry']['coordinates'][y][t][z+2][1])
                                if(hlen(c0,c1,c2) < math.sqrt(2)):
                                    del(rawdata['features'][x]['geometry']['coordinates'][y][t][z+1])
                                    k = k + 1


def main():
    data_dir_raw = os.path.abspath(os.path.join(os.path.dirname(__file__), 'subdataRAW'))
    data_dir_clean = os.path.abspath(os.path.join(os.path.dirname(__file__), 'subdataClean'))
    data = {}
    data['type'] = 'FeatureCollection'
    data['features'] = []
    i = 0
    #new js file with coordinates
    with io.open('output.js','w',encoding='utf-8') as ss:
        ss.write('var SubData = ')
        for fn in os.listdir(data_dir_raw):
            with io.open(os.path.join(data_dir_raw,fn),'r',encoding='utf-8') as f:
                tmp = f.read()
                if tmp[15] == '{':
                    tmp = tmp[15:-1]
                else:
                    tmp = tmp[16:-1]
                rawdata = json.loads(tmp)
                deletenodes(rawdata)
                find_center(rawdata)
                data['features'].append(rawdata['features'][0])
                with io.open(os.path.join(data_dir_clean,'SubData' + str(i) + '.js'),'w',encoding='utf-8') as f2:   
                    w = 'var SubData' + str(i) + ' = '
                    f2.write(w)
                    json.dump(rawdata, f2,ensure_ascii = False)
                    f2.write(';')
                    i = i + 1
        json.dump(data,ss,ensure_ascii = False)
        ss.write(';')

main()
