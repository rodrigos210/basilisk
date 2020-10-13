''' '''
'''
 ISC License

 Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
import matplotlib.pyplot as plt
import numpy
import pytest

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
splitPath = path.split('simulation')

from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport
from Basilisk.simulation import spacecraftPlus
from Basilisk.simulation import dualHingedRigidBodyStateEffector
from Basilisk.simulation import gravityEffector
from Basilisk.utilities import macros
from Basilisk.simulation import spacecraftDynamics
from Basilisk.simulation import simFswInterfaceMessages

@pytest.mark.parametrize("useFlag, testCase", [
    (False, 'NoGravity'),
    (False, 'Gravity')
])

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_
def test_dualHingedRigidBody(show_plots,useFlag,testCase):
    """Module Unit Test"""
    [testResults, testMessage] = dualHingedRigidBodyTest(show_plots,useFlag,testCase)
    assert testResults < 1, testMessage

def dualHingedRigidBodyTest(show_plots,useFlag,testCase):
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

    if testCase == 'Gravity':
        unitTestSim.earthGravBody = gravityEffector.GravBodyData()
        unitTestSim.earthGravBody.bodyInMsgName = "earth_planet_data"
        unitTestSim.earthGravBody.outputMsgName = "earth_display_frame_data"
        unitTestSim.earthGravBody.mu = 0.3986004415E+15 # meters!
        unitTestSim.earthGravBody.isCentralBody = True
        unitTestSim.earthGravBody.useSphericalHarmParams = False
        scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector([unitTestSim.earthGravBody])
        scObject.hub.r_CN_NInit = [[-4020338.690396649],	[7490566.741852513],	[5248299.211589362]]
        scObject.hub.v_CN_NInit = [[-5199.77710904224],	[-3436.681645356935],	[1041.576797498721]]

    unitTestSim.TotalSim.logThisMessage(scObject.scStateOutMsgName, testProcessRate)
    
    unitTestSim.InitializeSimulation()

    # Add energy and momentum variables to log
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totOrbEnergy", testProcessRate, 0, 0, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totOrbAngMomPntN_N", testProcessRate, 0, 2, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totRotAngMomPntC_N", testProcessRate, 0, 2, 'double')
    unitTestSim.AddVariableForLogging(scObject.ModelTag + ".totRotEnergy", testProcessRate, 0, 0, 'double')

    stopTime = 1.0
    unitTestSim.ConfigureStopTime(macros.sec2nano(stopTime))
    unitTestSim.ExecuteSimulation()

    orbEnergy = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totOrbEnergy")
    orbAngMom_N = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totOrbAngMomPntN_N")
    rotAngMom_N = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totRotAngMomPntC_N")
    rotEnergy = unitTestSim.GetLogVariableData(scObject.ModelTag + ".totRotEnergy")

    initialOrbAngMom_N = [
                [orbAngMom_N[0, 1], orbAngMom_N[0, 2], orbAngMom_N[0, 3]]
                ]

    finalOrbAngMom = [
                [orbAngMom_N[-1, 0], orbAngMom_N[-1, 1], orbAngMom_N[-1, 2], orbAngMom_N[-1, 3]]
                 ]

    initialRotAngMom_N = [
                [rotAngMom_N[0, 1], rotAngMom_N[0, 2], rotAngMom_N[0, 3]]
                ]

    finalRotAngMom = [
                [rotAngMom_N[-1, 0], rotAngMom_N[-1, 1], rotAngMom_N[-1, 2], rotAngMom_N[-1, 3]]
                 ]

    initialOrbEnergy = [
                [orbEnergy[0, 1]]
                ]

    finalOrbEnergy = [
                [orbEnergy[-1, 0], orbEnergy[-1, 1]]
                 ]

    initialRotEnergy = [
                [rotEnergy[int(len(rotEnergy)/2)+1, 1]]
                ]

    finalRotEnergy = [
                [rotEnergy[-1, 0], rotEnergy[-1, 1]]
                 ]

    plt.close('all')
    plt.figure()
    plt.clf()
    plt.plot(orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,1] - orbAngMom_N[0,1])/orbAngMom_N[0,1], orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,2] - orbAngMom_N[0,2])/orbAngMom_N[0,2], orbAngMom_N[:,0]*1e-9, (orbAngMom_N[:,3] - orbAngMom_N[0,3])/orbAngMom_N[0,3])
    plt.xlabel("Time (s)")
    plt.ylabel("Relative Difference")
    unitTestSupport.writeFigureLaTeX("ChangeInOrbitalAngularMomentum" + testCase, "Change in Orbital Angular Momentum " + testCase, plt, r"width=0.8\textwidth", path)
    plt.figure()
    plt.clf()
    plt.plot(orbEnergy[:,0]*1e-9, (orbEnergy[:,1] - orbEnergy[0,1])/orbEnergy[0,1])
    plt.xlabel("Time (s)")
    plt.ylabel("Relative Difference")
    unitTestSupport.writeFigureLaTeX("ChangeInOrbitalEnergy" + testCase, "Change in Orbital Energy " + testCase, plt, r"width=0.8\textwidth", path)
    plt.figure()
    plt.clf()
    plt.plot(rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,1] - rotAngMom_N[0,1])/rotAngMom_N[0,1], rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,2] - rotAngMom_N[0,2])/rotAngMom_N[0,2], rotAngMom_N[:,0]*1e-9, (rotAngMom_N[:,3] - rotAngMom_N[0,3])/rotAngMom_N[0,3])
    plt.xlabel("Time (s)")
    plt.ylabel("Relative Difference")
    unitTestSupport.writeFigureLaTeX("ChangeInRotationalAngularMomentum" + testCase, "Change in Rotational Angular Momentum " + testCase, plt, r"width=0.8\textwidth", path)
    plt.figure()
    plt.clf()
    plt.plot(rotEnergy[:,0]*1e-9, (rotEnergy[:,1] - rotEnergy[0,1])/rotEnergy[0,1])
    plt.xlabel("Time (s)")
    plt.ylabel("Relative Difference")
    unitTestSupport.writeFigureLaTeX("ChangeInRotationalEnergy" + testCase, "Change in Rotational Energy " + testCase, plt, r"width=0.8\textwidth", path)
    if show_plots:
        plt.show()
        plt.close("all")

    accuracy = 1e-10
    for i in range(0,len(initialOrbAngMom_N)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(finalOrbAngMom[i],initialOrbAngMom_N[i],3,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Dual Hinged Rigid Body Integrated Test failed orbital angular momentum unit test")

    for i in range(0,len(initialRotAngMom_N)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(finalRotAngMom[i],initialRotAngMom_N[i],3,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Dual Hinged Rigid Body Integrated Test failed rotational angular momentum unit test")

    for i in range(0,len(initialOrbEnergy)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(finalOrbEnergy[i],initialOrbEnergy[i],1,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Dual Hinged Rigid Body Integrated Test failed orbital energy unit test")

    for i in range(0,len(initialRotEnergy)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(finalRotEnergy[i],initialRotEnergy[i],1,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Dual Hinged Rigid Body Integrated Test failed rotational energy unit test")

    if testFailCount == 0:
        print("PASSED: " + " Dual Hinged Rigid Body Test")
    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]


@pytest.mark.parametrize("useScPlus", [True, False])
def test_dualHingedRigidBodyMotorTorque(show_plots, useScPlus):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    if useScPlus:
        scObject = spacecraftPlus.SpacecraftPlus()
        scObject.ModelTag = "spacecraftBody"
    else:
        scObject = spacecraftDynamics.SpacecraftDynamics()
        scObject.ModelTag = "spacecraftBody"
        scObject.primaryCentralSpacecraft.spacecraftName = scObject.ModelTag

    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    #   Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()

    # Create test thread
    testProcessRate = macros.sec2nano(0.01)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    unitTestSim.panel1 = dualHingedRigidBodyStateEffector.DualHingedRigidBodyStateEffector()
    unitTestSim.panel2 = dualHingedRigidBodyStateEffector.DualHingedRigidBodyStateEffector()

    # Define Variable for panel 1
    unitTestSim.panel1.ModelTag = "panel1"
    unitTestSim.panel1.mass1 = 50.0
    unitTestSim.panel1.IPntS1_S1 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel1.d1 = 0.75
    unitTestSim.panel1.l1 = 1.5
    unitTestSim.panel1.k1 = 0.0
    unitTestSim.panel1.c1 = 0.0
    unitTestSim.panel1.rH1B_B = [[0.5], [0.0], [1.0]]
    unitTestSim.panel1.dcmH1B = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]
    unitTestSim.panel1.nameOfTheta1State = "dualHingedRigidBody1Theta1"
    unitTestSim.panel1.nameOfTheta1DotState = "dualHingedRigidBody1ThetaDot1"
    unitTestSim.panel1.mass2 = 50.0
    unitTestSim.panel1.IPntS2_S2 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel1.d2 = 0.75
    unitTestSim.panel1.k2 = 100.0
    unitTestSim.panel1.c2 = 0.0
    unitTestSim.panel1.nameOfTheta2State = "dualHingedRigidBody1Theta2"
    unitTestSim.panel1.nameOfTheta2DotState = "dualHingedRigidBody1ThetaDot2"
    unitTestSim.panel1.theta1Init = 5*numpy.pi/180.0
    unitTestSim.panel1.theta1DotInit = 0.0
    unitTestSim.panel1.theta2Init = 0.0
    unitTestSim.panel1.theta2DotInit = 0.0
    unitTestSim.panel1.motorTorqueInMsgName = "motorTorque"

    # set a fixed motor torque message
    motorMsg = simFswInterfaceMessages.ArrayMotorTorqueIntMsg()
    motorMsg.motorTorque = [2.0, 4.0]
    unitTestSupport.setMessage(unitTestSim.TotalSim,
                               unitProcessName,
                               unitTestSim.panel1.motorTorqueInMsgName,
                               motorMsg)

    # Define Variables for panel 2
    unitTestSim.panel2.ModelTag = "panel2"
    unitTestSim.panel2.mass1 = 50.0
    unitTestSim.panel2.IPntS1_S1 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel2.d1 = 0.75
    unitTestSim.panel2.l1 = 1.5
    unitTestSim.panel2.k1 = 0.0
    unitTestSim.panel2.c1 = 0.0
    unitTestSim.panel2.rH1B_B = [[-0.5], [0.0], [1.0]]
    unitTestSim.panel2.dcmH1B = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    unitTestSim.panel2.nameOfTheta1State = "dualHingedRigidBody2Theta1"
    unitTestSim.panel2.nameOfTheta1DotState = "dualHingedRigidBody2ThetaDot1"
    unitTestSim.panel2.mass2 = 50.0
    unitTestSim.panel2.IPntS2_S2 = [[50.0, 0.0, 0.0], [0.0, 25.0, 0.0], [0.0, 0.0, 25.0]]
    unitTestSim.panel2.d2 = 0.75
    unitTestSim.panel2.k2 = 0.0
    unitTestSim.panel2.c2 = 0.0
    unitTestSim.panel2.nameOfTheta2State = "dualHingedRigidBody2Theta2"
    unitTestSim.panel2.nameOfTheta2DotState = "dualHingedRigidBody2ThetaDot2"
    unitTestSim.panel2.theta1Init = 5 * numpy.pi / 180.0
    unitTestSim.panel2.theta1DotInit = 0.0
    unitTestSim.panel2.theta2Init = 0.0
    unitTestSim.panel2.theta2DotInit = 0.0
    unitTestSim.panel2.hingedRigidBodyOutMsgName = "panelTwo"

    # Add panels to spaceCraft
    scObjectPrimary = scObject
    if not useScPlus:
        scObjectPrimary = scObject.primaryCentralSpacecraft

    scObjectPrimary.addStateEffector(unitTestSim.panel1)
    scObjectPrimary.addStateEffector(unitTestSim.panel2)

    # Define mass properties of the rigid part of the spacecraft
    scObjectPrimary.hub.mHub = 750.0
    scObjectPrimary.hub.r_BcB_B = [[0.0], [0.0], [1.0]]
    scObjectPrimary.hub.IHubPntBc_B = [[900.0, 0.0, 0.0], [0.0, 800.0, 0.0], [0.0, 0.0, 600.0]]

    # Set the initial values for the states
    scObjectPrimary.hub.r_CN_NInit = [[0.0], [0.0], [0.0]]
    scObjectPrimary.hub.v_CN_NInit = [[0.0], [0.0], [0.0]]
    scObjectPrimary.hub.sigma_BNInit = [[0.0], [0.0], [0.0]]
    scObjectPrimary.hub.omega_BN_BInit = [[0.0], [0.0], [0.0]]

    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, scObject)
    unitTestSim.AddModelToTask(unitTaskName, unitTestSim.panel1)
    unitTestSim.AddModelToTask(unitTaskName, unitTestSim.panel2)

    scStateLogName = "inertial_state_output"
    if not useScPlus:
        scStateLogName = scObject.primaryCentralSpacecraft.spacecraftName + scStateLogName
    unitTestSim.TotalSim.logThisMessage(scStateLogName, testProcessRate)
    unitTestSim.TotalSim.logThisMessage(unitTestSim.panel1.ModelTag + "_OutputStates0", testProcessRate)
    unitTestSim.TotalSim.logThisMessage(unitTestSim.panel1.ModelTag + "_OutputStates1", testProcessRate)
    unitTestSim.TotalSim.logThisMessage(unitTestSim.panel2.hingedRigidBodyOutMsgName + "_OutputStates0", testProcessRate)
    unitTestSim.TotalSim.logThisMessage(unitTestSim.panel2.hingedRigidBodyOutMsgName + "_OutputStates1", testProcessRate)
    # unitTestSim.TotalSim.logThisMessage(unitTestSim.panel1.hingedRigidBodyConfigLogOutMsgName, testProcessRate)
    # unitTestSim.TotalSim.logThisMessage(unitTestSim.panel2.hingedRigidBodyConfigLogOutMsgName, testProcessRate)

    unitTestSim.InitializeSimulation()

    variableLogTag = scObject.ModelTag
    if not useScPlus:
        variableLogTag += ".primaryCentralSpacecraft"

    unitTestSim.AddVariableForLogging(variableLogTag + ".totRotAngMomPntC_N",
                                      testProcessRate, 0, 2, 'double')

    stopTime = 10.0
    unitTestSim.ConfigureStopTime(macros.sec2nano(stopTime))
    unitTestSim.ExecuteSimulation()

    rOut_CN_N = unitTestSim.pullMessageLogData(scStateLogName + '.r_CN_N', list(range(3)))
    vOut_CN_N = unitTestSim.pullMessageLogData(scStateLogName + '.v_CN_N', list(range(3)))
    sigma_BN = unitTestSim.pullMessageLogData(scStateLogName + '.sigma_BN', list(range(3)))
    thetaP1A1 = unitTestSim.pullMessageLogData(unitTestSim.panel1.ModelTag + '_OutputStates0.theta')
    thetaP1A2 = unitTestSim.pullMessageLogData(unitTestSim.panel1.ModelTag + '_OutputStates1.theta')
    thetaP2A1 = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyOutMsgName+'_OutputStates0.theta')
    thetaP2A2 = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyOutMsgName+'_OutputStates1.theta')

    # rB1N = unitTestSim.pullMessageLogData(unitTestSim.panel1.hingedRigidBodyConfigLogOutMsgName + '.r_BN_N', list(range(3)))[0]
    # vB1N = unitTestSim.pullMessageLogData(unitTestSim.panel1.hingedRigidBodyConfigLogOutMsgName + '.v_BN_N', list(range(3)))[0]
    # sB1N = unitTestSim.pullMessageLogData(unitTestSim.panel1.hingedRigidBodyConfigLogOutMsgName + '.sigma_BN', list(range(3)))[0]
    # oB1N = unitTestSim.pullMessageLogData(unitTestSim.panel1.hingedRigidBodyConfigLogOutMsgName + '.omega_BN_B', list(range(3)))[0]
    # rB2N = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyConfigLogOutMsgName + '.r_BN_N', list(range(3)))[0]
    # vB2N = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyConfigLogOutMsgName + '.v_BN_N', list(range(3)))[0]
    # sB2N = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyConfigLogOutMsgName + '.sigma_BN', list(range(3)))[0]
    # oB2N = unitTestSim.pullMessageLogData(unitTestSim.panel2.hingedRigidBodyConfigLogOutMsgName + '.omega_BN_B', list(range(3)))[0]

    rotAngMom_N = unitTestSim.GetLogVariableData(
        variableLogTag + ".totRotAngMomPntC_N")

    # Get the last sigma and position
    dataPos = [rOut_CN_N[-1]]

    truePos = [[0., 0., 0.]]

    initialRotAngMom_N = [[rotAngMom_N[0, 1], rotAngMom_N[0, 2], rotAngMom_N[0, 3]]]

    finalRotAngMom = [rotAngMom_N[-1]]

    plt.close("all")

    plt.figure()
    plt.clf()
    plt.plot(rotAngMom_N[:, 0] * 1e-9, (rotAngMom_N[:, 1] - rotAngMom_N[0, 1]) ,
             rotAngMom_N[:, 0] * 1e-9, (rotAngMom_N[:, 2] - rotAngMom_N[0, 2]) ,
             rotAngMom_N[:, 0] * 1e-9, (rotAngMom_N[:, 3] - rotAngMom_N[0, 3]) )
    plt.xlabel('time (s)')
    plt.ylabel('Ang. Momentum Difference')

    plt.figure()
    plt.clf()
    plt.plot(vOut_CN_N[:, 0] * 1e-9, vOut_CN_N[:, 1], vOut_CN_N[:, 0] * 1e-9, vOut_CN_N[:, 2], vOut_CN_N[:, 0] * 1e-9,
             vOut_CN_N[:, 3])
    plt.xlabel('time (s)')
    plt.ylabel('m/s')

    plt.figure()
    plt.clf()
    plt.plot(sigma_BN[:, 0] * macros.NANO2SEC, sigma_BN[:, 1],
             color=unitTestSupport.getLineColor(1, 3),
             label=r'$\sigma_{1}$')
    plt.plot(sigma_BN[:, 0] * macros.NANO2SEC, sigma_BN[:, 2],
             color=unitTestSupport.getLineColor(2, 3),
             label=r'$\sigma_{2}$')
    plt.plot(sigma_BN[:, 0] * macros.NANO2SEC, sigma_BN[:, 3],
             color=unitTestSupport.getLineColor(3, 3),
             label=r'$\sigma_{3}$')
    plt.legend(loc='lower right')
    plt.xlabel('time (s)')
    plt.ylabel(r'MRP $\sigma_{B/N}$')

    plt.figure()
    plt.clf()
    plt.plot(thetaP1A1[:, 0] * macros.NANO2SEC, thetaP1A1[:, 1]*macros.R2D,
             color=unitTestSupport.getLineColor(1, 4),
             label=r'Panel 1 $\theta_{1}$')
    plt.plot(thetaP1A1[:, 0] * macros.NANO2SEC, thetaP1A2[:, 1]*macros.R2D,
             color=unitTestSupport.getLineColor(2, 4),
             label=r'Panel 1 $\theta_{2}$')
    plt.plot(thetaP1A1[:, 0] * macros.NANO2SEC, thetaP2A1[:, 1] * macros.R2D,
             color=unitTestSupport.getLineColor(3, 4),
             label=r'Panel 2 $\theta_{1}$')
    plt.plot(thetaP1A1[:, 0] * macros.NANO2SEC, thetaP2A2[:, 1] * macros.R2D,
             color=unitTestSupport.getLineColor(4, 4),
             label=r'Panel 2 $\theta_{2}$')
    plt.legend(loc='lower right')
    plt.xlabel('time (s)')
    plt.ylabel('Hinge Angles [deg]')

    if show_plots:
        plt.show()
    plt.close("all")

    accuracy = 1e-10
    for i in range(0, len(truePos)):
        # check a vector values
        if not unitTestSupport.isArrayEqual(dataPos[i], truePos[i], 3, accuracy):
            testFailCount += 1
            testMessages.append("FAILED:  Hinged Rigid Body integrated test failed position test")

    for i in range(0, len(initialRotAngMom_N)):
        # check a vector values
        if not unitTestSupport.isArrayEqual(finalRotAngMom[i], initialRotAngMom_N[i], 3, accuracy):
            testFailCount += 1
            testMessages.append(
                "FAILED: Hinged Rigid Body integrated test failed rotational angular momentum unit test")

    # check config log messages
    # if not unitTestSupport.isArrayEqual(rB1N, [2.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 1 r_BN_N config log test")
    # if not unitTestSupport.isArrayEqual(vB1N, [0.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 1 v_BN_N config log test")
    # if not unitTestSupport.isArrayEqual(sB1N, [0.0, 0, 1.0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 1 sigma_BN config log test")
    # if not unitTestSupport.isArrayEqual(oB1N, [0.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 1 omega_BN_B config log test")
    # if not unitTestSupport.isArrayEqual(rB2N, [-2.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 2 r_BN_N config log test")
    # if not unitTestSupport.isArrayEqual(vB2N, [0.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 2 v_BN_N config log test")
    # if not unitTestSupport.isArrayEqual(sB2N, [0.0, 0, 0.0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 2 sigma_BN config log test")
    # if not unitTestSupport.isArrayEqual(oB2N, [0.0, 0, 0], 3, accuracy):
    #     testFailCount += 1
    #     testMessages.append("FAILED:  Hinged Rigid Body integrated test failed panel 2 omega_BN_B config log test")


    if testFailCount == 0:
        print("PASSED: " + " Hinged Rigid Body integrated test with motor torques")

    assert testFailCount < 1, testMessages
    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]




if __name__ == "__main__":
    # dualHingedRigidBodyTest(True, False, 'Gravity')
    test_dualHingedRigidBodyMotorTorque(True,   # show plots
                                        True)   # use scPlus
