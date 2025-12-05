from cmu_graphics import *
from datetime import datetime, timezone
import math
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
from scipy.interpolate import griddata
import numpy as np
import tkinter as tk
from tkinter import filedialog

API = 'AIzaSyDvs5RfWLpzL4Ran3tDXuSRJ5utd9D76K4'

def onAppStart(app):
    app.setMaxShapeCount(10000)
    app.isStartToSat = False
    app.stepsPerSecond = 10000
    app.age, app.HRR = 0, 0

def start_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'lemonChiffon')
    drawImage('https://github.com/tanvi-c/elevashin-checkpoint1/blob/main/title%20img.jpg?raw=true',
              app.width/8, app.height/8, width = 3 * app.width/4, height = 3 * app.height/4)
    drawLine(app.width/2 - 70, 2 * app.height/3, app.width/2 + 70, 2 * app.height/3, lineWidth = 4)
    drawLine(app.width/2 - 70, 2 * app.height/3 + 50, app.width/2 + 70, 2 * app.height/3 + 50, lineWidth = 4)
    drawArc(app.width/2 - 70, 2 * app.height/3 + 25, 50, 53, 90, 180, fill = None, border = 'black', borderWidth = 4)
    drawArc(app.width/2 + 70, 2 * app.height/3 + 25, 50, 53, 270, 180, fill = None, border = 'black', borderWidth = 4)
    drawRect(app.width/2 - 75, 2 * app.height/3 + 2.5, 150, 45, fill = 'lemonChiffon')
    if app.isStartToSat:
        text = "Let's Plot!"
        sz = 24
    else:
        text = 'START!'
        sz = 32
    drawLabel(f'{text}', app.width/2, 2 * app.height/3 + 25, size = sz, bold = True, font = 'monospace')

def start_onMousePress(app, mouseX, mouseY):
    if app.width/2 - 70 < mouseX < app.width/2 + 70 and 2 * app.height/3 < mouseY < 2 * app.height/3 + 50:
        if app.isStartToSat:
            setActiveScreen('sat')
        else:
            gpx = getGPX()
            if gpx == None:
                gpx = '../test.gpx'

            reset(app, gpx)
            
            # Prompting questions
            res1 = app.getTextInput('Please enter your age.')
            if res1 != None and res1.isdigit():
                app.age = int(res1)
                res2 = app.getTextInput('Please enter your resting heart rate or 0 if unknown.')
                if res2 != None and res2.isdigit():
                    if res2 == '0':
                        app.RHR = 65
                    else:
                        app.RHR = int(res2)
                    app.isStartToSat = True
                    app.HRR = (207 - 0.7 * app.age) - app.RHR 
                else:
                    app.getTextInput('Please enter your resting heart rate or 0 if unknown.')
            else:
                app.getTextInput('Please enter your age.')

