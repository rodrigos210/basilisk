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
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Integrated test illustrating how to use a world magnetic model (WMM) for spacecraft about Earth.
# Author:   Hanspeter Schaub
# Creation Date:  March 16, 2019
#

import os, inspect
import numpy as np

import matplotlib.pyplot as plt
# The path to the location of Basilisk
# Used to get the location of supporting data.
fileName = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(fileName))

bskPath = path.split('src')[0]

# import simulation related support
from Basilisk.simulation import spacecraftPlus
from Basilisk.simulation import magneticFieldWMM
# general support file with common unit test functions
# import general simulation support files
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                simIncludeGravBody, unitTestSupport)


#attempt to import vizard
from Basilisk.utilities import vizSupport


## \defgroup scenarioMagneticFieldWMM
## @{
## Demonstration of setting up a World Magnetic Model (WMM) for an Earth simulation
#
# Orbital Simulation Including World Magnetic Model (WMM) {#scenarioMagneticFieldWMM}
# ====
#
# Scenario Description
# -----
# This script sets up a 3-DOF spacecraft which is orbiting the with a magnetic field model.  This scenario
# is similar to the centered dipole model
# [scenarioMagneticFieldCenteredDipole.py](@ref scenarioMagneticFieldCenteredDipole), but here
# the World Magnetic Model (WMM) is employed.  This model is specific to Earth and not suitable for
# other planets. The purpose
# is to illustrate how to create and setup the WMM magnetic field, as well as determine the
# magnetic field at a spacecraft location.  The orbit setup is similar to that used in
# [scenarioBasicOrbit.py](@ref scenarioBasicOrbit).  The scenarios can be run with the followings setups
# parameters:
# Setup | orbitCase
# ----- | -------------------
# 1     | circular
# 2     | elliptical
#
# To run the default scenario 1 call the python script through
#
#       python scenarioMagneticFieldWMM.py
#
#
# Simulation Scenario Setup Details
# -----
# The simulation layout is shown in the following illustration.  A single simulation process is created
# which contains the spacecraft object.  The spacecraft state message is connected to the magnetic field
# module which outputs the local magnetic field in inertial frame components.
# ![Simulation Flow Diagram](Images/doc/test_scenario_MagneticFieldWMM.svg "Illustration")
#
# When the simulation completes 2 plots are shown for each case.  One plot always shows
# the inertial position vector components, while the second plot shows the local magnetic field
# vector components with respect to the inertial frame.
#
# The dynamics simulation is setup using a SpacecraftPlus() module.  The magnetic field module is created using:
#~~~~~~~~~~~~~~~~~{.py}
#     magModule = magneticFieldWMM.MagneticFieldWMM()
#     magModule.ModelTag = "WMM"
#     magModule.dataPath = bskPath + '/supportData/MagneticField/'
#~~~~~~~~~~~~~~~~~
# As this model is specific to Earth, there are no parameters to set of tune.  Rather, the `WMM.COF` WMM coefficient
# file is loaded
# from the `dataPath` variable that is setup above.
#
# The default
# planet's position vector is assumed to be the inertial frame origin and an identity orientation matrix.
# If a different planet state message is required this can be specified through the optional input message
#~~~~~~~~~~~~~~~~~{.py}
#     magModule.planetPosInMsgName = "planet_state_ephemeris_msg"
#~~~~~~~~~~~~~~~~~
#
# The magnetic field module can produce the magnetic field for a vector of spacecraft locations, not just for a
# single spacecraft.  Let `scObject` be an instance of SpacecraftPlus(), then the spacecraft state output message
# is added to the magnetic field module through
#~~~~~~~~~~~~~~~~~{.py}
#     magModule.addSpacecraftToModel(scObject.scStateOutMsgName)
#~~~~~~~~~~~~~~~~~
# Note that this command can be repeated if the magnetic field should be evaluated for different spacecraft.
#
# Next, this module is attached to the simulation process with
#~~~~~~~~~~~~~~~~~{.py}
#   scSim.AddModelToTask(simTaskName, magModule)
#~~~~~~~~~~~~~~~~~
#
# The WMM module requires an epoch time to determine the magnetic field.  If this is not set, then the BSK
# default epoch time is used.  To set a general epoch time, the module can read in an epoch message with a
# gregorian UTC date.  This is set using the following code:
#~~~~~~~~~~~~~~~~~{.py}
#     magModule.epochInMsgName = "simEpoch"
#     epochMsg = unitTestSupport.timeStringToGregorianUTCMsg('2019 June 27, 10:23:0.0 (UTC)')
#     unitTestSupport.setMessage(scSim.TotalSim,
#                                simProcessName,
#                                magModule.epochInMsgName,
#                                epochMsg)
#~~~~~~~~~~~~~~~~~~~
# The WMM model is driven of a time variable that is a decimal year value.  The module can set this as well by
# specifying the module parameter `epochDateFractionalYear`.  However, note that if the epoch message is specified, the message
# information is used instead of the `epochDateFractionalYear` variable.
#
# Every time a spacecraft is added to the magnetic field module, an automated output message name is created.
# For `magModule` is "CenteredDipole_0_data" as the ModelTag string is `CenteredDipole` and the spacecraft number is 0.
# This output name is created in the  `addSpacecraftToModel()` function.
# However, if the default output name is used for the second planetary magnetic field model, then both module share
# the same output name and one will overwrite the others output.
#
# The reach of the magnetic field model is specified through the module variables `envMinReach` and `envMaxReach`.
# Their default values are -1 which turns off this feature, giving the magnetic field evaluation infinite reach.
# In the elliptical Earth scenario we set a mininum and maximum applicability of this WMM model using:
# ~~~~~~~~~~~~~~~~~{.py}
#   magModule.envMinReach = 10000*1000.
#   magModule.envMaxReach = 20000*1000.
# ~~~~~~~~~~~~~~~~~
#
# Setup 1
# -----
#
# Which scenario is run is controlled at the bottom of the file in the code
# ~~~~~~~~~~~~~{.py}
# if __name__ == "__main__":
#  run(
#         True,          # show_plots
#         'circular'   # orbit Case (circular, elliptical)
#     )
# ~~~~~~~~~~~~~
#
# This scenario places the spacecraft about the Earth in a circular LEO orbit.  The
# resulting position coordinates and magnetic field components are shown below.
# ![Orbit Radius History](Images/Scenarios/scenarioMagneticFieldWMM1circular.svg "radius history")
# ![Magnetic Field Illustration](Images/Scenarios/scenarioMagneticFieldWMM2circular.svg "Magnetic Field Illustration")
#
# Setup 2
# -----
#
# The next scenario is run by changing the bottom of the file in the scenario code to read
# ~~~~~~~~~~~~~{.py}
# if __name__ == "__main__":
#  run(
#         True,          # show_plots
#         'elliptical'  # orbit Case (circular, elliptical)
#     )
# ~~~~~~~~~~~~~
# This case illustrates an elliptical Earth orbit where we only use the WMM model between a
# lower and upper radius limit.
# The
# resulting position coordinates and magnetic field illustrations are shown below.
# ![Orbit Radius History](Images/Scenarios/scenarioMagneticFieldWMM1elliptical.svg "radius history")
# ![WMM Magnetic Field Illustration with limits in radius regions](Images/Scenarios/scenarioMagneticFieldWMM2elliptical.svg "Magnetic Field Illustration")
#
## @}
def run(show_plots, orbitCase):
    '''Call this routine directly to run the tutorial scenario.'''


    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()
    scSim.TotalSim.terminateSimulation()

    #
    #  create the simulation process
    #
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(60.)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    #
    #   setup the simulation tasks/objects
    #

    # initialize spacecraftPlus object and set properties
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"

    # add spacecraftPlus object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject)

    # setup Gravity Body
    gravFactory = simIncludeGravBody.gravBodyFactory()
    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    mu = planet.mu
    req = planet.radEquator

    # attach gravity model to spaceCraftPlus
    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector(gravFactory.gravBodies.values())


    # create the magnetic field
    magModule = magneticFieldWMM.MagneticFieldWMM()
    magModule.ModelTag = "WMM"
    magModule.dataPath = bskPath + '/supportData/MagneticField/'

    # set the minReach and maxReach values if on an elliptic orbit
    if orbitCase == 'elliptical':
        magModule.envMinReach = 10000*1000.
        magModule.envMaxReach = 20000*1000.

    # set epoch date/time message
    magModule.epochInMsgName = "simEpoch"
    epochMsg = unitTestSupport.timeStringToGregorianUTCMsg('2019 June 27, 10:23:0.0 (UTC)')
    unitTestSupport.setMessage(scSim.TotalSim,
                               simProcessName,
                               magModule.epochInMsgName,
                               epochMsg)

    # add spacecraft to the magnetic field module so it can read the sc position messages
    magModule.addSpacecraftToModel(scObject.scStateOutMsgName)  # this command can be repeated if multiple

    # add the magnetic field module to the simulation task stack
    scSim.AddModelToTask(simTaskName, magModule)

    #
    #   setup orbit and simulation time
    #
    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    rPeriapses = req*1.1     # meters
    if orbitCase == 'circular':
        oe.a = rPeriapses
        oe.e = 0.0000
    elif orbitCase == 'elliptical':
        rApoapses = req*3.5
        oe.a = (rPeriapses + rApoapses) / 2.0
        oe.e = 1.0 - rPeriapses / oe.a
    else:
        print "Unsupported orbit type " + orbitCase + " selected"
        exit(1)
    oe.i = 85.0 * macros.D2R
    oe.Omega = 48.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 85.3 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    # next lines stores consistent initial orbit elements
    # with circular or equatorial orbit, some angles are arbitrary
    oe = orbitalMotion.rv2elem(mu, rN, vN)

    #
    #   initialize Spacecraft States with the initialization variables
    #
    scObject.hub.r_CN_NInit = unitTestSupport.np2EigenVectorXd(rN)  # m   - r_BN_N
    scObject.hub.v_CN_NInit = unitTestSupport.np2EigenVectorXd(vN)  # m/s - v_BN_N

    # set the simulation time
    n = np.sqrt(mu / oe.a / oe.a / oe.a)
    P = 2. * np.pi / n
    simulationTime = macros.sec2nano(1. * P)

    #
    #   Setup data logging before the simulation is initialized
    #
    numDataPoints = 100
    samplingTime = simulationTime / (numDataPoints - 1)
    scSim.TotalSim.logThisMessage(magModule.envOutMsgNames[0], samplingTime)
    scSim.TotalSim.logThisMessage(scObject.scStateOutMsgName, samplingTime)

    # if this scenario is to interface with the BSK Viz, uncomment the following line
    # vizSupport.enableUnityVisualization(scSim, simTaskName, simProcessName, gravBodies=gravFactory, saveFile=fileName)

    #
    #   initialize Simulation:  This function clears the simulation log, and runs the self_init()
    #   cross_init() and reset() routines on each module.
    #   If the routine InitializeSimulationAndDiscover() is run instead of InitializeSimulation(),
    #   then the all messages are auto-discovered that are shared across different BSK threads.
    #
    scSim.InitializeSimulationAndDiscover()

    #
    #   configure a simulation stop time time and execute the simulation run
    #
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()

    #
    #   retrieve the logged data
    #
    magData = scSim.pullMessageLogData(magModule.envOutMsgNames[0] + '.magField_N', range(3))
    posData = scSim.pullMessageLogData(scObject.scStateOutMsgName + '.r_BN_N', range(3))

    np.set_printoptions(precision=16)

    #
    #   plot the results
    #
    # draw the inertial position vector components
    plt.close("all")  # clears out plots from earlier test runs

    plt.figure(1)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    rData = []
    for idx in range(0, len(posData)):
        rMag = np.linalg.norm(posData[idx, 1:4])
        rData.append(rMag / 1000.)
    plt.plot(posData[:, 0] * macros.NANO2SEC / P, rData, color='#aa0000')
    if orbitCase == 'elliptical':
        plt.plot(posData[:, 0] * macros.NANO2SEC / P, [magModule.envMinReach/1000.]*len(rData), color='#007700', dashes=[5, 5, 5, 5])
        plt.plot(posData[:, 0] * macros.NANO2SEC / P, [magModule.envMaxReach / 1000.] * len(rData),
                 color='#007700', dashes=[5, 5, 5, 5])

    plt.xlabel('Time [orbits]')
    plt.ylabel('Radius [km]')
    plt.ylim(min(rData)*0.9, max(rData)*1.1)
    figureList = {}
    pltName = fileName + "1" + orbitCase
    figureList[pltName] = plt.figure(1)

    plt.figure(2)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    for idx in range(1, 4):
        plt.plot(magData[:, 0] * macros.NANO2SEC / P, magData[:, idx] *1e9,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label='$B\_N_{' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [orbits]')
    plt.ylabel('Magnetic Field [nT]')
    pltName = fileName + "2" + orbitCase
    figureList[pltName] = plt.figure(2)


    if show_plots:
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    return magData, figureList



#
# This statement below ensures that the unit test scrip can be run as a
# stand-along python script
#
if __name__ == "__main__":
    run(
        True,          # show_plots
        'elliptical',  # orbit Case (circular, elliptical)
    )
