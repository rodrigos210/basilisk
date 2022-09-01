#
#  ISC License
#
#  Copyright (c) 2022, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
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

r"""

Overview
--------

This scenario demonstrates how to set up a spacecraft orbiting Earth subject to atmospheric drag, causing it to
deorbit. This is achieved using the :ref:`exponentialAtmosphere` environment module and the :ref:`dragDynamicEffector`
dynamics module. The simulation is repeatedly stepped on the order of minutes of sim time until the altitude falls
below some threshold.

The script is found in the folder ``basilisk/examples`` and executed by using::

      python3 scenarioDragDeorbit.py

Simulation Scenario Setup Details
---------------------------------

A single simulation with a spacecraft object is created, along with the atmosphere, drag, and gravity models.

The atmosphere model ``ExponentialAtmosphere()`` is initialized as ``atmo``; to set the model to use Earthlike values,
the utility::

    simSetPlanetEnvironment.exponentialAtmosphere(atmo, "earth")

is invoked.

The drag model ``DragDynamicEffector()`` is initialized, then model parameters are set. In this example, the projected
area ``coreParams.projectedArea`` is set to 10 meters squared and the drag coefficient :math:`C_D`
``coreParams.dragCoeff`` is set to 2.2.

Once the models have been added to the simulation task, the atmosphere, drag model, and spacecraft must be linked.
First, the atmosphere model is given the spacecraft state message so it knows the location for which to calculate
atmospheric conditions::

    atmo.addSpacecraftToModel(scObject.scStateOutMsg)

Then, the drag effector is linked to the spacecraft::

    scObject.addDynamicEffector(dragEffector)

The drag model will calculate zero drag unless it is passed atmospheric conditions. To link the atmosphere model to
the drag model::

    dragEffector.atmoDensInMsg.subscribeTo(atmo.envOutMsgs[0])

Illustration of Simulation Results
----------------------------------

The following images illustrate the expected simulation run returns.

The orbit is plotted in the orbital plane:

.. image:: /_images/Scenarios/scenarioDragDeorbit1.svg
   :align: center

The altitude as a function of time is plotted.

.. image:: /_images/Scenarios/scenarioDragDeorbit2.svg
   :align: center

The atmospheric density as a function of altitude is plotted in lin-log space. Since this uses the exponential
atmosphere model, the result should be linear.

.. image:: /_images/Scenarios/scenarioDragDeorbit3.svg
   :align: center

The magnitude of drag force over time is plotted in lin-log space.

.. image:: /_images/Scenarios/scenarioDragDeorbit4.svg
   :align: center

"""

#
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Demonstration of deorbit using exponentialAtmosphere and dragDynamicEffector modules.
# Author:   Mark Stephenson
# Creation Date:  Aug. 31, 2022
#

import os
import numpy as np
import matplotlib.pyplot as plt

# import simulation related support
from Basilisk.simulation import spacecraft
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                simIncludeGravBody, unitTestSupport, vizSupport, simSetPlanetEnvironment)

# import atmosphere and drag modules
from Basilisk.simulation import exponentialAtmosphere, dragDynamicEffector

# always import the Basilisk messaging support
from Basilisk.architecture import messaging

# The path to the location of Basilisk, used to get the location of supporting data
from Basilisk import __path__

bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])


