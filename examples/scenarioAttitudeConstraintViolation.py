#
#  ISC License
#
#  Copyright (c) 2021, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
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

Demonstrates how to set up conical keep-in and keep-out constraints for a spacecraft.
This script sets up a 6-DOF spacecraft which is orbiting the Earth, in the presence of the Sun.
The spacecraft is modelled according to the specifics of the Bevo-2 satellite, that has a sensitive
star tracker aligned with the x body axis and two sun sensors aligned with the y and z body axes.
The goal is to illustrate how to set up a Basilisk simulation to check whether certain slew 
maneuvers cause violations in the positional constraints of the spacecraft.

The script is found in the folder ``basilisk/examples`` and executed by using::

      python3 scenarioAttitudeConstraintViolation.py

The main simulation layout is the same as in :ref:`scenarioAttitudeFeedbackRW`, shown in the following illustration.  
A single simulation process is created which contains both the spacecraft simulation modules, as well as the Flight 
Software (FSW) algorithm modules.

.. image:: /_images/static/test_scenarioAttitudeFeedbackRW.svg
   :align: center

The spacecraft mass, inertia, and control gains in this example script have been designed to match the performance 
of the Bevo 2 satellite. To better understand how to add RW to the Spacecraft Simulation to perform slew maneuvers
from an initial to a final inertially fixed attitude, the reader is redirected to :ref:`scenarioAttitudeFeedbackRW`
where this process is explained in the details.

This script uses :ref:`simIncludeGravBody` to add Earth and Sun to the simulation. The method ``createSpiceInterface``
to create Spice modules for the celestial bodies and generate the respective Spice planet state messages.
The :ref:`boreAngCalc` module is set up for each of the instruments that have geometric angular constraints. This module 
subscribes to the :ref:`SCStatesMsgPayload` and :ref:`SpicePlanetStateMsgPayload` of the bright object (the Sun) and
returns a :ref:`BoreAngleMsgPayload` that contains the angle between the bright object and the direction of the 
boresight vector of the instrument.

Illustration of Simulation Results
----------------------------------

Each run of the script produces 6 figures. Figures 1-4 report, respectively, attitude error, RW motor torque, rate 
tracking error, and RW speed. These plots are only relevant to the spacecraft / RW dynamics. Figures 5 and 6 
show the angle between the boresight vector of the star tracker and the Sun (fig. 5), and of the sun sensor(s) and
the Sun (fig. 6). Each plot features a dashed line that represents an angular threshold for that specific instrument.
Opaque red zones in each plot represent the portions of each maneuver where that constraint has been violated.

Each plot describes a slew maneuver performed from an initial inertial attitude :math:`\sigma_{\mathcal{B/N},i}` to
a final inertial attitude :math:`\sigma_{\mathcal{B/N},f}`, both of which are set for each case to show the desired
constraint violation.

::

    show_plots = True, use2SunSensors = False, starTrackerFov = 20, sunSensorFov = 70, attitudeSetCase = 0

This case features the violation of the keep in constraint of the sun sensor only. Just for this case, only the sun
sensor along the y body axis is considered. The keep in constraint is violated when the boresight angle exceeds the 
70 def field of view of the instrument.

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation5020700.svg
   :align: center

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation6020700.svg
   :align: center

::

    show_plots = True, use2SunSensors = True, starTrackerFov = 20, sunSensorFov = 70, attitudeSetCase = 0

This case is identical to the previous one, except for the fact that both sun sensors along the y and z body axes are 
being used. No constraints are violated, since the keep in condition only needs to be satisfied for at least one sun 
sensor at  the time.

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation5120700.svg
   :align: center

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation6120700.svg
   :align: center

::

    show_plots = True, use2SunSensors = True, starTrackerFov = 20, sunSensorFov = 70, attitudeSetCase = 1

In this case there is a portion of the slew maneuver where both the sun sensor boresights exceed the threshold, 
therefore the keep in constraint is violated.

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation5120701.svg
   :align: center

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation6120701.svg
   :align: center

::

    show_plots = True, use2SunSensors = True, starTrackerFov = 20, sunSensorFov = 70, attitudeSetCase = 2

