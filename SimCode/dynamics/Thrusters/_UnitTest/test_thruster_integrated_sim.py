'''
Copyright (c) 2016, Autonomous Vehicle Systems Lab, Univeristy of Colorado at Boulder

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
splitPath = path.split('SimCode')
sys.path.append(splitPath[0] + '/modules')
sys.path.append(splitPath[0] + '/PythonModules')

import SimulationBaseClass
import unitTestSupport  # general support file with common unit test functions
import macros
import spacecraftPlus
import sim_model
import ctypes
import gravityEffector
import spice_interface
import simIncludeThruster
import thrusterDynamicEffector
import vehicleConfigData

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_
def thrusterIntegratedTest(show_plots):
    [testResults, testMessage] = test_thrusterIntegratedTest(show_plots)
    assert testResults < 1, testMessage

def test_thrusterIntegratedTest(show_plots):
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
    thrusterCommandName = "acs_thruster_cmds"
    
    #   Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    unitTestSim.TotalSim.terminateSimulation()
    
    # Create test thread
    testProcessRate = macros.sec2nano(0.1)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    # add thruster devices
    # The clearThrusterSetup() is critical if the script is to run multiple times
    simIncludeThruster.clearSetup()
    simIncludeThruster.create(
        'MOOG_Monarc_1',
        [1,0,0],                # location in S frame
        [0,1,0]                 # direction in S frame
    )

    # create thruster object container and tie to spacecraft object
    thrustersDynamicEffector = thrusterDynamicEffector.ThrusterDynamicEffector()
    simIncludeThruster.addToSpacecraft(  "Thrusters",
                                       thrustersDynamicEffector,
                                       scObject)

    # setup the thruster mass properties (This will be in the full tank - still to come!)
    # thrusterPropCM = [0.0, 0.0, 1.2]
    # thrusterPropMass = 40.0
    # thrusterPropRadius = 46.0 / 2.0 / 3.2808399 / 12.0
    # sphereInerita = 2.0 / 5.0 * thrusterPropMass * thrusterPropRadius * thrusterPropRadius
    # thrusterPropInertia = [sphereInerita, 0, 0, 0, sphereInerita, 0, 0, 0, sphereInerita]
    # thrustersDynamicEffector.objProps.Mass = thrusterPropMass
    # thrustersDynamicEffector.objProps.CoM = thrusterPropCM
    # thrustersDynamicEffector.objProps.InertiaTensor = thrusterPropInertia

    # set thruster commands
    ThrustMessage = thrusterDynamicEffector.ThrustCmdStruct()
    ThrustMessage.OnTimeRequest = 10.0
    unitTestSim.TotalSim.CreateNewMessage(unitProcessName, thrusterCommandName, 8, 2)
    unitTestSim.TotalSim.WriteMessageData(thrusterCommandName, 8, 0, ThrustMessage)

    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, thrustersDynamicEffector)
    unitTestSim.AddModelToTask(unitTaskName, scObject)
    
    unitTestSim.earthGravBody = gravityEffector.GravBodyData()
    unitTestSim.earthGravBody.bodyMsgName = "earth_planet_data"
    unitTestSim.earthGravBody.outputMsgName = "earth_display_frame_data"
    unitTestSim.earthGravBody.mu = 0.3986004415E+15 # meters!
    unitTestSim.earthGravBody.isCentralBody = True
    unitTestSim.earthGravBody.useSphericalHarmParams = False

    earthEphemData = spice_interface.SpicePlanetState()
    earthEphemData.J2000Current = 0.0
    earthEphemData.PositionVector = [0.0, 0.0, 0.0]
    earthEphemData.VelocityVector = [0.0, 0.0, 0.0]
    earthEphemData.J20002Pfix = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    earthEphemData.J20002Pfix_dot = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    earthEphemData.PlanetName = "earth"

    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector([unitTestSim.earthGravBody])

    unitTestSim.TotalSim.logThisMessage(scObject.scStateOutMsgName, testProcessRate)

    unitTestSim.TotalSim.CreateNewMessage(unitProcessName,
        unitTestSim.earthGravBody.bodyMsgName, 8+8*3+8*3+8*9+8*9+8+64, 2)
    unitTestSim.TotalSim.WriteMessageData(unitTestSim.earthGravBody.bodyMsgName, 8+8*3+8*3+8*9+8*9+8+64, 0, earthEphemData)

    unitTestSim.InitializeSimulation()

    posRef = scObject.dynManager.getStateObject("hubPosition")
    velRef = scObject.dynManager.getStateObject("hubVelocity")
    sigmaRef = scObject.dynManager.getStateObject("hubSigma")
    omegaRef = scObject.dynManager.getStateObject("hubOmega")

    posRef.setState([[-4020338.690396649],	[7490566.741852513],	[5248299.211589362]])
    velRef.setState([[-5199.77710904224],	[-3436.681645356935],	[1041.576797498721]])
    sigmaRef.setState([[0.1], [0.2], [-0.3]])
    omegaRef.setState([[0.001], [-0.01], [0.03]])

    scObject.hub.mHub = 790.0
    scObject.hub.rBcB_B = [[0.0], [0.0], [0.0]]
    scObject.hub.IHubPntBc_B = [[905.46063422339966, 0.0, 0.0], [0.0, 805.46063422339967, 0.0], [0.0, 0.0, 605.46063422339967]]

    stopTime = 60.0*10.0
    unitTestSim.ConfigureStopTime(macros.sec2nano(stopTime))
    unitTestSim.ExecuteSimulation()

    dataPos = posRef.getState()
    dataSigma = sigmaRef.getState()
    dataPos = [[stopTime, dataPos[0][0], dataPos[1][0], dataPos[2][0]]]
    dataSigma = [[stopTime, dataSigma[0][0], dataSigma[1][0], dataSigma[2][0]]]

    truePos = [
                [-6.7815933935338277e+06, 4.9468685979815889e+06, 5.4867416696776701e+06]
                ]

    trueSigma = [
                [1.4401781243854264e-01, -6.4168702021364002e-02, 3.0166086824900967e-01]
                ]

    print dataPos
    print truePos
    print dataSigma
    print trueSigma

    moduleOutputr_N = unitTestSim.pullMessageLogData(scObject.scStateOutMsgName + '.r_BN_N',
                                                  range(3))
    moduleOutputSigma = unitTestSim.pullMessageLogData(scObject.scStateOutMsgName + '.sigma_BN',
                                                  range(3))

    accuracy = 1e-8
    for i in range(0,len(truePos)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(dataPos[i],truePos[i],3,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Thruster Integrated Test failed pos unit test")

    accuracy = 1e-5
    for i in range(0,len(trueSigma)):
        # check a vector values
        if not unitTestSupport.isArrayEqualRelative(dataSigma[i],trueSigma[i],3,accuracy):
            testFailCount += 1
            testMessages.append("FAILED: Thruster Integrated Test failed attitude unit test")

    if testFailCount == 0:
        print "PASSED: " + " Thruster Integrated Sim Test"

    assert testFailCount < 1, testMessages

    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    test_thrusterIntegratedTest(False)
