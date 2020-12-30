
# ISC License
#
# Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


#
# Ephemeris Converter Unit Test
#
# Purpose:  Test the proper function of the ephemeris_converter module.
# Author:   Thibaud Teil
#

from Basilisk.utilities import unitTestSupport
from Basilisk.utilities import SimulationBaseClass
from Basilisk.simulation import spiceInterface
from Basilisk.simulation import ephemerisConverter
from Basilisk.utilities import macros
from Basilisk import __path__
bskPath = __path__[0]


# provide a unique test method name, starting with test_
def test_ephemConvert(show_plots):
    """Module Unit Test"""
    # each test method requires a single assert method to be called
    [testResults, testMessage] = unitephemeris_converter(show_plots)
    assert testResults < 1, testMessage


def unitephemeris_converter(show_plots):
    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty array to store test log messages

    # Create a sim module as an empty container
    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    # Create a sim module as an empty container
    sim = SimulationBaseClass.SimBaseClass()

    simulationTime = macros.sec2nano(30.)
    numDataPoints = 600
    samplingTime = simulationTime // (numDataPoints-1)
    DynUnitTestProc = sim.CreateNewProcess(unitProcessName)
    # create the dynamics task and specify the integration update time
    DynUnitTestProc.addTask(sim.CreateNewTask(unitTaskName, samplingTime))

    # List of planets tested
    planets = ["earth", "mars barycenter", "sun"]

    # Initialize the spice module
    spiceObject = spiceInterface.SpiceInterface()
    spiceObject.ModelTag = "SpiceInterfaceData"
    spiceObject.SPICEDataPath = bskPath + '/supportData/EphemerisData/'
    spiceObject.addPlanetNames(spiceInterface.StringVector(planets))
    spiceObject.UTCCalInit = "2015 February 10, 00:00:00.0 TDB"
    sim.AddModelToTask(unitTaskName, spiceObject)

    # Initialize the ephemeris module
    ephemObject = ephemerisConverter.EphemerisConverter()
    ephemObject.ModelTag = 'EphemData'
    ephemObject.addSpiceInputMsg(spiceObject.planetStateOutMsgs[0])  # earth
    ephemObject.addSpiceInputMsg(spiceObject.planetStateOutMsgs[1])  # mars
    ephemObject.addSpiceInputMsg(spiceObject.planetStateOutMsgs[2])  # sun
    sim.AddModelToTask(unitTaskName, ephemObject)

    # Configure simulation
    sim.ConfigureStopTime(int(simulationTime))

    dataSpiceLog = []
    dataEphemLog = []
    for i in range(0, len(planets)):
        dataSpiceLog.append(spiceObject.planetStateOutMsgs[i].recorder())
        dataEphemLog.append(ephemObject.ephemOutMsgs[i].recorder())
        sim.AddModelToTask(unitTaskName, dataSpiceLog[-1])
        sim.AddModelToTask(unitTaskName, dataEphemLog[-1])

    # Execute simulation
    sim.InitializeSimulation()
    sim.ExecuteSimulation()

    # Get the position, velocities and time for the message before and after the copy
    accuracy = 1e-12
    for i in range(0, len(planets)):
        ephemPlanetPosData = dataEphemLog[i].r_BdyZero_N
        spicePlanetPosData = dataSpiceLog[i].PositionVector
        ephemPlanetVelData = dataEphemLog[i].v_BdyZero_N
        spicePlanetVelData = dataSpiceLog[i].VelocityVector
        testFailCount, testMessages = unitTestSupport.compareArrayRelative(spicePlanetPosData[:,0:3], ephemPlanetPosData, accuracy, "Position", testFailCount, testMessages)
        testFailCount, testMessages = unitTestSupport.compareArrayRelative(spicePlanetVelData[:,0:3], ephemPlanetVelData, accuracy, "Velocity", testFailCount, testMessages)

    # print out success message if no error were found
    if testFailCount == 0:
        print(" \n PASSED ")
    else:
        print(testMessages)

    # each test method requires a single assert method to be called
    # this check below just makes sure no sub-test failures were found
    return [testFailCount, ''.join(testMessages)]


# This statement below ensures that the unit test scrip can be run as a
# stand-along python script
#
if __name__ == "__main__":
    test_ephemConvert(False)
