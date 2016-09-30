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
import stateManager
import sim_model
import ctypes

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_
def stateManagerAllTest(show_plots):
    [testResults, testMessage] = test_stateData(show_plots)
    assert testResults < 1, testMessage
    [testResults, testMessage] = test_stateManager(show_plots)
    assert testResults < 1, testMessage

def test_stateData(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    stateUse = [[10.0], [20.0]]
    stateName = "position"
    newState = stateManager.StateData(stateName, stateUse)
    newState.setState(stateUse)
    
    predictedDerivative = [[0.0], [0.0]]
    newState.zeroDerivative()

    if(newState.getRowSize() != len(stateUse)):
        testFailCount += 1
        testMessages.append("State row sized incorrectly") 
    if(newState.getColumnSize() != len(stateUse[0])):
        testFailCount += 1
        testMessages.append("State column sized incorrectly") 
    if(newState.getName() != stateName):
        testFailCount += 1
        testMessages.append("State name incorrect")
    if(newState.getState() != stateUse):
        testFailCount += 1
        testMessages.append("State equality check failure.")
    if(newState.getStateDeriv() != predictedDerivative):
        testFailCount += 1
        testMessages.append("State derivative zero check failure.")

    derivativeInc = [[1.0], [2.5]]
    newState.addToDerivative(derivativeInc)
    newState.propagateState(0.1)

    predictedDerivativeNum = numpy.array(predictedDerivative) + numpy.array(derivativeInc)
    obsDerivativeNum = numpy.array(newState.getStateDeriv())
    if(obsDerivativeNum.tolist() != predictedDerivativeNum.tolist()):
        testFailCount += 1
        testMessages.append("State derivative update check failure.")

    stateUpdateNum = numpy.array(newState.getState())
    predUpStateNum = numpy.array(stateUse) + predictedDerivativeNum*0.1
    if(stateUpdateNum.tolist() != stateUpdateNum.tolist()):
        testFailCount += 1
        testMessages.append("State propagation update check failure.")
    
    priorState = stateUpdateNum
    scaleFactor = 0.25
    priorState *= scaleFactor
    newState.scaleState(scaleFactor)
    stateUpdateNum = numpy.array(newState.getState())
    if(stateUpdateNum.tolist() != priorState.tolist()):
        testFailCount += 1
        testMessages.append("State scaling update check failure.")


    dummyState = stateManager.StateData()
    if(dummyState.getRowSize() != 0):
        testFailCount += 1
        testMessages.append("Dummy state row sized incorrectly")
    if(dummyState.getColumnSize() != 0):
        testFailCount += 1
        testMessages.append("Dummy state column sized incorrectly")

    if testFailCount == 0:
        print "PASSED: " + " State data"
    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

def test_stateManager(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    newManager = stateManager.StateManager()
    
    positionName = "position"
    stateDim = [3, 1]
    posState = newManager.registerState(stateDim[0], stateDim[1], positionName)
    
    velocityName = "velocity"
    stateDim = [3, 1]
    velState = newManager.registerState(stateDim[0], stateDim[1], velocityName)
    
    flexName = "Array1_flex"
    flexDim = [2, 1]
    flexState = newManager.registerState(flexDim[0], flexDim[1], flexName)
    
    if posState.getRowSize() != stateDim[0] or posState.getColumnSize() != stateDim[1]:
        testFailCount += 1
        testMessages.append("Position state returned improper size")
    
    if velState.getName() != velocityName:
        testFailCount += 1
        testMessages.append("Failed to return proper state name for velocity")
    
    if(newManager.registerState(stateDim[0], stateDim[1], positionName).getName() != positionName):
        testFailCount += 1
        testMessages.append("Failed to return proper state name in overload of call")
    newManager.registerState(stateDim[0], stateDim[1]+2, positionName)
    
    positionStateLookup = newManager.getStateObject("Array1_flex")

    if(positionStateLookup.getName() != flexName):
        testFailCount += 1
        testMessages.append("State lookup for solar array flex failed")
    

    if testFailCount == 0:
        print "PASSED: " + " State manager"
    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    stateManagerAllTest(False)
    
