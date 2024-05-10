#!/usr/bin/env pybricks-micropython
import sys
import time
sys.path.append('/home/robot/MapleBot/Robot')
from Drivebase import Drivebase
from sensors import Sensors
#from RobotPose import RobotPose
import math
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
#import drivebase
from Point2D import Point2D
from RobotPose import RobotPose
#from pybricks.media.ev3dev import SoundFile, ImageFile


#IL RESTE :
    #-LA CONDITION POUR QUE LE ROBOT ARRÊTE
    #-LA PRÉCISION QUE LE ROBOT NE TOURNE PAS DANS LE MUR OU SON QUEST SE TROUVE, MAIS PLUS LOIN, OU MOIN, DÉPENDAMENT SUR QUELLE FONCT QU'ON CALL, (CASE 2/3) 
    #-FAIT LA FONCT AVANCE LONGEURE ROBOT TOURNE VERS QUEST ET LA METTRE DANS CASEfour
    #-quand le robot undo, fait que quand tu tourne vers le quest, c'est un step 2 de tourner du coté x, ensuite quql chs jai oublié
    #-
    #-
    #-
class States:
    CALIBRATING = tuple(("CALIBRATING", 0))
    ADVANCE_UNTIL_OBSTACLE = tuple(("ADVANCE_UNTIL_OBSTACLE", 1))
    TURN = tuple(("TURN", 2))
    GO_TO_LAST_POINT_OF_INTEREST = tuple(("UNDO", 3)) #a changer de nom potentiellement pour un plus clair
    FINISHED_EXLORATION = tuple(("FINISHED_EXLORATION", 4))

class AutonomousMovingEnhaced :
    drivebase = None
    sensors = None

    #variables de la state machine
    currentState = tuple
    previousState = tuple

    #variables nécessaire au fonctionnement de l'algorithme de déplacament autonome
    _RANGE = math.sqrt(math.pow(90,2)+ math.pow(90,2))/2 /300 * 1000 # dest d'environ 0.2121 mètres #avant était math.sqrt(math.pow(90,2)+ math.pow(90,2))/2
    pointsOfInterestTravelled = [] #la position 0 du tableau est la position de départ du robot
    quests = [] #places to explore aka quests available
    indexOfActiveQuest = int
    lastPointOfInterest = Point2D
    repeatLastAction = False
    indexToRemove = int


    def __init__(self, d : Drivebase, s : Sensors):
        self.drivebase = d
        self.sensors = s

    def start(self):
        self.currentState = States.CALIBRATING
        print(self.currentState)
        while True:
            self.consumeStateInput()
    
    def consumeStateInput(self): # il faut faire boucler le consume state input jusqu'à ce que quests = 0
############### None ##########################
        if self.currentState == None:
            print("current state == Null")
            self.drivebase.stopMotors()

############### CALIBRATING ##########################
        if self.currentState == States.CALIBRATING and self.previousState != States.CALIBRATING:
            print("Entering state CALIBRATING")
            self.calibrate(0)
            self.addNewPointOfInterestTravelled()
            print("End of CALIBRATING")
            self.setState(States.ADVANCE_UNTIL_OBSTACLE)

