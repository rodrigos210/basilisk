#
#  ISC License
#
#  Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
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

.. figure:: /_images/static/Vizard1.jpg
   :align: center

   Illustration of Vizard showing a custom spacecraft camera view.

Overview
--------

This scenario demonstrates how instantiate a visualization interface. This includes setting camera
parameters and capture rates. This stems for an attitude detumble scenario, but focuses on
pointing towards a celestial body in order to display the visualization Vizard, and show
the camera capabilities.

The script is found in the folder ``src/examples`` and executed by using::

    python3 scenarioVizPoint.py

When the simulation completes 3 plots are shown for the MRP attitude history, the rate
tracking errors, as well as the control torque vector.  The ``run()`` method is setup to write out the
Vizard data file to sub-folder ``_VizFiles/scenarioVizPoint_UnityViz.bin``.  By running :ref:`Vizard <vizard>`
and playing back this data file you will see the custom camera view that is created as
illustrated in the Vizard snapshot above.

The simulation layout is identical the the :ref:`scenarioAttitudeFeedback` scenario when it comes to FSW modules
The spacecraft starts in a tumble and controls it's rate as well as points to the Earth.

Two mission scenarios can be simulated.
The first one mimics the DSCOVR mission spacecraft and its EPIC camera pointing towards Earth.
The second simulates a spacecraft orbiting about Mars. The attitude results are the same as
the attitude feedback scenario, and pictured in the following plots. The differences lies in
where they are pointing.

.. image:: /_images/Scenarios/scenarioVizPoint1.svg
   :align: center

.. image:: /_images/Scenarios/scenarioVizPoint2.svg
   :align: center

.. image:: /_images/Scenarios/scenarioVizPoint3.svg
   :align: center

In each case a spacecraft fixed camera is simulated.  This is done by creating a camera
configuration message called ``camera_config_data``.  The :ref:`vizInterface` module
searches for a message with this name by default.  If it exists, the camera information
is read in and sent across to Vizard to render out that camera view point image.  If the
camera message should be written to another message name, then the :ref:`vizInterface` parameter
``cameraConfInMsgName`` can be set to this new name.

DSCOVR Mission Setup
--------------------

The first setup has the spacecraft pointing to Earth, from a distant, L1 vantage point.
The scenario controls the spacecraft attitude to Earth pointing mode, and snaps pictures at
a defined rate.
This camera parameters are taken from NASA's `EPIC <https://epic.gsfc.nasa.gov>`__ camera website on the date
2018 OCT 23 04:35:25.000 (UTC time).
In this setup the pointing needs to be set to Earth, given it's position.

Mars Orbit Setup
----------------

The second control scenario points the spacecraft towards Mars on a Mars orbit.

