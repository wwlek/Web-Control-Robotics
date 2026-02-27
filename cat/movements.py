#movements.py

#// Rotors
from machine import I2C
import sys
import esp
import time

from pca9685 import PCA9685Driver

#// Display
import st7789py as st7789
import tft_config
import vga2_bold_16x32 as font
import machine

#// Display init

#display = tft_config.config()
#display.fill(st7789.BLACK)
controllerBatteries = machine.ADC(0)
rotorBatteries = machine.ADC(1)

#// Rotor init

pwm = PCA9685Driver(scl_pin=5,sda_pin=4,i2c_freq=400000)
print(pwm.i2c.scan())
pwm.set_pwm_frequency(50)

pmwLowerBand = 0.5
pmwUpperBand = 2.5

delayBetweenSteps = 0.2

#// Walk Cycle Animations ------------------------------------

upperLegSteps = [[90, 120, 161, 50], # Left Front (0)
                 [90, 60, 20, 130], # Right Front (1)
                 [25, 50, 90, 0], # Left Back (2)
                 [150, 125, 85, 177]]  # Right Back (3)

lowerLegSteps = [[180, 150, 175, 180], # Left Front (4)
                 [10, 40, 15, 15], # Right Front (5)
                 [178, 140, 175, 180], # Left Back (6)
                 [0, 40, 10, 0]]  # Right Back (7)

#// Dance Cycle Animations ------------------------------------

upperLegDanceSteps = [[110, 100], # Left Front (0)
                     [70, 80], # Right Front (1)
                     [50, 40], # Left Back (2)
                     [120, 140]]  # Right Back (3)

lowerLegDanceSteps = [[150, 180], # Left Front (4)
                     [30, 10], # Right Front (5)
                     [148, 180], # Left Back (6)
                     [30, 0]]  # Right Back (7)

#// Sit & Wave Animations ------------------------------------

upperSitSteps = [[90, 100, 5, 30], # Left Front (0)
                [90, 80, 80, 80], # Right Front (1)
                [2, 2, 2, 2], # Left Back (2)
                [179, 179, 179, 179]]  # Right Back (3)

lowerSitSteps = [[90, 70, 170, 60], # Left Front (4)
                [90, 110, 110, 110], # Right Front (5)
                [180, 90, 90, 90], # Left Back (6)
                [0, 90, 90, 90]]  # Right Back (7)

#// Climp & Wave Animations ------------------------------------

upperClimbSteps = [[90,  100, 2,   2,   2,  150], # Left Front (0)
                   [90,  80,  178, 178, 178, 30], # Right Front (1)
                   [2,   2,   2,   2,   50, 50], # Left Back (2)
                   [179, 179, 179, 179, 130, 130]]  # Right Back (3)

lowerClimbSteps = [ [90,  70,  90,  90, 90,  45, 90], # Left Front (4)
                    [90,  110, 90,  90, 90, 135, 90], # Right Front (5)
                    [180, 90,  130, 90, 90,  90, 90], # Left Back (6)
                    [0,   90,  50,  90, 90,  90, 90]]  # Right Back (7)

