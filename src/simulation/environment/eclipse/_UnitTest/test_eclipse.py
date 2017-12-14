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


#
# Eclipse Condition Unit Test
#
# Purpose:  Test the proper function of the Eclipse environment module.
#           This is done by comparing computed expected shadow factors in
#           particular eclipse conditions to what is simulated
# Author:   Patrick Kenneally
# Creation Date:  May. 31, 2017
#

import pytest
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport
from Basilisk.simulation import spacecraftPlus
from Basilisk.utilities import macros
from Basilisk.simulation import spice_interface
from Basilisk.simulation import eclipse
from Basilisk import pyswice
from Basilisk.simulation import gravityEffector
from Basilisk.utilities import orbitalMotion
from Basilisk import __path__
bskPath = __path__[0]


# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail(True)
@pytest.mark.parametrize("eclipseCondition, planet", [
("partial", "earth"), ("full", "earth"), ("none", "earth"), ("annular", "earth"),
("partial", "mars"), ("full", "mars"), ("none", "mars"), ("annular", "mars")])

def test_unitEclipse(show_plots, eclipseCondition, planet):
    [testResults, testMessage] = unitEclipse(show_plots, eclipseCondition, planet)
    assert testResults < 1, testMessage


def unitEclipse(show_plots, eclipseCondition, planet):
    # The __tracebackhide__ setting influences pytest showing of tracebacks:
    # the mrp_steering_tracking() function will not be shown unless the
    # --fulltrace command line option is specified.
    __tracebackhide__ = True

    testFailCount = 0
    testMessages = []
    testTaskName = "unitTestTask"
    testProcessName = "unitTestProcess"
    testTaskRate = macros.sec2nano(1)

    # Create a simulation container
    unitTestSim = SimulationBaseClass.SimBaseClass()
    # Ensure simulation is empty
    unitTestSim.TotalSim.terminateSimulation()
    testProc = unitTestSim.CreateNewProcess(testProcessName)
    testProc.addTask(unitTestSim.CreateNewTask(testTaskName, testTaskRate))

    # Set up first spacecraft
    scObject_0 = spacecraftPlus.SpacecraftPlus()
    scObject_0.scStateOutMsgName = "inertial_state_output"
    unitTestSim.AddModelToTask(testTaskName, scObject_0)

    # setup SPICE ephemeris support
    if planet == "earth":
        earth = gravityEffector.GravBodyData()
        earth.bodyInMsgName = "earth_planet_data"
        earth.outputMsgName = "earth_display_frame_data"
        earth.mu = 0.3986004415E+15  # meters^3/s^2
        earth.radEquator = 6378136.6  # meters
        earth.isCentralBody = True
        earth.useSphericalHarmParams = False
        # attach gravity model to spaceCraftPlus
        scObject_0.gravField.gravBodies = spacecraftPlus.GravBodyVector([earth])
    elif planet == "mars":
        mars = gravityEffector.GravBodyData()
        mars.bodyInMsgName = "mars_planet_data"
        mars.outputMsgName = "mars_display_frame_data"
        mars.mu = 0.42828375214E+14  # meters^3/s^2
        mars.radEquator = 3396190  # meters
        mars.isCentralBody = True
        mars.useSphericalHarmParams = False
        # attach gravity model to spaceCraftPlus
        scObject_0.gravField.gravBodies = spacecraftPlus.GravBodyVector([mars])

    spiceObject = spice_interface.SpiceInterface()
    spiceObject.PlanetNames = spice_interface.StringVector(["sun", "venus", "earth", "mars barycenter"])
    # spiceObject.PlanetNames = spice_interface.StringVector(["sun", "mars barycenter"])

    spiceObject.ModelTag = "SpiceInterfaceData"
    spiceObject.SPICEDataPath = bskPath + 'External/EphemerisData/'
    spiceObject.OutputBufferCount = 100000
    spiceObject.UTCCalInit = '2021 MAY 04 07:47:49.965 (UTC)'
    # spiceObject.UTCCalInit = '2022 APR 03 07:47:49.965 (UTC)'
    # spiceObject.UTCCalInit = '2022 JUN 06 07:47:49.965 (UTC)'


    # pull in SPICE support libraries
    pyswice.furnsh_c(spiceObject.SPICEDataPath + 'de430.bsp')  # solar system bodies
    pyswice.furnsh_c(spiceObject.SPICEDataPath + 'naif0011.tls')  # leap second file
    pyswice.furnsh_c(spiceObject.SPICEDataPath + 'de-403-masses.tpc')  # solar system masses
    pyswice.furnsh_c(spiceObject.SPICEDataPath + 'pck00010.tpc')  # generic Planetary Constants Kernel

    if planet == "earth":
        if eclipseCondition == "full":
            spiceObject.zeroBase = "earth"
            # set up spacecraft 0 position and velocity for full eclipse
            oe = orbitalMotion.ClassicElements()
            r_0 = (500 + orbitalMotion.REQ_EARTH)  # km
            oe.a = r_0
            oe.e = 0.00001
            oe.i = 5.0 * macros.D2R
            oe.Omega = 48.2 * macros.D2R
            oe.omega = 0 * macros.D2R
            oe.f = 173 * macros.D2R
            r_N_0, v_N_0 = orbitalMotion.elem2rv(orbitalMotion.MU_EARTH, oe)
            scObject_0.hub.r_CN_NInit = r_N_0 * 1000  # convert to meters
            scObject_0.hub.v_CN_NInit = v_N_0 * 1000  # convert to meters
        elif eclipseCondition == "partial":
            spiceObject.zeroBase = "earth"
            # set up spacecraft 0 position and velocity for full eclipse
            oe = orbitalMotion.ClassicElements()
            r_0 = (500 + orbitalMotion.REQ_EARTH)  # km
            oe.a = r_0
            oe.e = 0.00001
            oe.i = 5.0 * macros.D2R
            oe.Omega = 48.2 * macros.D2R
            oe.omega = 0 * macros.D2R
            oe.f = 107.5 * macros.D2R
            r_N_0, v_N_0 = orbitalMotion.elem2rv(orbitalMotion.MU_EARTH, oe)
            scObject_0.hub.r_CN_NInit = r_N_0 * 1000  # convert to meters
            scObject_0.hub.v_CN_NInit = v_N_0 * 1000  # convert to meters
        elif eclipseCondition == "none":
            oe = orbitalMotion.ClassicElements()
            r_0 = 9959991.68982  # km
            oe.a = r_0
            oe.e = 0.00001
            oe.i = 5.0 * macros.D2R
            oe.Omega = 48.2 * macros.D2R
            oe.omega = 0 * macros.D2R
            oe.f = 107.5 * macros.D2R
            r_N_0, v_N_0 = orbitalMotion.elem2rv(orbitalMotion.MU_EARTH, oe)
            scObject_0.hub.r_CN_NInit = r_N_0 * 1000  # convert to meters
            scObject_0.hub.v_CN_NInit = v_N_0 * 1000  # convert to meters
        elif eclipseCondition == "annular":
            spiceObject.zeroBase = "earth"
            scObject_0.hub.r_CN_NInit = [-326716535628.942, -287302983139.247, -124542549301.050]

    elif planet == "mars":
        if eclipseCondition == "full":
            spiceObject.zeroBase = "mars barycenter"
            scObject_0.hub.r_CN_NInit = [-2930233.55919119, 2567609.100747609, 41384.23366372246] # meters
        elif eclipseCondition == "partial":
            print "partial mars"
            spiceObject.zeroBase = "mars barycenter"
            scObject_0.hub.r_CN_NInit = [-6050166.454829555, 2813822.447404055, 571725.5651779658] # meters
        elif eclipseCondition == "none":
            oe = orbitalMotion.ClassicElements()
            r_0 = 9959991.68982  # km
            oe.a = r_0
            oe.e = 0.00001
            oe.i = 5.0 * macros.D2R
            oe.Omega = 48.2 * macros.D2R
            oe.omega = 0 * macros.D2R
            oe.f = 107.5 * macros.D2R
            r_N_0, v_N_0 = orbitalMotion.elem2rv(orbitalMotion.MU_MARS, oe)
            scObject_0.hub.r_CN_NInit = r_N_0 * 1000  # convert to meters
            scObject_0.hub.v_CN_NInit = v_N_0 * 1000  # convert to meters
        elif eclipseCondition == "annular":
            spiceObject.zeroBase = "mars barycenter"
            scObject_0.hub.r_CN_NInit = [-427424601171.464, 541312532797.400, 259820030623.064]  # meters

    unitTestSim.AddModelToTask(testTaskName, spiceObject)
    eclipseObject = eclipse.Eclipse()
    eclipseObject.addPositionMsgName(scObject_0.scStateOutMsgName)
    eclipseObject.addPlanetName('earth')
    eclipseObject.addPlanetName('mars barycenter')
    eclipseObject.addPlanetName('venus')
    unitTestSim.AddModelToTask(testTaskName, eclipseObject)
    unitTestSim.TotalSim.logThisMessage("eclipse_data_0")
    unitTestSim.TotalSim.logThisMessage("mars barycenter_planet_data")
    unitTestSim.TotalSim.logThisMessage("sun_planet_data")
    unitTestSim.TotalSim.logThisMessage("earth_planet_data")

    unitTestSim.InitializeSimulation()

    # Execute the simulation for one time step
    unitTestSim.TotalSim.SingleStepProcesses()

    eclipseData_0 = unitTestSim.pullMessageLogData("eclipse_data_0.shadowFactor")
    # Obtain body position vectors to check with MATLAB
    marsData = unitTestSim.pullMessageLogData("mars barycenter_planet_data.PositionVector", range(3))
    sunData = unitTestSim.pullMessageLogData("sun_planet_data.PositionVector", range(3))
    earthData = unitTestSim.pullMessageLogData("earth_planet_data.PositionVector", range(3))
    marsData = numpy.delete(marsData[-1],0, axis = 0)
    sunData = numpy.delete(sunData[-1],0, axis = 0)
    earthData = numpy.delete(earthData[-1],0, axis = 0)
    eclipseData = numpy.delete(eclipseData_0[-1],0,axis=0)
    position = numpy.array(scObject_0.hub.r_CN_NInit)
    print repr(float(eclipseData))
    print repr(float(marsData[0])), repr(float(marsData[1])), repr(float(marsData[2]))
    print repr(float(sunData[0])), repr(float(sunData[1])), repr(float(sunData[2]))
    print repr(float(earthData[0])), repr(float(earthData[1])), repr(float(earthData[2]))
    print repr(float(position[0])), repr(float(position[1])), repr(float(position[2]))

    errTol = 1E-12
    if planet is "earth":
        if eclipseCondition is "partial":
            truthShadowFactor = 0.62310760206735027
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Earth partial eclipse condition")

        elif eclipseCondition is "full":
            truthShadowFactor = 0.0
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Earth full eclipse condition")

        elif eclipseCondition is "none":
            truthShadowFactor = 1.0
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Earth none eclipse condition")
        elif eclipseCondition is "annular":
            truthShadowFactor = 1.497253388113018e-04
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Earth annular eclipse condition")

    elif planet is "mars":
        if eclipseCondition is "partial":
            truthShadowFactor = 0.18745025055615416
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Mars partial eclipse condition")
        elif eclipseCondition is "full":
            truthShadowFactor = 0.0
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Mars full eclipse condition")
        elif eclipseCondition is "none":
            truthShadowFactor = 1.0
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Mars none eclipse condition")
        elif eclipseCondition is "annular":
            truthShadowFactor = 4.245137380531894e-05
            if not unitTestSupport.isDoubleEqual(eclipseData_0[0, :], truthShadowFactor, errTol):
                testFailCount += 1
                testMessages.append("Shadow Factor failed for Mars annular eclipse condition")


    if testFailCount == 0:
        print "PASSED: " + planet + "-" + eclipseCondition
        # return fail count and join into a single string all messages in the list
        # testMessage
    if testFailCount == 0:
        colorText = 'ForestGreen'
        passFailMsg = ""  # "Passed: " + name + "."
        passedText = '\\textcolor{' + colorText + '}{' + "PASSED" + '}'
    else:
        colorText = 'Red'
        passFailMsg = "Failed: " + eclipseCondition + "."
        testMessages.append(passFailMsg)
        testMessages.append(" | ")
        passedText = '\\textcolor{' + colorText + '}{' + "FAILED" + '}'

    # Write some snippets for AutoTex
    snippetName = planet+eclipseCondition + "PassedText"
    snippetContent = passedText
    unitTestSupport.writeTeXSnippet(snippetName, snippetContent, path)

    snippetName = planet+eclipseCondition + "PassFailMsg"
    snippetContent = passFailMsg
    unitTestSupport.writeTeXSnippet(snippetName, snippetContent, path)

    snippetName = eclipseCondition + "error"
    snippetContent = str(errTol)
    unitTestSupport.writeTeXSnippet(snippetName, snippetContent, path)
    print testFailCount, ''.join(testMessages)
    return [testFailCount, ''.join(testMessages)]

if __name__ == "__main__":
    unitEclipse(False, "annular", "earth")
