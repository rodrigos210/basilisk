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
#
#   Unit Test Script
#   Module Name:        rwMotorTorque
#   Author:             Hanspeter Schaub
#   Creation Date:      July 4, 2016
#

import pytest
import sys, os, inspect
# import packages as needed e.g. 'numpy', 'ctypes, 'math' etc.

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))




# Import all of the modules that we are going to be called in this simulation
from Basilisk.utilities import SimulationBaseClass
from Basilisk.simulation import alg_contain
from Basilisk.utilities import unitTestSupport                  # general support file with common unit test functions
import matplotlib.pyplot as plt
from Basilisk.fswAlgorithms import rwMotorTorque
from Basilisk.utilities import macros

# Uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed.
# @pytest.mark.skipif(conditionstring)
# Uncomment this line if this test has an expected failure, adjust message as needed.
# @pytest.mark.xfail(conditionstring)
# Provide a unique test method name, starting with 'test_'.
# The following 'parametrize' function decorator provides the parameters and expected results for each
#   of the multiple test runs for this test.
@pytest.mark.parametrize("numControlAxes, dropWheels",[
                         pytest.param(1, False),
                         pytest.param(2, False),
                         pytest.param(3, False),
                         pytest.param(3, True)])


# update "module" in this function name to reflect the module name
def test_rwMotorTorque(show_plots, numControlAxes, dropWheels):
    # each test method requires a single assert method to be called
    [testResults, testMessage] = rwMotorTorqueTest(show_plots, numControlAxes, dropWheels)
    assert testResults < 1, testMessage