############### ADVANCE_UNTIL_OBSTACLE ##########################
        if self.currentState == States.ADVANCE_UNTIL_OBSTACLE and self.previousState != States.ADVANCE_UNTIL_OBSTACLE:
            print("Entering state ADVANCE_UNTIL_OBSTACLE")
            self.drivebase.setSpeed(400)

            wasObstacleLeft = self.sensors.isObstacleLeft()
            wasObstacleRight = self.sensors.isObstacleRight()

            while not self.sensors.isObstacleInFront(): #tant qu'il n'a pas de mur en face il vérifier les cotés pour créer des quests

                if wasObstacleLeft == True and self.sensors.isObstacleLeft() == False : #mur avant et pas mur actuellement
                    print("LEFT wall has DISAPPEARED")
                    self.pointsOfInterestTravelled.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()-90.0)) #crée quest a gauche
                    self.quests.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()-90.0))
                    wasObstacleLeft = False
                
                if wasObstacleLeft == False and self.sensors.isObstacleLeft() == True:
                    print("LEFT wall has APPEARED")
                    self.quests.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()-90.0)) #crée quest a gauche
                    wasObstacleLeft = True
                
                if wasObstacleRight == True and self.sensors.isObstacleRight() == False:
                    print("RIGHT wall has DISAPPEARED")
                    self.pointsOfInterestTravelled.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()+90.0)) #crée quest a droite
                    self.quests.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()+90.0))
                    wasObstacleRight = False

                if wasObstacleRight == False and self.sensors.isObstacleRight == True:
                    print("RIGHT wall has DISAPPEARED")
                    self.quests.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()+90.0)) #crée quest a droite
                    wasObstacleRight = True


            print("Wall in front")
            self.drivebase.stopMotors()
            print(self.drivebase.getPosition())
            if self.isPositionAlreadyExplored(self.drivebase.getPosition()) == False: #si la position ou il est rendu est nouvelle (pas encore exploré) il continue avec un TURN
                print("new position explored")
                self.addNewPointOfInterestTravelled()
                self.setState(States.TURN)
                print("Exiting ADVANCE_UNTIL_OBSTACLE")
            else : #la position où il est rendu est déjà marqué comme un pointOfInterestTravelled
                print("position already explored")
                self.pointsOfInterestTravelled.pop(self.indexToRemove)
                
                for i in range(len(self.quests)):
                    if self.arePointsInRange(self.drivebase.getPosition(), self.quests[i], self._RANGE): #est-ce que position actuelle correspond à une quest?
                        if self.equalsWithTolerance(self.quests[i].getDir(), self.drivebase.getPosition().getDir()+180, 2.0): #est-ce que la quest et la position du robot font face dans la direction opposé +- 2°?
                            self.quests.remove(self.indexToRemove) #enlève la quest, car on vient de l'accomplir à sens inverse par une autre quest
                            self.setState(States.GO_TO_LAST_POINT_OF_INTEREST)
                            break
                        elif self.equalsWithTolerance(self.quests[i].getDir(), self.drivebase.getPosition().getDir(), 2.0) :#est-ce que la quest et la position du robot font face dans la même direction +- 2°?
                            self.indexOfActiveQuest = i
                            self.setState(States.ADVANCE_UNTIL_OBSTACLE)#part explorer la quest
                            break
                        else :
                            self.drivebase.turnRad(self.drivebase.getPosition().deltaDir(self.quests[i])) #aligne le robot dans la direction de la quest
                            self.indexOfActiveQuest = i
                            self.setState(States.ADVANCE_UNTIL_OBSTACLE) #part explorer la quest
                            break
                
                self.setState(States.FINISHED_EXLORATION)#je vois pas d'autre raison sur pourquoi le robot reviendrait sur un point déjà connu qui ne corresponds pas a une quest
          
############### TURN ##########################
        if self.currentState == States.TURN and self.previousState != States.TURN:
            print("Entering state TURN")

            if(self.sensors.isObstacleLeft() and not self.sensors.isObstacleRight()):#peut tourner a droite
                print("Turning right")
                self.drivebase.turnNotTime(90)
                self.setState(States.ADVANCE_UNTIL_OBSTACLE)
            
            elif (self.sensors.isObstacleRight() and not self.sensors.isObstacleLeft()):#peut tourner a gauche
                print("Turning left")
                self.drivebase.turnNotTime(-90)
                self.setState(States.ADVANCE_UNTIL_OBSTACLE)
            
            elif (self.sensors.isObstacleLeft() == False and self.sensors.isObstacleRight() == False): #pas de mur ni a gauche ni a droite
                print("NO walls on the SIDES")
                self.pointsOfInterestTravelled.append(Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation()-90.0)) #crée quest a gauche
                print("Turning right")
                self.drivebase.turnNotTime(90) #tourne a droite
                self.setState(States.ADVANCE_UNTIL_OBSTACLE)
            
            else : #mur des 2 cotés
                #print("nowhere to turn, undoing last action")
                #self.pointsOfInterestTravelled.pop()
                #self.setState(States.GO_TO_LAST_POINT_OF_INTEREST)
                print("wall on two side, turning right")
                self.drivebase.turnNotTime(-90)
                self.setState(States.ADVANCE_UNTIL_OBSTACLE)



