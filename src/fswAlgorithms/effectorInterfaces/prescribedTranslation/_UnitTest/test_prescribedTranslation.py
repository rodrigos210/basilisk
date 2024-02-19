#
#  ISC License
#
#  Copyright (c) 2023, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
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
#   Unit Test Script
#   Module Name:        prescribedTranslation
#   Author:             Patrick Kenneally and Leah Kiner
#   Creation Date:      Feb 12, 2024
#

import inspect
import os

import matplotlib.pyplot as plt
import numpy as np
import pytest
from Basilisk.architecture import bskLogging
from Basilisk.architecture import messaging
from Basilisk.fswAlgorithms import prescribedTranslation
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import macros

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
bskName = 'Basilisk'
splitPath = path.split(bskName)


@pytest.mark.parametrize("scalarPosInit", [0, 2*np.pi/3])
@pytest.mark.parametrize("scalarPosRef", [0, 2*np.pi/3])
@pytest.mark.parametrize("scalarAccelMax", [0.0005, 0.002])
@pytest.mark.parametrize("accuracy", [1e-12])
def test_prescribedTranslation(show_plots, scalarPosInit, scalarPosRef, scalarAccelMax, accuracy):
    r"""
    **Validation Test Description**

    This unit test ensures that the profiled translational maneuver for a secondary rigid body connected
    to the spacecraft hub is properly computed for a series of initial and reference positions and maximum
    accelerations. The final prescribed position and velocity magnitudes are compared with the reference values.

    **Test Parameters**

    Args:
        scalarPosInit (float): [m] Initial scalar position of the F frame with respect to the M frame
        scalarPosRef (float): [m] Reference scalar position of the F frame with respect to the M frame
        scalarAccelMax (float): [m/s^2] Maximum acceleration for the translational maneuver
        accuracy (float): absolute accuracy value used in the validation tests

    **Description of Variables Being Tested**

    This unit test ensures that the profiled translational maneuver is properly computed for a series of initial and
    reference positions and maximum accelerations. The final prescribed position magnitude ``r_FM_M_Final`` and
    velocity magnitude ``rPrime_FM_M_Final`` are compared with the reference values ``r_FM_M_Ref`` and
    ``rPrime_FM_M_Ref``, respectively.
    """

    unitTaskName = "unitTask"
    unitProcessName = "TestProcess"
    bskLogging.setDefaultLogLevel(bskLogging.BSK_WARNING)

    # Create a sim module as an empty container
    unitTestSim = SimulationBaseClass.SimBaseClass()

    testProcessRate = macros.sec2nano(0.1)
    testProc = unitTestSim.CreateNewProcess(unitProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(unitTaskName, testProcessRate))

    prescribedTrans = prescribedTranslation.PrescribedTranslation()
    prescribedTrans.ModelTag = "prescribedTranslation"

    unitTestSim.AddModelToTask(unitTaskName, prescribedTrans)

    transAxis_M = np.array([0.5, 0.0, 0.5 * np.sqrt(3)])
    prescribedTrans.transAxis_M = transAxis_M
    prescribedTrans.scalarAccelMax = scalarAccelMax  # [rad/s^2]
    prescribedTrans.r_FM_M = scalarPosInit * transAxis_M
    prescribedTrans.rPrime_FM_M = np.array([0.0, 0.0, 0.0])
    prescribedTrans.rPrimePrime_FM_M = np.array([0.0, 0.0, 0.0])

    # Create input message
    scalarVelRef = 0.0  # [m/s]
    linearTranslationRigidBodyMessageData = messaging.LinearTranslationRigidBodyMsgPayload()
    linearTranslationRigidBodyMessageData.rho = scalarPosRef
    linearTranslationRigidBodyMessageData.rhoDot = scalarVelRef
    linearTranslationRigidBodyMessage = messaging.LinearTranslationRigidBodyMsg().write(linearTranslationRigidBodyMessageData)
    prescribedTrans.linearTranslationRigidBodyInMsg.subscribeTo(linearTranslationRigidBodyMessage)

    dataLog = prescribedTrans.prescribedTranslationOutMsg.recorder()
    unitTestSim.AddModelToTask(unitTaskName, dataLog)

    simTime = np.sqrt(((0.5 * np.abs(scalarPosRef - scalarPosInit)) * 8) / scalarAccelMax) + 5
    unitTestSim.ConfigureStopTime(macros.sec2nano(simTime))
    unitTestSim.InitializeSimulation()
    unitTestSim.ExecuteSimulation()

    # Extract logged data
    r_FM_M = dataLog.r_FM_M
    rPrime_FM_M = dataLog.rPrime_FM_M
    timespan = dataLog.times()

    scalarVel_Final = np.linalg.norm(rPrime_FM_M[-1, :])
    scalarPos_Final = np.linalg.norm(r_FM_M[-1, :])

    # Plot r_FM_F
    r_FM_M_Ref = scalarPosRef * transAxis_M
    r_FM_M_1_Ref = np.ones(len(timespan)) * r_FM_M_Ref[0]
    r_FM_M_2_Ref = np.ones(len(timespan)) * r_FM_M_Ref[1]
    r_FM_M_3_Ref = np.ones(len(timespan)) * r_FM_M_Ref[2]

    plt.figure()
    plt.clf()
    plt.plot(timespan * macros.NANO2SEC, r_FM_M[:, 0], label=r'$r_{1}$')
    plt.plot(timespan * macros.NANO2SEC, r_FM_M[:, 1], label=r'$r_{2}$')
    plt.plot(timespan * macros.NANO2SEC, r_FM_M[:, 2], label=r'$r_{3}$')
    plt.plot(timespan * macros.NANO2SEC, r_FM_M_1_Ref, '--', label=r'$r_{1 Ref}$')
    plt.plot(timespan * macros.NANO2SEC, r_FM_M_2_Ref, '--', label=r'$r_{2 Ref}$')
    plt.plot(timespan * macros.NANO2SEC, r_FM_M_3_Ref, '--', label=r'$r_{3 Ref}$')
    plt.title(r'${}^\mathcal{M} r_{\mathcal{F}/\mathcal{M}}$ Profiled Trajectory', fontsize=14)
    plt.ylabel('(m)', fontsize=16)
    plt.xlabel('Time (s)', fontsize=16)
    plt.legend(loc='center left', prop={'size': 16})

    # Plot rPrime_FM_F
    plt.figure()
    plt.clf()
    plt.plot(timespan * macros.NANO2SEC, rPrime_FM_M[:, 0], label='$r\'_{1}$')
    plt.plot(timespan * macros.NANO2SEC, rPrime_FM_M[:, 1], label='$r\'_{2}$')
    plt.plot(timespan * macros.NANO2SEC, rPrime_FM_M[:, 2], label='$r\'_{3}$')
    plt.title(r'${}^\mathcal{M} r\'_{\mathcal{F}/\mathcal{M}}$ Profiled Trajectory', fontsize=14)
    plt.ylabel('(m/s)', fontsize=16)
    plt.xlabel('Time (s)', fontsize=16)
    plt.legend(loc='upper left', prop={'size': 16})

    if show_plots:
        plt.show()
    plt.close("all")

    np.testing.assert_allclose(scalarVelRef,
                               scalarVel_Final,
                               atol=accuracy,
                               err_msg="scalarVel_Final and scalarVelRef do not match",
                               verbose=True)

    np.testing.assert_allclose(scalarPosRef,
                               scalarPos_Final,
                               atol=accuracy,
                               err_msg="scalarPos_Final and scalarPosRef do not match",
                               verbose=True)


if __name__ == "__main__":
    test_prescribedTranslation(
                 True,
                 0.0,         # scalarPosInit
                 0.25,        # scalarPosRef
                 0.001,       # scalarAccelMax
                 1e-12        # accuracy
               )
