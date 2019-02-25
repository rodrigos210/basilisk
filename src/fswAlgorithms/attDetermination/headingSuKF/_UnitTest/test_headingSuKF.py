''' '''
'''
 ISC License

 Copyright (c) 2016-2018, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
import numpy as np
import pytest
import math

from Basilisk.utilities import SimulationBaseClass, macros, unitTestSupport
from Basilisk.simulation import coarse_sun_sensor
import matplotlib.pyplot as plt
from Basilisk.fswAlgorithms import headingSuKF, cssComm, fswMessages  # import the module that is to be tested

import SunLineSuKF_test_utilities as FilterPlots

def setupFilterData(filterObject):
    filterObject.opnavOutMsgName = "opnav_state_estimate"
    filterObject.filtDataOutMsgName = "heading_filter_data"
    filterObject.opnavDataInMsgName = "opnav_sensors_data"

    filterObject.alpha = 0.02
    filterObject.beta = 2.0
    filterObject.kappa = 0.0

    # filterObject.state = [0.0, 0., 0., 0., 0.]
    filterObject.stateInit = [0.0, 0.0, 1.0, 0.0, 0.0]
    filterObject.covarInit = [1., 0.0, 0.0, 0.0, 0.0,
                          0.0, 1., 0.0, 0.0, 0.0,
                          0.0, 0.0, 1., 0.0, 0.0,
                          0.0, 0.0, 0.0, 0.02, 0.0,
                          0.0, 0.0, 0.0, 0.0, 0.02]

    qNoiseIn = np.identity(5)
    qNoiseIn[0:3, 0:3] = qNoiseIn[0:3, 0:3]*0.01*0.01
    qNoiseIn[3:5, 3:5] = qNoiseIn[3:5, 3:5]*0.001*0.001
    filterObject.qNoise = qNoiseIn.reshape(25).tolist()
    filterObject.qObsVal = 0.001
    filterObject.sensorUseThresh = 0.


def test_functions_ukf(show_plots):
    [testResults, testMessage] = heading_utilities_test(show_plots)
    assert testResults < 1, testMessage

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_

def test_all_heading_kf(show_plots):
    [testResults, testMessage] = StatePropSunLine(show_plots)
    assert testResults < 1, testMessage
    [testResults, testMessage] = StateUpdateSunLine(show_plots)
    assert testResults < 1, testMessage

def heading_utilities_test(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    # Initialize the test module configuration data
    AMatrix = [0.488894, 0.888396, 0.325191, 0.319207,
                1.03469, -1.14707, -0.754928, 0.312859, 
                0.726885, -1.06887, 1.3703, -0.86488,
               -0.303441, -0.809499, -1.71152, -0.0300513,
                0.293871, -2.94428, -0.102242, -0.164879,
               -0.787283, 1.43838, -0.241447, 0.627707]
   
    RVector = headingSuKF.new_doubleArray(len(AMatrix))
    AVector = headingSuKF.new_doubleArray(len(AMatrix))
    for i in range(len(AMatrix)):
        headingSuKF.doubleArray_setitem(AVector, i, AMatrix[i])
        headingSuKF.doubleArray_setitem(RVector, i, 0.0)

        headingSuKF.ukfQRDJustR(AVector, 6, 4, RVector)
    RMatrix = []
    for i in range(4*4):
        RMatrix.append(headingSuKF.doubleArray_getitem(RVector, i))
    RBaseNumpy = np.array(RMatrix).reshape(4,4)
    AMatNumpy = np.array(AMatrix).reshape(6,4)
    q,r = np.linalg.qr(AMatNumpy)
    for i in range(r.shape[0]):
        if r[i,i] < 0.0:
            r[i,:] *= -1.0
    if np.linalg.norm(r - RBaseNumpy) > 1.0E-15:
        testFailCount += 1
        testMessages.append("QR Decomposition accuracy failure")
    
    AMatrix = [1.09327, 1.10927, -0.863653, 1.32288,
     -1.21412, -1.1135, -0.00684933, -2.43508,
     -0.769666, 0.371379, -0.225584, -1.76492,
     -1.08906, 0.0325575, 0.552527, -1.6256,
     1.54421, 0.0859311, -1.49159, 1.59683]

    RVector = headingSuKF.new_doubleArray(len(AMatrix))
    AVector = headingSuKF.new_doubleArray(len(AMatrix))
    for i in range(len(AMatrix)):
        headingSuKF.doubleArray_setitem(AVector, i, AMatrix[i])
        headingSuKF.doubleArray_setitem(RVector, i, 0.0)

    headingSuKF.ukfQRDJustR(AVector, 5, 4, RVector)
    RMatrix = []
    for i in range(4*4):
        RMatrix.append(headingSuKF.doubleArray_getitem(RVector, i))
    RBaseNumpy = np.array(RMatrix).reshape(4,4)
    AMatNumpy = np.array(AMatrix).reshape(5,4)
    q,r = np.linalg.qr(AMatNumpy)
    for i in range(r.shape[0]):
        if r[i,i] < 0.0:
            r[i,:] *= -1.0
    if np.linalg.norm(r - RBaseNumpy) > 1.0E-14:
        testFailCount += 1
        testMessages.append("QR Decomposition accuracy failure")
    
    AMatrix = [ 0.2236,         0,
               0,    0.2236,
               -0.2236,         0,
               0,   -0.2236,
               0.0170,         0,
               0,    0.0170]

    RVector = headingSuKF.new_doubleArray(len(AMatrix))
    AVector = headingSuKF.new_doubleArray(len(AMatrix))
    for i in range(len(AMatrix)):
        headingSuKF.doubleArray_setitem(AVector, i, AMatrix[i])
        headingSuKF.doubleArray_setitem(RVector, i, 0.0)

    headingSuKF.ukfQRDJustR(AVector, 6, 2, RVector)
    RMatrix = []
    for i in range(2*2):
        RMatrix.append(headingSuKF.doubleArray_getitem(RVector, i))
    RBaseNumpy = np.array(RMatrix).reshape(2,2)
    AMatNumpy = np.array(AMatrix).reshape(6,2)
    q,r = np.linalg.qr(AMatNumpy)
    for i in range(r.shape[0]):
        if r[i,i] < 0.0:
            r[i,:] *= -1.0

    if np.linalg.norm(r - RBaseNumpy) > 1.0E-15:
        testFailCount += 1
        testMessages.append("QR Decomposition accuracy failure")


    LUSourceMat = [8,1,6,3,5,7,4,9,2]
    LUSVector = headingSuKF.new_doubleArray(len(LUSourceMat))
    LVector = headingSuKF.new_doubleArray(len(LUSourceMat))
    UVector = headingSuKF.new_doubleArray(len(LUSourceMat))
    intSwapVector = headingSuKF.new_intArray(3)
    
    for i in range(len(LUSourceMat)):
        headingSuKF.doubleArray_setitem(LUSVector, i, LUSourceMat[i])
        headingSuKF.doubleArray_setitem(UVector, i, 0.0)
        headingSuKF.doubleArray_setitem(LVector, i, 0.0)

    exCount = headingSuKF.ukfLUD(LUSVector, 3, 3, LVector, intSwapVector)
    #headingSuKF.ukfUInv(LUSVector, 3, 3, UVector)
    LMatrix = []
    UMatrix = []
    #UMatrix = []
    for i in range(3):
        currRow = headingSuKF.intArray_getitem(intSwapVector, i)
        for j in range(3):
            if(j<i):
                LMatrix.append(headingSuKF.doubleArray_getitem(LVector, i*3+j))
                UMatrix.append(0.0)
            elif(j>i):
                LMatrix.append(0.0)
                UMatrix.append(headingSuKF.doubleArray_getitem(LVector, i*3+j))
            else:
                LMatrix.append(1.0)
                UMatrix.append(headingSuKF.doubleArray_getitem(LVector, i*3+j))
    #    UMatrix.append(headingSuKF.doubleArray_getitem(UVector, i))

    LMatrix = np.array(LMatrix).reshape(3,3)
    UMatrix = np.array(UMatrix).reshape(3,3)
    outMat = np.dot(LMatrix, UMatrix)
    outMatSwap = np.zeros((3,3)) 
    for i in range(3):
        currRow = headingSuKF.intArray_getitem(intSwapVector, i)
        outMatSwap[i,:] = outMat[currRow, :]
        outMat[currRow,:] = outMat[i, :]
    LuSourceArray = np.array(LUSourceMat).reshape(3,3)

    if(np.linalg.norm(outMatSwap - LuSourceArray) > 1.0E-14):
        testFailCount += 1
        testMessages.append("LU Decomposition accuracy failure")

    EqnSourceMat = [2.0, 1.0, 3.0, 2.0, 6.0, 8.0, 6.0, 8.0, 18.0]
    BVector = [1.0, 3.0, 5.0]
    EqnVector = headingSuKF.new_doubleArray(len(EqnSourceMat))
    EqnBVector = headingSuKF.new_doubleArray(len(LUSourceMat)/3)
    EqnOutVector = headingSuKF.new_doubleArray(len(LUSourceMat)/3)

    for i in range(len(EqnSourceMat)):
        headingSuKF.doubleArray_setitem(EqnVector, i, EqnSourceMat[i])
        headingSuKF.doubleArray_setitem(EqnBVector, i/3, BVector[i/3])
        headingSuKF.intArray_setitem(intSwapVector, i/3, 0)
        headingSuKF.doubleArray_setitem(LVector, i, 0.0)
    
    exCount = headingSuKF.ukfLUD(EqnVector, 3, 3, LVector, intSwapVector)
    
    headingSuKF.ukfLUBckSlv(LVector, 3, 3, intSwapVector, EqnBVector, EqnOutVector)
    
    expectedSol = [3.0/10.0, 4.0/10.0, 0.0]
    errorVal = 0.0
    for i in range(3):
        errorVal += abs(headingSuKF.doubleArray_getitem(EqnOutVector, i) -expectedSol[i])

    if(errorVal > 1.0E-14):
        testFailCount += 1
        testMessages.append("LU Back-Solve accuracy failure")


    InvSourceMat = [8,1,6,3,5,7,4,9,2]
    SourceVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    InvVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    for i in range(len(InvSourceMat)):
        headingSuKF.doubleArray_setitem(SourceVector, i, InvSourceMat[i])
        headingSuKF.doubleArray_setitem(InvVector, i, 0.0)
    nRow = int(math.sqrt(len(InvSourceMat)))
    headingSuKF.ukfMatInv(SourceVector, nRow, nRow, InvVector)

    InvOut = []
    for i in range(len(InvSourceMat)):
        InvOut.append(headingSuKF.doubleArray_getitem(InvVector, i))

    InvOut = np.array(InvOut).reshape(nRow, nRow)
    expectIdent = np.dot(InvOut, np.array(InvSourceMat).reshape(3,3))
    errorNorm = np.linalg.norm(expectIdent - np.identity(3))
    if(errorNorm > 1.0E-14):
        testFailCount += 1
        testMessages.append("LU Matrix Inverse accuracy failure")

    
    cholTestMat = [1.0, 0.0, 0.0, 0.0, 10.0, 5.0, 0.0, 5.0, 10.0]
    SourceVector = headingSuKF.new_doubleArray(len(cholTestMat))
    CholVector = headingSuKF.new_doubleArray(len(cholTestMat))
    for i in range(len(cholTestMat)):
        headingSuKF.doubleArray_setitem(SourceVector, i, cholTestMat[i])
        headingSuKF.doubleArray_setitem(CholVector, i, 0.0)
    nRow = int(math.sqrt(len(cholTestMat)))
    headingSuKF.ukfCholDecomp(SourceVector, nRow, nRow, CholVector)
    cholOut = []
    for i in range(len(cholTestMat)):
        cholOut.append(headingSuKF.doubleArray_getitem(CholVector, i))

    cholOut = np.array(cholOut).reshape(nRow, nRow)
    cholComp = np.linalg.cholesky(np.array(cholTestMat).reshape(nRow, nRow))
    errorNorm = np.linalg.norm(cholOut - cholComp)
    if(errorNorm > 1.0E-14):
        testFailCount += 1
        testMessages.append("Cholesky Matrix Decomposition accuracy failure")


    InvSourceMat = [2.1950926119414667, 0.0, 0.0, 0.0,
               1.0974804773131115, 1.9010439702743847, 0.0, 0.0,
               0.0, 1.2672359635912551, 1.7923572711881284, 0.0,
               1.0974804773131113, -0.63357997864171967, 1.7920348101787789, 0.033997451205364251]
               
    SourceVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    InvVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    for i in range(len(InvSourceMat)):
        headingSuKF.doubleArray_setitem(SourceVector, i, InvSourceMat[i])
        headingSuKF.doubleArray_setitem(InvVector, i, 0.0)
    nRow = int(math.sqrt(len(InvSourceMat)))
    headingSuKF.ukfLInv(SourceVector, nRow, nRow, InvVector)

    InvOut = []
    for i in range(len(InvSourceMat)):
        InvOut.append(headingSuKF.doubleArray_getitem(InvVector, i))

    InvOut = np.array(InvOut).reshape(nRow, nRow)
    expectIdent = np.dot(InvOut, np.array(InvSourceMat).reshape(nRow,nRow))
    errorNorm = np.linalg.norm(expectIdent - np.identity(nRow))
    if(errorNorm > 1.0E-12):
        print errorNorm
        testFailCount += 1
        testMessages.append("L Matrix Inverse accuracy failure")

    InvSourceMat = np.transpose(np.array(InvSourceMat).reshape(nRow, nRow)).reshape(nRow*nRow).tolist()
    SourceVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    InvVector = headingSuKF.new_doubleArray(len(InvSourceMat))
    for i in range(len(InvSourceMat)):
        headingSuKF.doubleArray_setitem(SourceVector, i, InvSourceMat[i])
        headingSuKF.doubleArray_setitem(InvVector, i, 0.0)
    nRow = int(math.sqrt(len(InvSourceMat)))
    headingSuKF.ukfUInv(SourceVector, nRow, nRow, InvVector)

    InvOut = []
    for i in range(len(InvSourceMat)):
        InvOut.append(headingSuKF.doubleArray_getitem(InvVector, i))

    InvOut = np.array(InvOut).reshape(nRow, nRow)
    expectIdent = np.dot(InvOut, np.array(InvSourceMat).reshape(nRow,nRow))
    errorNorm = np.linalg.norm(expectIdent - np.identity(nRow))
    if(errorNorm > 1.0E-12):
        print errorNorm
        testFailCount += 1
        testMessages.append("U Matrix Inverse accuracy failure")


    # If the argument provided at commandline "--show_plots" evaluates as true,
    # plot all figures
    if show_plots:
        plt.show()

    # print out success message if no error were found
    if testFailCount == 0:
        print "PASSED: " + " UKF utilities"

    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

def StateUpdateSunLine(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True
    
    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    #   Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    unitTestSim.TotalSim.terminateSimulation()

    # Create test thread
    testProcessRate = macros.sec2nano(0.5)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    # Construct algorithm and associated C++ container
    moduleConfig = headingSuKF.HeadingSuKFConfig()
    moduleWrap = unitTestSim.setModelDataWrap(moduleConfig)
    moduleWrap.ModelTag = "headingSuKF"

    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, moduleWrap, moduleConfig)
    
    setupFilterData(moduleConfig)
    unitTestSim.TotalSim.logThisMessage('heading_filter_data', testProcessRate)

    testVector = np.array([0.9, 0.1, 0.02])
    testOmega = np.array([0.01, 0.05, 0.001])
    inputData = headingSuKF.OpnavFswMsg()
    inputMessageSize = inputData.getStructSize()
    unitTestSim.TotalSim.CreateNewMessage(unitProcessName,
                                      moduleConfig.opnavDataInMsgName,
                                      inputMessageSize,
                                      2)  # number of buffers (leave at 2 as default, don't make zero)

    stateTarget = testVector.tolist()
    stateTarget.extend([0.0, 0.0])
    moduleConfig.stateInit = [1., 0.0, 0.0, 0.01, 0.001]

    unitTestSim.InitializeSimulation()

    for i in range(400):
        if i > 20:
            inputData.rel_pos += - np.cross(testOmega, testVector) * 0.5
            unitTestSim.TotalSim.WriteMessageData(moduleConfig.opnavDataInMsgName,
                                      inputMessageSize,
                                      unitTestSim.TotalSim.CurrentNanos,
                                      inputData)
        unitTestSim.ConfigureStopTime(macros.sec2nano((i+1)*0.5))
        unitTestSim.ExecuteSimulation()

    stateLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".state", range(5))
    postFitLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".postFitRes", range(3))
    covarLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".covar", range(5*5))

    for i in range(5):
        if(covarLog[-1, i*5+1+i] > covarLog[0, i*5+1+i]/100):
            testFailCount += 1
            testMessages.append("Covariance update failure")
        if(abs(stateLog[-1, i+1] - stateTarget[i]) > 1.0E-5):
            print abs(stateLog[-1, i+1] - stateTarget[i])
            testFailCount += 1
            testMessages.append("State update failure")

        
    for i in range(400):
        if i > 20:
            unitTestSim.TotalSim.WriteMessageData(moduleConfig.opnavDataInMsgName,
                                      inputMessageSize,
                                      unitTestSim.TotalSim.CurrentNanos,
                                      inputData)
        unitTestSim.ConfigureStopTime(macros.sec2nano((i+401)*0.5))
        unitTestSim.ExecuteSimulation()

    stateLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".state", range(5))
    postFitLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".postFitRes", range(3))
    covarLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".covar", range(5*5))

    stateTarget = testVector.tolist()
    stateTarget.extend([0.0, 0.0, 0.0])
    for i in range(5):
        if(covarLog[-1, i*5+1+i] > covarLog[0, i*5+1+i]/100):
            testFailCount += 1
            testMessages.append("Covariance update failure")
        if(abs(stateLog[-1, i+1] - stateTarget[i]) > 1.0E-5):
            print abs(stateLog[-1, i+1] - stateTarget[i])
            testFailCount += 1
            testMessages.append("State update failure")

    FilterPlots.StateCovarPlot(stateLog, covarLog, show_plots)
    FilterPlots.PostFitResiduals(postFitLog, moduleConfig.qObsVal, show_plots)

    # print out success message if no error were found
    if testFailCount == 0:
        print "PASSED: " + moduleWrap.ModelTag + " state update"

    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

def StatePropSunLine(show_plots):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True
    
    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty list to store test log messages

    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    #   Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    unitTestSim.TotalSim.terminateSimulation()

    # Create test thread
    testProcessRate = macros.sec2nano(0.5)  # update process rate update time
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    # Construct algorithm and associated C++ container
    moduleConfig = headingSuKF.HeadingSuKFConfig()
    moduleWrap = unitTestSim.setModelDataWrap(moduleConfig)
    moduleWrap.ModelTag = "headingSuKF"

    # Add test module to runtime call list
    unitTestSim.AddModelToTask(unitTaskName, moduleWrap, moduleConfig)
    
    setupFilterData(moduleConfig)
    unitTestSim.TotalSim.logThisMessage('heading_filter_data', testProcessRate)

    unitTestSim.InitializeSimulation()
    unitTestSim.ConfigureStopTime(macros.sec2nano(8000.0))
    unitTestSim.ExecuteSimulation()
    
    stateLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".state", range(5))
    postFitLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".postFitRes", range(8))
    covarLog = unitTestSim.pullMessageLogData('heading_filter_data' + ".covar", range(5*5))

    FilterPlots.StateCovarPlot(stateLog, covarLog,show_plots)
    FilterPlots.PostFitResiduals(postFitLog, moduleConfig.qObsVal, show_plots)

    for i in range(5):
        if(abs(stateLog[-1, i+1] - stateLog[0, i+1]) > 1.0E-10):
            print abs(stateLog[-1, i+1] - stateLog[0, i+1])
            testFailCount += 1
            testMessages.append("State propagation failure")

    

    # print out success message if no error were found
    if testFailCount == 0:
        print "PASSED: " + moduleWrap.ModelTag + " state propagation"

    # return fail count and join into a single string all messages in the list
    # testMessage
    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    # test_all_heading_kf(True)
    StateUpdateSunLine(True)
