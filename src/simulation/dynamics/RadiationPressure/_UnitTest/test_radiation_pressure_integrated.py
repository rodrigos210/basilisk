
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
# Basilisk Integrated Test of the Solar Radiation Pressure Evaluation
#
# Purpose:  Integrated test of the spacecraftPlus(), gravity modules and the solar
#           radiation pressure modeling.  Currently the cannonball model is only tested.
# Author:   Patrick Kenneally
# Creation Date:  June 11, 2018
#

import numpy as np
import matplotlib.pyplot as plt
import os
from Basilisk import __path__
bskPath = __path__[0]
from Basilisk.simulation import spacecraftPlus, radiationPressure
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                unitTestSupport)
from Basilisk.utilities.simIncludeGravBody import gravBodyFactory
from Basilisk.architecture import messaging2

# uncomment this line is this test is to be skipped in the global unit test run, adjust message as needed
# @pytest.mark.skipif(conditionstring)
# uncomment this line if this test has an expected failure, adjust message as needed
# @pytest.mark.xfail() # need to update how the RW states are defined
# provide a unique test method name, starting with test_
def test_radiationPressureIntegratedTest(show_plots):
    """Module Unit Test"""
    [testResults, testMessage] = radiationPressureIntegratedTest(show_plots)
    assert testResults < 1, testMessage


def radiationPressureIntegratedTest(show_plots):
    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    sim = SimulationBaseClass.SimBaseClass()

    dynProcess = sim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(10.0)
    dynProcess.addTask(sim.CreateNewTask(simTaskName, simulationTimeStep))

    # initialize spacecraftPlus object and set properties
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"
    sim.AddModelToTask(simTaskName, scObject)

    srp = radiationPressure.RadiationPressure() # default model is the SRP_CANNONBALL_MODEL
    srp.area = 1.0
    srp.coefficientReflection = 1.3
    sim.AddModelToTask(simTaskName, srp, None, -1)
    scObject.addDynamicEffector(srp)
    srp.stateInMsg.subscribeTo(scObject.scStateOutMsg)

    # setup Gravity Body
    gravFactory = gravBodyFactory()
    planet = gravFactory.createEarth()
    planet.isCentralBody = True
    mu = planet.mu
    gravFactory.createSun()
    spice_path = bskPath + '/supportData/EphemerisData/'
    gravFactory.createSpiceInterface(spice_path, '2021 MAY 04 07:47:49.965 (UTC)')
    sim.AddModelToTask(simTaskName, gravFactory.spiceObject, None, -1)
    srp.sunEphmInMsg.subscribeTo(gravFactory.spiceObject.planetStateOutMsgs[1])

    # attach gravity model to spaceCraftPlus
    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector(list(gravFactory.gravBodies.values()))

    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    rGEO = 42000. * 1000     # meters
    oe.a = rGEO
    oe.e = 0.00001
    oe.i = 0.0 * macros.D2R
    oe.Omega = 48.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 85.3 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    oe = orbitalMotion.rv2elem(mu, rN, vN)      # this stores consistent initial orbit elements
    # with circular or equatorial orbit, some angles are arbitrary

    #
    #   initialize Spacecraft States with the initialization variables
    #
    scObject.hub.r_CN_NInit = rN  # m   - r_BN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_BN_N

    # set the simulation time
    n = np.sqrt(mu / oe.a / oe.a / oe.a)
    P = 2. * np.pi / n
    simulationTime = macros.sec2nano(P)

    #   Setup data logging before the simulation is initialized
    numDataPoints = 100
    samplingTime = simulationTime // (numDataPoints - 1)
    dataLog = scObject.scStateOutMsg.log()
    earthLog = gravFactory.spiceObject.planetStateOutMsgs[0].log()
    logTaskName = "logTask"
    dynProcess.addTask(sim.CreateNewTask(logTaskName, samplingTime))
    sim.AddModelToTask(logTaskName, dataLog)
    sim.AddModelToTask(logTaskName, earthLog)

    #
    #   initialize Simulation:  This function clears the simulation log, and runs the self_init()
    #   cross_init() and reset() routines on each module.
    #   If the routine InitializeSimulationAndDiscover() is run instead of InitializeSimulation(),
    #   then the all messages are auto-discovered that are shared across different BSK threads.
    #
    sim.InitializeSimulationAndDiscover()

    #
    #   configure a simulation stop time time and execute the simulation run
    #
    sim.ConfigureStopTime(simulationTime)
    sim.ExecuteSimulation()

    # unload spice kernels
    gravFactory.unloadSpiceKernels()

    #
    #   retrieve the logged data
    #
    earthEphm = earthLog.PositionVector
    posData = dataLog.r_BN_N

    pos_rel_earth = posData[:, 0:3] - earthEphm[:, 0:3]
    testFailCount = 0  # zero unit test result counter
    testMessages = []  # create empty array to store test log messages

    numTruthPoints = 10
    skipValue = int(len(pos_rel_earth) / (numTruthPoints - 1))
    pos_rel_earth_parse = pos_rel_earth[::skipValue]
    print("earth pos:")
    print(pos_rel_earth_parse)

    # true position for un perturbed 2 body GEO orbit with cannonball SRP
    true_pos = np.array([[-2.18197848e+07,  3.58872415e+07,  0.00000000e+00]
                        ,[-3.97753183e+07,  1.34888783e+07, -7.34006882e+01]
                        ,[-3.91389821e+07, -1.52401394e+07, -3.06392342e+02]
                        ,[-2.01837904e+07, -3.68366949e+07, -6.37825333e+02]
                        ,[ 8.21685433e+06, -4.11950336e+07, -9.13451012e+02]
                        ,[ 3.27532829e+07, -2.63023741e+07, -9.57894936e+02]
                        ,[ 4.19944582e+07,  9.02560169e+05, -6.78189034e+02]
                        ,[ 3.15827901e+07,  2.76842665e+07, -1.40584587e+02]
                        ,[ 6.38612441e+06,  4.15047641e+07,  4.29547195e+02]
                        ,[-2.18007315e+07,  3.58874482e+07,  7.40749634e+02]])

    # compare the results to the truth values
    accuracy = 1.0  # meters

    testFailCount, testMessages = unitTestSupport.compareArray(
        true_pos, pos_rel_earth_parse, accuracy, "r_BN_N Vector",
        testFailCount, testMessages)

    #   print out success message if no error were found
    if testFailCount == 0:
        print("PASSED ")
    else:
        print(testFailCount)
        print(testMessages)

    plt.close("all")  # clears out plots from earlier test runs
    plt.figure(1)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='plain')
    for idx in range(0, 3):
        plt.plot(dataLog.times() * macros.NANO2SEC / P, pos_rel_earth[:, idx] / 1000.,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label='$r_{BN,' + str(idx) + '}$')

    plt.legend(loc='lower right')
    plt.xlabel('Time [orbits]')
    plt.ylabel('Inertial Position [km]')
    plt.title('Position Relative To Earth')
    if show_plots:
        plt.show()
        plt.close('all')

    figureList = {}
    fileName = os.path.basename(os.path.splitext(__file__)[0])
    pltName = fileName + "srp_integrated"
    figureList[pltName] = plt.figure(1)

    return testFailCount, testMessages


#
# This statement below ensures that the unit test script can be run as a stand-alone python script
#
if __name__ == "__main__":
    radiationPressureIntegratedTest(True)