def updateLegClimb(imLegIndex, imAnimationIndex):
    pwm.servo_set_angle_custom(imLegIndex, upperClimbSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
    pwm.servo_set_angle_custom(imLegIndex + 4, lowerClimbSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)

def updateLeg(imLegIndex, imAnimationIndex):
    pwm.servo_set_angle_custom(imLegIndex, upperLegSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
    pwm.servo_set_angle_custom(imLegIndex + 4, lowerLegSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)

def climb():
    
    #for legIndex in range(len(upperClimbSteps)):
    #    updateLegClimb(legIndex, 4)
    
    #// Neutral Initialize Position
    """for legIndex in range(len(upperClimbSteps)):
        updateLeg(legIndex, 0)
    time.sleep(2)
    
    for animationIndex in range(len(upperClimbSteps[0])):
        
        for legIndex in range(len(upperClimbSteps)):
            updateLegClimb(legIndex, animationIndex)
        time.sleep(2)"""

#climb() 

def updateLegSit(imLegIndex, imAnimationIndex):
    pwm.servo_set_angle_custom(imLegIndex, upperSitSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
    pwm.servo_set_angle_custom(imLegIndex + 4, lowerSitSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
    
def sitUpAndWave():
    currentStep = 0
    totalSteps = 0
    while (currentStep <= 3): #// Sit Up Animation
        
        for legIndex in range(len(upperSitSteps)):
            updateLegSit(legIndex, currentStep)
        
        time.sleep(0.35)
        currentStep += 1
    
    while (totalSteps < 12):
        if currentStep == 3:
            currentStep = 2
        else:
            currentStep = 3
        for legIndex in range(len(upperSitSteps)):
            updateLegSit(legIndex, currentStep)
        
        totalSteps += 1
        time.sleep(0.5)
    
def walk():
    currentStep = 0
    totalSteps = 0
    while (totalSteps <= 2):
        
        for legIndex in range(len(upperLegSteps)):
            #actualIndex = (currentStep + legIndex) % 4 #// Quarter Step
            animationIndex = currentStep #// Diagonal Half Step
            if legIndex == 0 or legIndex == 3:
                animationIndex = (currentStep + 2) % 4
            updateLeg(legIndex, animationIndex)
        
        #updateDisplay()
        time.sleep(delayBetweenSteps)
        currentStep += 1;
        if currentStep == 4:
            currentStep = 0
            totalSteps += 1
    for legIndex in range(len(upperLegSteps)):
        updateLeg(legIndex, 0)
    
def lerp(imStart, imTarget, imPercentage):
    return ((1.0 - imPercentage) * imStart) + (imPercentage * imTarget) 

def updateDisplay():
    display.text(font,str(controllerBatteries.read()),0,0,st7789.GREEN,st7789.BLACK)
    display.text(font,str(rotorBatteries.read()),0,30,st7789.GREEN,st7789.BLACK)

def updateLegForDance(imLegIndex, imAnimationIndex):
    pwm.servo_set_angle_custom(imLegIndex, upperLegDanceSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
    pwm.servo_set_angle_custom(imLegIndex + 4, lowerLegDanceSteps[imLegIndex][imAnimationIndex], pmwLowerBand, pmwUpperBand)
            
def rotateRight():
    currentStep = 0
    totalSteps = 0
    updateLeg(1, 2) # Right Front
    updateLeg(3, 2) # Right Back
        
    while (totalSteps < 4):
        for legIndex in range(0, 3, 2):
            animationIndex = currentStep #// Diagonal Half Step
            print(legIndex)
            if legIndex == 2:
                animationIndex = (currentStep + 2) % 4
            updateLeg(legIndex, animationIndex)
        
        time.sleep(delayBetweenSteps)
        currentStep += 1;
        if currentStep == 4:
            currentStep = 0
            totalSteps += 1
            
def rotateLeft():
    currentStep = 0
    totalSteps = 0
    updateLeg(0, 2) # Left Front
    updateLeg(2, 2) # Left Back
        
    while (totalSteps < 4):
        for legIndex in range(1, 4, 2):
            animationIndex = currentStep #// Diagonal Half Step
            if legIndex == 3:
                animationIndex = (currentStep + 2) % 4
            updateLeg(legIndex, animationIndex)
        
        time.sleep(delayBetweenSteps)
        currentStep += 1;
        if currentStep == 4:
            currentStep = 0
            totalSteps += 1
        
def dance():
    currentStep = 0
    updateLegForDance(2, 0) # Right Front
    updateLegForDance(3, 0) # Right Back
    danceDelay = 0.75
    while (True):
        
        for legIndex in range(len(upperLegDanceSteps)):
            #actualIndex = (currentStep + legIndex) % 4 #// Quarter Step
            animationIndex = currentStep 
            if legIndex == 0 or legIndex == 1:
                animationIndex = (currentStep + 1) % 2
            updateLegForDance(legIndex, animationIndex)
            
            #else:
                #updateLegForDance(legIndex, animationIndex)
                #time.sleep(delayBetweenSteps)
            
        time.sleep(danceDelay)
        #updateDisplay()
        currentStep += 1;
        if currentStep == 2:
            currentStep = 0
 
def legLerpDance(imLegIndex, imAnimationIndexStart, imAnimationIndexTarget, percentage):
    targetAngle = lerp(lowerLegDanceSteps[imLegIndex][imAnimationIndexStart], lowerLegDanceSteps[imLegIndex][imAnimationIndexTarget], percentage)
    pwm.servo_set_angle_custom(imLegIndex + 4, targetAngle, pmwLowerBand, pmwUpperBand)
    targetAngle = lerp(upperLegDanceSteps[imLegIndex][imAnimationIndexStart], upperLegDanceSteps[imLegIndex][imAnimationIndexTarget], percentage)
    pwm.servo_set_angle_custom(imLegIndex, targetAngle, pmwLowerBand, pmwUpperBand)

def smoothDance():
    animProgress = 0.0
    
    animationIndices = [1, 0, 1, 0]
    animationProgress = [0.0, 0.0, 0.0, 0.0]
    
    danceCount = 0
    
    while (danceCount < 900):   
        
        for legIndex in range(len(upperLegDanceSteps)):
            
            startIndex = animationIndices[legIndex]
            endIndex = 0
            if (startIndex == 0):
                endIndex = 1
            
            legLerpDance(legIndex, startIndex, endIndex, animationProgress[legIndex])
            animationProgress[legIndex] += 0.015
            if (animationProgress[legIndex] > 1.0):
                animationProgress[legIndex] = 0.0
                if (startIndex == 0):
                    animationIndices[legIndex] = 1
                else:
                    animationIndices[legIndex] = 0
                    
        danceCount += 1
    
#smoothDance()
#walk()
#sitUpAndWave()
#rotateLeft()
#dance()
#rotateRight()
#sitUpAndWave()


