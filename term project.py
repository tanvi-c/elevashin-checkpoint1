from cmu_graphics import *
import math
import xml.etree.ElementTree as ET 

#used Python ElementTree XML API docs https://docs.python.org/3/library/xml.etree.elementtree.html
def parseGPX(file):
    tree = ET.parse(file)
    root = tree.getroot()

    points = []
    ns = {'gdx': 'http://www.topografix.com/GPX/1/1'}

    for trackpoint in root.findall('.//gdx:trkpt', ns):
        lat = float(trackpoint.get('lat'))
        lon = float(trackpoint.get('lon'))
        ele = float(trackpoint.find('gdx:ele', ns).text)
        time = (trackpoint.find('gdx:time', ns).text)

        ext = trackpoint.find("gdx:extensions", ns)
        speed = float(ext.find("gdx:speed", ns).text)
        course = float(ext.find("gdx:course", ns).text)
        hAcc = float(ext.find("gdx:hAcc", ns).text)
        vAcc = float(ext.find("gdx:vAcc", ns).text)
        # FUTURE: extract hr

        newPt = Point(lat, lon, ele, time, speed, course, hAcc, vAcc, hr = None)
        points.append(newPt)
    
    newPath = Path(points)
    newPath.getStats()

    return newPath

# haversine is analogous to the distance function but for latitude and longitude (Source: medium.com)
# assumes Earth is a perfect sphere - minor errors OK in this app (relatively small distances) 
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000 #Earth's radius in meters
    phi1, phi2 = lat1 * (math.pi/180), lat2 * (math.pi/180)
    lam1, lam2 = lon1 * (math.pi/180), lon2 * (math.pi/180)
    a = math.sin((phi2 - phi1)/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin((lam2 - lam1)/2)**2
    c = 2 * math.atan(a**0.5, (1-a)**0.5)
    d = r * c

class Path: 
    def __init__(self, points):
        self.points = points
        self.totalDist = 0
        self.netEle= 0
        self.duration = 0
        self.dateTime = ''

    def getStats(self):
        if len(self.points) < 2:
            return

        for i in range(1, len(self.points)):
            p1 = self.points[i-1]
            p2 = self.points[i]

            d = p1.distanceTo(p2)
            self.totalDist += d
            self.netEle += (p2.ele - p1.ele)

        start, end = self.points[0], self.points[-1]
        self.duration = Path.getDuration(start, end)
    
    @staticmethod
    def getDuration(start, end):
        startDays = (start.year * 365) + ((start.month - 1)*30) + (start.day)
        startSec = startDays * 24 * 3600
        endDays = (end.year * 365) + ((end.month - 1)*30) + (end.day)
        endSec = endDays * 24 * 3600
        resHr = endSec // 3600
        resMin = (endSec - resHr * 3600) // 60
        resSec = rounded(endSec - resHr * 3600 - resMin * 60)
        return f'{resHr}:{resMin}:{resSec}'

class Point:
    #sometimes HR not recorded; current GPX does not include HR -- need to get new data set for testing
    def __init__(self, lat, lon, ele, time, speed, course, hAcc, vAcc, hr = None):
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.time = str(time)
        self.timeStr = Point.getTimeStr(self.time)
        self.speed = speed
        self.course = course
        self.hAcc = hAcc
        self.vAcc = vAcc
        self.hr = hr

    def __repr__(self):
        return f'Point(lat: {self.lat}, lon: {self.lon}, ele: {self.ele}, hr: {self.hr}) at {self.timeStr}'
    
    def getTimeStr(self, s):
    # current format: 2025-11-02T17:05:54Z
        self.year = int(s[:4])
        self.month = int(s[5:7])
        self.day = int(s[8:10])
        # default time is est -- FUTURE: make timezone options available
        utcHr = int(s[11:13])
        self.hour = int((utcHr) - 5 % 24)
        self.min = int(s[14:16])
        self.sec = int(s[17:-1])
        # FUTURE: implement hour, day, month rollover

        return f'{self.month}/{self.day}/{self.year} {self.hour}:{self.min}:{self.sec}'

    # 3D distance logic: taking the arc length of the curve is summing all the hypotenuses (dx, dy) of infinitesimally small right triangles 
    # haversine gives the horizontal distance and elevation gives vertical distance
    def distanceTo(self, other):
        if isinstance(other, Point):
            horiz = haversine(self.lat, self.lon, other.lat, other.lon)
            vert = abs(other.ele - self.ele)
            return (horiz**2 + vert**2)**0.5
    
cmu_graphics.run()