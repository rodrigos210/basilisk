# 
#  ISC License
# 
#  Copyright (c) 2021, Autonomous Vehicle Systems Lab, University of Colorado Boulder
# 
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
# 
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 
# 

import pytest
import numpy as np

from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport
from Basilisk.utilities import macros
from Basilisk.utilities import fswSetupThrusters

from Basilisk.architecture import messaging

from Basilisk.fswAlgorithms import forceTorqueThrForceMapping

def test_forceTorqueThrForceMapping():
    r"""
    **Test Description**

    This pytest ensures that the forceTorqueThrForce module can compute a valid solution for cases where:
    1. There is a direction where no thrusters point - ensures matrix invertibility is handled
    2. There is zero requested torque, but a requested force
    3. Thrusters point in each direction
    4. The CoM of the spacecraft is offset

    """

    # Test 1 - No thrusters pointing in one direction, CoM offset
    rcsLocationData = [[-0.86360, -0.82550, 1.79070],
                            [-0.82550, -0.86360, 1.79070],
                            [0.82550, 0.86360, 1.79070],
                            [0.86360, 0.82550, 1.79070],
                            [-0.86360, -0.82550, -1.79070],
                            [-0.82550, -0.86360, -1.79070],
                            [0.82550, 0.86360, -1.79070],
                            [0.86360, 0.82550, -1.79070]]

    rcsDirectionData = [[1.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, -1.0, 0.0],
                             [-1.0, 0.0, 0.0],
                             [1.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, -1.0, 0.0],
                             [-1.0, 0.0, 0.0]]

    requested_torque = [0.4, 0.2, 0.4]

    requested_force = [0.9, 1.1, 0.]

    CoM_B = [0.1, 0.1, 0.1]

    truth = np.array([[0.7082, 0.5500, 0.0810, 0.1772, 0.6272, 0.6310, 0., 0.2582]])

    [testResults, testMessage] = forceTorqueThrForceMappingTestFunction(rcsLocationData, rcsDirectionData, requested_torque, requested_force, CoM_B,
                                                                        truth)

    assert testResults < 1, testMessage

    # Test 2 - No torque
    requested_torque = [0.0, 0.0, 0.0]

    truth = np.array([[0.5340, 0.5807, 0., 0.0588, 0.5088, 0.5500, 0.0307, 0.0840]])

    [testResults, testMessage] = forceTorqueThrForceMappingTestFunction(rcsLocationData, rcsDirectionData, requested_torque, requested_force, CoM_B,
                                                                        truth)

    assert testResults < 1, testMessage

    # Test 3 - Thrusters pointing in each direction
    rcsLocationData = [[-1, -1, 1],
                        [-1, -1, 1],
                        [-1, -1, 1],
                        [1, 1, 1],
                        [1, 1, 1],
                        [1, 1, 1],
                        [1, 1, -1],
                        [1, 1, -1],
                        [1, 1, -1],
                        [-1, -1, -1],
                        [-1, -1, -1],
                        [-1, -1, -1]]

    rcsDirectionData = [[1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, -1.0],
                        [0.0, 0.0, -1.0],
                        [0.0, -1.0, 0.0],
                        [-1.0, 0.0, 0.0],
                        [0.0, -1.0, 0.0],
                        [-1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0],
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0]]

    requested_force = [0.9, 1.1, 1.]

    truth = np.array([[0.5050, 0.5550, 0.0300, 0.0300, 0., 0.0600, 0.0050, 0.0550, 0.5300, 0.5100, 0.5500, 0.5300]])

    [testResults, testMessage] = forceTorqueThrForceMappingTestFunction(rcsLocationData, rcsDirectionData, requested_torque, requested_force, CoM_B,
                                                                        truth)
    assert testResults < 1, testMessage


def forceTorqueThrForceMappingTestFunction(rcsLocation, rcsDirection, requested_torque, requested_force, CoM_B,
                                           truth):
    """Test method"""
    testFailCount = 0
    testMessages = []
    unitTaskName = "unitTask"
    unitProcessName = "TestProcess"

    unitTestSim = SimulationBaseClass.SimBaseClass()
    testProcessRate = macros.sec2nano(0.5)
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    # setup module to be tested
    moduleConfig = forceTorqueThrForceMapping.forceTorqueThrForceMappingConfig()
    moduleWrap = unitTestSim.setModelDataWrap(moduleConfig)
    moduleWrap.ModelTag = "forceTorqueThrForceMappingTag"
    unitTestSim.AddModelToTask(unitTaskName, moduleWrap, moduleConfig)

    # Configure blank module input messages
    cmdTorqueInMsgData = messaging.CmdTorqueBodyMsgPayload()
    cmdTorqueInMsgData.torqueRequestBody = requested_torque
    cmdTorqueInMsg = messaging.CmdTorqueBodyMsg().write(cmdTorqueInMsgData)

    cmdForceInMsgData = messaging.CmdForceBodyMsgPayload()
    cmdForceInMsgData.forceRequestBody = requested_force
    cmdForceInMsg = messaging.CmdForceBodyMsg().write(cmdForceInMsgData)

    numThrusters = len(rcsLocation)
    maxThrust = 3.0  # N
    MAX_EFF_CNT = messaging.MAX_EFF_CNT
    rcsLocationData = np.zeros((MAX_EFF_CNT, 3))
    rcsDirectionData = np.zeros((MAX_EFF_CNT, 3))

    rcsLocationData[0:len(rcsLocation)] = rcsLocation

    rcsDirectionData[0:len(rcsLocation)] = rcsDirection

    fswSetupThrusters.clearSetup()
    for i in range(numThrusters):
        fswSetupThrusters.create(rcsLocationData[i], rcsDirectionData[i], maxThrust)
    thrConfigInMsg = fswSetupThrusters.writeConfigMessage()

    vehConfigInMsgData = messaging.VehicleConfigMsgPayload()
    vehConfigInMsgData.CoM_B = CoM_B
    vehConfigInMsg = messaging.VehicleConfigMsg().write(vehConfigInMsgData)

    # subscribe input messages to module
    moduleConfig.cmdTorqueInMsg.subscribeTo(cmdTorqueInMsg)
    moduleConfig.cmdForceInMsg.subscribeTo(cmdForceInMsg)
    moduleConfig.thrConfigInMsg.subscribeTo(thrConfigInMsg)
    moduleConfig.vehConfigInMsg.subscribeTo(vehConfigInMsg)

    unitTestSim.InitializeSimulation()
    unitTestSim.ConfigureStopTime(macros.sec2nano(0.5))
    unitTestSim.ExecuteSimulation()

    testFailCount, testMessages = unitTestSupport.compareArray(truth, np.array([moduleConfig.thrForceCmdOutMsg.read().thrForce[0:len(rcsLocation)]]), 1e-3,
                                                                 "CompareForces", testFailCount, testMessages)

    if testFailCount == 0:
        print("PASSED: " + moduleWrap.ModelTag)
    else:
        print(testMessages)

    return [testFailCount, "".join(testMessages)]


if __name__ == "__main__":
    test_forceTorqueThrForceMapping()


