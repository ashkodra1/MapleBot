#!/usr/bin/env pybricks-micropython
from sensors import Sensors
#from AutonomousMoving import AutonomousMoving
import sys
sys.path.append('/home/robot/MapleBot/Util')
from RobotPose import RobotPose
import math
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog


class Drivebase :
    """
    Classe représentant la base mobile du robot.\n
    Cette classe permet de controler les moteurs et gère l'odometrie du robot
    """
    #motors
    _kLeftMotor = Motor(Port.D)
    _kRightMotor = Motor(Port.A)
    #encoders
    rightOldEncoderVal = float(0)
    leftOldEncoderVal = float(0)
    rightEncoderMemory = 0
    leftEncoderMemory = 0
    #constants
    _kWheelCirconference = float(math.pi*43) #en mm
    VALUE_FROM_OBSTACLE = 20.0
    #Odometrie
    _s = Sensors()
    _pos = None
    #idk
    _hasFinishedAction = False
    #_a = AutonomousMoving()
    
    
    def __init__(self):
        """Constructeur de Drivebase"""
        self.setEncoders(0)
        self.rightEncoderVal = self._kRightMotor.angle()
        self.leftEncoderVal =  self._kLeftMotor.angle()
        self._pos = RobotPose(0,0,0)

    def __str__(self):
        """affiche les valeur des encodeurs des moteurs"""
        return "leftMotorAngle : " + str(self._kLeftMotor.angle()) + "; righMotorAngle : " + str(self._kRightMotor.angle())

    def setEncoders(self, angle):
        """
        Override la valeur des encodeurs à un angle donné\n
        Param
            angle (float) : angle auquel on veut mettre les encodeurs
        """
        self._kLeftMotor.reset_angle(angle)
        self._kRightMotor.reset_angle(angle)
    
    def stopMotors(self):
        """Arrête et stall les moteurs"""
        self._kLeftMotor.hold()
        self._kRightMotor.hold()
    
    def setSpeed(self, speed):
        """
        Fait fonctionner les moteurs à la vitesse voulue\n
        Param
            speed (number) : vitesse voulue (positif = avancer, négatif = reculer)
        """
        self._kLeftMotor.run(speed)
        self._kRightMotor.run(speed)
    
    def getSpeed(self):
        """Return : la vitesse des moteurs"""
        return self._kLeftMotor.speed()
    
    def getDistance(self): #en mm
        """
        Return: (float) (mm) distance parcourue depuis la dernière fois que la méthode à été appelé
        """
        diffRightEncodervalue = self._kRightMotor.angle() - self.rightEncoderMemory
        diffLeftEncodervalue = self._kLeftMotor.angle() - self.leftEncoderMemory
        d = float((diffRightEncodervalue+diffLeftEncodervalue)/2 * self._kWheelCirconference / float(360))
        self.rightEncoderMemory = self._kRightMotor.angle()
        self.leftEncoderMemory = self._kLeftMotor.angle()
        return d #if d > 0.0 else d*-1.0
    
    #droite = angle positif, gauche = angle négatif
    def turn(self, angle, speed):
        self._hasFinishedAction = False
        targetAngle = self.getAngle()+angle
        print(float(targetAngle))
        if(angle > 0): #tourne vers la droite
            rightSpeed = float(speed)*-1
            leftSpeed = float(speed)
        else: #tourne vers la gauche
            rightSpeed = float(speed)
            leftSpeed = float(speed)*-1
        
        self._kRightMotor.run(rightSpeed)
        self._kLeftMotor.run(leftSpeed)
        
        while True:
            #peux faire mieux pour plus de précision mais flemme/condition 
            #bcp plus complexe faut vérifier sens de rotation
            if(int(self.getAngle()) == int(targetAngle)): 
                self.stopMotors()
                self._hasFinishedAction = True
                break

        #while self.getAngle() != targetAngle:

    def avanceUntilObstacle(self):
        s = Sensors()
        self._hasFinishedAction = False
        self.setSpeed(-400)
        print(str(s.degrés()) + " : Avance")
        while self._hasFinishedAction == False:
            if(s.getFrontValue() < self.VALUE_FROM_OBSTACLE):
                self._hasFinishedAction = True
                self.setSpeed(0)


    def avanceDistance(self, distance : float): #distance en mm
        self._hasFinishedAction = False
        self.setEncoders(0)
        self.setSpeed(200)
        
        while self._hasFinishedAction == False:
            self._hasFinishedAction = (self.getDistance() >= distance)
        
        print("J'AI AVANCÉ : "+str(self.getDistance()))
        self.stopMotors()

    def moveAuto(self, sensor):
        hasObstacleInFront = False
        while True:#à determiner la condition de fin du movement autonome
            #commence a avancer
            if(not hasObstacleInFront and self.getSpeed() == 0 and self._hasFinishedAction):
                self.setSpeed(200)
            #s'arrette quand il a un obstacle devant lui
            elif(sensor.getFrontValue() <= self.VALUE_FROM_OBSTACLE and self._hasFinishedAction):
                print("obstacle found")
                self.stopMotors()
                hasObstacleInFront = True

            if(hasObstacleInFront):
                print("avoiding obstacle")
                #tourne a droite
                if(not sensor.getIsObstacleRight()):
                    self._kRightMotor.run(-100)
                    self._kLeftMotor.run(100)
                    if(sensor.getFrontValue() > self.VALUE_FROM_OBSTACLE and self._hasFinishedAction):
                        self.turn(30, 100)

                #tourne a gauche
                if(not sensor.getIsObstacleLeft()):
                    self._kRightMotor.run(100)
                    self._kLeftMotor.run(-100)
                    if(sensor.getFrontValue() > self.VALUE_FROM_OBSTACLE and self._hasFinishedAction):
                        self.turn(-30, 100)
                
                hasObstacleInFront = not self._hasFinishedAction
                print("obstacle avoided")
    
    def equalsWithTolerance(self, value : float, tolerance : float):
        if(float(value) <= float(value) + float(tolerance) 
           and float(value) >= float(value)+float(tolerance)):
            return True
        else:
            return False
    

    #cette fonction reçoit dist : le rapport de déplacement sur un temps déterminé, et reçoit angle : la valeur que le gyro retourne.
    def updatePos(self):
        """
        Update la position du robot
        """
        deg = self._s.degrés()
        dis = self.getDistance()
        x = self._pos.getX() + (math.cos(math.radians(deg)) *dis)
        y = self._pos.getY() + (math.sin(math.radians(deg)) *dis)*-1
        self._pos.set(
            x,
            y,
            deg
        )    
    #Cette fonction reçoit la distance en centimètres et retourne le nombre de degrés que les moteurs doivent tourner
    def cmToAngleRot(dist : float): 
        """
        Permet de transformer une distance en centimètre en valeur d'encodeur (angles)\n
        Param
            dist (float) : distance en cm à convertir en angles
        """
        return ((dist * 0.0949) * 360)
    
    def turnRad(self, deg, spd):
        currDeg = self._s.degrés()
        quadActuel = self.déterminerQuad(0)    
        quadVoulu = self.déterminerQuad(deg)
        #print(quadActuel)
        #print(quadVoulu)
        used = False
        works = True
        #prob = quee il stop le quad après le but alors y arrête pas
        while(quadActuel != quadVoulu and works):
            #print(str(tooBig(distToDeg(deg,currDeg))) + " quadFonct")
            #print("QuadActuel : " + str(quadActuel) + "---QuadVoulu : " + str(quadVoulu))
            self.gaucheOuDroiteSpd(deg, spd)
            quadActuel = self.déterminerQuad(0)
            #print(s.degrés())
            if(abs(self.tooBig(self.distToDeg(deg,currDeg))) > 5*spd):
            #if(abs(tooBig(distToDeg(deg,currDeg))) > 10*spd):
                works = False
        if(abs(self.tooBig(self.distToDeg(deg,currDeg))) >= 0.5):
            while(abs(self.tooBig(self.distToDeg(deg,currDeg))) > 5*spd):
            #while(abs(tooBig(distToDeg(deg,currDeg))) > 10*spd):
                #print(s.degrés())
                #print(str(tooBig(abs(distToDeg(deg,currDeg)))) + " : more than 10")
                self.gaucheOuDroiteSpd(deg, spd)
            if(self.tooBig(self.distToDeg(deg,currDeg)) >= 0.5):  
                while(self.tooBig(self.distToDeg(deg,currDeg)) >= 0.5):
                    #print(s.degrés())
                    #print(str(tooBig(distToDeg(deg,currDeg))) + " : less than 10-1")
                    self.gaucheOuDroiteSlw(deg)        
                used = True
            if(used  != True):
                while(self.tooBig(self.distToDeg(deg,currDeg)) <= -0.5):
                    #print(s.degrés())
                    #print(str(tooBig(distToDeg(deg,currDeg))) + " : less than 10-2 ")
                    self.gaucheOuDroiteSlw(deg)
        self.stopMotors()       
        print(str(self.distToDeg(deg,currDeg)) + " supposed to be done")
        #recal(deg)

    def distToDeg(self, deg, currDeg):
        #print(str(s.degrés()) + " " + str(deg))
        answer = self._s.degrés() - deg - currDeg
        if(answer < -360):
            answer = answer + 360
        if(answer > 360):
            answer = answer + -360
        return answer #

    def tooBig(self, distDiff):
        # if(distDiff > 180):
        #     return distDiff - 180
        # if(distDiff < -180): 
        #     return distDiff + 180
        return distDiff
    
    def déterminerQuad(self, deg):
        if (deg == 0): deg = self._s.degrés()
        if(math.sin(math.radians(deg)) > 0): si = 1
        else: si = 2 
        if(math.cos(math.radians(deg)) > 0): co = 1
        else: co = 2 
        if (si == 1): 
            if(co==1): quad = 1 
            elif(co==2): quad = 2
        elif(si==2): 
            if(co==2): quad = 3 
            elif(co==1): quad = 4
        return quad

    def gaucheOuDroiteSpd(self, deg, spd):
        baseSpeed = 45 * spd
        #droite
        if(deg > 0):  
            #print("right")
            self._kLeftMotor.run(-baseSpeed)
            self._kRightMotor.run(baseSpeed)
        #gauche
        if(deg < 0):
            #print("left")
            self._kLeftMotor.run(baseSpeed)
            self._kRightMotor.run(-baseSpeed)

    def gaucheOuDroiteSlw(self, deg):
        #droite
        if(deg > 0):  
            #print("right")
            self._kLeftMotor.run(-45/8)
            self._kRightMotor.run(45/8)
        #gauche
        if(deg < 0):
            #print("left")
            self._kLeftMotor.run(45/8)
            self._kRightMotor.run(-45/8)

    def recal(self, deg):
        #while(abs(distToDeg(deg)) > 0.5):
            while(self._s.degrés() - deg > 0.5 and deg > 0):#gauche
                print("RE-CALIBRATING GAUCHE diff : " + str(self._s.degrés() - deg)+" deg: " +  str(self._s.degrés()))
                self.d._kLeftMotor.run(45/10)
                self.d._kRightMotor.run(-45/10)
            while(self._s.degrés() - deg < -0.5 and deg < 0):#droite
                print("RE-CALIBRATING DROIT diff : " + str(self._s.degrés() - deg)+" deg: " +  str(self._s.degrés()))
                self.d._kLeftMotor.run(-45/10)
                self.d._kRightMotor.run(45/10)