def rwMotorTorqueTest(show_plots, numControlAxes, dropWheels):
    testFailCount = 0                       # zero unit test result counter
    testMessages = []                       # create empty array to store test log messages
    unitTaskName = "unitTask"               # arbitrary name (don't change)
    unitProcessName = "TestProcess"         # arbitrary name (don't change)

    # Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    # terminateSimulation() is needed if multiple unit test scripts are run
    # that run a simulation for the test. This creates a fresh and
    # consistent simulation environment for each test run.
    unitTestSim.TotalSim.terminateSimulation()

    # Create test thread
    testProcessRate = macros.sec2nano(0.5)     # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))


    # Construct algorithm and associated C++ container
    moduleConfig = rwMotorTorque.rwMotorTorqueConfig()
    moduleWrap = unitTestSim.setModelDataWrap(moduleConfig)
    moduleWrap.ModelTag = "rwMotorTorque"
    # Initialize the test module msg names
    moduleConfig.outputDataName = "rwMotorTorqueOut"
    moduleConfig.inputVehControlName = "LrRequested"
    moduleConfig.rwAvailInMsgName = "rw_availability"
    moduleConfig.rwParamsInMsgName = "rwa_config_data_parsed"
    # Initialize module variables
    if numControlAxes == 3:
        controlAxes_B = [
            1, 0, 0
            , 0, 1, 0
            , 0, 0, 1
        ]
    elif numControlAxes == 2:
        controlAxes_B = [
             1,0,0
            ,0,0,1
        ]
    else:
        controlAxes_B = [
            1, 0, 0
        ]

    moduleConfig.controlAxes_B = controlAxes_B


    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, moduleWrap, moduleConfig)


    # attControl message
    inputMessageData = rwMotorTorque.CmdTorqueBodyIntMsg()  # Create a structure for the input message
    inputMessageSize = inputMessageData.getStructSize()
    unitTestSim.TotalSim.CreateNewMessage(unitProcessName, moduleConfig.inputVehControlName,
                                          inputMessageSize, 2) # number of buffers (leave at 2 as default)
    requestedTorque = [1.0, -0.5, 0.7] # Set up a list as a 3-vector
    inputMessageData.torqueRequestBody = requestedTorque # write torque request to input message
    unitTestSim.TotalSim.WriteMessageData(moduleConfig.inputVehControlName, inputMessageSize,
                                          0, inputMessageData) # write data into the simulator

    # wheelConfigData message
    rwConfigParams = rwMotorTorque.RWArrayConfigFswMsg()
    inputMessageSize = rwConfigParams.getStructSize()
    unitTestSim.TotalSim.CreateNewMessage(unitProcessName, moduleConfig.rwParamsInMsgName,
                                          inputMessageSize, 2) # number of buffers (leave at 2 as default)
    rwConfigParams.GsMatrix_B = [
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        0.5773502691896258, 0.5773502691896258, 0.5773502691896258
    ]
    rwConfigParams.JsList = [0.1, 0.1, 0.1, 0.1]
    rwConfigParams.numRW = 4
    unitTestSim.TotalSim.WriteMessageData(moduleConfig.rwParamsInMsgName, inputMessageSize,
                                          0, rwConfigParams)

    # wheelAvailability message
    def writeMsgInWheelAvailability(dropWheels):
        rwAvailabilityMessage = rwMotorTorque.RWAvailabilityFswMsg()
        inputMessageSize = rwAvailabilityMessage.getStructSize()
        unitTestSim.TotalSim.CreateNewMessage(unitProcessName, moduleConfig.rwAvailInMsgName,
                                              inputMessageSize, 2) # number of buffers (leave at 2 as default)
        if dropWheels:
            avail = [rwMotorTorque.AVAILABLE, rwMotorTorque.AVAILABLE, rwMotorTorque.UNAVAILABLE, rwMotorTorque.UNAVAILABLE]
        else:
            avail = [rwMotorTorque.AVAILABLE, rwMotorTorque.AVAILABLE, rwMotorTorque.AVAILABLE, rwMotorTorque.AVAILABLE]

        rwAvailabilityMessage.wheelAvailability = avail
        unitTestSim.TotalSim.WriteMessageData(moduleConfig.rwAvailInMsgName, inputMessageSize,
                                              0, rwAvailabilityMessage)
    if len(moduleConfig.rwAvailInMsgName)>0:
        writeMsgInWheelAvailability(dropWheels)

    # Setup logging on the test module output message so that we get all the writes to it
    unitTestSim.TotalSim.logThisMessage(moduleConfig.outputDataName, testProcessRate)

    # Need to call the self-init and cross-init methods
    unitTestSim.InitializeSimulation()

    moduleWrap.Reset(0)

    # Set the simulation time.
    # NOTE: the total simulation time may be longer than this value. The
    # simulation is stopped at the next logging event on or after the
    # simulation end time.
    unitTestSim.ConfigureStopTime(macros.sec2nano(0.5))        # seconds to stop simulation

    # Begin the simulation time run set above
    unitTestSim.ExecuteSimulation()

    # This pulls the actual data log from the simulation run.
    # Note that range(3) will provide [0, 1, 2]  Those are the elements you get from the vector (all of them)
    moduleOutputName = "motorTorque"
    moduleOutput = unitTestSim.pullMessageLogData(moduleConfig.outputDataName + '.' + moduleOutputName,
                                                  range(rwConfigParams.numRW))


    # set the output truth states
    if numControlAxes == 1 and not dropWheels:
        trueVector = [
            [-0.7499999999999999, 0.0, 0.0, -0.4330127018922193],
            [-0.7499999999999999, 0.0, 0.0, -0.4330127018922193]
        ]
    if numControlAxes == 2 and not dropWheels:
        trueVector = [
            [-0.6599999999999999,-0.,-0.3599999999999999,-0.5888972745734183],
            [-0.6599999999999999,-0.,-0.3599999999999999,-0.5888972745734183]
        ]
    elif numControlAxes == 3 and not dropWheels:
        trueVector = [
                     [-0.8, 0.7000000000000001, -0.5, -0.3464101615137755],
                     [-0.8, 0.7000000000000001, -0.5, -0.3464101615137755]
                   ]
    elif numControlAxes == 3 and dropWheels:
        trueVector = [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0]
        ]

    # compare the module results to the truth values
    accuracy = 1e-8
    for i in range(0,len(trueVector)):
        # check a vector values
        if not unitTestSupport.isArrayEqual(moduleOutput[i], trueVector[i], rwConfigParams.numRW, accuracy):
            testFailCount += 1
            testMessages.append("FAILED: " + moduleWrap.ModelTag + " Module failed " +
                                moduleOutputName + " unit test at t=" +
                                str(moduleOutput[i,0]*macros.NANO2SEC) +
                                "sec\n")

    accuracy = 1e-8
        
    testFailCount, testMessages = unitTestSupport.compareArrayND(trueVector, moduleOutput, accuracy, "rwMotorTorques",
                                                                 2, testFailCount, testMessages)
        

        
        
    #   print out success message if no error were found
    unitTestSupport.writeTeXSnippet('toleranceValue', str(accuracy), path)
    
    snippentName = "passFail_"+"numAxes_"+str(len(controlAxes_B)/3) + "_numWheels_" + str(4-2*int(dropWheels))
    if testFailCount == 0:
        colorText = 'ForestGreen'
        print "PASSED: " + moduleWrap.ModelTag
        passedText = '\\textcolor{' + colorText + '}{' + "PASSED" + '}'
    else:
        colorText = 'Red'
        print "Failed: " + moduleWrap.ModelTag
        passedText = '\\textcolor{' + colorText + '}{' + "Failed" + '}'
    unitTestSupport.writeTeXSnippet(snippentName, passedText, path)

    #   print out success message if no error were found
    if testFailCount == 0:
        print "PASSED: " + moduleWrap.ModelTag

    # each test method requires a single assert method to be called
    # this check below just makes sure no sub-test failures were found
    return [testFailCount, ''.join(testMessages)]


#
# This statement below ensures that the unitTestScript can be run as a
# stand-along python script
#
if __name__ == "__main__":
    test_rwMotorTorque(
                3,
                True
               )
