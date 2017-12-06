''' '''
'''
 ISC License

 Copyright (c) 2016-2017, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

 Permission to use, copy, modify, and/or distribute this software for any
 purpose with or without fee is hereby granted, provided that the above
 copyright notice and this permission notice appear in all copies.

 THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
import sys, os, inspect
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy
import pytest
import math

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
splitPath = path.split('simulation')

from Basilisk.utilities import SimulationBaseClass
from Basilisk.simulation import spacecraftPlus
from Basilisk.simulation import dualHingedRigidBodyStateEffector
from Basilisk.utilities import macros

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_
def spacecraftPlusAllTest(show_plots):
    [testResults, testMessage] = test_hubPropagate(show_plots)
    assert testResults < 1, testMessage

def test_hubPropagate(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages
    
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"
    
    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)
    
    #   Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    unitTestSim.TotalSim.terminateSimulation()
    
    # Create test thread
    testProcessRate = macros.sec2nano(0.0001)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    unitTestSim.panel1 = dualHingedRigidBodyStateEffector.DualHingedRigidBodyStateEffector()
    unitTestSim.panel2 = dualHingedRigidBodyStateEffector.DualHingedRigidBodyStateEffector()

    # Define Variable for panel 1
    unitTestSim.panel1.mass1 = 50.0
    unitTestSim.panel1.IPntS1_S1 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel1.d1 = 0.75
    unitTestSim.panel1.l1 = 1.5
    unitTestSim.panel1.k1 = 100.0
    unitTestSim.panel1.c1 = 0.0
    unitTestSim.panel1.rH1B_B = [[0.5], [0.0], [1.0]]
    unitTestSim.panel1.dcmH1B = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]
    unitTestSim.panel1.nameOfTheta1State = "dualHingedRigidBody1Theta1"
    unitTestSim.panel1.nameOfTheta1DotState = "dualHingedRigidBody1ThetaDot1"
    unitTestSim.panel1.mass2 = 50.0
    unitTestSim.panel1.IPntS2_S2 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel1.d2 = 0.75
    unitTestSim.panel1.l2 = 1.5
    unitTestSim.panel1.k2 = 100.0
    unitTestSim.panel1.c2 = 0.0
    unitTestSim.panel1.nameOfTheta2State = "dualHingedRigidBody1Theta2"
    unitTestSim.panel1.nameOfTheta2DotState = "dualHingedRigidBody1ThetaDot2"
    unitTestSim.panel1.theta1Init = 5*numpy.pi/180.0
    unitTestSim.panel1.theta1DotInit = 0.0
    unitTestSim.panel1.theta2Init = 0.0
    unitTestSim.panel1.theta2DotInit = 0.0

    # Define Variables for panel 2
    unitTestSim.panel2.mass1 = 50.0
    unitTestSim.panel2.IPntS1_S1 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel2.d1 = 0.75
    unitTestSim.panel2.l1 = 1.5
    unitTestSim.panel2.k1 = 100.0
    unitTestSim.panel2.c1 = 0.0
    unitTestSim.panel2.rH1B_B = [[-0.5], [0.0], [1.0]]
    unitTestSim.panel2.dcmH1B = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    unitTestSim.panel2.nameOfTheta1State = "dualHingedRigidBody2Theta1"
    unitTestSim.panel2.nameOfTheta1DotState = "dualHingedRigidBody2ThetaDot1"
    unitTestSim.panel2.mass2 = 50.0
    unitTestSim.panel2.IPntS2_S2 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel2.d2 = 0.75
    unitTestSim.panel2.l2 = 1.5
    unitTestSim.panel2.k2 = 100.0
    unitTestSim.panel2.c2 = 0.0
    unitTestSim.panel2.nameOfTheta2State = "dualHingedRigidBody2Theta2"
    unitTestSim.panel2.nameOfTheta2DotState = "dualHingedRigidBody2ThetaDot2"
    unitTestSim.panel2.theta1Init = 5*numpy.pi/180.0
    unitTestSim.panel2.theta1DotInit = 0.0
    unitTestSim.panel2.theta2Init = 0.0
    unitTestSim.panel2.theta2DotInit = 0.0

    # Add panels to spaceCraft
    # this next line is not working
    scObject.addStateEffector(unitTestSim.panel1)
    scObject.addStateEffector(unitTestSim.panel2)

    scObject.hub.mHub = 750.0
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]]
    scObject.hub.IHubPntBc_B = [[900.0, 0.0, 0.0], [0.0, 800.0, 0.0], [0.0, 0.0, 600.0]]

    # Set the initial values for the states
    scObject.hub.r_CN_NInit = [[0.1], [-0.4], [0.3]]
    scObject.hub.v_CN_NInit = [[-0.2], [0.5], [0.1]]
    scObject.hub.sigma_BNInit = [[0.0], [0.0], [0.0]]
    scObject.hub.omega_BN_BInit = [[0.1], [-0.1], [0.1]]

    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, scObject)

    unitTestSim.TotalSim.logThisMessage(scObject.scStateOutMsgName, testProcessRate)
    
    unitTestSim.InitializeSimulation()

    # Add energy and momentum variables to log
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totOrbEnergy", testProcessRate, 0, 0, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totOrbAngMomPntN_N", testProcessRate, 0, 2, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totRotAngMomPntC_N", testProcessRate, 0, 2, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totRotEnergy", testProcessRate, 0, 0, 'double')

    stopTime = 10.0
    unitTestSim.ConfigureStopTime(macros.sec2nano(stopTime))
    unitTestSim.ExecuteSimulation()

    orbEnergy = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totOrbEnergy")
    orbAngMom_N = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totOrbAngMomPntN_N")
    rotAngMom_N = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totRotAngMomPntC_N")
    rotEnergy = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totRotEnergy")

    sigmaOut = unitTestSim.pullMessageLogData(scObject.scStateOutMsgName+'.sigma_BN',range(3))
    rOut_BN_N = unitTestSim.pullMessageLogData(scObject.scStateOutMsgName+'.r_BN_N',range(3))
    vOut_CN_N = unitTestSim.pullMessageLogData(scObject.scStateOutMsgName+'.v_CN_N',range(3))

    plt.figure()
    plt.clf()
    plt.plot(orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,1] - orbAngMom_N[0,1])/orbAngMom_N[0,1], orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,2] - orbAngMom_N[0,2])/orbAngMom_N[0,2], orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,3] - orbAngMom_N[0,3])/orbAngMom_N[0,3])
    plt.xlabel('time (s)')
    plt.ylabel('Relative Difference')

    plt.figure()
    plt.clf()
    plt.plot(orbEnergy[:,0]*1e-9, (orbEnergy[:,1] - orbEnergy[0,1])/orbEnergy[0,1])
    plt.xlabel('time (s)')
    plt.ylabel('Relative Difference')

    plt.figure()
    plt.clf()
    plt.plot(rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,1] - rotAngMom_N[0,1])/rotAngMom_N[0,1], rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,2] - rotAngMom_N[0,2])/rotAngMom_N[0,2], rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,3] - rotAngMom_N[0,3])/rotAngMom_N[0,3])
    plt.xlabel('time (s)')
    plt.ylabel('Relative Difference')

    plt.figure()
    plt.clf()
    plt.plot(rotEnergy[:,0]*1e-9, (rotEnergy[:,1] - rotEnergy[0,1])/rotEnergy[0,1])
    plt.xlabel('time (s)')
    plt.ylabel('Relative Difference')

    plt.figure()
    plt.clf()
    plt.plot(vOut_CN_N[:,0]*1e-9, vOut_CN_N[:,1], vOut_CN_N[:,0]*1e-9, vOut_CN_N[:,2], vOut_CN_N[:,0]*1e-9, vOut_CN_N[:,3])
    plt.xlabel('time (s)')
    plt.ylabel('m/s')

    plt.figure()
    plt.clf()
    plt.plot(vOut_CN_N[:,0]*1e-9, (vOut_CN_N[:,1] - vOut_CN_N[0,1])/vOut_CN_N[0,1], vOut_CN_N[:,0]*1e-9, (vOut_CN_N[:,2] - vOut_CN_N[0,2])/vOut_CN_N[0,2], vOut_CN_N[:,0]*1e-9, (vOut_CN_N[:,3] - vOut_CN_N[0,3])/vOut_CN_N[0,3])
    plt.xlabel('time (s)')
    plt.ylabel('Relative Difference')

    plt.show(show_plots)
    plt.close("all")

    if testFailCount == 0:
        print "PASSED: " + " Hub Propagate"
    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    spacecraftPlusAllTest(True)