def run(show_plots, initial_alt=250, deorbit_alt=200):
    """
    Initialize a satellite with drag and propagate until it falls below a deorbit altitude. Note that an excessively
    low deorbit_alt can lead to intersection with the Earth prior to deorbit being detected, causing some terms to blow
    up and the simulation to terminate.

    Args:
        show_plots (bool): Toggle plotting on/off
        initial_alt (float): Starting altitude in km
        deorbit_alt (float): Terminal altitude in km

    Returns:
        Dictionary of figure handles
    """
    # Create simulation and dynamics process
    simTaskName = "simTask"
    simProcessName = "simProcess"
    scSim = SimulationBaseClass.SimBaseClass()
    dynProcess = scSim.CreateNewProcess(simProcessName)
    simulationTimeStep = macros.sec2nano(10.)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    # Initialize atmosphere model and add to sim
    atmo = exponentialAtmosphere.ExponentialAtmosphere()
    atmo.ModelTag = "ExpAtmo"
    atmoTaskName = "atmosphere"
    simSetPlanetEnvironment.exponentialAtmosphere(atmo, "earth")
    dynProcess.addTask(scSim.CreateNewTask(atmoTaskName, simulationTimeStep))
    scSim.AddModelToTask(atmoTaskName, atmo)

    # Initialize drag effector and add to sim
    projArea = 10.0  # drag area in m^2
    dragCoeff = 2.2  # drag coefficient
    dragEffector = dragDynamicEffector.DragDynamicEffector()
    dragEffector.ModelTag = "DragEff"
    dragEffectorTaskName = "drag"
    dragEffector.coreParams.projectedArea = projArea
    dragEffector.coreParams.dragCoeff = dragCoeff
    dynProcess.addTask(scSim.CreateNewTask(dragEffectorTaskName, simulationTimeStep))
    scSim.AddModelToTask(dragEffectorTaskName, dragEffector)

    # Set up the spacecraft
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "bsk-Sat"
    scSim.AddModelToTask(simTaskName, scObject)

    # Link spacecraft to drag model
    atmo.addSpacecraftToModel(scObject.scStateOutMsg)
    scObject.addDynamicEffector(dragEffector)
    # and drag model to atmosphere model
    dragEffector.atmoDensInMsg.subscribeTo(atmo.envOutMsgs[0])

    # Set up gravity
    gravFactory = simIncludeGravBody.gravBodyFactory()
    planet = gravFactory.createEarth()
    mu = planet.mu
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))

    # Set up a circular orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    oe.a = planet.radEquator + initial_alt * 1000  # meters
    oe.e = 0.0001
    oe.i = 33.3 * macros.D2R
    oe.Omega = 48.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 85.3 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    oe = orbitalMotion.rv2elem(mu, rN, vN)
    # this stores consistent initial orbit elements; with circular or equatorial orbit, some angles are arbitrary

    # To set the spacecraft initial conditions, the following initial position and velocity variables are set:
    scObject.hub.r_CN_NInit = rN  # m   - r_BN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_BN_N

    # set the simulation time increments
    n = np.sqrt(mu / oe.a / oe.a / oe.a)
    P = 2. * np.pi / n
    orbit_frac = 0.1  # fraction of initial orbit period to step the simulation by
    simulationTime = macros.sec2nano(orbit_frac * P)
    numDataPoints = int(10000 * orbit_frac)  # per orbit_fraction at initial orbit conditions
    samplingTime = unitTestSupport.samplingTime(simulationTime, simulationTimeStep, numDataPoints)

    # Setup data logging before the simulation is initialized
    dataRec = scObject.scStateOutMsg.recorder(samplingTime)
    dataAtmoLog = atmo.envOutMsgs[0].recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, dataRec)
    scSim.AddModelToTask(simTaskName, dataAtmoLog)
    scSim.AddVariableForLogging('DragEff.forceExternal_B', samplingTime, StartIndex=0, StopIndex=2)

    # Vizard Visualization Option
    # ---------------------------
    # If you wish to transmit the simulation data to the United based Vizard Visualization application,
    # then uncomment the following
    # line from the python scenario script.  This will cause the BSK simulation data to
    # be stored in a binary file inside the _VizFiles sub-folder with the scenario folder.  This file can be read in by
    # Vizard and played back after running the BSK simulation.
    # To enable this, uncomment this line:]
    viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObject,
                                              # saveFile=__file__
                                              # liveStream=True
                                              )

    # initialize Simulation
    scSim.InitializeSimulation()

    # Repeatedly step the simulation ahead and break once deorbit altitude encountered
    steps = 0
    deorbited = False
    while not deorbited:
        steps += 1
        scSim.ConfigureStopTime(steps * simulationTime)
        scSim.ExecuteSimulation()
        r = orbitalMotion.rv2elem(mu, dataRec.r_BN_N[-1], dataRec.v_BN_N[-1]).rmag
        alt = (r - planet.radEquator) / 1000  # km
        if alt < deorbit_alt or alt > 1e10:
            deorbited = True

    # retrieve the logged data
    posData = dataRec.r_BN_N
    velData = dataRec.v_BN_N
    dragForce = scSim.GetLogVariableData('DragEff.forceExternal_B')
    denseData = dataAtmoLog.neutralDensity

    figureList = plotOrbits(dataRec.times(), posData, velData, dragForce, denseData, oe, mu, planet)

    if show_plots:
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    return figureList


def plotOrbits(timeAxis, posData, velData, dragForce, denseData, oe, mu, planet):
    # draw the inertial position vector components
    plt.close("all")  # clears out plots from earlier test runs
    figureList = {}

    def register_fig(i):
        pltName = fileName + str(i)
        figureList[pltName] = plt.figure(i)
        fig = plt.gcf()
        ax = fig.gca()
        return fig, ax

    # draw orbit in perifocal frame
    b = oe.a * np.sqrt(1 - oe.e * oe.e)
    plt.figure(1, figsize=np.array((1.0, b / oe.a)) * 4.75, dpi=100)
    plt.axis(np.array([-oe.rApoap, oe.rPeriap, -b, b]) / 1000 * 1.25)
    # draw the planet
    fig, ax = register_fig(1)
    ax.axis('equal')
    planetColor = '#008800'
    planetRadius = planet.radEquator / 1000
    ax.add_artist(plt.Circle((0, 0), planetRadius, color=planetColor))
    # draw the actual orbit
    rData = []
    fData = []
    for idx in range(0, len(posData)):
        oeData = orbitalMotion.rv2elem(mu, posData[idx], velData[idx])
        rData.append(oeData.rmag)
        fData.append(oeData.f + oeData.omega - oe.omega)
    plt.plot(rData * np.cos(fData) / 1000, rData * np.sin(fData) / 1000, color='#aa0000', linewidth=1.0
             )
    plt.xlabel('$i_e$ Cord. [km]')
    plt.ylabel('$i_p$ Cord. [km]')

    # draw altitude as a function of time
    fig, ax = register_fig(2)
    ax.ticklabel_format(useOffset=False, style='plain')
    alt = np.array(rData) / 1000 - planetRadius
    plt.plot(timeAxis * macros.NANO2HOUR, alt)
    plt.xlabel('$t$ [h]')
    plt.ylabel('Alt. [km]')
    pltName = fileName + "2"
    figureList[pltName] = plt.figure(2)

    # draw density as a function of altitude
    fig, ax = register_fig(3)
    plt.semilogy(alt, denseData)
    plt.xlabel('Alt. [km]')
    plt.ylabel('$\\rho$ [kg/m$^2$]')

    # draw drag as a function of time
    fig, ax = register_fig(4)
    plt.semilogy(timeAxis * macros.NANO2HOUR, np.linalg.norm(dragForce[:, 1:], 2, 1))
    plt.xlabel('$t$ [hr]')
    plt.ylabel('$|F_drag|$ [N]')

    return figureList


if __name__ == "__main__":
    run(
        show_plots=True,
        initial_alt=250,
        deorbit_alt=150
    )