def sat_redrawAll(app):
    centX = app.width - ((app.width - app.imgW) / 2)
    drawRect(0, 0, app.width, app.height, fill = 'seashell')
    
    colors = {0: 'cornflowerBlue', 1: 'aqua', 2: 'greenYellow',
              3: 'orange', 4: 'deepPink', 5: 'dimGray'}
    
    if app.map != None:
        drawImage(app.map, 0, 0, width = app.imgW, height = app.imgH)

    for i in range(len(app.plotPoints) - 1):
        x1, y1 = app.plotPoints[i]
        x2, y2 = app.plotPoints[i + 1]
        n = app.path.getColorIndex(app, app.path.points[i])
        color = colors[n]
        if i == app.currDot:
            currX, currY = app.plotPoints[i]
            drawCircle(currX, currY, 8, fill = 'white')
        drawLine(x1, y1, x2, y2, fill = color)

    # Key 
    drawRect(centX - 55, 270, 110, 240, fill = None, border = 'black')
    drawLabel('Key', centX, 290, size = 24, font = 'monospace')
    for i in range(5):
        drawRect(centX - 40, 30 * i + 320, 20, 20, fill = colors[i])
        drawLabel(f'Zone {i + 1}', centX - 10, 30 * i + 330, align = 'left', size = 14, font = 'monospace')

    drawStar(centX - 30, 485, 15, 5, fill = 'lightgray', border = 'black', borderWidth = 1)
    drawLabel('Miles', centX - 10, 485, align = 'left', size = 14, font = 'monospace')

    # Show stats when mouse over point
    if app.selectedDot != None:
        currX, currY = app.plotPoints[app.selectedDot]
        curr = app.path.points[app.selectedDot]
        drawCircle(currX, currY, 4, fill = 'gray')
        drawRect(currX+10, currY-40, 95, 35, fill = 'lightgray')
        drawLabel(f'Pace: {pythonRound(curr.speed * 2.23694, 2)} mph', currX+15, currY-30, align = 'left')
        drawLabel(f'Elev: {pythonRound(curr.ele * 3.28084, 2)} ft', currX+15, currY-15, align = 'left')

    # Mile Markers
    for i in range(len(app.path.markers)):
        currX, currY = app.plotPoints[app.path.markers[i]]
        drawStar(currX, currY, 16, 5, fill = 'lightgray', border = 'black', borderWidth = 1)
        drawLabel(f'{i + 1}', currX, currY, fill = 'black', size = 10)
    
    # Exercise Summary
    drawLabel(f'SUMMARY', centX, 35, size = 32, font = 'monospace', bold = True)
    drawLabel(f'Distance: {pythonRound(app.path.totalDist, 2)} miles', centX, 
              70, font = 'monospace', size = 18)
    drawLabel(f'Duration: {app.path.durationStr}', centX, 95, 
              font = 'monospace', size = 18)
    drawLabel(f'Avg Speed: {pythonRound(app.path.avgSpeed, 2)} mph', centX, 
              120, font = 'monospace', size = 18)

    # Speed / HR button
    if app.isSpeedSelected:
        mode = 'SPEED'
        color = 'gray'
        otherColor = 'white'
    else:
        mode = 'HEART RATE'
        color = 'lightgray'
        otherColor = 'black'
    drawRect(centX - 70, 155, 140, 40, fill=color)
    drawLabel(f'{mode}', centX, 175, fill = otherColor, size = 18, font = 'monospace')
    drawLabel('Press to Toggle', centX, 205, size = 12, font = 'monospace')
    
    if not app.isHRAvail:
        drawLabel('HR Data Unavailable', centX, 235, size = 16, font = 'monospace',
                  italic = True)
    
    # Elevate Score
    drawRect(centX, 550, 200, 30, fill=gradient('red', 'orange', 'yellow',
            start='right'), align = 'center')
    drawLabel(f'Elevate Score: {app.path.getScore()}', centX, 595, font = 'monospace', size = 16)
    drawCircle(centX - 100 + app.path.getScore() * 2, 550, 12, fill = 'white')

    # File Folder  
    drawImage('https://github.com/tanvi-c/elevashin/blob/main/file%20folder.jpg?raw=true', 
              centX - 130, 640, width = 120, height = 96)
    
    if app.isFileHover:
        drawRect(centX - 100, 710, 60, 16, fill = 'gray')
        drawLabel('New File', centX - 70, 717, fill = 'white')

    # Contour Map Toggle
    drawImage('https://github.com/tanvi-c/elevashin/blob/main/ele.jpg?raw=true', 
              centX + 30, 640, width = 96, height = 96)
    if app.isContourHover:
        drawRect(centX + 40, 710, 80, 16, fill = 'gray')
        drawLabel('Contour Map', centX + 80, 717, fill = 'white')

def sat_onMouseMove(app, mouseX, mouseY):
    centX = app.width - ((app.width - app.imgW) / 2)
    app.selectedDot = None
    for i in range(len(app.plotPoints)):
        x, y = app.plotPoints[i]
        if ((x - mouseX)**2 + (y - mouseY)**2)**0.5 < 8:
            app.selectedDot = i
    if centX - 120 <= mouseX <= centX - 20 and 660 <= mouseY <= 720:
        app.isFileHover = True
    else:
        app.isFileHover = False

    if centX + 30 <= mouseX <= centX + 106 and 640 <= mouseY <= 709:
        app.isContourHover = True
    else:
        app.isContourHover = False