In this case, the keep out constraint of the star tracker is violated, alongside with the keep in constraints
for both the sun sensors.

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation5120702.svg
   :align: center

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation6120702.svg
   :align: center

::

    show_plots = True, use2SunSensors = True, starTrackerFov = 30, sunSensorFov = 70, attitudeSetCase = 3

In this last case, only the keep out constraint is violated. Since the fields of view of star tracker and 
sun sensors for the Bevo 2 are, respectively, 20 deg and 70 deg, and they are mounted 90 deg apart from 
each other on the spacecraft, this keep-out-only violation would not be possible. In this case it is 
obtained by increasing the field of view of the star tracker to 30 deg.

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation5130703.svg
   :align: center

.. image:: /_images/Scenarios/scenarioAttitudeConstraintViolation6130703.svg
   :align: center

"""


import sys
import os
import numpy as np
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from copy import copy

from Basilisk.fswAlgorithms import (mrpFeedback, attTrackingError, inertial3D, rwMotorTorque)
from Basilisk.simulation import (reactionWheelStateEffector, simpleNav, spacecraft, boreAngCalc)
from Basilisk.utilities import (SimulationBaseClass, macros,
                                orbitalMotion, simIncludeGravBody,
                                simIncludeRW, unitTestSupport, vizSupport)
from Basilisk.architecture import messaging


from Basilisk import __path__
bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])



def run(show_plots, use2SunSensors, starTrackerFov, sunSensorFov, attitudeSetCase):

    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()

    # (Optional) If you want to see a simulation progress bar in the terminal window, the
    # use the following SetProgressBar(True) statement
    scSim.SetProgressBar(False)

    #  create the simulation process
    dynProcess = scSim.CreateNewProcess(simProcessName)

    # create the dynamics task and specify the simulation time and integration update time
    simulationTime = macros.min2nano(1.5)
    simulationTimeStep = macros.sec2nano(0.5)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))
    
    #
    # setup the simulation tasks/objects
    # 

    # initialize spacecraft object and set properties
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "Bevo2-Sat"

    # add spacecraft object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject, None, 1)

    # setup Gravity Body
    gravFactory = simIncludeGravBody.gravBodyFactory()

    # Next a series of gravitational bodies are included
    gravBodies = gravFactory.createBodies(['earth', 'sun'])
    planet = gravBodies['earth']
    planet.isCentralBody = True

    mu = planet.mu
    # The configured gravitational bodies are added to the spacecraft dynamics with the usual command:
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))

    # Next, the default SPICE support module is created and configured.
    timeInitString = "2021 JANUARY 15 00:28:30.0"
    spiceTimeStringFormat = '%Y %B %d %H:%M:%S.%f'
    timeInit = datetime.strptime(timeInitString, spiceTimeStringFormat)

    # The following is a support macro that creates a `gravFactory.spiceObject` instance
    gravFactory.createSpiceInterface(bskPath +'/supportData/EphemerisData/',
                                     timeInitString,
                                     epochInMsg=True)

    # Earth is gravity center
    gravFactory.spiceObject.zeroBase = 'Earth'

    # The SPICE object is added to the simulation task list.
    scSim.AddModelToTask(simTaskName, gravFactory.spiceObject, None, 2)

    # The gravitational body is connected to the spacecraft object
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))

    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    oe.a = 7000. * 1000      # meters
    oe.e = 0.0001
    oe.i = 33.3 * macros.D2R
    oe.Omega = 148.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 135 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    oe = orbitalMotion.rv2elem(mu, rN, vN)
	
	# sets of initial attitudes that yield the desired constraint violations (attitudeSetCase)
    sigma_BN_start = [ [0.522, -0.065,  0.539],     # to violate one keepIn only
                       [0.314, -0.251,  0.228],     # to violate two keepIn and not keepOut
                       [-0.378, 0.119, -0.176],     # to violate keepOut and both keepIn 
                       [-0.412, 0.044, -0.264] ]    # to violate keepOut only

    # To set the spacecraft initial conditions, the following initial position and velocity variables are set:
    scObject.hub.r_CN_NInit = rN  # m   - r_BN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_BN_N
    scObject.hub.sigma_BNInit = sigma_BN_start[attitudeSetCase]   # change this MRP set to customize initial inertial attitude        
    scObject.hub.omega_BN_BInit = [[0.], [0.], [0.]]              # rad/s - omega_CN_B
    
    # define the simulation inertia
    I = [0.02 / 3,  0.,         0.,
         0.,        0.1256 / 3, 0.,
         0.,        0.,         0.1256 / 3]
    scObject.hub.mHub = 4.0  # kg - spacecraft mass
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]]  # m - position vector of body-fixed point B relative to CM
    scObject.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I)

    #
    # add RW devices
    #
    # Make RW factory instance
    rwFactory = simIncludeRW.rwFactory()

    # store the RW dynamical model type
    varRWModel = messaging.BalancedWheels

    # create each RW by specifying the RW type, the spin axis gsHat, plus optional arguments
    maxMomentum = 0.01
    maxSpeed = 6000 * macros.RPM
    RW1 = rwFactory.create('custom', [1, 0, 0], Omega=0.  # RPM
                           , Omega_max=maxSpeed
                           , maxMomentum=maxMomentum
                           , u_max=0.001
                           , RWModel=varRWModel)
    RW2 = rwFactory.create('custom', [0, 1, 0], Omega=0.  # RPM
                           , Omega_max=maxSpeed
                           , maxMomentum=maxMomentum
                           , u_max=0.001
                           , RWModel=varRWModel)
    RW3 = rwFactory.create('custom', [0, 0, 1], Omega=0.  # RPM
                           , Omega_max=maxSpeed
                           , maxMomentum=maxMomentum
                           , u_max=0.001
                           , RWModel=varRWModel)

    numRW = rwFactory.getNumOfDevices()

    # create RW object container and tie to spacecraft object
    rwStateEffector = reactionWheelStateEffector.ReactionWheelStateEffector()
    rwStateEffector.ModelTag = "RW_cluster"
    rwFactory.addToSpacecraft(scObject.ModelTag, rwStateEffector, scObject)

    # add RW object array to the simulation process
    scSim.AddModelToTask(simTaskName, rwStateEffector, None, 2)

    # add the simple Navigation sensor module
    sNavObject = simpleNav.SimpleNav()
    sNavObject.ModelTag = "SimpleNavigation"
    scSim.AddModelToTask(simTaskName, sNavObject)

    #
    #   setup the FSW algorithm tasks
    #

  	# sets of initial attitudes that yield the desired constraint violations (attitudeSetCase)
    sigma_BN_target = [ [0.342,  0.223, -0.432],     # to violate one keepIn only
                        [0.326, -0.206, -0.823],     # to violate two keepIn and not keepOut
                        [0.350,  0.220, -0.440],     # to violate keepOut and both keepIn 
                        [0.350,  0.220, -0.440] ]    # to violate keepOut only
	
    # setup inertial3D guidance module
    inertial3DConfig = inertial3D.inertial3DConfig()
    inertial3DWrap = scSim.setModelDataWrap(inertial3DConfig)
    inertial3DWrap.ModelTag = "inertial3D"
    scSim.AddModelToTask(simTaskName, inertial3DWrap, inertial3DConfig)
    inertial3DConfig.sigma_R0N = sigma_BN_target[attitudeSetCase]     # change this MRP set to customize final inertial attitude

    # setup the attitude tracking error evaluation module
    attErrorConfig = attTrackingError.attTrackingErrorConfig()
    attErrorWrap = scSim.setModelDataWrap(attErrorConfig)
    attErrorWrap.ModelTag = "attErrorInertial3D"
    scSim.AddModelToTask(simTaskName, attErrorWrap, attErrorConfig)

    # setup the MRP Feedback control module
    mrpControlConfig = mrpFeedback.mrpFeedbackConfig()
    mrpControlWrap = scSim.setModelDataWrap(mrpControlConfig)
    mrpControlWrap.ModelTag = "mrpFeedback"
    scSim.AddModelToTask(simTaskName, mrpControlWrap, mrpControlConfig)
    decayTime = 10.0
    xi = 1.0
    mrpControlConfig.Ki = -1  # make value negative to turn off integral feedback
    mrpControlConfig.P = 3*np.max(I)/decayTime
    mrpControlConfig.K = (mrpControlConfig.P/xi)*(mrpControlConfig.P/xi)/np.max(I)
    mrpControlConfig.integralLimit = 2. / mrpControlConfig.Ki * 0.1

    # add module that maps the Lr control torque into the RW motor torques
    rwMotorTorqueConfig = rwMotorTorque.rwMotorTorqueConfig()
    rwMotorTorqueWrap = scSim.setModelDataWrap(rwMotorTorqueConfig)
    rwMotorTorqueWrap.ModelTag = "rwMotorTorque"
    scSim.AddModelToTask(simTaskName, rwMotorTorqueWrap, rwMotorTorqueConfig)

    # Make the RW control all three body axes
    controlAxes_B = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    rwMotorTorqueConfig.controlAxes_B = controlAxes_B
    
    # Boresight vector modules.
    stBACObject = boreAngCalc.BoreAngCalc()
    stBACObject.ModelTag = "starTrackerBoresight"
    stBACObject.boreVec_B = [1., 0., 0.]  # boresight in body frame
    scSim.AddModelToTask(simTaskName, stBACObject)

    ssyBACObject = boreAngCalc.BoreAngCalc()
    ssyBACObject.ModelTag = "SunSensorBoresight"
    ssyBACObject.boreVec_B = [0., 1., 0.]  # boresight in body frame
    scSim.AddModelToTask(simTaskName, ssyBACObject)
    
    if use2SunSensors:
        sszBACObject = boreAngCalc.BoreAngCalc()
        sszBACObject.ModelTag = "SunSensorBoresight"
        sszBACObject.boreVec_B = [0., 0., 1.]  # boresight in body frame
        scSim.AddModelToTask(simTaskName, sszBACObject)

    #
    #   Setup data logging before the simulation is initialized
    #
    numDataPoints = 200
    samplingTime = unitTestSupport.samplingTime(simulationTime, simulationTimeStep, numDataPoints)
    dataRec = scObject.scStateOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, dataRec)
    rwMotorLog = rwMotorTorqueConfig.rwMotorTorqueOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, rwMotorLog)
    attErrorLog = attErrorConfig.attGuidOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, attErrorLog)
    stBACOLog = stBACObject.angOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, stBACOLog)
    ssyBACOLog = ssyBACObject.angOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, ssyBACOLog)
    if use2SunSensors:
        sszBACOLog = sszBACObject.angOutMsg.recorder(samplingTime)
        scSim.AddModelToTask(simTaskName, sszBACOLog)

    # To log the RW information, the following code is used:
    mrpLog = rwStateEffector.rwSpeedOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, mrpLog)

    # A message is created that stores an array of the Omega wheel speeds
    rwLogs = []
    for item in range(numRW):
        rwLogs.append(rwStateEffector.rwOutMsgs[item].recorder(samplingTime))
        scSim.AddModelToTask(simTaskName, rwLogs[item])

    #
    # create simulation messages
    #

    # create the FSW vehicle configuration message
    vehicleConfigOut = messaging.VehicleConfigMsgPayload()
    vehicleConfigOut.ISCPntB_B = I  # use the same inertia in the FSW algorithm as in the simulation
    vcMsg = messaging.VehicleConfigMsg().write(vehicleConfigOut)

    # Setup the FSW RW configuration message.
    fswRwParamMsg = rwFactory.getConfigMessage()

    # link messages
    attErrorConfig.attNavInMsg.subscribeTo(sNavObject.attOutMsg)
    sNavObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)
    attErrorConfig.attNavInMsg.subscribeTo(sNavObject.attOutMsg)
    attErrorConfig.attRefInMsg.subscribeTo(inertial3DConfig.attRefOutMsg)    # for inertial3D
    mrpControlConfig.guidInMsg.subscribeTo(attErrorConfig.attGuidOutMsg)
    mrpControlConfig.vehConfigInMsg.subscribeTo(vcMsg)
    mrpControlConfig.rwParamsInMsg.subscribeTo(fswRwParamMsg)
    mrpControlConfig.rwSpeedsInMsg.subscribeTo(rwStateEffector.rwSpeedOutMsg)
    rwMotorTorqueConfig.rwParamsInMsg.subscribeTo(fswRwParamMsg)
    rwMotorTorqueConfig.vehControlInMsg.subscribeTo(mrpControlConfig.cmdTorqueOutMsg)
    rwStateEffector.rwMotorCmdInMsg.subscribeTo(rwMotorTorqueConfig.rwMotorTorqueOutMsg)
    
    # Boresight modules
    stBACObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)
    stBACObject.celBodyInMsg.subscribeTo(gravFactory.spiceObject.planetStateOutMsgs[1])
    ssyBACObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)
    ssyBACObject.celBodyInMsg.subscribeTo(gravFactory.spiceObject.planetStateOutMsgs[1])
    if use2SunSensors:
        sszBACObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)
        sszBACObject.celBodyInMsg.subscribeTo(gravFactory.spiceObject.planetStateOutMsgs[1])

    # Vizard Visualization Option
    # ---------------------------

    viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObject,
             # saveFile=__file__
             )
    vizSupport.createConeInOut(viz, toBodyName='sun_planet_data', coneColor = 'r',
                       normalVector_B=[1, 0, 0], incidenceAngle=starTrackerFov*macros.D2R, isKeepIn=False,
                       coneHeight=10.0, coneName='sunKeepOut')
    vizSupport.createConeInOut(viz, toBodyName='sun_planet_data', coneColor = 'g',
                       normalVector_B=[0, 1, 0], incidenceAngle=sunSensorFov*macros.D2R, isKeepIn=True,
                       coneHeight=10.0, coneName='sunKeepIn')
    if use2SunSensors:
        vizSupport.createConeInOut(viz, toBodyName='sun_planet_data', coneColor = 'b',
                       normalVector_B=[0, 0, 1], incidenceAngle=sunSensorFov*macros.D2R, isKeepIn=True,
                       coneHeight=10.0, coneName='sunKeepIn')

    # initialize Simulation:  This function runs the self_init()
    # cross_init() and reset() routines on each module.
    scSim.InitializeSimulation()

    # configure a simulation stop time time and execute the simulation run
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()

    # retrieve the logged data

    # Orbit
    posData = dataRec.r_BN_N
    velData = dataRec.v_BN_N

    # RW
    dataUsReq = rwMotorLog.motorTorque
    dataSigmaBR = attErrorLog.sigma_BR
    dataOmegaBR = attErrorLog.omega_BR_B
    dataOmegaRW = mrpLog.wheelSpeeds
    dataSTMissAngle = stBACOLog.missAngle
    dataSSyMissAngle = ssyBACOLog.missAngle
    if use2SunSensors:
        dataSSzMissAngle = sszBACOLog.missAngle
    
    dataRW = []
    for i in range(numRW):
        dataRW.append(rwLogs[i].u_current)

    np.set_printoptions(precision=16)


    # Displays the plots relative to the S/C attitude, maneuver, RW speeds and torques and boresight angles    
    
    timeData = rwMotorLog.times() * macros.NANO2MIN

    plot_attitude_error(timeData, dataSigmaBR)
    figureList = {}
    pltName = fileName + "1" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)
    figureList[pltName] = plt.figure(1)

    plot_rw_motor_torque(timeData, dataUsReq, dataRW, numRW)
    pltName = fileName + "2" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)
    figureList[pltName] = plt.figure(2)

    plot_rate_error(timeData, dataOmegaBR)
    pltName = fileName + "3" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)     
    figureList[pltName] = plt.figure(3)

    plot_rw_speeds(timeData, dataOmegaRW, numRW)
    pltName = fileName + "4" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)
    figureList[pltName] = plt.figure(4)

    plot_st_miss_angle(timeData, dataSTMissAngle, starTrackerFov)
    pltName = fileName + "5" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)
    figureList[pltName] = plt.figure(5)
        
    dataSS = [dataSSyMissAngle]
    if use2SunSensors:
        dataSS.append(dataSSzMissAngle)
    plot_ss_miss_angle(timeData, dataSS, sunSensorFov)
    pltName = fileName + "6" + str(int(use2SunSensors)) + str(starTrackerFov) + str(sunSensorFov) + str(attitudeSetCase)
    figureList[pltName] = plt.figure(6)

    if show_plots:  
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    return figureList


# Plotting RW functions
def plot_attitude_error(timeData, dataSigmaBR):
    """Plot the attitude errors."""
    plt.figure(1)
    for idx in range(3):
        plt.plot(timeData, dataSigmaBR[:, idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\sigma_' + str(idx) + '$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel(r'Attitude Error $\sigma_{B/R}$')

def plot_rw_cmd_torque(timeData, dataUsReq, numRW):
    """Plot the RW command torques."""
    plt.figure(2)
    for idx in range(3):
        plt.plot(timeData, dataUsReq[:, idx],
                 '--',
                 color=unitTestSupport.getLineColor(idx, numRW),
                 label=r'$\hat u_{s,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('RW Motor Torque (Nm)')

def plot_rw_motor_torque(timeData, dataUsReq, dataRW, numRW):
    """Plot the RW actual motor torques."""
    plt.figure(2)
    for idx in range(3):
        plt.plot(timeData, dataUsReq[:, idx],
                 '--',
                 color=unitTestSupport.getLineColor(idx, numRW),
                 label=r'$\hat u_{s,' + str(idx) + '}$')
        plt.plot(timeData, dataRW[idx],
                 color=unitTestSupport.getLineColor(idx, numRW),
                 label='$u_{s,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('RW Motor Torque (Nm)')

def plot_rate_error(timeData, dataOmegaBR):
    """Plot the body angular velocity rate tracking errors."""
    plt.figure(3)
    for idx in range(3):
        plt.plot(timeData, dataOmegaBR[:, idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\omega_{BR,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('Rate Tracking Error (rad/s) ')

def plot_rw_speeds(timeData, dataOmegaRW, numRW):
    """Plot the RW spin rates."""
    plt.figure(4)
    for idx in range(numRW):
        plt.plot(timeData, dataOmegaRW[:, idx] / macros.RPM,
                 color=unitTestSupport.getLineColor(idx, numRW),
                 label=r'$\Omega_{' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('RW Speed (RPM) ')

def plot_st_miss_angle(timeData, dataMissAngle, Fov):
    """Plot the miss angle between star tacker boresight and Sun."""
    fig, ax = plt.subplots()
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    dataFov = np.ones(len(timeData))*Fov
    plt.plot(timeData, dataFov, '--',
                 color = 'r', label = r'f.o.v.')
    data = dataMissAngle*macros.R2D
    for idx in range(1):
        plt.plot(timeData, data,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\alpha $')
    plt.fill_between(timeData, 0, 1, where=dataFov >= data, facecolor='red',
                  alpha = 0.4, interpolate=True, transform = trans)
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('StarTracker/Sun angle \u03B1 (deg)')

def plot_ss_miss_angle(timeData, dataMissAngle, Fov):
    """Plot the miss angle between sun sensor(s) boresight and Sun."""
    fig, ax = plt.subplots()
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    dataFov = np.ones(len(timeData))*Fov
    plt.plot(timeData, dataFov, '--',
                 color = 'r', label = r'f.o.v.')
    data = []
    for d in dataMissAngle:
        data.append(d*macros.R2D)
    for idx in range(len(data)):
        plt.plot(timeData, data[idx],
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$\beta_{' + str(idx+1) + '}$')
    dataMinAngle = 180*np.ones(len(timeData))
    for i in range(len(timeData)):
        for j in range(len(data)):
            if data[j][i] < dataMinAngle[i]:
                dataMinAngle[i] = data[j][i]
    plt.fill_between(timeData, 0, 1, where = dataFov < dataMinAngle, facecolor='red',
                  alpha = 0.4, interpolate=True, transform = trans)
    plt.legend(loc='lower right')
    plt.xlabel('Time [min]')
    plt.ylabel('SunSensor/Sun angle \u03B2 (deg)')



if __name__ == "__main__":
    run(
        True,           # show_plots
        True,           # use2SunSensors
        20,             # starTrackerFov
        70,             # sunSensorFov
        2               # attitudeSetCase
    )
