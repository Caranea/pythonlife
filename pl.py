import numpy as np
import colorsys as cs
import random as rd
import sys
import math
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

width = 800
height = 800

#function definitions
def buildAttractionMatrix(m):
    return (m*2)-1 # Multiple random between [0.0,1.0] by 2 and substract one to get random between [-1.0,1.0]

#With HSL, unlike RGB, to change color we have to update only one value [[H]SL -> Hue]. Hence, it will work perfectly
#for generating predefined no of colors, sufficiently distinct from one another. Since our GUI library accepts only RGB colors,
#we have to convert it RGB.
def createColors(m):
    colors = list()
    for i in range(m):
        hueValue = (i *( 360/(m - 1)))
        #hsvtorgb() returns values between [0.0,1.0] hence i*255
        color = tuple(round(i * 255) for i in cs.hsv_to_rgb(hueValue/100,1,1))
        colors.append(QColor(color[0],color[1],color[2]))
    return colors

def force(d, f): #d - ratio of particles distance and max distance , f - force according to attraction matrix
    repRadius = 0.25 #universal repulsive force that prevents our particles from collapsing into each other
    #25% is an arbitrary value I tested to behave the best - feel free to experiment, like with other system parameters.
    if (d<repRadius):
        #if d is within the range of universal repulsive we return negative value. As the distance approaches 0 returned value approaches -1 which is max value
        #for our repulsive force
        return (d/repRadius - 1)
    elif (repRadius < d and d<1): #our distance is within max radius for standard force defined by attraction matrix
        #the closer we get the particles together, the stronger their interaction is.
        #As the particle move apart from each other, the force dissipates to reach 0 as we
        #reach max radius
        return f * (1-d)
    else:
        return 0 #particles are indiffirent to each other

def updatePositions():
    #we initiate a loop to update all particles in our system
    for i in range(n):
        #every particle will accumulate total force value we'll get by evaluating it's attraction to every other particle in the system. Hence, our algorithm
        #has a time complexity of O(n^2) if we don't add any optimizations.
        totalForceX = 0
        totalForceY = 0
        for j in range(n):
            if (i!=j):#we're not calculating the particle's influence on itself
                #calculating distance between tested particle (i) to all other particles (j)
                x = positionsX[j]-positionsX[i]
                y = positionsY[j]-positionsY[i]
                d = math.sqrt(x * x + y* y)

                if (d<radius): #we're only proceeding with calculating distance if the distance between particle is less than max radius we specified for our system
                    #1st param: We have to apply force proportionally to the distance between particles instead of simply using the value from out matrix
                    #2nd param: To get the right value from the attraction matrix we need to get colors of particles we test
                    f = force(d/radius, attractionMatrix[colors.index(particlesColors[i])][colors.index(particlesColors[j])])
                    #lets add our force for this particle (j) to our total forces for particle (i)
                    totalForceX+=(x / d)*f
                    totalForceY+=(y / d)*f
        #total force we just calculated will increase the particle's velocity
        velocitiesX[i]+=totalForceX
        velocitiesY[i]+=totalForceY
        #we have to apply friction so that our particles don't accumulate velocity forever
        velocitiesX[i]*=fr
        velocitiesY[i]*=fr
        #now that we have the particles velocity we can know how to change its position
        positionsX[i]+=velocitiesX[i]
        positionsY[i]+=velocitiesY[i]

#system properties
n = 400 #number of particles
m = 5 #number of colors
radius = 0.20
fr = math.pow(.5, 10) #friction

#init arrays to hold our values
attractionMatrix = buildAttractionMatrix(np.random.random((m,m))) #create 2-d matrix based on number of colors
colors = createColors(m)
particlesColors = [rd.choice(colors) for _ in range(n)] #every particle is assigned random color from colors we created
#every particle is assigned random position
positionsX = [rd.random() for _ in range(n)]
positionsY = [rd.random() for _ in range(n)]
#every particle is assigned velocity = 0
velocitiesX = np.empty(n, dtype=float)
velocitiesY = np.empty(n, dtype=float)

class Window(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)

        updatePositions()
        for i in range(n):
            x = positionsX[i] * width
            y = positionsY[i] * height
            painter.setPen(particlesColors[i])
            painter.drawEllipse(x, y, 1, 1)
            self.update()


app = QApplication(sys.argv)
window = Window()
window.height = height
window.width = width
window.show()

sys.exit(app.exec())
