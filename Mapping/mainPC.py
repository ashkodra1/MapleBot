from ConnexionBluetooth import connexionBluetooth
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import threading
import math

_x = [0]
_y = [0]

fig, (axHeatmap, axScatter) = plt.subplots(1, 2)

#fonction 1
b = connexionBluetooth()
def fonction1():
    global b
    global _x
    global _y
    while True:
        b.dataExchange()
        #print("fin echange donnes")
        sensorData = b.separateData()
        print("sensorData : " + str(sensorData))

        #print(connexionBluetooth.getNumData(sensorData[0]), connexionBluetooth.getNumData(sensorData[1]))
        b.resetData()

        #ajout des points au tableau s'il sont différents du précédent:
        #if(connexionBluetooth.getNumData(sensorData[0]) != _x[len(_x)-1] and connexionBluetooth.getNumData(sensorData[1])!=_y[len(_y)-1]):
        _x[0] = connexionBluetooth.getNumData(sensorData[0])
        _y[0] = connexionBluetooth.getNumData(sensorData[1])
        

        """
        if(len(sensorData)>3):
            for i in range (len(sensorData)-3):
                if i%2==0:
                    _x.append(connexionBluetooth.getNumData(sensorData[i+3]))
                else :
                    _y.append(connexionBluetooth.getNumData(sensorData[i+3]))
        """

        if(len(sensorData)>3):
            distanceGauche = connexionBluetooth.getNumData(sensorData[3])/1000 #transforme la distance vue par l'ultrason gauche en mm en m
            if(distanceGauche < 2.0):
                _x.append(calculerPointX(_x[0], distanceGauche, (connexionBluetooth.getNumData(sensorData[2])-90)%360)) #La position x du point ultrason gauche
                _y.append(calculerPointY(_y[0], distanceGauche, (connexionBluetooth.getNumData(sensorData[2])-90)%360)) #La position Y du point ultrason gauche
                #print("x = " + calculerPointX(_x[0],connexionBluetooth.getNumData(sensorData[3]), connexionBluetooth.getNumData(sensorData[2])) + ", y = " + calculerPointY(_y[0],connexionBluetooth.getNumData(sensorData[3]), connexionBluetooth.getNumData(sensorData[2])))

            distanceDroite = connexionBluetooth.getNumData(sensorData[4])/1000 #transforme la distance vue par l'ultrason droit en mm en m
            if(distanceDroite < 2.0):
                _x.append(calculerPointX(_x[0], distanceDroite, (connexionBluetooth.getNumData(sensorData[2])+90)%360))
                _y.append(calculerPointY(_y[0], distanceDroite, (connexionBluetooth.getNumData(sensorData[2])+90)%360))
                #print("_x = " + str(_x[len(_x)-1]) + "_y = " + str(_y[len(_y)-1]))

def calculerPointX(posX:float, distance:float, angle:float):
    return posX + distance*math.cos(math.radians(angle))

def calculerPointY(posY:float, distance:float, angle:float):
    return posY + distance*math.sin(math.radians(angle))

threadBluetooth = threading.Thread(target=fonction1)
threadBluetooth.start()

def update(frame):
    # Calculate 2D histogram
    axHeatmap.clear()
    axHeatmap.hist2d(_x, _y, density=True, cmin=1, cmax=7, cmap='OrRd')
    axHeatmap.scatter(_x[0], _y[0], color='blue')
    axScatter.clear()
    axScatter.scatter(_x, _y, color='blue')
    axScatter.scatter(_x[0], _y[0], color='red')

# Create animation#
ani = FuncAnimation(fig, update, frames=100, interval=200)
plt.show()

"""
repetition =0
while repetition<100:
    b.dataExchange()
    sensorData = b.separateData()
    b.resetData()
    print(connexionBluetooth.getNumData(sensorData[0]), connexionBluetooth.getNumData(sensorData[1]))
    #ajouterPoint(connexionBluetooth.getNumData(sensorData[0]), connexionBluetooth.getNumData(sensorData[1]))
    print(100-repetition)
    repetition+=1
"""

