''' '''
'''
 ISC License

 Copyright (c) 2016-2017, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
import pytest
import sys, os, inspect

#
# orb_elem_convert Unit Test
#
# Purpose:  Test the precision of the orb_elem_convert module. Functionality
#           is tested by comparing input/output data as well as calculated
#           conversions.
# Author:   Gabriel Chapel
# Creation Date:  July 27, 2017
#

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
splitPath = path.split('SimCode')
sys.path.append(splitPath[0] + '/modules')
sys.path.append(splitPath[0] + '/PythonModules')

# @cond DOXYGEN_IGNOREimport spice_interface
import SimulationBaseClass
import numpy
import orb_elem_convert
import macros
import matplotlib.pyplot as plt
import math
import macros as mc

# @endcond

# Class in order to plot using data accross the different paramatrized scenarios
class DataStore:
    def __init__(self):
        self.Date = [] # replace these with appropriate containers for the data to be stored for plotting
        self.MarsPosErr = []
        self.EarthPosErr = []
        self.SunPosErr = []

@pytest.mark.parametrize("a, e, i, AN, AP, f, mu", [
    # Inclined Elliptical Orbit Varying e
    (10000000.0, 0.01, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.10, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.25, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.50, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.75, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    # Inclined Elliptical Orbit Varying a
    (10000000.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (100000.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (10000.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (100.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (10.0, 0.50, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # Equatorial Elliptical Orbit Varying e
    (10000000.0, 0.01, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.10, 0.0, 0.0, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.25, 0.0, 0.0, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.50, 0.0, 0.0, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    (10000000.0, 0.75, 0.0, 0.0, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15),
    # Equatorial Elliptical Orbit Varying a
    (10000000.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15), # For i=0 => AN=0
    (100000.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (10000.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (100.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (10.0, 0.50, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # Inclined Circular Orbit
    (10000000.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000000.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (100000.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (10000.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (100.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (10.0, 0.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    # Equatorial Circular Orbit
    (10000000.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000000.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (100000.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (10000.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (1000.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (100.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),
    (10.0, 0.0, 0.0, 0.0, 0.0, 85.3 * mc.D2R, 0.3986004415E+15),

    # Inclined Parabolic Orbit
    (-10.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),   # For input of -a,
    (-100.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),  # must have e= 1.0
    (-1000.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15), # or e >1.0
    (-10000.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    # Equatorial Parabolic Orbit
    (-10.0, 1.0, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),   # For input of -a,
    (-100.0, 1.0, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),  # must have e= 1.0
    (-1000.0, 1.0, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15), # or e >1.0
    (-10000.0, 1.0, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.0, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # Inclined Hyperbolic Orbit varying a
    (-10.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-1000.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-10000.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    # Inclined Hyperbolic Orbit varying e
    (-100000.0, 1.1, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.2, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.3, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.4, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.5, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # Equatorial Hyperbolic Orbit varying a
    (-10.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-1000.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-10000.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    # Equatorial Hyperbolic Orbit varying e
    (-100000.0, 1.1, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.2, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.3, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.4, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),
    (-100000.0, 1.5, 0.0, 0.0, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # # Approaching circular orbit
    # (100000.0, 0.000001, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15),

    # These don't work
    # (10000000.0, 1.0, 33.3 * mc.D2R, 48.2 * mc.D2R, 347.8 * mc.D2R, 85.3 * mc.D2R, 0.3986004415E+15), # or e >1.0
    # (-10, 0.9, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15)
])

# provide a unique test method name, starting with test_
def test_orb_elem_convert(a, e, i, AN, AP, f, mu, DispPlot=False):
    # each test method requires a single assert method to be called
    [testResults, testMessage] = orbElem(a, e, i, AN, AP, f, mu, DispPlot)
    assert testResults < 1, testMessage

# Run unit test
def orbElem(a, e, i, AN, AP, f, mu, DispPlot):
    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty array to store test log messages

    # Create a sim module as an empty container
    unitTaskName = "unitTask"  # arbitrary name (don't change)
    unitProcessName = "TestProcess"  # arbitrary name (don't change)

    # Create a sim module as an empty container
    TotalSim = SimulationBaseClass.SimBaseClass()
    TotalSim.TotalSim.terminateSimulation()

    DynUnitTestProc = TotalSim.CreateNewProcess(unitProcessName)
    # # create the dynamics task and specify the integration update time
    testProcessRate = macros.sec2nano(1.0)
    DynUnitTestProc.addTask(TotalSim.CreateNewTask(unitTaskName, testProcessRate))

    # Initialize the modules that we are using.
    orb_elemObject = orb_elem_convert.OrbElemConvert()
    orb_elemObject.ModelTag = "OrbElemConvertData"

    # Add Model To Task
    TotalSim.AddModelToTask(unitTaskName, orb_elemObject)

    # Set element values
    epsDiff = 0.000001
    orb_elemObject.mu = mu
    orb_elemObject.Elements2Cart = True
    orb_elemObject.inputsGood = True
    orb_elemObject.ReinitSelf = True
    orb_elemObject.useEphemFormat = True


    ###### ELEM2RV ######
    TotalSim.AddVariableForLogging('OrbElemConvertData.r_N', testProcessRate, 0, 2, 'double')
    TotalSim.AddVariableForLogging('OrbElemConvertData.v_N', testProcessRate, 0, 2, 'double')
    TotalSim.AddVariableForLogging('OrbElemConvertData.ReinitSelf')

    orb_elemObject.StateString = "ClassicElemString"
    ElemMessage = orb_elem_convert.classicElements()
    inputMessageSize = ElemMessage.getStructSize()

    # Create and write messages
    TotalSim.TotalSim.CreateNewMessage(unitProcessName, orb_elemObject.StateString, inputMessageSize, 2)
    # number of buffers (leave at 2 as default, don't make zero)

    ElemMessage.a = a  # meters
    ElemMessage.e = e
    ElemMessage.i = i
    ElemMessage.Omega = AN
    ElemMessage.omega = AP
    ElemMessage.f = f

    TotalSim.TotalSim.WriteMessageData(orb_elemObject.StateString, inputMessageSize, 0, ElemMessage)

    # Log Message to test WriteOutputMessage()
    TotalSim.TotalSim.logThisMessage(orb_elemObject.OutputDataString)

    # Execute simulation
    TotalSim.ConfigureStopTime(int(1E9))
    TotalSim.InitializeSimulation()
    TotalSim.ExecuteSimulation()

    # Get r and v from sim
    vSim = TotalSim.GetLogVariableData('OrbElemConvertData.v_N')
    vSim = numpy.delete(vSim[-1], 0, axis=0)
    rSim = TotalSim.GetLogVariableData('OrbElemConvertData.r_N')
    rSim = numpy.delete(rSim[-1], 0, axis=0)

    # Get r and v from message
    if orb_elemObject.useEphemFormat:
        rMsgPlanet = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + '.PositionVector', range(3))
        rMsgPlanet = numpy.delete(rMsgPlanet[-1], 0, axis=0)
        vMsgPlanet = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + '.VelocityVector', range(3))
        vMsgPlanet = numpy.delete(vMsgPlanet[-1], 0, axis=0)
        rMsgPlanetDiff = numpy.subtract(rSim, rMsgPlanet)
        for g in range(3):
            if abs(rMsgPlanetDiff[g]) > 0:
                testMessages.append(" FAILED: Planet Position Message, column " + str(g))
                testFailCount += 1
        vMsgPlanetDiff = numpy.subtract(vSim, vMsgPlanet)
        for g in range(3):
            if abs(vMsgPlanetDiff[g]) > 0:
                testMessages.append(" FAILED: Planet Velocity Message, column " + str(g))
                testFailCount += 1
    else:
        rMsgSC = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + '.r_BN_N', range(3))
        rMsgSC = numpy.delete(rMsgSC[-1], 0, axis=0)
        vMsgSC = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + '.v_BN_N', range(3))
        vMsgSC = numpy.delete(vMsgSC[-1], 0, axis=0)
        rMsgSCDiff = numpy.subtract(rSim, rMsgSC)
        for g in range(3):
            if abs(rMsgSCDiff[g]) > 0:
                testMessages.append(" FAILED: Spacecraft Position Message, column " + str(g))
                testFailCount += 1
        vMsgSCDiff = numpy.subtract(vSim, vMsgSC)
        for g in range(3):
            if abs(vMsgSCDiff[g]) > 0:
                testMessages.append(" FAILED: Spacecraft Velocity Message, column " + str(g))
                testFailCount += 1


    ReinitSelf = TotalSim.GetLogVariableData('OrbElemConvertData.ReinitSelf')
    ReinitSelf = numpy.delete(ReinitSelf[-1], 0, axis=0)
    if ReinitSelf:
        testMessages.append(" FAILED: ReinitSelf")
        testFailCount += 1

    # Calculation of elem2rv
    if e == 1.0 and a > 0.0:  # rectilinear elliptic orbit case
        Ecc = f  # f is treated as ecc.anomaly
        r = a * (1 - e * math.cos(Ecc))  # orbit radius
        v = math.sqrt(2 * mu / r - mu / a)
        ir = numpy.zeros(3)
        ir[0] = math.cos(AN) * math.cos(AP) - math.sin(AN) * math.sin(AP) * math.cos(i)
        ir[1] = math.sin(AN) * math.cos(AP) + math.cos(AN) * math.sin(AP) * math.cos(i)
        ir[2] = math.sin(AP) * math.sin(i)
        rTruth = numpy.multiply(r, ir)
        if math.sin(Ecc) > 0:
            vTruth = numpy.multiply(-v, ir)
        else:
            vTruth = numpy.multiply(v, ir)
    else:
        if e == 1 and a < 0:  # parabolic case
            rp = -a  # radius at periapses
            p = 2 * rp  # semi-latus rectum
        else:  # elliptic and hyperbolic cases
            p = a * (1 - e * e)  # semi-latus rectum

        r = p / (1 + e * math.cos(f))  # orbit radius
        theta = AP + f  # true latitude angle
        h = math.sqrt(mu * p)  # orbit ang.momentum mag.

        rTruth = numpy.zeros(3)
        rTruth[0] = r * (math.cos(AN) * math.cos(theta) - math.sin(AN) * math.sin(theta) * math.cos(i))
        rTruth[1] = r * (math.sin(AN) * math.cos(theta) + math.cos(AN) * math.sin(theta) * math.cos(i))
        rTruth[2] = r * (math.sin(theta) * math.sin(i))

        vTruth = numpy.zeros(3)
        vTruth[0] = -mu / h * (math.cos(AN) * (math.sin(theta) + e * math.sin(AP)) + math.sin(AN) * (math.cos(
            theta) + e * math.cos(AP)) * math.cos(i))
        vTruth[1] = -mu / h * (math.sin(AN) * (math.sin(theta) + e * math.sin(AP)) - math.cos(AN) * (math.cos(
            theta) + e * math.cos(AP)) * math.cos(i))
        vTruth[2] = -mu / h * (-(math.cos(theta) + e * math.cos(AP)) * math.sin(i))

    # Position and Velocity Diff Checks
    rDiff = numpy.subtract(rSim, rTruth)
    vDiff = numpy.subtract(vSim, vTruth)
    rDiffcsv = numpy.asarray(rDiff)
    vDiffcsv = numpy.asarray(vDiff)
    for g in range(3):
        if abs(rDiff[g]) > epsDiff:
            testMessages.append(" FAILED: Position Vector, column " + str(g))
            testFailCount += 1
    for g in range(3):
        if abs(vDiff[g]) > epsDiff:
            testMessages.append(" FAILED: Velocity Vector, column " + str(g))
            testFailCount += 1

    ###### RV2ELEM ######
    for g in range(2):
        TotalSim = SimulationBaseClass.SimBaseClass()
        TotalSim.TotalSim.terminateSimulation()
        DynUnitTestProc = TotalSim.CreateNewProcess(unitProcessName)

        # # create the dynamics task and specify the integration update time
        testProcessRate = macros.sec2nano(1.0)
        DynUnitTestProc.addTask(TotalSim.CreateNewTask(unitTaskName, testProcessRate))

        # Initialize the modules that we are using.
        orb_elemObject = orb_elem_convert.OrbElemConvert()
        orb_elemObject.ModelTag = "OrbElemConvertData"

        # Add Model To Task
        TotalSim.AddModelToTask(unitTaskName, orb_elemObject)

        # Log Variables
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.a')
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.e')
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.i')
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.Omega')
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.omega')
        TotalSim.AddVariableForLogging('OrbElemConvertData.CurrentElem.f')
        TotalSim.AddVariableForLogging('OrbElemConvertData.Elements2Cart')
        TotalSim.AddVariableForLogging('OrbElemConvertData.inputsGood')
        TotalSim.AddVariableForLogging('OrbElemConvertData.r_N', testProcessRate, 0, 2, 'double')
        TotalSim.AddVariableForLogging('OrbElemConvertData.v_N', testProcessRate, 0, 2, 'double')

        orb_elemObject.Elements2Cart = False
        orb_elemObject.inputsGood = True
        orb_elemObject.mu = mu

        if g == 0:
            orb_elemObject.useEphemFormat = False
            CartMessage = orb_elem_convert.SCPlusStatesSimMsg()
            CartMessage.r_BN_N = rSim
            CartMessage.v_BN_N = vSim
        else:
            orb_elemObject.useEphemFormat = True
            CartMessage = orb_elem_convert.SpicePlanetStateSimMsg()
            CartMessage.PositionVector = rSim
            CartMessage.VelocityVector = vSim

        orb_elemObject.StateString = "inertial_state_output"
        inputMessageSize = CartMessage.getStructSize()

        # Create and write messages
        TotalSim.TotalSim.CreateNewMessage(unitProcessName, orb_elemObject.StateString, inputMessageSize, 2)
        # number of buffers (leave at 2 as default, don't make zero)


        TotalSim.TotalSim.WriteMessageData(orb_elemObject.StateString, inputMessageSize, 0, CartMessage)

        TotalSim.TotalSim.logThisMessage(orb_elemObject.OutputDataString)

        # Execute simulation
        TotalSim.ConfigureStopTime(int(1E9))
        TotalSim.InitializeSimulation()
        TotalSim.ExecuteSimulation()

        aOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.a')
        aOut = numpy.delete(aOut[-1], 0, axis=0)
        eOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.e')
        eOut = numpy.delete(eOut[-1], 0, axis=0)
        iOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.i')
        iOut = numpy.delete(iOut[-1], 0, axis=0)
        ANOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.Omega')
        ANOut = numpy.delete(ANOut[-1], 0, axis=0)
        APOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.omega')
        APOut = numpy.delete(APOut[-1], 0, axis=0)
        fOut = TotalSim.GetLogVariableData('OrbElemConvertData.CurrentElem.f')
        fOut = numpy.delete(fOut[-1], 0, axis=0)

        # Element Diff Check
        ElemDiff = [(a - aOut), (e - eOut), (i - iOut), (AN - ANOut), (AP - APOut), (f - fOut)]
        ElemDiffcsv = numpy.asarray(ElemDiff)
        for g in range(6):
            if abs(ElemDiff[g]) > epsDiff:
                testMessages.append(" FAILED: Sim Orbital Element " + str(g))
                testFailCount += 1

    aMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".a", range(1))
    aMsg = numpy.delete(aMsg[-1], 0, axis=0)
    eMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".e", range(1))
    eMsg = numpy.delete(eMsg[-1], 0, axis=0)
    iMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".i", range(1))
    iMsg = numpy.delete(iMsg[-1], 0, axis=0)
    ANMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".Omega", range(1))
    ANMsg = numpy.delete(ANMsg[-1], 0, axis=0)
    APMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".omega", range(1))
    APMsg = numpy.delete(APMsg[-1], 0, axis=0)
    fMsg = TotalSim.pullMessageLogData(orb_elemObject.OutputDataString + ".f", range(1))
    fMsg = numpy.delete(fMsg[-1], 0, axis=0)

    ElemMsgDiff = [(aOut - aMsg), (eOut - eMsg), (iOut - iMsg), (ANOut - ANMsg), (APOut - APMsg), (fOut - fMsg)]
    for g in range(6):
        if abs(ElemMsgDiff[g]) > 0:
            testMessages.append(" FAILED: Orbital Element Message " + str(g))
            testFailCount += 1
    ######### Calculate rv2elem #########
    # Calculate the specific angular momentum and its magnitude
    epsConv = 0.000000000001
    hVec = numpy.cross(rTruth, vTruth)
    h = numpy.linalg.norm(hVec)
    p = h * h / mu

    # Calculate the line of nodes
    v3 = numpy.array([0.0, 0.0, 1.0])
    nVec = numpy.cross(v3, hVec)
    n = numpy.linalg.norm(nVec)

    # Orbit eccentricity and energy
    r = numpy.linalg.norm(rTruth)
    v = numpy.linalg.norm(vTruth)
    eVec = numpy.multiply(v * v / mu - 1.0 / r, rTruth)
    v3 = numpy.multiply(numpy.dot(rTruth, vTruth) / mu, vTruth)
    eVec = numpy.subtract(eVec, v3)
    eO = numpy.linalg.norm(eVec)
    rmag = r
    rPeriap = p / (1.0 + eO)

    # compute semi - major axis
    alpha = 2.0 / r - v * v / mu
    if (math.fabs(alpha) > epsConv): # elliptic or hyperbolic case
        aO = 1.0 / alpha
        rApoap = p / (1.0 - eO)
    else:                        # parabolic case
        rp = p / 2.0
        aO = -rp # a is not defined for parabola, so -rp is returned instead
        rApoap = -1.0

    # Calculate the inclination
    iO = math.acos(hVec[2] / h)

    # Calculate AP, AN, and True anomaly
    if eO >= 1e-11 and iO >= 1e-11:
    # Case 1: Non - circular, inclined orbit
        Omega = math.acos(nVec[0] / n)
        if (nVec[1] < 0.0):
            Omega = 2.0 * math.pi - Omega
        omega = math.acos(numpy.dot(nVec, eVec) / n / eO)
        if eVec[2] < 0.0:
            omega = 2.0 * math.pi - omega
        fO = math.acos(numpy.dot(eVec, rTruth) / eO / r)
        if numpy.dot(rTruth, vTruth) < 0.0:
            fO = 2.0 * math.pi - fO
    elif eO >= 1e-11 and iO < 1e-11:
    # Case 2: Non - circular, equatorial orbit
    # Equatorial orbit has no ascending node
        Omega = 0.0
        # True longitude of periapsis, omegatilde_true
        omega = math.acos(eVec[0] / eO)
        if eVec[1] < 0.0:
            omega = 2.0 * math.pi - omega
        fO = math.acos(numpy.dot(eVec, rTruth) / eO / r)
        if numpy.dot(rTruth, vTruth) < 0.0:
            fO = 2.0 * math.pi - fO
    elif eO < 1e-11 and iO >= 1e-11:
    # Case 3: Circular, inclined orbit
        Omega = math.acos(nVec[0] / n)
        if (nVec[1] < 0.0):
            Omega = 2.0 * math.pi - Omega
        omega = 0.0
        # Argument of latitude, u = omega + f * /
        fO = math.acos(numpy.dot(nVec, rTruth) / n / r)
        if rTruth[2] < 0.0:
            fO = 2.0 * math.pi - fO
    elif eO < 1e-11 and iO < 1e-11:
    # Case 4: Circular, equatorial orbit
        Omega = 0.0
        omega = 0.0
        # True longitude, lambda_true
        fO = math.acos(rTruth[0] / r)
        if rTruth[1] < 0:
            fO = 2.0 * math.pi - fO
    else:
        print("Error: rv2elem couldn't identify orbit type.\n")
    if (eO >= 1.0 and math.fabs(fO) > math.pi):
        twopiSigned = math.copysign(2.0 * math.pi, fO)
        fO -= twopiSigned

    # Element Diff Check
    ElemCalcDiff = [(aO - aOut), (eO - eOut), (iO - iOut), (Omega - ANOut), (omega - APOut), (fOut - fOut)]
    ElemCalcDiffcsv = numpy.asarray(ElemCalcDiff)
    for g in range(6):
        if abs(ElemCalcDiff[g]) > epsDiff:
            testMessages.append(" FAILED: Calculated Orbital Element " + str() + str(g))
            testFailCount += 1

    # create plot

    plt.close("all")

    fig1 = plt.figure(1)
    plt.clf()
    ax1 = fig1.add_subplot(211)
    index = numpy.arange(3)
    bar_width = 0.35
    opacity = 0.8
    rects1 = ax1.bar(index, rSim, bar_width, alpha=opacity, color='b', label='Simulated Position')
    rects2 = ax1.bar(index + bar_width, rTruth, bar_width, alpha=opacity, color='g', label='Calculated Position')
    ax1.spines['left'].set_position('zero')
    ax1.spines['right'].set_color('none')
    ax1.spines['bottom'].set_position('zero')
    ax1.spines['top'].set_color('none')
    ax1.spines['left'].set_smart_bounds(False)
    ax1.spines['bottom'].set_smart_bounds(False)
    for xtick in ax1.get_xticklabels():
        xtick.set_bbox(dict(facecolor='white', edgecolor='None', alpha=0.5))
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    plt.xlabel('Axis')
    plt.ylabel('Position (m)')
    plt.xticks(index + bar_width, ('X', 'Y', 'Z'))
    plt.legend(loc='lower right')

    ax2 = fig1.add_subplot(212)
    rects1 = ax2.bar(index, vSim, bar_width, alpha=opacity, color='b', label='Simulated Velocity')
    rects2 = ax2.bar(index + bar_width, vTruth, bar_width, alpha=opacity, color='g', label='Calculated Velocity')
    ax2.spines['left'].set_position('zero')
    ax2.spines['right'].set_color('none')
    ax2.spines['bottom'].set_position('zero')
    ax2.spines['top'].set_color('none')
    ax2.spines['left'].set_smart_bounds(False)
    ax2.spines['bottom'].set_smart_bounds(False)
    for xtick in ax2.get_xticklabels():
        xtick.set_bbox(dict(facecolor='white', edgecolor='None', alpha=0.5))
    ax2.xaxis.set_ticks_position('bottom')
    ax2.yaxis.set_ticks_position('left')
    plt.xlabel('Axis')
    plt.ylabel('Velocity (m/s)')
    plt.xticks(index + bar_width, ('X', 'Y', 'Z'))
    plt.legend(loc='lower right')

    fact = (len(str(abs(a)))-3.0)
    fig2, ax = plt.subplots()
    index = numpy.arange(6)
    initElem = (a/(10**fact), e, i, AN, AP, f)
    simElem = (aOut/(10**fact), eOut, iOut, ANOut, APOut, fOut)
    calcElem = (aO/(10**fact), eO, iO, Omega, omega, fO)
    rects1 = plt.bar(index, initElem, 0.2, alpha=opacity, color='b', label='Initial Elements')
    rects2 = plt.bar(index + 0.2, simElem, 0.2, alpha=opacity, color='g', label='Simulated Elements')
    rects3 = plt.bar(index + 2*0.2, calcElem, 0.2, alpha=opacity, color='c', label='Calculated Elements')
    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(False)
    ax.spines['bottom'].set_smart_bounds(False)
    for xtick in ax.get_xticklabels():
        xtick.set_bbox(dict(facecolor='white', edgecolor='None', alpha=0.5))
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.xlabel('Element')
    plt.ylabel('Magnitude')
    plt.xticks(index + bar_width, ('a*10^' + str(fact), 'e', 'i', 'AN', 'AP', 'f'))
    plt.legend(loc='upper left')
    plt.show(DispPlot)

    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    test_orb_elem_convert(10000000.0, 0.01, 33.3*mc.D2R, 48.2*mc.D2R, 347.8*mc.D2R, 85.3*mc.D2R, 0.3986004415E+15, True)