"""


#
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Integrated test of the vizInterface, spacecraftPlus, simple_nav, MRP_Feedback. and inertial3D modules.
# Illustrates a spacecraft pointing with visualization.
# Author:   Thibaud Teil
# Creation Date:  Nov. 01, 2018
#

import os
import numpy as np
from Basilisk import __path__
bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])
fileNamePath = os.path.abspath(__file__)


# import general simulation support files
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport  # general support file with common unit test functions
import matplotlib.pyplot as plt
from Basilisk.utilities import macros, orbitalMotion
from Basilisk.utilities import RigidBodyKinematics as rbk

# import simulation related support
from Basilisk.simulation import spacecraftPlus
from Basilisk.simulation import extForceTorque
from Basilisk.utilities import simIncludeGravBody
from Basilisk.simulation import simple_nav, simFswInterfaceMessages

# import FSW Algorithm related support
from Basilisk.fswAlgorithms import MRP_Feedback
from Basilisk.fswAlgorithms import inertial3D
from Basilisk.fswAlgorithms import attTrackingError

# import message declarations
from Basilisk.fswAlgorithms import fswMessages

# attempt to import vizard
from Basilisk.utilities import vizSupport


def run(show_plots, missionType, saveVizardFile):
    """
    At the end of the python script you can specify the following example parameters.

    Args:
        show_plots (bool): Determines if the script should display plots
        missionType (str):

            ===========  ==================================
            String       Definition
            ===========  ==================================
            'dscovr'     Simulates the NASA DSCOVR mission
            'marsOrbit'  Simulates an orbit about Mars
            ===========  ==================================

        saveVizardFile (bool): Flag to save off the Vizard data file

    """

    missionOptions = ['dscovr', 'marsOrbit'];
    if missionType not in missionOptions:
        print("ERROR: scenarioVizPoint received the wrong mission type " + missionType
              + ". Options include " + str(missionOptions))
        exit(1)

    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()

    # set the simulation time variable used later on
    simulationTime = macros.min2nano(10.)

    #
    #  create the simulation process
    #
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(.1)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    # if this scenario is to interface with the BSK Viz, uncomment the following lines
    if missionType ==  'dscovr':
        # setup Grav Bodies and Spice messages
        gravFactory = simIncludeGravBody.gravBodyFactory()
        bodies = gravFactory.createBodies(['earth', 'sun'])
        bodies['earth'].isCentralBody = True  # ensure this is the central gravitational body
        spiceObject, epochMsg = gravFactory.createSpiceInterface(bskPath + '/supportData/EphemerisData/',
                                                       '2018 OCT 23 04:35:25.000 (UTC)',
                                                        epochInMsgName = 'simEpoch')
        unitTestSupport.setMessage(scSim.TotalSim,
                                   simProcessName,
                                   spiceObject.epochInMsgName,
                                   epochMsg)

        gravFactory.spiceObject.zeroBase = 'earth'
        scSim.AddModelToTask(simTaskName, spiceObject)
        # Setup Camera.
        cameraConfig = simFswInterfaceMessages.CameraConfigMsg()
        cameraConfig.cameraID = 1
        cameraConfig.renderRate = int(59 * 1E9)  # in ns
        cameraConfig.sigma_CB = [0, 0, 1]
        cameraConfig.cameraPos_B = [5000. * 1E-3, 0., 0.]  # in meters
        cameraConfig.fieldOfView = 0.62  # in degrees
        cameraConfig.sensorSize = [30.72 , 30.72 ]  # in mm
        cameraConfig.resolution = [2048, 2048]  # in pixels
        cameraMsgName = 'camera_config_data'
        cameraMessageSize = cameraConfig.getStructSize()
        scSim.TotalSim.CreateNewMessage(simProcessName, cameraMsgName, cameraMessageSize, 2, "CameraConfigMsg")
        scSim.TotalSim.WriteMessageData(cameraMsgName, cameraMessageSize, 0, cameraConfig)
    else:
        simulationTime = macros.min2nano(6.25)
        gravFactory = simIncludeGravBody.gravBodyFactory()
        # setup Earth Gravity Body
        mars = gravFactory.createMarsBarycenter()
        mars.isCentralBody = True  # ensure this is the central gravitational body
        mu = mars.mu
        cameraConfig = simFswInterfaceMessages.CameraConfigMsg()
        cameraConfig.cameraID = 1
        cameraConfig.renderRate = int(30 * 1E9)  # in ns
        cameraConfig.sigma_CB = [0, 0, 1]
        cameraConfig.cameraPos_B = [5000. * 1E-3, 0., 0.]  # in meters
        cameraConfig.fieldOfView = 50.  # in degrees
        cameraConfig.sensorSize = [10. , 10. ]  # in mm
        cameraConfig.resolution = [512, 512]  # in pixels
        cameraMsgName = 'camera_config_data'
        cameraMessageSize = cameraConfig.getStructSize()
        scSim.TotalSim.CreateNewMessage(simProcessName, cameraMsgName, cameraMessageSize, 2, "CameraConfigMsg")
        scSim.TotalSim.WriteMessageData(cameraMsgName, cameraMessageSize, 0, cameraConfig)

    #
    #   setup the simulation tasks/objects
    #
    # initialize spacecraftPlus object and set properties
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"
    # define the simulation inertia
    I = [900., 0., 0.,
         0., 800., 0.,
         0., 0., 600.]
    scObject.hub.mHub = 750.0  # kg - spacecraft mass
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]]  # m - position vector of body-fixed point B relative to CM
    scObject.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I)
    # attach gravity model to spaceCraftPlus
    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector(list(gravFactory.gravBodies.values()))

    # add spacecraftPlus object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject)

    # setup extForceTorque module
    # the control torque is read in through the messaging system
    extFTObject = extForceTorque.ExtForceTorque()
    extFTObject.ModelTag = "externalDisturbance"
#    extFTObject.extTorquePntB_B = [[0.25], [-0.25], [0.1]]
    scObject.addDynamicEffector(extFTObject)
    scSim.AddModelToTask(simTaskName, extFTObject)

    # add the simple Navigation sensor module.  This sets the SC attitude, rate, position
    # velocity navigation message
    sNavObject = simple_nav.SimpleNav()
    sNavObject.ModelTag = "SimpleNavigation"
    scSim.AddModelToTask(simTaskName, sNavObject)

    #
    #   setup the FSW algorithm tasks
    #

    if missionType == 'dscovr':
        # Set up pointing frame and camera position given the initial conditions on Oct 23rd 2018 4:35 UTC
        # and the DDSCOVR data
        earthVec = np.array([129559501208.24178, 68180766143.44236,29544768114.76163])
        normal = np.array([0.,0.,1.])
        sunVec = np.array([-32509693.54023, 1002377617.77831, 423017670.86700])
        dscovrEarthDistance = 1405708000.
        SEVangle = 7.28

        r_sc = dscovrEarthDistance * (sunVec-earthVec)/np.linalg.norm(sunVec-earthVec)
        v_sc = np.zeros(3)

        b1_n = -(sunVec-earthVec)/np.linalg.norm(sunVec-earthVec)
        b3_n = (normal - np.dot(normal, b1_n)*b1_n)/np.linalg.norm(normal - np.dot(normal, b1_n)*b1_n)
        assert np.abs(np.dot(b1_n, b3_n)) < 1E-10, 'Wrong dcm'
        b2_n = np.cross(b3_n, b1_n)/np.linalg.norm( np.cross(b3_n, b1_n))
        NB = np.zeros([3,3])
        NB[:,0] = b1_n
        NB[:, 1] = b2_n
        NB[:, 2] = b3_n

        earthPoint = rbk.C2MRP(NB.T)
    else:
        earthPoint = np.array([0.,0.,0.1])

    # setup inertial3D guidance module
    inertial3DConfig = inertial3D.inertial3DConfig()
    inertial3DWrap = scSim.setModelDataWrap(inertial3DConfig)
    inertial3DWrap.ModelTag = "inertial3D"
    scSim.AddModelToTask(simTaskName, inertial3DWrap, inertial3DConfig)
    inertial3DConfig.sigma_R0N = earthPoint.tolist()  # set the desired inertial orientation
    inertial3DConfig.outputDataName = "guidanceInertial3D"

    # setup the attitude tracking error evaluation module
    attErrorConfig = attTrackingError.attTrackingErrorConfig()
    attErrorWrap = scSim.setModelDataWrap(attErrorConfig)
    attErrorWrap.ModelTag = "attErrorInertial3D"
    scSim.AddModelToTask(simTaskName, attErrorWrap, attErrorConfig)
    attErrorConfig.outputDataName = "attErrorInertial3DMsg"
    attErrorConfig.inputRefName = inertial3DConfig.outputDataName
    attErrorConfig.inputNavName = sNavObject.outputAttName

    # setup the MRP Feedback control module
    mrpControlConfig = MRP_Feedback.MRP_FeedbackConfig()
    mrpControlWrap = scSim.setModelDataWrap(mrpControlConfig)
    mrpControlWrap.ModelTag = "MRP_Feedback"
    scSim.AddModelToTask(simTaskName, mrpControlWrap, mrpControlConfig)
    mrpControlConfig.inputGuidName = attErrorConfig.outputDataName
    mrpControlConfig.vehConfigInMsgName = "vehicleConfigName"
    mrpControlConfig.outputDataName = extFTObject.cmdTorqueInMsgName
    mrpControlConfig.K = 3.5
    mrpControlConfig.Ki = -1  # make value negative to turn off integral feedback
    mrpControlConfig.P = 30.0
    mrpControlConfig.integralLimit = 2. / mrpControlConfig.Ki * 0.1
#    mrpControlConfig.knownTorquePntB_B = [0.25, -0.25, 0.1]

    #
    #   Setup data logging before the simulation is initialized
    #
    numDataPoints = 100
    samplingTime = simulationTime // (numDataPoints - 1)
    scSim.TotalSim.logThisMessage(mrpControlConfig.outputDataName, samplingTime)
    scSim.TotalSim.logThisMessage(attErrorConfig.outputDataName, samplingTime)
    scSim.TotalSim.logThisMessage(sNavObject.outputTransName, samplingTime)

    #
    # create simulation messages
    #

    # create the FSW vehicle configuration message
    vehicleConfigOut = fswMessages.VehicleConfigFswMsg()
    vehicleConfigOut.ISCPntB_B = I  # use the same inertia in the FSW algorithm as in the simulation
    unitTestSupport.setMessage(scSim.TotalSim,
                               simProcessName,
                               mrpControlConfig.vehConfigInMsgName,
                               vehicleConfigOut)

    #
    #   set initial Spacecraft States
    #
    # setup the orbit using classical orbit elements
    # for orbit around Earth
    if missionType == 'marsOrbit':
        oe = orbitalMotion.ClassicElements()
        oe.a = 16000000 # meters
        oe.e = 0.1
        oe.i = 10. * macros.D2R
        oe.Omega = 25. * macros.D2R
        oe.omega = 10. * macros.D2R
        oe.f = 160. * macros.D2R
        rN, vN = orbitalMotion.elem2rv(mu, oe)
    else:
        rN = r_sc
        vN = v_sc
    scObject.hub.r_CN_NInit = unitTestSupport.np2EigenVectorXd(rN)  # m   - r_CN_N
    scObject.hub.v_CN_NInit = unitTestSupport.np2EigenVectorXd(vN)  # m/s - v_CN_N
    scObject.hub.sigma_BNInit = [[0.1], [0.2], [-0.3]]  # sigma_BN_B
    scObject.hub.omega_BN_BInit = [[0.001], [-0.01], [0.03]]  # rad/s - omega_BN_B

    #
    #   initialize Simulation
    #
    if saveVizardFile:
        vizSupport.enableUnityVisualization(scSim, simTaskName, simProcessName,
                                            saveFile=fileNamePath, gravBodies=gravFactory)
    scSim.InitializeSimulationAndDiscover()

    #
    #   configure a simulation stop time time and execute the simulation run
    #
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()

    #
    #   retrieve the logged data
    #
    dataLr = scSim.pullMessageLogData(mrpControlConfig.outputDataName + ".torqueRequestBody", list(range(3)))
    dataSigmaBR = scSim.pullMessageLogData(attErrorConfig.outputDataName + ".sigma_BR", list(range(3)))
    dataOmegaBR = scSim.pullMessageLogData(attErrorConfig.outputDataName + ".omega_BR_B", list(range(3)))
    dataPos = scSim.pullMessageLogData(sNavObject.outputTransName + ".r_BN_N", list(range(3)))
    np.set_printoptions(precision=16)


    #
    #   plot the results
    #
    plt.close("all")  # clears out plots from earlier test runs
    plt.figure(1)
    for idx in range(1, 4):
        plt.plot(dataSigmaBR[:, 0] * macros.NANO2MIN, dataSigmaBR[:, idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\sigma_' + str(idx) + '$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel(r'Attitude Error $\sigma_{B/R}$')
    figureList = {}
    pltName = fileName + "1"
    figureList[pltName] = plt.figure(1)

    plt.figure(2)
    for idx in range(1, 4):
        plt.plot(dataLr[:, 0] * macros.NANO2MIN, dataLr[:, idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label='$L_{r,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('Control Torque $L_r$ [Nm]')
    pltName = fileName + "2"
    figureList[pltName] = plt.figure(2)

    plt.figure(3)
    for idx in range(1, 4):
        plt.plot(dataOmegaBR[:, 0] * macros.NANO2MIN, dataOmegaBR[:, idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\omega_{BR,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('Rate Tracking Error [rad/s] ')
    pltName = fileName + "3"
    figureList[pltName] = plt.figure(3)

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
        True,               # show_plots
        'dscovr',           # missionType: dscovr or marsOrbit
        True                # saveVizardFile: flag to save the Vizard data file
    )
