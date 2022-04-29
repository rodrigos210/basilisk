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

This scenario demonstrates mapping several points on the surface of the Earth.

The script is found in the folder ``basilisk/examples`` and executed by using::

    python3 scenarioGroundMapping.py

The simulation uses :ref:`groundMapping` to check if a spacecraft has access to any of the mapping points defined on the
surface of the Earth. For each mapping point, a :ref:`accessMsgPayload` is output to the :ref:`mappingInstrument` module,
which images the mapping points and sends the simulated data to a :ref:`partitionedStorageUnit`. While this is not
representative of the total amount of data collected during mapping, it does store which points have and have not been
mapped, which is useful for many operations problems. It is suggested that the user adds a :ref:`simpleInstrument` and
:ref:`simpleStorageUnit` if they desire to realistically capture how much data was actually collected.

Illustration of Simulation Results
----------------------------------

::

    show_plots = True

The following plots illustrate the number of collected points and storage level of the data buffer.

.. image:: /_images/Scenarios/scenarioGroundLocationImaging1.svg
   :align: center

.. image:: /_images/Scenarios/scenarioGroundLocationImaging2.svg
   :align: center

.. image:: /_images/Scenarios/scenarioGroundLocationImaging3.svg
   :align: center

.. image:: /_images/Scenarios/scenarioGroundLocationImaging4.svg
   :align: center

