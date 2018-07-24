''' '''
'''
 ISC License

 Copyright (c) 2016-2018, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
# Basilisk Integrated Test
#
# Purpose:  Integrated test of the MonteCarlo module.  Runs multiple
#           scenarioAttitudeFeedbackRW with dispersed initial parameters
#


import inspect
import math
import os
import numpy as np
import shutil
import matplotlib.pyplot as plt
import datetime

# @cond DOXYGEN_IGNORE
filename = inspect.getframeinfo(inspect.currentframe()).filename
fileNameString = os.path.basename(os.path.splitext(__file__)[0])
path = os.path.dirname(os.path.abspath(filename))
# @endcond

from Basilisk import __path__
bskPath = __path__[0]

# import general simulation support files
from Basilisk.utilities import SimulationBaseClass
from Basilisk.utilities import unitTestSupport                  # general support file with common unit test functions
from Basilisk.utilities import macros
from Basilisk.utilities import orbitalMotion

# import simulation related support
from Basilisk.simulation import spacecraftPlus
from Basilisk.utilities import simIncludeGravBody
from Basilisk.utilities import simIncludeRW
from Basilisk.simulation import simple_nav
from Basilisk.simulation import reactionWheelStateEffector
from Basilisk.simulation import rwVoltageInterface

# import FSW Algorithm related support
from Basilisk.fswAlgorithms import MRP_Feedback
from Basilisk.fswAlgorithms import inertial3D
from Basilisk.fswAlgorithms import attTrackingError
from Basilisk.fswAlgorithms import rwMotorTorque
from Basilisk.utilities import fswSetupRW
from Basilisk.fswAlgorithms import rwMotorVoltage

# import message declarations
from Basilisk.fswAlgorithms import fswMessages
from Basilisk.utilities.MonteCarlo.Controller import Controller, RetentionPolicy
from Basilisk.utilities.MonteCarlo.Dispersions import (UniformEulerAngleMRPDispersion, UniformDispersion,
                                                       NormalVectorCartDispersion, InertiaTensorDispersion)

import numpy as np
import pandas as pd
import holoviews as hv
import datashader as ds
from bokeh.plotting import show
import datashader.transfer_functions as tf
from datashader.utils import export_image
from holoviews.operation.datashader import datashade

# This import is for reaggregating data when zooming if that is ever pursued
from datashader.bokeh_ext import InteractiveImage


NUMBER_OF_RUNS = 1000
VERBOSE = True
ONLY_GRAPH = 1

# Here are the name of some messages that we want to retain or otherwise use
inertial3DConfigOutputDataName = "guidanceInertial3D"
attErrorConfigOutputDataName = "attErrorInertial3DMsg"
mrpControlConfigOutputDataName = "LrRequested"
rwMotorTorqueConfigOutputDataName = "rw_torque_Lr"
mrpControlConfigInputRWSpeedsName = "reactionwheel_output_states"
sNavObjectOutputTransName = "simple_trans_nav_output"
fswRWVoltageConfigVoltageOutMsgName = "rw_voltage_input"

# Create data retention names based on what data we want to save
rwMotorTorqueConfigOutputDataName_motorTorque = rwMotorTorqueConfigOutputDataName + ".motorTorque"
attErrorConfigOutputDataName_sigma_BR = attErrorConfigOutputDataName + ".sigma_BR"
attErrorConfigOutputDataName_omega_BR_B = attErrorConfigOutputDataName + ".omega_BR_B"
sNavObjectOutputTransName_r_BN_N = sNavObjectOutputTransName + ".r_BN_N"
mrpControlConfigInputRWSpeedsName_wheelSpeeds = mrpControlConfigInputRWSpeedsName + ".wheelSpeeds"
fswRWVoltageConfigVoltageOutMsgName_voltage = fswRWVoltageConfigVoltageOutMsgName + ".voltage"

# Create a list of retained data names to loop through while graphing
retainedDataList = [rwMotorTorqueConfigOutputDataName_motorTorque, attErrorConfigOutputDataName_sigma_BR,
                    attErrorConfigOutputDataName_omega_BR_B, sNavObjectOutputTransName_r_BN_N,
                    mrpControlConfigInputRWSpeedsName_wheelSpeeds, fswRWVoltageConfigVoltageOutMsgName_voltage]

# Set global dataframes to populate with data when executing callbacks
rwMotorTorqueConfigOutputDataName_motorTorque_dataFrame = pd.DataFrame()
attErrorConfigOutputDataName_sigma_BR_dataFrame = pd.DataFrame()
attErrorConfigOutputDataName_omega_BR_B_dataFrame = pd.DataFrame()
sNavObjectOutputTransName_r_BN_N_dataFrame = pd.DataFrame()
mrpControlConfigInputRWSpeedsName_wheelSpeeds_dataFrame = pd.DataFrame()
fswRWVoltageConfigVoltageOutMsgName_voltage_dataFrame = pd.DataFrame()

rwOutName = ["rw_config_0_data", "rw_config_1_data", "rw_config_2_data"]

# We also will need the simulationTime and samplingTimes
numDataPoints = 1000
simulationTime = macros.min2nano(60.)
samplingTime = simulationTime / (numDataPoints-1)

## \defgroup Tutorials_5_0
##   @{
## Demonstrates how to run basic Monte-Carlo (MC) RW-based attitude simulations.
#
# MC Simulation of an Attitude Detumbling Simulation using RW Effectors {#MonteCarloSimulation}
# ====
#
# Scenario Description
# -----
# This script duplicates the scenario in [scenarioAttitudeFeedbackRW.py](@ref scenarioAttitudeFeedbackRW) where a
# 6-DOF spacecraft  is orbiting the Earth.  Here some simulation parameters are dispersed randomly
# using a multi threaded Monte-Carlo setup. Reaction Wheel (RW) state effector are added
# to the rigid spacecraftPlus() hub, and what flight
# algorithm module is used to control these RWs. The scenario is run in a single configuration:
# by not using the Jitter model and by using the RW Voltage IO. Given this scenario we can add dispersions
# to the variables in between each MC run.
#
#
# To run the MC simulation, call the python script from a Terminal window through
#
#       python scenarioMonteCarloAttRW.py
#
# For more information on the Attitude Feedback Simulation with RW, please see the documentation
# on the [scenarioAttitudeFeedbackRW.py](@ref scenarioAttitudeFeedbackRW) file.
#
#
# ### Setup Changes for Monte-Carlo Runs
#
# In order to set up the multi-threaded MC simulation, the user must first instantiate the Controller class.
# The function that is being simulated is the set in this class (in this case, it's defined in the same file as the
# MC scenario). The user can then set other variables such as the number of runs, the dispersion seeds, and number of
# cores.
# The specific code required is:
# ~~~~~~~~~~~~~{.py}
#   #First, the `Controller` class is used in order to define the simulation
#   monteCarlo = Controller()
#
#   # Every MonteCarlo simulation must define a function that creates the `SimulationBaseClass` to execute and returns it. Within this function, the simulation is created and configured
#   monteCarlo.setSimulationFunction(createScenarioAttitudeFeedbackRW)
#
#   # Also, every MonteCarlo simulation must define a function which executes the simulation that was created.
#   monteCarlo.setExecutionFunction(executeScenario)
#
#   # A Monte Carlo simulation must define how many simulation runs to execute
#   monteCarlo.setExecutionCount(NUMBER_OF_RUNS)
#
#   # The simulations can have random seeds of each simulation dispersed randomly
#   monteCarlo.setShouldDisperseSeeds(True)
#
#   # Optionally set the number of cores to use
#   # monteCarlo.setThreadCount(PROCESSES)
#
#   # Whether to print more verbose information during the run
#   monteCarlo.setVerbose(VERBOSE)
#
#   # We set up where to retain the data to.
#   dirName = "montecarlo_test"
#   monteCarlo.setArchiveDir(dirName)
# ~~~~~~~~~~~~~
# The next important step to setting up the MC runs is to disperse the necessary variables.
# The dispersions that are set are listed in the following table:
#
# Input      | Description of Element    | Distribution
# ------------- | ---------|-----------------
# Inertial attitude       |Using Modified Rodrigues Parameters | Uniform for all 3 rotations betweenr [0, 2 pi]
# Inertial rotation rate         | Using omega vector      | Normal dispersions for each of the rotation components, each of mean 0 and standard deviation 0.25 deg/s
# Mass of the hub   | Total Mass of the spacecraft | Uniform around +/-5% of expected values. Bounds are [712.5, 787.5]
# Center of Mass Offset | Position vector offset on the actual center of mass, and its theoretical position | Normally around a mean [0, 0, 1], with standard deviations of [0.05/3, 0.05/3, 0.1/3]
# Inertia Tensor  |3x3 inertia tensor. Dispersed by 3 rotations | Normally about mean value of diag(900, 800, 600). Each of the 3 rotations are normally distributed with angles of mean 0 and standard deviation 0.1 deg.
# RW axes  |The rotation axis for each of the 3 wheels | Normally around a respective means [1,0,0], [0,1,0], and [0,0,1] with respective standard deviations [0.01/3, 0.005/3, 0.005/3], [0.005/3, 0.01/3, 0.005/3], and [0.005/3, 0.005/3, 0.01/3]
# RW speeds | The rotation speed for each of the 3 wheels |Uniform around  +/-5% of expected values. Bounds are [95, 105], [190, 210], and [285, 315]
# Voltage to Torque Gain         |The gain between the commanded torque and the actual voltage | Uniform around  +/-5% of expected values. Bounds are [0.019, 0.021]
#
# The python commands to add these dispersions are shown below:
#
# ~~~~~~~~~~~~~~~~~{.py}
#     # Statistical dispersions can be applied to initial parameters using the MonteCarlo module
#     dispMRPInit = 'TaskList[0].TaskModels[0].hub.sigma_BNInit'
#     dispOmegaInit = 'TaskList[0].TaskModels[0].hub.omega_BN_BInit'
#     dispMass = 'TaskList[0].TaskModels[0].hub.mHub'
#     dispCoMOff = 'TaskList[0].TaskModels[0].hub.r_BcB_B'
#     dispInertia = 'hubref.IHubPntBc_B'
#     dispRW1Axis = 'RW1.gsHat_B'
#     dispRW2Axis = 'RW2.gsHat_B'
#     dispRW3Axis = 'RW3.gsHat_B'
#     dispRW1Omega = 'RW1.Omega'
#     dispRW2Omega = 'RW2.Omega'
#     dispRW3Omega = 'RW3.Omega'
#     dispVoltageIO = 'rwVoltageIO.voltage2TorqueGain'
#     dispList = [dispMRPInit, dispOmegaInit, dispMass, dispCoMOff, dispInertia]
#
#     # Add dispersions with their dispersion type
#     monteCarlo.addDispersion(UniformEulerAngleMRPDispersion(dispMRPInit))
#     monteCarlo.addDispersion(NormalVectorCartDispersion(dispOmegaInit, 0.0, 0.75 / 3.0 * np.pi / 180))
#     monteCarlo.addDispersion(UniformDispersion(dispMass, ([750.0 - 0.05*750, 750.0 + 0.05*750])))
#     monteCarlo.addDispersion(NormalVectorCartDispersion(dispCoMOff, [0.0, 0.0, 1.0], [0.05 / 3.0, 0.05 / 3.0, 0.1 / 3.0]))
#     monteCarlo.addDispersion(InertiaTensorDispersion(dispInertia, stdAngle=0.1))
#     monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW1Axis, [1.0, 0.0, 0.0], [0.01 / 3.0, 0.005 / 3.0, 0.005 / 3.0]))
#     monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW2Axis, [0.0, 1.0, 0.0], [0.005 / 3.0, 0.01 / 3.0, 0.005 / 3.0]))
#     monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW3Axis, [0.0, 0.0, 1.0], [0.005 / 3.0, 0.005 / 3.0, 0.01 / 3.0]))
#     monteCarlo.addDispersion(UniformDispersion(dispRW1Omega, ([100.0 - 0.05*100, 100.0 + 0.05*100])))
#     monteCarlo.addDispersion(UniformDispersion(dispRW2Omega, ([200.0 - 0.05*200, 200.0 + 0.05*200])))
#     monteCarlo.addDispersion(UniformDispersion(dispRW3Omega, ([300.0 - 0.05*300, 300.0 + 0.05*300])))
#     monteCarlo.addDispersion(UniformDispersion(dispVoltageIO, ([0.2/10. - 0.05 * 0.2/10., 0.2/10. + 0.05 * 0.2/10.])))
# ~~~~~~~~~~~~~~~~~
#
# A retention policy is used to log the desired data. This is shown in the following code:
#
# ~~~~~~~~~~~~~{.py}
#     # A `RetentionPolicy` is used to define what data from the simulation should be retained. A `RetentionPolicy` is a list of messages and variables to log from each simulation run. It also has a callback, used for plotting/processing the retained data.
#     retentionPolicy = RetentionPolicy()
#     # define the data to retain
#     retentionPolicy.addMessageLog(rwMotorTorqueConfigOutputDataName, [("motorTorque", range(5))], samplingTime)
#     retentionPolicy.addMessageLog(attErrorConfigOutputDataName, [("sigma_BR", range(3)), ("omega_BR_B", range(3))], samplingTime)
#     retentionPolicy.addMessageLog(sNavObjectOutputTransName, [("r_BN_N", range(3))], samplingTime)
#     retentionPolicy.addMessageLog(mrpControlConfigInputRWSpeedsName, [("wheelSpeeds", range(3))], samplingTime)
#     retentionPolicy.addMessageLog(fswRWVoltageConfigVoltageOutMsgName, [("voltage", range(3))], samplingTime)
# ~~~~~~~~~~~~~
#
# The simulation can now be run. It returns the failed jobs, which should not occur.
# The data can then be loaded:
#
# ~~~~~~~~~~~~~{.py}
# After the monteCarlo run is configured, it is executed.
# This method returns the list of jobs that failed.
# failures = monteCarlo.executeSimulations()
#
# assert len(failures) == 0, "No runs should fail"
#
# # Now in another script (or the current one), the data from this simulation can be easily loaded.
# # This demonstrates loading it from disk
# monteCarloLoaded = Controller.load(dirName)
# ~~~~~~~~~~~~~
#
# ### Accessing Data
#
# Now that the MC have been executed, the data can be accessed and tested in different ways
# This is explained in the following python code and comments
#
# ~~~~~~~~~~~~~~~{.py}
#        # Then retained data from any run can then be accessed in the form of a dictionary with two sub-dictionaries for messages and variables:
#     retainedData = monteCarloLoaded.getRetainedData(NUMBER_OF_RUNS-1)
#     assert retainedData is not None, "Retained data should be available after execution"
#     assert "messages" in retainedData, "Retained data should retain messages"
#     assert "attErrorInertial3DMsg.sigma_BR" in retainedData["messages"], "Retained messages should exist"
#
#     # We also can rerun a case using the same parameters and random seeds
#     # If we rerun a properly set-up run, it should output the same data.
#     # Here we test that if we rerun the case the data doesn't change
#     oldOutput = retainedData["messages"]["attErrorInertial3DMsg.sigma_BR"]
#
#     # Rerunning the case shouldn't fail
#     failed = monteCarloLoaded.reRunCases([NUMBER_OF_RUNS-1])
#     assert len(failed) == 0, "Should rerun case successfully"
#
#     # Now access the newly retained data to see if it changed
#     retainedData = monteCarloLoaded.getRetainedData(NUMBER_OF_RUNS-1)
#     newOutput = retainedData["messages"]["attErrorInertial3DMsg.sigma_BR"]
#     for k1, v1 in enumerate(oldOutput):
#         for k2, v2 in enumerate(v1):
#             assert math.fabs(oldOutput[k1][k2] - newOutput[k1][k2]) < .001, \
#             "Outputs shouldn't change on runs if random seeds are same"
#
#     # We can also access the initial parameters
#     # The random seeds should differ between runs, so we will test that
#     params1 = monteCarloLoaded.getParameters(NUMBER_OF_RUNS-1)
#     params2 = monteCarloLoaded.getParameters(NUMBER_OF_RUNS-2)
#     assert "TaskList[0].TaskModels[0].RNGSeed" in params1, "random number seed should be applied"
#     for dispName in dispList:
#         assert dispName in params1, "dispersion should be applied"
#         # assert two different runs had different parameters.
#         assert params1[dispName] != params2[dispName], "dispersion should be different in each run"
#
# ~~~~~~~~~~~~~~~
#  Finally the data can be plotted as desired:
#
#
# ~~~~~~~~~~~~~~~{.py}
# # Now we execute our callback for the retained data.
# # For this run, that means executing the plot.
# # We can plot only runs 4,6,7 overlapped
# monteCarloLoaded.executeCallbacks([4, 6, 7])
# # or execute the plot on all runs
# # monteCarloLoaded.executeCallbacks()
#
# # Now we clean up data from this test
# shutil.rmtree(dirName)
# assert not os.path.exists(dirName), "No leftover data should exist after the test"
#
# # And possibly show the plots
# if show_plots:
#     print "Test concluded, showing plots now..."
#     plt.show()
#     # close the plots being saved off to avoid over-writing old and new figures
#     plt.close("all")
#
# ~~~~~~~~~~~~~~~
#
# The resulting simulation illustrations are shown below.
# ![MRP Attitude Error History](Images/Scenarios/scenarioMonteCarloAttRW_AttitudeError.svg "Attitude Error history")
# ![Rate Tracking Error History](Images/Scenarios/scenarioMonteCarloAttRW_RateTrackingError.svg "Rate Tracking Error history")
# ![RW Motor Torque History](Images/Scenarios/scenarioMonteCarloAttRW_RWMotorTorque.svg "RW Motor Torque history")
# ![RW Speeds History](Images/Scenarios/scenarioMonteCarloAttRW_RWSpeed.svg "RW Speeds history")
# ![RW Voltage History](Images/Scenarios/scenarioMonteCarloAttRW_RWVoltage.svg "RW Voltage history")
#
# These are the same plots output by the [scenarioAttitudeFeedbackRW.py](@ref scenarioAttitudeFeedbackRW) scenario. Please refer to this document for me details on the plots.
##  @}


def run(saveFigures, case, show_plots):
    '''This function is called by the py.test environment.'''

    # A MonteCarlo simulation can be created using the `MonteCarlo` module.
    # This module is used to execute monte carlo simulations, and access
    # retained data from previously executed MonteCarlo runs.

    if ONLY_GRAPH:
        graph()
        return
    # First, the `Controller` class is used in order to define the simulation
    monteCarlo = Controller()

    # Every MonteCarlo simulation must define a function that creates the `SimulationBaseClass` to execute and returns it. Within this function, the simulation is created and configured
    monteCarlo.setSimulationFunction(createScenarioAttitudeFeedbackRW)

    # Also, every MonteCarlo simulation must define a function which executes the simulation that was created.
    monteCarlo.setExecutionFunction(executeScenario)

    # A Monte Carlo simulation must define how many simulation runs to execute
    monteCarlo.setExecutionCount(NUMBER_OF_RUNS)

    # The simulations can have random seeds of each simulation dispersed randomly
    monteCarlo.setShouldDisperseSeeds(True)

    # Optionally set the number of cores to use
    # monteCarlo.setThreadCount(PROCESSES)

    # Whether to print more verbose information during the run
    monteCarlo.setVerbose(VERBOSE)

    # We set up where to retain the data to.
    dirName = "montecarlo_test"
    monteCarlo.setArchiveDir(dirName)

    # Statistical dispersions can be applied to initial parameters using the MonteCarlo module
    dispMRPInit = 'TaskList[0].TaskModels[0].hub.sigma_BNInit'
    dispOmegaInit = 'TaskList[0].TaskModels[0].hub.omega_BN_BInit'
    dispMass = 'TaskList[0].TaskModels[0].hub.mHub'
    dispCoMOff = 'TaskList[0].TaskModels[0].hub.r_BcB_B'
    dispInertia = 'hubref.IHubPntBc_B'
    dispRW1Axis = 'RW1.gsHat_B'
    dispRW2Axis = 'RW2.gsHat_B'
    dispRW3Axis = 'RW3.gsHat_B'
    dispRW1Omega = 'RW1.Omega'
    dispRW2Omega = 'RW2.Omega'
    dispRW3Omega = 'RW3.Omega'
    dispVoltageIO_0 = 'rwVoltageIO.voltage2TorqueGain[0]'
    dispVoltageIO_1 = 'rwVoltageIO.voltage2TorqueGain[1]'
    dispVoltageIO_2 = 'rwVoltageIO.voltage2TorqueGain[2]'
    dispList = [dispMRPInit, dispOmegaInit, dispMass, dispCoMOff, dispInertia]

    # Add dispersions with their dispersion type
    monteCarlo.addDispersion(UniformEulerAngleMRPDispersion(dispMRPInit))
    monteCarlo.addDispersion(NormalVectorCartDispersion(dispOmegaInit, 0.0, 0.75 / 3.0 * np.pi / 180))
    monteCarlo.addDispersion(UniformDispersion(dispMass, ([750.0 - 0.05*750, 750.0 + 0.05*750])))
    monteCarlo.addDispersion(NormalVectorCartDispersion(dispCoMOff, [0.0, 0.0, 1.0], [0.05 / 3.0, 0.05 / 3.0, 0.1 / 3.0]))
    monteCarlo.addDispersion(InertiaTensorDispersion(dispInertia, stdAngle=0.1))
    monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW1Axis, [1.0, 0.0, 0.0], [0.01 / 3.0, 0.005 / 3.0, 0.005 / 3.0]))
    monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW2Axis, [0.0, 1.0, 0.0], [0.005 / 3.0, 0.01 / 3.0, 0.005 / 3.0]))
    monteCarlo.addDispersion(NormalVectorCartDispersion(dispRW3Axis, [0.0, 0.0, 1.0], [0.005 / 3.0, 0.005 / 3.0, 0.01 / 3.0]))
    monteCarlo.addDispersion(UniformDispersion(dispRW1Omega, ([100.0 - 0.05*100, 100.0 + 0.05*100])))
    monteCarlo.addDispersion(UniformDispersion(dispRW2Omega, ([200.0 - 0.05*200, 200.0 + 0.05*200])))
    monteCarlo.addDispersion(UniformDispersion(dispRW3Omega, ([300.0 - 0.05*300, 300.0 + 0.05*300])))
    monteCarlo.addDispersion(UniformDispersion(dispVoltageIO_0, ([0.2/10. - 0.05 * 0.2/10., 0.2/10. + 0.05 * 0.2/10.])))
    monteCarlo.addDispersion(UniformDispersion(dispVoltageIO_1, ([0.2/10. - 0.05 * 0.2/10., 0.2/10. + 0.05 * 0.2/10.])))
    monteCarlo.addDispersion(UniformDispersion(dispVoltageIO_2, ([0.2/10. - 0.05 * 0.2/10., 0.2/10. + 0.05 * 0.2/10.])))

    # A `RetentionPolicy` is used to define what data from the simulation should be retained. A `RetentionPolicy`
    # is a list of messages and variables to log from each simulation run. It also has a callback,
    # used for plotting/processing the retained data.
    retentionPolicy = RetentionPolicy()
    # define the data to retain
    retentionPolicy.addMessageLog(rwMotorTorqueConfigOutputDataName, [("motorTorque", range(5))], samplingTime)
    retentionPolicy.addMessageLog(attErrorConfigOutputDataName, [("sigma_BR", range(3)), ("omega_BR_B", range(3))], samplingTime)
    retentionPolicy.addMessageLog(sNavObjectOutputTransName, [("r_BN_N", range(3))], samplingTime)
    retentionPolicy.addMessageLog(mrpControlConfigInputRWSpeedsName, [("wheelSpeeds", range(3))], samplingTime)
    retentionPolicy.addMessageLog(fswRWVoltageConfigVoltageOutMsgName, [("voltage", range(3))], samplingTime)

    for message in rwOutName:
        retentionPolicy.addMessageLog(message, [("u_current", range(1))], samplingTime)
    if show_plots:
        # plot data only if show_plots is true, otherwise just retain
        retentionPolicy.setDataCallback(plotSim)
    if saveFigures:
        # plot data only if show_plots is true, otherwise just retain
        retentionPolicy.setDataCallback(plotSimAndSave)
    monteCarlo.addRetentionPolicy(retentionPolicy)

    if case ==1:
        # After the monteCarlo run is configured, it is executed.
        # This method returns the list of jobs that failed.
        failures = monteCarlo.executeSimulations()

        assert len(failures) == 0, "No runs should fail"

        # Now in another script (or the current one), the data from this simulation can be easily loaded.
        # This demonstrates loading it from disk
        monteCarloLoaded = Controller.load(dirName)

        # Then retained data from any run can then be accessed in the form of a dictionary with two sub-dictionaries for messages and variables:
        retainedData = monteCarloLoaded.getRetainedData(NUMBER_OF_RUNS-1)
        assert retainedData is not None, "Retained data should be available after execution"
        assert "messages" in retainedData, "Retained data should retain messages"
        assert "attErrorInertial3DMsg.sigma_BR" in retainedData["messages"], "Retained messages should exist"

        # We also can rerun a case using the same parameters and random seeds
        # If we rerun a properly set-up run, it should output the same data.
        # Here we test that if we rerun the case the data doesn't change
        oldOutput = retainedData["messages"]["attErrorInertial3DMsg.sigma_BR"]

        # Rerunning the case shouldn't fail
        failed = monteCarloLoaded.reRunCases([NUMBER_OF_RUNS-1])
        assert len(failed) == 0, "Should rerun case successfully"

        # Now access the newly retained data to see if it changed
        retainedData = monteCarloLoaded.getRetainedData(NUMBER_OF_RUNS-1)
        newOutput = retainedData["messages"]["attErrorInertial3DMsg.sigma_BR"]
        for k1, v1 in enumerate(oldOutput):
            for k2, v2 in enumerate(v1):
                assert math.fabs(oldOutput[k1][k2] - newOutput[k1][k2]) < .001, \
                "Outputs shouldn't change on runs if random seeds are same"

        # We can also access the initial parameters
        # The random seeds should differ between runs, so we will test that
        params1 = monteCarloLoaded.getParameters(NUMBER_OF_RUNS-1)
        params2 = monteCarloLoaded.getParameters(NUMBER_OF_RUNS-2)
        assert "TaskList[0].TaskModels[0].RNGSeed" in params1, "random number seed should be applied"
        for dispName in dispList:
            assert dispName in params1, "dispersion should be applied"
            # assert two different runs had different parameters.
            assert params1[dispName] != params2[dispName], "dispersion should be different in each run"

        # Now we execute our callback for the retained data.
        # For this run, that means executing the plot.
        # We can plot only runs 4,6,7 overlapped
        # monteCarloLoaded.executeCallbacks([4,6,7])
        # or execute the plot on all runs
        monteCarloLoaded.executeCallbacks()

        # Now we clean up data from this test
        shutil.rmtree(dirName)
        assert not os.path.exists(dirName), "No leftover data should exist after the test"

        # And possibly show the plots
        if show_plots:
            print "Test concluded, showing plots now...", datetime.datetime.now()
            saveDataframesToFile()
            graph()
            print "done graphing. ", datetime.datetime.now()
            # plt.show()
            # close the plots being saved off to avoid over-writing old and new figures
            # plt.close("all")

    #########################################################
    if case ==2:
        return
        # Now run initial cocnditions
        # icName = bskPath + "/tests/testScripts/Support/run_MC_IC"
        # monteCarlo.setICDir(icName)
        # monteCarlo.setICRunFlag(True)
        # numberICs = 3
        # monteCarlo.setExecutionCount(numberICs)
        #
        #
        # # Rerunning the case shouldn't fail
        # runsList = list(range(numberICs))
        # failed = monteCarlo.runInitialConditions(runsList)
        # assert len(failed) == 0, "Should run ICs successfully"
        #
        # # monteCarlo.executeCallbacks([4,6,7])
        # runsList = list(range(numberICs))
        # monteCarlo.executeCallbacks(runsList)
        #
        # # And possibly show the plots
        # if show_plots:
        #     print "Test concluded, showing plots now..."
        #     plt.show()
        #     # close the plots being saved off to avoid over-writing old and new figures
        #     plt.close("all")
        #
        # # Now we clean up data from this test
        # os.remove(icName + '/' + 'MonteCarlo.data' )
        # for i in range(numberICs):
        #     os.remove(icName + '/' + 'run' + str(i) + '.data')
        # assert not os.path.exists(icName + '/' + 'MonteCarlo.data'), "No leftover data should exist after the test"


## This function creates the simulation to be executed in parallel.
# It is copied directly from src/tests/scenarios.
def createScenarioAttitudeFeedbackRW():

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
    simulationTimeStep = macros.sec2nano(.1)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

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
    scObject.hub.mHub = 750.0                   # kg - spacecraft mass
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]] # m - position vector of body-fixed point B relative to CM
    scObject.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I)
    scSim.hubref = scObject.hub

    # add spacecraftPlus object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject, None, 1)

    rwVoltageIO = rwVoltageInterface.RWVoltageInterface()
    rwVoltageIO.ModelTag = "rwVoltageInterface"

    # set module parameters(s)
    rwVoltageIO.setGains(np.array([0.2/10.]*3))  # [Nm/V] conversion gain

    #Add RW Voltage to sim for dispersion
    scSim.rwVoltageIO = rwVoltageIO
    # Add test module to runtime call list
    scSim.AddModelToTask(simTaskName, rwVoltageIO)

    # clear prior gravitational body and SPICE setup definitions
    gravFactory = simIncludeGravBody.gravBodyFactory()

    # setup Earth Gravity Body
    earth = gravFactory.createEarth()
    earth.isCentralBody = True  # ensure this is the central gravitational body
    mu = earth.mu

    # attach gravity model to spaceCraftPlus
    scObject.gravField.gravBodies = spacecraftPlus.GravBodyVector(gravFactory.gravBodies.values())
    #
    # add RW devices
    #
    # Make a fresh RW factory instance, this is critical to run multiple times
    rwFactory = simIncludeRW.rwFactory()

    # store the RW dynamical model type
    varRWModel = rwFactory.BalancedWheels


    # create each RW by specifying the RW type, the spin axis gsHat, plus optional arguments
    RW1 = rwFactory.create('Honeywell_HR16'
                           , [1, 0, 0]
                           , maxMomentum=50.
                           , Omega=100.                 # RPM
                           , RWModel= varRWModel
                           )
    RW2 = rwFactory.create('Honeywell_HR16'
                           , [0, 1, 0]
                           , maxMomentum=50.
                           , Omega=200.                 # RPM
                           , RWModel= varRWModel
                           )
    RW3 = rwFactory.create('Honeywell_HR16'
                           , [0, 0, 1]
                           , maxMomentum=50.
                           , Omega=300.                 # RPM
                           , rWB_B = [0.5, 0.5, 0.5]    # meters
                           , RWModel= varRWModel
                           )
    numRW = rwFactory.getNumOfDevices()
    # create RW object container and tie to spacecraft object
    rwStateEffector = reactionWheelStateEffector.ReactionWheelStateEffector()
    rwFactory.addToSpacecraft("ReactionWheels", rwStateEffector, scObject)

    #Add RWs to sim for dispersion
    scSim.RW1 = RW1
    scSim.RW2 = RW2
    scSim.RW3 = RW3
    # add RW object array to the simulation process
    scSim.AddModelToTask(simTaskName, rwStateEffector, None, 2)

    # add the simple Navigation sensor module.  This sets the SC attitude, rate, position
    # velocity navigation message
    sNavObject = simple_nav.SimpleNav()
    sNavObject.ModelTag = "SimpleNavigation"
    scSim.AddModelToTask(simTaskName, sNavObject)

    #
    #   setup the FSW algorithm tasks
    #

    # setup inertial3D guidance module
    inertial3DConfig = inertial3D.inertial3DConfig()
    inertial3DWrap = scSim.setModelDataWrap(inertial3DConfig)
    inertial3DWrap.ModelTag = "inertial3D"
    scSim.AddModelToTask(simTaskName, inertial3DWrap, inertial3DConfig)
    inertial3DConfig.sigma_R0N = [0., 0., 0.]       # set the desired inertial orientation
    inertial3DConfig.outputDataName = inertial3DConfigOutputDataName

    # setup the attitude tracking error evaluation module
    attErrorConfig = attTrackingError.attTrackingErrorConfig()
    attErrorWrap = scSim.setModelDataWrap(attErrorConfig)
    attErrorWrap.ModelTag = "attErrorInertial3D"
    scSim.AddModelToTask(simTaskName, attErrorWrap, attErrorConfig)
    attErrorConfig.outputDataName = attErrorConfigOutputDataName
    attErrorConfig.inputRefName = inertial3DConfig.outputDataName
    attErrorConfig.inputNavName = sNavObject.outputAttName

    # setup the MRP Feedback control module
    mrpControlConfig = MRP_Feedback.MRP_FeedbackConfig()
    mrpControlWrap = scSim.setModelDataWrap(mrpControlConfig)
    mrpControlWrap.ModelTag = "MRP_Feedback"
    scSim.AddModelToTask(simTaskName, mrpControlWrap, mrpControlConfig)
    mrpControlConfig.inputGuidName  = attErrorConfig.outputDataName
    mrpControlConfig.vehConfigInMsgName  = "vehicleConfigName"
    mrpControlConfig.outputDataName = mrpControlConfigOutputDataName
    mrpControlConfig.rwParamsInMsgName = "rwa_config_data_parsed"
    mrpControlConfig.inputRWSpeedsName = rwStateEffector.OutputDataString
    mrpControlConfig.K  =   3.5
    mrpControlConfig.Ki =   -1          # make value negative to turn off integral feedback
    mrpControlConfig.P  = 30.0
    mrpControlConfig.integralLimit = 2./mrpControlConfig.Ki * 0.1
    mrpControlConfig.domega0 = [0.0, 0.0, 0.0]

    # add module that maps the Lr control torque into the RW motor torques
    rwMotorTorqueConfig = rwMotorTorque.rwMotorTorqueConfig()
    rwMotorTorqueWrap = scSim.setModelDataWrap(rwMotorTorqueConfig)
    rwMotorTorqueWrap.ModelTag = "rwMotorTorque"
    scSim.AddModelToTask(simTaskName, rwMotorTorqueWrap, rwMotorTorqueConfig)
    # Initialize the test module msg names
    rwMotorTorqueConfig.outputDataName = rwMotorTorqueConfigOutputDataName
    rwMotorTorqueConfig.inputVehControlName = mrpControlConfig.outputDataName
    rwMotorTorqueConfig.rwParamsInMsgName = mrpControlConfig.rwParamsInMsgName
    # Make the RW control all three body axes
    controlAxes_B = [
             1,0,0
            ,0,1,0
            ,0,0,1
        ]
    rwMotorTorqueConfig.controlAxes_B = controlAxes_B

    fswRWVoltageConfig = rwMotorVoltage.rwMotorVoltageConfig()
    fswRWVoltageWrap = scSim.setModelDataWrap(fswRWVoltageConfig)
    fswRWVoltageWrap.ModelTag = "rwMotorVoltage"

    # Add test module to runtime call list
    scSim.AddModelToTask(simTaskName, fswRWVoltageWrap, fswRWVoltageConfig)

    # Initialize the test module configuration data
    fswRWVoltageConfig.torqueInMsgName = rwMotorTorqueConfig.outputDataName
    fswRWVoltageConfig.rwParamsInMsgName = mrpControlConfig.rwParamsInMsgName
    fswRWVoltageConfig.voltageOutMsgName = rwVoltageIO.rwVoltageInMsgName

    # set module parameters
    fswRWVoltageConfig.VMin = 0.0  # Volts
    fswRWVoltageConfig.VMax = 10.0  # Volts

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

    # FSW RW configuration message
    # use the same RW states in the FSW algorithm as in the simulation
    fswSetupRW.clearSetup()
    for key, rw in rwFactory.rwList.iteritems():
        fswSetupRW.create(unitTestSupport.EigenVector3d2np(rw.gsHat_B), rw.Js, 0.2)
    fswSetupRW.writeConfigMessage(mrpControlConfig.rwParamsInMsgName, scSim.TotalSim, simProcessName)

    #
    #   set initial Spacecraft States
    #
    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    oe.a     = 10000000.0                                           # meters
    oe.e     = 0.01
    oe.i     = 33.3*macros.D2R
    oe.Omega = 48.2*macros.D2R
    oe.omega = 347.8*macros.D2R
    oe.f     = 85.3*macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    scObject.hub.r_CN_NInit = unitTestSupport.np2EigenVectorXd(rN)  # m   - r_CN_N
    scObject.hub.v_CN_NInit = unitTestSupport.np2EigenVectorXd(vN)  # m/s - v_CN_N
    scObject.hub.sigma_BNInit = [[0.1], [0.2], [-0.3]]              # sigma_CN_B
    scObject.hub.omega_BN_BInit = [[0.001], [-0.01], [0.03]]        # rad/s - omega_CN_B

    # This is a hack because of a bug in Basilisk... leave this line it keeps
    # variables from going out of scope after this function returns
    scSim.additionalReferences = [rwVoltageIO, fswRWVoltageWrap, scObject, earth, rwMotorTorqueWrap, mrpControlWrap, attErrorWrap, inertial3DWrap]

    return scSim

def executeScenario(sim):
    #
    #   initialize Simulation
    #
    sim.InitializeSimulationAndDiscover()

    #
    #   configure a simulation stop time time and execute the simulation run
    #
    sim.ConfigureStopTime(simulationTime)
    sim.ExecuteSimulation()
# This method is used to plot the retained data of a simulation.
# It is called once for each run of the simulation, overlapping the plots
def plotSim(data, retentionPolicy):
    #
    #   retrieve the logged data
    #

    # Get the data from messages using the global data names
    dataUsReq = data["messages"][rwMotorTorqueConfigOutputDataName_motorTorque]
    dataSigmaBR = data["messages"][attErrorConfigOutputDataName_sigma_BR]
    dataOmegaBR = data["messages"][attErrorConfigOutputDataName_omega_BR_B]
    dataPos = data["messages"][sNavObjectOutputTransName_r_BN_N]
    dataOmegaRW = data["messages"][mrpControlConfigInputRWSpeedsName_wheelSpeeds]
    dataVolt = data["messages"][fswRWVoltageConfigVoltageOutMsgName_voltage]

    run_number = data["index"]

    # Use the global keyword to modify global dataframes in the module's scope.
    global time_dataFrame
    global rwMotorTorqueConfigOutputDataName_motorTorque_dataFrame
    global attErrorConfigOutputDataName_sigma_BR_dataFrame
    global attErrorConfigOutputDataName_omega_BR_B_dataFrame
    global sNavObjectOutputTransName_r_BN_N_dataFrame
    global mrpControlConfigInputRWSpeedsName_wheelSpeeds_dataFrame
    global fswRWVoltageConfigVoltageOutMsgName_voltage_dataFrame

    # Update the dataframes by appending the current run to the dataframe
    rwMotorTorqueConfigOutputDataName_motorTorque_dataFrame = updateDataframes(dataUsReq, rwMotorTorqueConfigOutputDataName_motorTorque_dataFrame)
    attErrorConfigOutputDataName_sigma_BR_dataFrame = updateDataframes(dataSigmaBR, attErrorConfigOutputDataName_sigma_BR_dataFrame)
    attErrorConfigOutputDataName_omega_BR_B_dataFrame = updateDataframes(dataOmegaBR, attErrorConfigOutputDataName_omega_BR_B_dataFrame)
    sNavObjectOutputTransName_r_BN_N_dataFrame = updateDataframes(dataPos, sNavObjectOutputTransName_r_BN_N_dataFrame)
    mrpControlConfigInputRWSpeedsName_wheelSpeeds_dataFrame = updateDataframes(dataOmegaRW, mrpControlConfigInputRWSpeedsName_wheelSpeeds_dataFrame)
    fswRWVoltageConfigVoltageOutMsgName_voltage_dataFrame = updateDataframes(dataVolt, fswRWVoltageConfigVoltageOutMsgName_voltage_dataFrame)


def plotSimAndSave(data, retentionPolicy):

    figureList = plotSim(data, retentionPolicy)

    for pltName, plt in figureList.items():
        unitTestSupport.saveScenarioFigure(
            fileNameString + "_" + pltName
            , plt, path)

    return

# Write directories based on monte carlo name and sub directory name
def writeDirectories():
    monteCarloName = "/mc1/"
    mainDirectoryName = "data/"
    path = mainDirectoryName + monteCarloName
    systemWriteDirectories(path)

# Helper function for writing directories
def systemWriteDirectories(path):
    try:
        os.makedirs(path)
    except OSError:
        print "Creating failed, may be a directory there already"
    else:
        print "success"

# This methods adds the next run of the monte carlo below the previous run, with the two runs separated
# by a row of NaN values.
def updateDataframes(data, dataframe):
    df = pd.DataFrame(data, columns=None)

    # Using pd.concat we can put the new run to the right of the current right run instead of below.
    # This is not how datashader needs the data, however it is an example of maniuplating data
    # into a different shape with pandas
    # result = pd.concat([df, dataframe], axis = 1, sort = False)

    # Create a dataframe full of NaN values to append below the previous run and above the next run to append
    nandf = pd.DataFrame([np.nan])
    df = df.append(nandf, ignore_index=True)
    result = df.append(dataframe, ignore_index=True)
    return result

# This method configures the path for each file, and saves the dataframe as a csv
def saveDataframesToFile():

    print "beginning writing csv..", datetime.datetime.now()

    monteCarloName = "/mc1/"
    mainDirectoryName = "data/"

    path = mainDirectoryName + monteCarloName + "/" + rwMotorTorqueConfigOutputDataName_motorTorque + ".csv"
    rwMotorTorqueConfigOutputDataName_motorTorque_dataFrame.to_csv(path, encoding='utf-8', index=False)

    path = mainDirectoryName + monteCarloName + "/" + attErrorConfigOutputDataName_sigma_BR + ".csv"
    attErrorConfigOutputDataName_sigma_BR_dataFrame.to_csv(path, encoding='utf-8', index=False)

    path = mainDirectoryName + monteCarloName + "/" + attErrorConfigOutputDataName_omega_BR_B + ".csv"
    attErrorConfigOutputDataName_omega_BR_B_dataFrame.to_csv(path, encoding='utf-8', index=False)

    path = mainDirectoryName + monteCarloName + "/" + sNavObjectOutputTransName_r_BN_N + ".csv"
    sNavObjectOutputTransName_r_BN_N_dataFrame.to_csv(path, encoding='utf-8', index=False)

    path = mainDirectoryName + monteCarloName + "/" + mrpControlConfigInputRWSpeedsName_wheelSpeeds + ".csv"
    mrpControlConfigInputRWSpeedsName_wheelSpeeds_dataFrame.to_csv(path, encoding='utf-8', index=False)

    path = mainDirectoryName + monteCarloName + "/" + fswRWVoltageConfigVoltageOutMsgName_voltage + ".csv"
    fswRWVoltageConfigVoltageOutMsgName_voltage_dataFrame.to_csv(path, encoding='utf-8', index=False)

    print "done writing csv..", datetime.datetime.now()


# This method is the driver method for graphing all of the data.
def graph():
    for data in retainedDataList:
        configureGraph(data)

# This method reads data from the csv files, and converts them into dataframes. It currently plots
# the data via holoviews framework, and datashades the plot. It passes this plot to the bokeh front end
# where the datashaded plot is used as a basis for the plot in the html file. Since the plot is datashaded,
# the html file is small ~2mbs.

# In addition, this method illustrates how to save the datashaded plots as a stack of images, and then save
# the image as a file.
def configureGraph(data):

    print "Starting graph", datetime.datetime.now()
    # Read csv file and create a dataframe from it.
    # If the user doesn't want to write any data to disc, the user can not write any data
    # and instead just use the global dataframes to plot the data.
    df = pd.read_csv(
        "data/mc1/" + data + ".csv")
    findOutliers(df, data)

    # Plot the columns 1,2,3 against column 0
    curvesx = hv.Curve(df[['0','1']])
    curvesy = hv.Curve(df[['0','2']])
    curvesz = hv.Curve(df[['0','3']])

    # Create a layout consisting of the curves
    layout = curvesx * curvesy * curvesz

    # Instantiate a renderer using bokeh's interface, and generating an html file
    renderer = hv.renderer('bokeh').instance(fig='html')

    # Pass a datashaded version of the layout to the get_plot function, to return a bokeh figure
    # called 'plot'. Then set the figure details such as title, dimensions, axis labels etc.
    # Then finally, show the plot in the browser.
    plot = renderer.get_plot(datashade(layout, dynamic = False).opts(plot=dict(fig_size=1000, aspect='equal'))).state
    plot.plot_width = 800
    plot.plot_height = 500
    plot.title.text = data
    plot.xaxis.axis_label = "Time"
    plot.yaxis.axis_label = data
    # show(plot)

    # Create an empty list of imgs soon to be filled, and set the canvas to put the images on.
    imgs = []
    cvs = ds.Canvas(plot_height=500, plot_width=800)

    # Plot columns 1,2,3 against column 0. Using the count of the overlapping data to create darker colors
    # to indicate density. After every image is created, append it to the list of images. And then created
    # a stacked image, and save it to file via export_image.
    for column in range(1,4):
        agg = cvs.line(df, '0', str(column), ds.count())
        img = tf.shade(agg, how='eq_hist')
        imgs.append(img)

    stacked = tf.stack(*imgs)
    export_image(stacked, data)
    print "done saving png ", data, datetime.datetime.now()


# If working within a jupyter notebook, or using a local server. We can use this example of
# method as an argument for the InteractiveImage method that allows the data to be
# re-aggregated when zooming in.
def image_callback(x_range, y_range, w, h):
    cvs = ds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
    df = pd.read_csv("data/mc1/" + retainedDataList[1]+".csv")
    agg = cvs.line(df, '0', '1', ds.count())
    img = tf.shade(agg)
    tf.shade(agg, how='eq_hist')
    return tf.dynspread(img, threshold=1)

# This method finds the outliers of the dataframe to identify runs with rogue behavior.
def findOutliers(df, data):
    from numpy import mean, std
    from scipy import stats
    # print df.describe()
    col = 1
    print data, df.quantile(.1)
    print data, df.quantile(.99)
    # outliers = df[df[col] > df[col].mean() + 3 * df[col].std()]
    # print outliers


# This method is given a datashader image object, and saves it as a png file under
# a directory called "image".
def export_image(img, filename, fmt=".png", _return=True):
    export_path = "image/"
    if not os.path.exists(export_path):
        os.mkdir(export_path)

    img.to_pil().save(os.path.join(export_path, filename + fmt))
    return img if _return else None

# This statement below ensures that the unit test scrip can be run as a
# stand-along python script
#
if __name__ == "__main__":
    run(  False        # safe figures to file
         , 1
        , True         # show_plots
       )