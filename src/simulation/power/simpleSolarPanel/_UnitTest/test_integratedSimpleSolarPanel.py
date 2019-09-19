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
#   Module Name:        simpleSolarPanel
#   Author:             Andrew Harris
#   Creation Date:      July 17th 2019
#

import pytest
import os, inspect
import numpy as np
import math

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
bskName = 'Basilisk'
splitPath = path.split(bskName)

# Import all of the modules that we are going to be called in this simulation
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport                  # general support file with common unit test functions
from Basilisk.simulation import simplePowerSink
from Basilisk.simulation import simplePowerMonitor
from Basilisk.simulation import simMessages
from Basilisk.simulation import simFswInterfaceMessages
from Basilisk.simulation import simpleSolarPanel
from Basilisk.simulation import simMessages
from Basilisk.simulation import simFswInterfaceMessages
from Basilisk.simulation import eclipse
from Basilisk.simulation import spacecraftPlus
from Basilisk.utilities import macros
from Basilisk.utilities import orbitalMotion
from Basilisk.utilities import simIncludeGravBody



# Uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed.
# @pytest.mark.skipif(conditionstring)
# Uncomment this line if this test has an expected failure, adjust message as needed.
# @pytest.mark.xfail(conditionstring)
# Provide a unique test method name, starting with 'test_'.

# update "module" in this function name to reflect the module name
def test_module():
    # each test method requires a single assert method to be called

    defaultResults, defaultMessage = test_default()


    assert defaultResults < 1, defaultMessage


def test_default():
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

    # Create a spacecraft around Earth
    # initialize spacecraftPlus object and set properties
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"

    # clear prior gravitational body and SPICE setup definitions
    gravFactory = simIncludeGravBody.gravBodyFactory()

    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    mu = planet.mu
    # attach gravity model to spaceCraftPlus
    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector(gravFactory.gravBodies.values())

    #   setup orbit using orbitalMotion library
    oe = orbitalMotion.ClassicElements()
    oe.a = 6371*1000.0 + 1000.*1000
    oe.e = 0.0
    oe.i = 0.0*macros.D2R

    oe.Omega = 0.0*macros.D2R
    oe.omega = 0.0*macros.D2R
    oe.f     = 0.0*macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)

    scObject.hub.r_CN_NInit = unitTestSupport.np2EigenVectorXd(rN)
    scObject.hub.v_CN_NInit = unitTestSupport.np2EigenMatrix3d(vN)

    #   Create an eclipse object so the panels don't always work
    eclipseObject = eclipse.Eclipse()
    eclipseObject.addPositionMsgName(scObject.scStateOutMsgName)
    eclipseObject.addPlanetName('earth')

    # Create a power sink/source
    testPanel = simpleSolarPanel.SimpleSolarPanel()
    testPanel.ModelTag = "solarPanel"
    testPanel.setPanelParameters(unitTestSupport.np2EigenMatrix3d(np.array([1,0,0])), 0.2*0.3, 0.20)
    testPanel.nodePowerOutMsgName = "panelPowerMsg"
    unitTestSim.AddModelToTask(unitTaskName, testPanel)


    # setup Spice interface for some solar system bodies
    timeInitString = '2021 MAY 04 07:47:48.965 (UTC)'
    gravFactory.createSpiceInterface(bskPath + '/supportData/EphemerisData/'
                                     , timeInitString
                                     , spicePlanetNames = ["sun", "venus", "earth", "mars barycenter"]
                                     )

    # Create a power sink/source
    testSourceModule = simplePowerSink.SimplePowerSink()
    testSourceModule.ModelTag = "powerSource"
    testSourceModule.nodePowerOut = 15. # Watts
    testSourceModule.nodePowerOutMsgName = "powerSourceMsg"
    unitTestSim.AddModelToTask(unitTaskName, testSourceModule)

    testSinkModule = simplePowerSink.SimplePowerSink()
    testSinkModule.ModelTag = "powerSink2"
    testSinkModule.nodePowerOut = -10. # Watts
    testSourceModule.nodePowerOutMsgName = "powerSinkMsg"
    unitTestSim.AddModelToTask(unitTaskName, testSinkModule)

    # Create a simplePowerMonitor and attach the source/sink to it
    testMonitorModule = simplePowerMonitor.SimplePowerMonitor()
    testMonitorModule.ModelTag = "powerMonitor"
    testMonitorModule.batPowerOutMsgName = "powerMonitorMsg"
    testMonitorModule.addPowerNodeToModel(testSourceModule.nodePowerOutMsgName)
    testMonitorModule.addPowerNodeToModel(testSinkModule.nodePowerOutMsgName)
    unitTestSim.AddModelToTask(unitTaskName, testMonitorModule)


    # Setup logging on the test module output message so that we get all the writes to it
    unitTestSim.TotalSim.logThisMessage(testSourceModule.nodePowerOutMsgName, testProcessRate)
    unitTestSim.TotalSim.logThisMessage(testSinkModule.nodePowerOutMsgName, testProcessRate)
    unitTestSim.TotalSim.logThisMessage(testMonitorModule.batPowerOutMsgName, testProcessRate)

    # Need to call the self-init and cross-init methods
    unitTestSim.InitializeSimulation()

    # Set the simulation time.
    # NOTE: the total simulation time may be longer than this value. The
    # simulation is stopped at the next logging event on or after the
    # simulation end time.
    unitTestSim.ConfigureStopTime(macros.sec2nano(1.0))        # seconds to stop simulation

    # Begin the simulation time run set above
    unitTestSim.ExecuteSimulation()

    # This pulls the actual data log from the simulation run.
    # Note that range(3) will provide [0, 1, 2]  Those are the elements you get from the vector (all of them)
    supplyData = unitTestSim.pullMessageLogData(testSourceModule.nodePowerOutMsgName + ".netPower_W")
    sinkData = unitTestSim.pullMessageLogData(testSinkModule.nodePowerOutMsgName + ".netPower_W")
    storageData = unitTestSim.pullMessageLogData(testMonitorModule.batPowerOutMsgName + ".storageLevel")
    netData = unitTestSim.pullMessageLogData(testMonitorModule.batPowerOutMsgName + ".currentNetPower")






    # compare the module results to the truth values
    accuracy = 1e-16
    unitTestSupport.writeTeXSnippet("unitTestToleranceValue", str(accuracy), path)

    trueNetPower = 5.0 #Module should be off
    trueStorageData = [0, 2.5, 5]

    testFailCount, testMessages = unitTestSupport.compareDoubleArray(
        [trueNetPower]*3, netData, accuracy, "powerStorageNetCalculation",
        testFailCount, testMessages)

    testFailCount, testMessages = unitTestSupport.compareDoubleArray(
        trueStorageData, storageData, accuracy, "powerStorageAccumulatedCalculation",
        testFailCount, testMessages)

    # each test method requires a single assert method to be called
    # this check below just makes sure no sub-test failures were found
    return [testFailCount, ''.join(testMessages)]



#
# This statement below ensures that the unitTestScript can be run as a
# stand-alone python script
#
if __name__ == "__main__":
    test_module()