"""

#
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Integrated test of the spacecraft(), extForceTorque(), simpleNav(), locationPoint(), groundLocation(),
#           simpleInstrumentController(), simpleInstrument(), partitionedStorageUnit(), and spaceToGroundTransmitter()
#           modules.  Will point a spacecraft axis at two Earth fixed locations and downlink the associated data.
# Author:   Adam Herrmann
# Creation Date:  April 18th, 2022
#

import os
import numpy as np
import math as m

# import general simulation support files
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport  # general support file with common unit test functions
import matplotlib.pyplot as plt
from Basilisk.utilities import macros
from Basilisk.utilities import orbitalMotion

# import simulation related support
from Basilisk.simulation import spacecraft
from Basilisk.utilities import simIncludeGravBody
from Basilisk.simulation import simpleNav
from Basilisk.simulation import groundMapping
from Basilisk.utilities import astroFunctions
from Basilisk.simulation import mappingInstrument
from Basilisk.simulation import extForceTorque
from Basilisk.simulation import partitionedStorageUnit

# import FSW Algorithm related support
from Basilisk.fswAlgorithms import mrpFeedback
from Basilisk.fswAlgorithms import locationPointing

# import message declarations
from Basilisk.architecture import messaging

# attempt to import vizard
from Basilisk.utilities import vizSupport
try:
    from Basilisk.simulation import vizInterface
    vizFound = True
except ImportError:
    vizFound = False

# The path to the location of Basilisk
# Used to get the location of supporting data.
from Basilisk import __path__
bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])


# Plotting functions
def plot_attitude_error(timeLineSet, dataSigmaBR):
    """Plot the attitude result."""
    plt.figure(1)
    fig = plt.gcf()
    ax = fig.gca()
    vectorData = dataSigmaBR
    sNorm = np.array([np.linalg.norm(v) for v in vectorData])
    plt.plot(timeLineSet, sNorm,
             color=unitTestSupport.getLineColor(1, 3),
             )
    plt.xlabel('Time [min]')
    plt.ylabel(r'Attitude Error Norm $|\sigma_{B/R}|$')
    ax.set_yscale('log')

    return


def plot_data_levels(timeLineSet, storageLevel, storedData):
    plt.figure(4)
    plt.plot(timeLineSet, storageLevel / 8E3, label='Data Unit Total Storage Level (KB)')
    plt.plot(timeLineSet, storedData[:, 0] / 8E3, label='Boulder Partition Level (KB)')
    plt.plot(timeLineSet, storedData[:, 1] / 8E3, label='Santiago Partition Level (KB)')
    plt.xlabel('Time (min)')
    plt.ylabel('Data Stored (KB)')
    plt.grid(True)
    plt.legend()

    return


def plot_device_status(timeLineSet, deviceStatus):
    plt.figure(3)
    plt.plot(timeLineSet, deviceStatus)
    plt.xlabel('Time [min]')
    plt.ylabel('Device Status')

    return


def plot_access(timeLineSet, hasAccess):
    plt.figure(2)
    plt.plot(timeLineSet, hasAccess)
    plt.xlabel('Time [min]')
    plt.ylabel('Imaging Target Access')

    return

def generate_mapping_points(num_points, radius):
    """Generates a number of mapping points on the surface of the body using a Fibonnaci sphere
       Algorithm from:
       https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere"""

    points = []
    phi = m.pi * (3. - m.sqrt(5.))  # golden angle in radians

    for i in range(num_points):
        y = 1 - (i / float(num_points - 1)) * 2  # y goes from 1 to -1
        r = m.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = m.cos(theta) * r
        z = m.sin(theta) * r

        points.append(radius*np.array([x, y, z]))

    return np.array(points)


def run(show_plots):
    """
    The scenarios can be run with the followings setups parameters:

    Args:
        show_plots (bool): Determines if the script should display plots

    """

    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()

    # set the simulation time variable used later on
    simulationTime = macros.min2nano(20.)

    #
    #  create the simulation process
    #
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(1.0)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    #
    #   setup the simulation tasks/objects
    #

    # initialize spacecraft object and set properties
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "bsk-Sat"
    # define the simulation inertia
    I = [900., 0., 0.,
         0., 800., 0.,
         0., 0., 600.]
    scObject.hub.mHub = 750.0  # kg - spacecraft mass
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]]  # m - position vector of body-fixed point B relative to CM
    scObject.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I)

    # add spacecraft object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject)

    # clear prior gravitational body and SPICE setup definitions
    gravFactory = simIncludeGravBody.gravBodyFactory()

    # setup Earth Gravity Body
    earth = gravFactory.createEarth()
    earth.isCentralBody = True  # ensure this is the central gravitational body
    mu = earth.mu

    # attach gravity model to spacecraft
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))

    #
    #   initialize Spacecraft States with initialization variables
    #
    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    oe.a = (6378 + 600)*1000.  # meters
    oe.e = 0.01
    oe.i = 63.3 * macros.D2R
    oe.Omega = 88.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 135.3 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    scObject.hub.r_CN_NInit = rN  # m   - r_CN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_CN_N
    scObject.hub.sigma_BNInit = [[0.1], [0.2], [-0.3]]  # sigma_BN_B
    scObject.hub.omega_BN_BInit = [[0.001], [-0.01], [0.03]]  # rad/s - omega_BN_B

    # setup extForceTorque module
    # the control torque is read in through the messaging system
    extFTObject = extForceTorque.ExtForceTorque()
    extFTObject.ModelTag = "externalDisturbance"
    # use the input flag to determine which external torque should be applied
    # Note that all variables are initialized to zero.  Thus, not setting this
    # vector would leave it's components all zero for the simulation.
    scObject.addDynamicEffector(extFTObject)
    scSim.AddModelToTask(simTaskName, extFTObject)

    # add the simple Navigation sensor module.  This sets the SC attitude, rate, position
    # velocity navigation message
    sNavObject = simpleNav.SimpleNav()
    sNavObject.ModelTag = "SimpleNavigation"
    scSim.AddModelToTask(simTaskName, sNavObject)
    sNavObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)

    # Generate the mapping points
    N = 2000
    mapping_points = generate_mapping_points(N, astroFunctions.E_radius*1e3)

    # Create the initial imaging target
    groundMap = groundMapping.GroundMapping()
    groundMap.ModelTag = "groundMapping"
    #groundMap.planetRadius = astroFunctions.E_radius*1e3
    for map_idx in range(N):
        print(mapping_points[map_idx,:].tolist())
        groundMap.addPointToModel(unitTestSupport.np2EigenVectorXd(mapping_points[map_idx,:]))
    #groundMap.minimumElevation = np.radians(10.)
    #groundMap.maximumRange = 1e9
    # groundMap.addSpacecraftToModel(scObject.scStateOutMsg)
    scSim.AddModelToTask(simTaskName, groundMap, ModelPriority=1000)



    #
    #   plot the results
    #
    # timeLineSet = attErrLog.times() * macros.NANO2MIN
    # plt.close("all")  # clears out plots from earlier test runs
    #
    # plot_attitude_error(timeLineSet, dataSigmaBR)
    figureList = {}
    # pltName = fileName + "1"
    # figureList[pltName] = plt.figure(1)
    #
    # plot_access(timeLineSet, hasAccess)
    # pltName = fileName + "2"
    # figureList[pltName] = plt.figure(2)
    #
    # plot_device_status(timeLineSet, deviceCmd)
    # pltName = fileName + "3"
    # figureList[pltName] = plt.figure(3)
    #
    # plot_data_levels(timeLineSet, storageLevel, storedData)
    # pltName = fileName + "4"
    # figureList[pltName] = plt.figure(4)

    if show_plots:
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    return figureList

#
# This statement below ensures that the unit test scrip can be run as a
# stand-along python script
#
if __name__ == "__main__":
    run(
        True  # show_plots
    )