############### GO_TO_LAST_POINT_OF_INTEREST ##########################
        if self.currentState == States.GO_TO_LAST_POINT_OF_INTEREST or self.repeatLastAction:
            print("Starting state GO_TO_LAST_POINT_OF_INTEREST")
            indexOfLastPointOfInterest = len(self.pointsOfInterestTravelled)-1
            lastPointOfInterest = self.pointsOfInterestTravelled[indexOfLastPointOfInterest]

            #1) yaw du robot doit être a 90° de dir du point d'interet
            diffAngle = lastPointOfInterest.deltaDir(self.drivebase.getPosition())
            self.drivebase.turnRad(90.0 - diffAngle, 2)
            #2) deplacement en x de la distance qui sépare le robot du point d'interet
            self.drivebase.avanceDistance(lastPointOfInterest.deltaX(self.drivebase.getPosition()))
            #3) faire tourner le robot pour qu'il soit dans la même direction que le point d'interet
            self.drivebase.turnRad(diffAngle, 2)
            #4) déplacement en y de la distance qui sépare le robot du point d'interet
            self.drivebase.avanceDistance(lastPointOfInterest.deltaY(self.drivebase.getPosition()))

            if self.arePointsInRange(lastPointOfInterest, self.quests[len(self.quests)-1],self._RANGE) and self.arePointsInRange(lastPointOfInterest, self.drivebase.getPosition(), self._RANGE):
                self.pointsOfInterestTravelled.pop(indexOfLastPointOfInterest)

                self.setState(States.ADVANCE_UNTIL_OBSTACLE)
                print("End of GO_TO_LAST_POINT_OF_INTEREST")
                print("Starting Quest #"+str(len(self.quests)-1))
            else : #le point où le robot est n'est pas un point de quest
                self.pointsOfInterestTravelled.pop(indexOfLastPointOfInterest) #enleve le point
                self.repeatLastAction = True #répète l'action pour aller au point d'intêret précédent
                print("REPEATING of GO_TO_LAST_POINT_OF_INTEREST")

############### FINISHED_EXLORATION ##########################
        if self.currentState == States.FINISHED_EXLORATION :
            self.drivebase.stopMotors()
            print("FINISHED_EXLORATION")
            exit()
    
    previousState = currentState
### fin du consumeStateInput()

    
    def calibrate(self, x):
        """
        Cette fonction calibre le robot d'une position face contre le mur.\n
        Params
            x : valeur arbitraire qui determine la distance qu'il recule
        """
        time.sleep(3)
        while (x < 5000):
            self.drivebase.setSpeed(-45)
            x = x + 1
        self.drivebase.turnNotTime(180)

    def addNewPointOfInterestTravelled(self):
            """Ajoute une position (x,y,yaw) d'intéret au tableau de places déjà visité"""
            pt = Point2D(self.drivebase.getPosition().getX(), self.drivebase.getPosition().getY(), self.drivebase.getPosition().getOrientation())
            print("pt added to list : " + str(pt))
            self.pointsOfInterestTravelled.append(pt)

    #cette fonct retourne vrai si le robot était passé par cette position autrefois
    def isPositionAlreadyExplored(self, currentPosition : Point2D):
        """
        Permet de savoir si le robot est déjà passé par la coordonée où il est.\n
        Param
            currentPosition (Point2D): position Actuelle du robot (x,y)
        Return
            True : si le robot est déjà passé par la coordonnée
            False : si le robot n'est jamais passé par la coordonnée
        """
        i = 0
        bool = False
        while (i< len(self.pointsOfInterestTravelled) and not bool):
            print("comparing with range of : "+str(self._RANGE))
            print("pt : "+ self.pointsOfInterestTravelled[i].__str__()+" RobotPose : "+self.drivebase.getPosition().__str__())
            print(self.arePointsInRange(self.drivebase.getPosition(), self.pointsOfInterestTravelled[i], self._RANGE))
            if(self.arePointsInRange(self.drivebase.getPosition(), self.pointsOfInterestTravelled[i], self._RANGE)):
                print(str(self.drivebase.getPosition()) + " " + str(self.pointsOfInterestTravelled[i]))
                print("place already explored")
                self.indexToRemove = i
                bool = True
            else:
                i += 1
        
        return bool
    
    def arePointsInRange(self, point1 : Point2D, point2 : Point2D, range  : float) -> bool:
        """
        Vérifie si deux points sont égaux selon une certaine marge d'erreur\n
        Params 
            point1 (Point2D) : premier point qu'on veut comparer\n
            point2 (Point2D) : deuxième point qu'on veux comparer\n
            range (float) : marge d'erreur accepté
        """

        print("dx : "+str(abs(point1.getX() - point2.getX()) <= range))
        print("dy : "+str(abs(point1.getY() - point2.getY()) <= range))
        return abs(point1.getX() - point2.getX()) <= range and abs(point1.getY() - point2.getY()) <= range

    def setState(self, newState : States):
        self.previousState = self.currentState
        self.currentState = newState

    def equalsWithTolerance(self, value1 : float, value2 : float, tolerance : float) -> bool:
        """
        Compare deux valeurs en tenant compte de la tolérance spécifié\n
        Param
            value1 (float) : valeur qu'on veut comparer
            value2 (float) : valeur avec la quelle on compare
            tolerance (float) : tolérance de la valeur2
        """
        if(float(value1) <= float(value2) + float(tolerance) 
           and float(value1) >= float(value2)+float(tolerance)):
            return True
        else:
            return False