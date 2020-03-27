#
#   Unit Test Script
#   Module Name:        rwNullSpace
#   Creation Date:      October 5, 2018
#

from Basilisk.utilities import SimulationBaseClass, unitTestSupport, macros
from Basilisk.fswAlgorithms import rwNullSpace
from Basilisk.fswAlgorithms import fswMessages
from Basilisk.simulation import simFswInterfaceMessages
import pytest
import numpy as np
import os, inspect
from numpy.linalg import inv

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

# Uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed.
# @pytest.mark.skipif(conditionstring)
# Uncomment this line if this test has an expected failure, adjust message as needed.
# @pytest.mark.xfail(conditionstring)
# Provide a unique test method name, starting with 'test_'.
# The following 'parametrize' function decorator provides the parameters and expected results for each
#   of the multiple test runs for this test.
@pytest.mark.parametrize("numWheels", [
     (3)
    ,(4)
])


def test_rwNullSpace(numWheels):
    """ Test rwNullSpace. """
    [testResults, testMessage] = rwNullSpaceTestFunction(numWheels)
    assert testResults < 1, testMessage

def rwNullSpaceTestFunction(numWheels):
    """ Test the rwNullSpace module. Setup a simulation, """

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty array to store test log messages
    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    # Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()

    # This is needed if multiple unit test scripts are run
    # This create a fresh and consistent simulation environment for each test run

    # Create test thread
    testProcessRate = macros.sec2nano(0.5)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))  # Add a new task to the process

    # Construct the rwNullSpace module
    # Set the names for the input messages
    moduleConfig = rwNullSpace.rwNullSpaceConfig()  # Create a config struct
    moduleConfig.inputRWSpeeds = "input_rw_speeds"
    moduleConfig.inputRWConfigData = "input_rw_constellation"
    moduleConfig.inputRWCommands = "input_rw_commands"
    moduleConfig.outputControlName = "output_rw_cmd"

    # Set the necessary data in the module. NOTE: This information is more or less random
    moduleConfig.OmegaGain = .5 # The feedback gain value applied for the RW despin control law

    # This calls the algContain to setup the selfInit, crossInit, update, and reset
    moduleWrap = unitTestSim.setModelDataWrap(moduleConfig)
    moduleWrap.ModelTag = "rwNullSpace"

    # Add the module to the task
    unitTestSim.AddModelToTask(unitTaskName, moduleWrap, moduleConfig)

    numRW = numWheels

    inputRWConstellationMsg = fswMessages.RWConstellationFswMsg()
    inputRWConstellationMsg.numRW = numRW

    # Initialize the msg that gives the speed of the reaction wheels
    inputSpeedMsg = rwNullSpace.RWSpeedIntMsg()

    gsHat = [[1, 0, 0], [0,1,0], [0, 0, 1]]
    if numWheels == 4:
        gs4Hat = np.array([1,1,1])
        gs4Hat = gs4Hat/np.sqrt(gs4Hat.dot(gs4Hat))
        gsHat.append(gs4Hat.tolist())

    # Iterate over all of the reaction wheels, create a rwConfigElementFswMsg, and add them to the rwConstellationFswMsg
    rwConfigElementList = list()
    for rw in range(numRW):
        rwConfigElementMsg = fswMessages.RWConfigElementFswMsg()
        rwConfigElementMsg.gsHat_B = gsHat[rw] # Spin axis unit vector of the wheel in structure
        rwConfigElementMsg.Js = 0.08 # Spin axis inertia of wheel [kgm2]
        rwConfigElementMsg.uMax = 0.2 # maximum RW motor torque [Nm]

        # Add this to the list
        rwConfigElementList.append(rwConfigElementMsg)

    rwSpeeds = [10, 20, 30] # [rad/sec] The current angular velocities of the RW wheel
    if numWheels == 4:
        rwSpeeds.append(40)  # [rad/sec]
    inputSpeedMsg.wheelSpeeds = rwSpeeds

    # Set the array of the reaction wheels in RWConstellationFswMsg to the list created above
    inputRWConstellationMsg.reactionWheels = rwConfigElementList

    inputRWCmdMsg = simFswInterfaceMessages.RWArrayTorqueIntMsg()
    usControl = [0.1, 0.2, 0.15] # [Nm] RW motor torque array
    if numWheels == 4:
        usControl.append(-0.2) # [Nm]
    inputRWCmdMsg.motorTorque = usControl


    # Set these messages
    unitTestSupport.setMessage(unitTestSim.TotalSim, unitProcessName, moduleConfig.inputRWSpeeds, inputSpeedMsg)
    unitTestSupport.setMessage(unitTestSim.TotalSim, unitProcessName, moduleConfig.inputRWConfigData, inputRWConstellationMsg)
    unitTestSupport.setMessage(unitTestSim.TotalSim, unitProcessName, moduleConfig.inputRWCommands, inputRWCmdMsg)

    unitTestSim.TotalSim.logThisMessage(moduleConfig.outputControlName, testProcessRate)

    # Initialize the simulation
    unitTestSim.InitializeSimulation()

    #   Step the simulation to 3*process rate so 4 total steps including zero
    unitTestSim.ConfigureStopTime(macros.sec2nano(2.0))  # seconds to stop simulation
    unitTestSim.ExecuteSimulation()

    outputCrtlData = unitTestSim.pullMessageLogData(moduleConfig.outputControlName+'.motorTorque', list(range(3)))
    print(outputCrtlData)

    if numWheels == 3:
        # in this case there is no nullspace of the RW configuration.  The output torque should be the input torque
        trueVector = [inputRWCmdMsg.motorTorque,
                     inputRWCmdMsg.motorTorque,
                     inputRWCmdMsg.motorTorque,
                     inputRWCmdMsg.motorTorque,
                     inputRWCmdMsg.motorTorque]
    elif numWheels == 4:
        # in this case there is a 1D nullspace of [Gs]
        GsT = np.array(gsHat)
        Gs = GsT.transpose()
        tmp = Gs.dot(GsT)
        tmp = GsT.dot(inv(tmp))
        tmp = tmp.dot(Gs)
        tau = np.identity(numWheels) - tmp
        d = - moduleConfig.OmegaGain * np.array(rwSpeeds)
        uNull = tau.dot(d)
        trueTorque = np.array(usControl) + uNull
        trueVector = [
            trueTorque.tolist(),
            trueTorque.tolist(),
            trueTorque.tolist(),
            trueTorque.tolist(),
            trueTorque.tolist()
        ]


    accuracy = 1e-6
    unitTestSupport.writeTeXSnippet("toleranceValue", str(accuracy), path)

    # At each timestep, make sure the vehicleConfig values haven't changed from the initial values
    testFailCount, testMessages = unitTestSupport.compareArrayND(trueVector, outputCrtlData,
                                                                 accuracy,
                                                                 "numWheels = " + str(numWheels),
                                                                 2, testFailCount, testMessages)


    snippentName = "passFail" + str(numWheels)
    if testFailCount == 0:
        colorText = 'ForestGreen'
        print("PASSED: " + moduleWrap.ModelTag)
        passedText = r'\textcolor{' + colorText + '}{' + "PASSED" + '}'
    else:
        colorText = 'Red'
        print("Failed: " + moduleWrap.ModelTag)
        passedText = r'\textcolor{' + colorText + '}{' + "Failed" + '}'
    unitTestSupport.writeTeXSnippet(snippentName, passedText, path)


    return [testFailCount, ''.join(testMessages)]

if __name__ == '__main__':
    test_rwNullSpace()
