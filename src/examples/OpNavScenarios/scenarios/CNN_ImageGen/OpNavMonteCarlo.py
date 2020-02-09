import os
import inspect
import scenario_CNNImages as scenario
from BSK_masters import BSKSim, BSKScenario
import BSK_OpNavDynamics, BSK_OpNavFsw
import csv, subprocess, signal

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

from Basilisk import __path__
bskPath = __path__[0]

from Basilisk.utilities.MonteCarlo.Controller import Controller, RetentionPolicy
from Basilisk.utilities.MonteCarlo.Dispersions import OrbitalElementDispersion, MRPDispersionPerAxis, UniformDispersion, NormalVectorCartDispersion
# import simulation related support
from Basilisk.utilities import RigidBodyKinematics as rbk
from Basilisk.utilities import macros
import matplotlib.pyplot as plt
import numpy as np


retainedMessageName1 = "inertial_state_output"
retainedMessageName2 = "circles_data"
retainedRate = macros.sec2nano(10)
var1 = "r_BN_N"
var2 = "sigma_BN"
var3 = "valid"
dataType1 = range(3)
dataType2 = range(3)
dataType3 = range(1)

NUMBER_OF_RUNS = 10
VERBOSE = True
PROCESSES = 1
RUN = True
POST = True

dirName = os.path.abspath(os.path.dirname(__file__)) + "/cnn_MC_data"
if RUN:
    myExecutionFunction = scenario.run
    myCreationFunction = scenario.scenario_OpNav

    monteCarlo = Controller()
    monteCarlo.setShouldDisperseSeeds(True)
    monteCarlo.setExecutionFunction(myExecutionFunction)
    monteCarlo.setSimulationFunction(myCreationFunction)
    monteCarlo.setExecutionCount(NUMBER_OF_RUNS)
    monteCarlo.setThreadCount(PROCESSES)
    monteCarlo.setVerbose(True)
    monteCarlo.setArchiveDir(dirName)

    # Add some dispersions
    dispDict = {}
    dispDict["mu"] = 4.2828371901284001E+13
    dispDict["a"] = ["normal", 14000*1E3, 2500*1E3] # 12000
    dispDict["e"] = ["uniform", 0.2, 0.5]           # 0.4, 0.7
    dispDict["i"] = ["uniform", np.deg2rad(40), np.deg2rad(90)]
    dispDict["Omega"] = None
    dispDict["omega"] = None
    dispDict["f"] = ["uniform", np.deg2rad(0), np.deg2rad(359)]

    disp1Name = 'get_DynModel().scObject.hub.r_CN_NInit'
    disp2Name = 'get_DynModel().scObject.hub.v_CN_NInit'
    disp3Name = 'get_FswModel().trackingErrorCamData.sigma_R0R'
    dispGauss = 'get_DynModel().cameraMod.gaussian'
    dispDC = 'get_DynModel().cameraMod.darkCurrent'
    dispSP = 'get_DynModel().cameraMod.saltPepper'
    dispCR = 'get_DynModel().cameraMod.cosmicRays'
    dispBlur = 'get_DynModel().cameraMod.blurParam'

    monteCarlo.addDispersion(OrbitalElementDispersion(disp1Name,disp2Name, dispDict))
    monteCarlo.addDispersion(MRPDispersionPerAxis(disp3Name, bounds=[[1./3-0.051, 1./3+0.051], [1./3-0.051, 1./3+0.051], [-1./3-0.051, -1./3+0.051]]))
    monteCarlo.addDispersion(UniformDispersion(dispGauss, [0,5]))
    monteCarlo.addDispersion(UniformDispersion(dispSP, [0,2.5]))
    monteCarlo.addDispersion(UniformDispersion(dispCR, [0.5,4]))
    monteCarlo.addDispersion(UniformDispersion(dispBlur, [1,6]))

    # Add retention policy
    retentionPolicy = RetentionPolicy()
    retentionPolicy.addMessageLog(retainedMessageName1, [(var1, dataType1), (var2, dataType2)], retainedRate)
    retentionPolicy.addMessageLog(retainedMessageName2, [(var3, dataType3)], retainedRate)
    monteCarlo.addRetentionPolicy(retentionPolicy)

    failures = monteCarlo.executeSimulations()
    assert len(failures) == 0, "No runs should fail"

if POST:
    monteCarlo = Controller.load(dirName)
    for i in range(0,NUMBER_OF_RUNS):
        try:
            monteCarloData = monteCarlo.getRetainedData(i)
        except FileNotFoundError:
            print("File not found, ",  i)
            continue
        csvfile = open(dirName + "/run" + str(i) + "/data.csv", 'w')
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Valid', 'X_p', 'Y_p', 'rho_p', 'r_BN_N_1', 'r_BN_N_2', 'r_BN_N_3'])

        position_N = np.array(monteCarloData["messages"]["inertial_state_output.r_BN_N"])
        sigma_BN = np.array(monteCarloData["messages"]["inertial_state_output.sigma_BN"])
        validCircle = np.array(monteCarloData["messages"]["circles_data.valid"])

        renderRate = 60*1E9
        sigma_CB = [0., 0., 0.]  # Arbitrary camera orientation
        sizeOfCam = [512, 512]
        sizeMM = [10. * 1E-3, 10. * 1E-3]  # in m
        fieldOfView = np.deg2rad(55)  # in degrees
        focal = sizeMM[0] / 2. / np.tan(fieldOfView / 2.)  # in m

        pixelSize = []
        pixelSize.append(sizeMM[0] / sizeOfCam[0])
        pixelSize.append(sizeMM[1] / sizeOfCam[1])

        dcm_CB = rbk.MRP2C(sigma_CB)
        # Plot results

        trueRhat_C = np.full([len(validCircle[:, 0]), 4], np.nan)
        trueCircles = np.full([len(validCircle[:, 0]), 4], np.nan)
        trueCircles[:, 0] = validCircle[:, 0]
        trueRhat_C[:, 0] = validCircle[:, 0]

        ModeIdx = 0
        Rmars = 3396.19 * 1E3
        for j in range(len(position_N[:, 0])):
            if position_N[j, 0] in validCircle[:, 0]:
                ModeIdx = j
                break
        for i in range(len(validCircle[:, 0])):
            if validCircle[i, 1] > 1E-5 or (validCircle[i, 0]%renderRate ==0 and validCircle[i, 0] > 1):
                trueRhat_C[i, 1:] = np.dot(np.dot(dcm_CB, rbk.MRP2C(sigma_BN[ModeIdx + i, 1:4])),
                                           position_N[ModeIdx + i, 1:4]) / np.linalg.norm(position_N[ModeIdx + i, 1:4])
                trueCircles[i, 3] = focal * np.tan(np.arcsin(Rmars / np.linalg.norm(position_N[ModeIdx + i, 1:4]))) / pixelSize[0]
                trueRhat_C[i, 1:] *= focal / trueRhat_C[i, 3]
                trueCircles[i, 1] = trueRhat_C[i, 1] / pixelSize[0] + sizeOfCam[0] / 2 - 0.5
                trueCircles[i, 2] = trueRhat_C[i, 2] / pixelSize[1] + sizeOfCam[1] / 2 - 0.5

                writer.writerow([str("{0:.6f}".format(position_N[i,0]*1E-9))+".jpg", validCircle[i, 1], trueCircles[i, 1], trueCircles[i, 2], trueCircles[i, 3], position_N[i,1], position_N[i,2], position_N[i,3]])
        csvfile.close()