def sat_onMousePress(app, mouseX, mouseY):
    centX = app.width - ((app.width - app.imgW) / 2)
    if centX - 70 <= mouseX <= centX + 70 and 150 <= mouseY <= 190:
        app.isSpeedSelected = not app.isSpeedSelected
    if centX - 120 <= mouseX <= centX - 20 and 660 <= mouseY <= 720:
        gpx = getGPX()
        if gpx != None:
            reset(app, gpx)
    if centX + 30 <= mouseX <= centX + 106 and 640 <= mouseY <= 709:    
        buildContour(app)

def sat_onKeyPress(app, key):
    if key == 'space':
        app.isAnimated = not app.isAnimated

def sat_onStep(app):
    if app.isAnimated == True:
        if app.currDot >= len(app.plotPoints):
            app.currDot = 0
        else:
            app.currDot += 1

def reset(app, gpx):
    app.path = parseGPX(gpx)
    app.zoom = getZoom(app)
    app.map = getMap(app)
    imgW, imgH = getImageSize(app.map)
    app.imgW, app.imgH = imgW * ((app.height)//imgH), app.height
    app.plotPoints = app.path.getPlotPoints(app)
    app.isHRAvail = app.path.isHRAvail()
    app.isFileHover = False
    app.isContourHover = False
    app.isSpeedSelected = True
    app.isAnimated = True
    app.selectedDot = None
    app.currDot = 0

# User can select their files
# https://docs.python.org/3/library/dialog.html
# https://tkdocs.com/tutorial/windows.html

def getGPX():
    root = tk.Tk()
    root.withdraw()  
    root.attributes('-topmost', True)  
    
    filename = filedialog.askopenfilename(
        title='Select a GPX file',
        filetypes=[('GPX files', '*.gpx')]
    )
    root.destroy()
    return filename if filename else None  

# Used Python ElementTree XML API docs https://docs.python.org/3/library/xml.etree.elementtree.html
def parseGPX(file):
    tree = ET.parse(file)
    root = tree.getroot()

    points = []
    ns = {'gpx': root.tag.split('}')[0].strip('{'),
          'gpxtpx': "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"}

    for trackpoint in root.findall('.//gpx:trkpt', ns):
        lat = float(trackpoint.get('lat'))
        lon = float(trackpoint.get('lon'))

        ele = trackpoint.find('gpx:ele', ns)
        ele = float(ele.text) if ele != None else 0.0

        time = trackpoint.find('gpx:time', ns)
        time = time.text if time != None else '2025-01-01T00:00:00Z'

        ext = trackpoint.find("gpx:extensions", ns)

        speed, course, hr = 0.0, 0.0, None
        if ext != None:
            speed1 = ext.find("gpx:speed", ns)
            speed = float(speed1.text) if speed1 != None else 0.0

            course1 = ext.find("gpx:course", ns)
            course = float(course1.text) if course1 != None else 0.0

            hr1 = ext.find("gpx:hr", ns)
            hr = int(hr1.text) if hr1 != None else None

            hr2 = ext.find("gpx:heartrate", ns)
            hr = int(hr2.text) if hr2 != None else None
            
            tpe = ext.find("gpxtpx:TrackPointExtension", ns)
            if tpe != None:
                hr3 = tpe.find("gpxtpx:hr", ns)
                hr = int(hr3.text) if hr3 != None else None

        newPt = Point(lat, lon, ele, time, speed, course, hr)
        points.append(newPt)
    
    newPath = Path(points)
    newPath.getStats()

    return newPath

# Haversine is analogous to the distance function but for latitude and longitude (Source: medium.com)
# Assumes Earth is a perfect sphere - minor errors OK in this app (relatively small distances) 
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000 #Earth's radius in meters
    phi1, phi2 = lat1 * (math.pi/180), lat2 * (math.pi/180)
    lam1, lam2 = lon1 * (math.pi/180), lon2 * (math.pi/180)
    a = math.sin((phi2 - phi1)/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin((lam2 - lam1)/2)**2
    c = 2 * math.atan2(a**0.5, (1-a)**0.5)
    d = r * c
    return d

# Source: https://developers.google.com/maps/documentation/maps-static/start
def getMap(app):
    centerLat, centerLon = getCenter(app)

    mapUrl = (f'https://maps.googleapis.com/maps/api/staticmap?center={centerLat},{centerLon}'
              f'&markers=color:red|label:S|{app.path.points[0].lat},{app.path.points[0].lon}'
              f'&markers=color:blue|label:E|{app.path.points[-1].lat},{app.path.points[-1].lon}'
              f'&zoom={app.zoom}&size={app.width}x{app.height}&format=jpg&maptype=satellite&key={API}')
    
    return mapUrl

# Get path to overlay on maps precisely

def getCenter(app):
    lats = [p.lat for p in app.path.points]
    lons = [p.lon for p in app.path.points]
    north = max(lats)
    south = min(lats)
    east  = max(lons)
    west  = min(lons)

    return (north + south) / 2, (east + west) / 2

# https://medium.com/@suverov.dmitriy/how-to-convert-latitude-and-longitude-coordinates-into-pixel-offsets-8461093cb9f5
# AI suggested using the Web (Google) Mercator projection
def getMercatorPts(lat, lon):
        siny = math.sin(lat * math.pi / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = 256 * (0.5 + lon / 360) 
        y = 256 * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi))
        return x, y

def getZoom(app):
    lats = [p.lat for p in app.path.points]
    lons = [p.lon for p in app.path.points]
    
    minLat, maxLat = min(lats), max(lats)
    minLon, maxLon = min(lons), max(lons)

    # Google Maps uses 256 pixels per tile at zoom 0
    for zoom in range(20, 0, -1): 
        scale = 2 ** zoom
        
        x1, y1 = getMercatorPts(minLat, minLon)
        x2, y2 = getMercatorPts(maxLat, maxLon)
        
        pixelX1, pixelY1 = x1 * scale, y1 * scale
        pixelX2, pixelY2 = x2 * scale, y2 * scale
        
        pixelWidth = abs(pixelX2 - pixelX1)
        pixelHeight = abs(pixelY2 - pixelY1)
        
        padding = 0.6
        
        if (pixelWidth <= app.width * padding and 
            pixelHeight <= app.height * padding):
            return zoom 
    
    return 1

# Contour Map

# https://numpy.org/devdocs/user/numpy-for-matlab-users.html - Reccommends usage of NumPy & SciPy for MatLab
def getGriddedData(app):
    lats = np.array([p.lat for p in app.path.points])
    lons = np.array([p.lon for p in app.path.points])
    eles = np.array([p.ele for p in app.path.points])
    latGrid = np.linspace(min(lats), max(lats), 100)
    lonGrid= np.linspace(min(lons), max(lons), 100)
    lonMesh, latMesh = np.meshgrid(lonGrid, latGrid)
    pts = np.column_stack((lons, lats))
    eleGrid = griddata(pts, eles, (lonMesh, latMesh), method = 'linear')
    return lonMesh, latMesh, eleGrid

# https://matplotlib.org/stable/gallery/mplot3d/surface3d.html
def buildContour(app):
    X, Y, Z = getGriddedData(app)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap= cm.coolwarm, linewidth=0, antialiased=False)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    ax.grid(True, linestyle='-.')
    ax.tick_params(axis='x', colors='gray')
    ax.tick_params(axis='y', colors='gray')
    ax.tick_params(axis='z', colors='gray')
    ax.set_title("Total Elevation Overview. You're leveling up!")
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Elevation (m)')
    fig.align_labels()  
    fig.align_titles()
    fig.text(0.02, 0.05, f'Your Net Elevation: {pythonRound(app.path.netEle, 2)} m', fontsize=10, 
             va = 'top', family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue'))

    def animate(frame):
        ax.view_init(elev=30, azim=frame)
        return surf,
    
    anim = animation.FuncAnimation(fig, animate, frames=np.arange(0, 360, 3), interval=50, blit=False)
    
    plt.tight_layout()
    plt.show()

class Path: 
    def __init__(self, points):
        self.points = points
        self.totalDist = 0
        self.totalGain = 0
        self.netEle= 0
        self.markers = []

    def getStats(self):
        if len(self.points) < 2:
            return None

        seen = set()
        for i in range(1, len(self.points)):
            p1 = self.points[i-1]
            p2 = self.points[i]

            d = p1.distanceTo(p2)
            self.totalDist += d
            # m --> mi conversion for mile markers
            miles = int(self.totalDist // 1609)
            if miles not in seen and miles >= 1:
                seen.add(miles)
                self.markers.append(i)
            self.netEle += (p2.ele - p1.ele)
            if p2.ele - p1.ele > 0:
                self.totalGain += p2.ele - p1.ele
        self.totalDist /= 1609

        start, end = self.points[0], self.points[-1]
        self.durationStr, self.durationSec = Path.getDuration(start, end)
        self.avgSpeed = (self.totalDist / self.durationSec) * 3600 if self.durationSec > 0 else 0

    def getPlotPoints(self, app):
        scale = 2 ** app.zoom
        centerLat, centerLon = getCenter(app)

        # Compute center pixel (based on same centerLat/centerLon used in map url) to get focused image
        centerX, centerY = getMercatorPts(centerLat, centerLon)
        pixelCentX, pixelCentY = centerX * scale, centerY * scale

        plotPoints = []
        for pt in self.points:
            ptX, ptY = getMercatorPts(pt.lat, pt.lon)
            pixelX, pixelY = ptX * scale, ptY * scale
            screenX = app.imgW/2 + (pixelX - pixelCentX)
            screenY = app.imgH/2 + (pixelY - pixelCentY)
            plotPoints.append((screenX, screenY))

        return plotPoints
    
    def getColorIndex(self, app, point):
        if app.isSpeedSelected == True:
            if point.speed < 1:
                return 0
            elif point.speed < 3:
                return 1
            elif point.speed < 5:
                return 2
            elif point.speed < 7:
                return 3
            else:
                return 4
        else:
            if point.HR == None:
                return 5
            elif point.HR < 0.2 * app.HRR:
                return 0
            elif point.HR < 0.4 * app.HRR:
                return 1
            elif point.HR < 0.6 * app.HRR:
                return 2
            elif point.HR < 0.8 * app.HRR:
                return 3
            else:
                return 4
    
    def isHRAvail(self):
        for p in self.points:
            if p.HR != None:
                return True
        return False
    
    def getScore(self):
        if len(self.points) < 2:
            return 0
        distScore = min(self.totalDist * 3.5, 25)
        eleGainScore = min(self.totalGain / 300 * 3, 35)
        avgGrade = (self.totalGain / self.totalDist * 100)
        gradeScore = min(avgGrade * 5, 25)
        durationScore = min(self.durationSec / 360, 15)

        return rounded(distScore + eleGainScore + gradeScore + durationScore)

    @staticmethod
    def getDuration(start, end):
        duration = end.dateTime - start.dateTime
        secDiff = int(duration.total_seconds())
        hr = secDiff // 3600
        min = (secDiff % 3600) // 60
        sec = secDiff % 60
        return (f'{hr}:{min}:{sec}', secDiff)
    
    
class Point:
    def __init__(self, lat, lon, ele, time, speed, course, hr):
        self.lat = lat
        self.lon = lon
        self.ele = ele

        # datetime documentation: https://docs.python.org/3/library/datetime.html#datetime.datetime
        dateTime = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
        dateTime = dateTime.replace(tzinfo=timezone.utc)
        dateTime = dateTime.astimezone()
        self.dateTime = dateTime

        self.speed = speed
        self.course = course
        self.HR = hr

    # For Debugging
    def __repr__(self):
        return f'Point(lat: {self.lat}, lon: {self.lon}, ele: {self.ele}, hr: {self.hr}) at {self.dateTime}'

    # 3D distance logic: Taking the arc length of the curve is summing all the hypotenuses (dx, dy) of 
    # infinitesimally small right triangles.
    # Haversine gives the horizontal distance and elevation gives vertical distance
    def distanceTo(self, other):
        if isinstance(other, Point):
            horiz = haversine(self.lat, self.lon, other.lat, other.lon)
            vert = abs(other.ele - self.ele)
            return (horiz**2 + vert**2)**0.5

runAppWithScreens(initialScreen = 'start', width=1000, height=750)