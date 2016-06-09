'''
Copyright (c) 2016, Autonomous Vehicle Systems Lab, Univeristy of Colorado at Boulder

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
import sys, os, inspect

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
sys.path.append(path + '/../PythonModules/')
import AVSSim
import matplotlib.pyplot as plt
import ctypes
import math
import MessagingAccess
import sim_model
import logging
import numpy as np
import macros as mc
import astroFunctions as af
import RigidBodyKinematics as rbk
from numpy import linalg as la

# ------------------- PLOTS ------------------- #

def plotRV_mag(r_BN_N, v_BN_N):
    t = r_BN_N[:, 0]
    r = np.array([])
    v = np.array([])
    for i in range(len(t)):
        r = np.append(r, la.norm(r_BN_N[i, 1:]))
        v = np.append(v, la.norm(v_BN_N[i, 1:]))
    print 'R_mag = ', r
    print 'V_mag = ', v
    print 'Initial Pos Vec: ', r_BN_N[0,:]
    print 'Final Pos Vec: ', r_BN_N[len(t)-1,:]
    print '\n'
    plt.figure(0)
    plt.plot(t * 1E-9, r * 1E-3, 'b')
    plt.legend(['Pos Mag [km]', 'Vel Mag [km/s]'])
    plt.figure(1)
    plt.plot(t * 1E-9, v * 1E-3, 'g')
    plt.title('Pos Mag [km]')
    plt.figure(2)
    plt.plot(t * 1E-9, r, 'b', t * 1E-9, v, 'g')
    plt.title('Vel Mag [km/s]')

def plotRotNav(sigma_BN, omega_BN_B):
    print 'sigma_BN = ', sigma_BN[:, 1:]
    print 'omega_BN_N = ', omega_BN_B[:, 1:]
    print '\n'

    plt.figure(5)
    plt.ylim([-1.0, 1.0])
    plt.plot(sigma_BN[:, 0] * 1E-9, sigma_BN[:, 1]
             , sigma_BN[:, 0] * 1E-9, sigma_BN[:, 2]
             , sigma_BN[:, 0] * 1E-9, sigma_BN[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\sigma_{BN}$')
    plt.figure(6)
    plt.plot(omega_BN_B[:, 0] * 1E-9, omega_BN_B[:, 1]
             , omega_BN_B[:, 0] * 1E-9, omega_BN_B[:, 2]
             , omega_BN_B[:, 0] * 1E-9, omega_BN_B[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\omega_{BN, B}$')

def plotReference(sigma_RN, omega_RN_N):
    print 'sigma_RN = ', sigma_RN[:, 1:]
    print 'omega_RN_N = ', omega_RN_N[:, 1:]
    print '\n'

    plt.figure(10)
    plt.ylim([-1.0, 1.0])
    plt.plot(sigma_RN[:, 0] * 1E-9, sigma_RN[:, 1]
             , sigma_RN[:, 0] * 1E-9, sigma_RN[:, 2]
             , sigma_RN[:, 0] * 1E-9, sigma_RN[:, 3])

    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\sigma_{RN}$')
    plt.figure(11)
    plt.plot(omega_RN_N[:, 0] * 1E-9, omega_RN_N[:, 1]
             , omega_RN_N[:, 0] * 1E-9, omega_RN_N[:, 2]
             , omega_RN_N[:, 0] * 1E-9, omega_RN_N[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\omega_{RN, N}$')

def plotBaseReference(sigma_R0N, omega_R0N_N):
    print 'sigma_R0N = ', sigma_R0N[:, 1:]
    print 'omega_R0N_N = ', omega_R0N_N[:, 1:]
    print '\n'

    plt.figure(30)
    plt.ylim([-1.0, 1.0])
    plt.plot(sigma_R0N[:, 0] * 1E-9, sigma_R0N[:, 1]
             , sigma_R0N[:, 0] * 1E-9, sigma_R0N[:, 2]
             , sigma_R0N[:, 0] * 1E-9, sigma_R0N[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title('BaseRef: $\sigma_{R0N}$')
    plt.figure(31)
    plt.plot(omega_R0N_N[:, 0] * 1E-9, omega_R0N_N[:, 1]
             , omega_R0N_N[:, 0] * 1E-9, omega_R0N_N[:, 2]
             , omega_R0N_N[:, 0] * 1E-9, omega_R0N_N[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title('BaseRef: $\omega_{R0N, N}$')

def plotTrackingError(sigma_BR, omega_BR_B):
    print 'sigma_BR = ', sigma_BR[:, 1:]
    print 'omega_BR_B = ', omega_BR_B[:, 1:]
    print '\n'

    plt.figure(20)
    plt.plot(sigma_BR[:, 0] * 1E-9, sigma_BR[:, 1]
             , sigma_BR[:, 0] * 1E-9, sigma_BR[:, 2]
             ,sigma_BR[:, 0] * 1E-9, sigma_BR[:, 3])
    plt.ylim([-1.0, 1.0])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\sigma_{BR}$')
    plt.figure(21)
    plt.plot(omega_BR_B[:, 0] * 1E-9, omega_BR_B[:, 1]
             , omega_BR_B[:, 0] * 1E-9, omega_BR_B[:, 2]
             , omega_BR_B[:, 0] * 1E-9, omega_BR_B[:, 3])
    plt.legend(['$x_1$', '$x_2$', '$x_3$'])
    plt.title(TheAVSSim.modeRequest + ': $\omega_{BR, B}$')


# ------------------- MAIN ------------------- #

def executeGuidance(TheAVSSim):
    def doubleTest(mode1, mode2):
        TheAVSSim.modeRequest = mode1
        print '\n Mode Request = ', TheAVSSim.modeRequest
        TheAVSSim.ConfigureStopTime(int(60 * 10 * 2 * 1E9))
        TheAVSSim.ExecuteSimulation()

        TheAVSSim.modeRequest = mode2
        print '\n Mode Request = ', TheAVSSim.modeRequest
        TheAVSSim.ConfigureStopTime(int(60 * 20 * 4 * 1E9))
        TheAVSSim.ExecuteSimulation()
    def singleTest(mode):
        TheAVSSim.modeRequest = mode
        print '\n Mode Request = ', TheAVSSim.modeRequest
        TheAVSSim.ConfigureStopTime(int(60 * 20 * 4 * 1E9))
        TheAVSSim.ExecuteSimulation()

    # hillPoint Data:
    TheAVSSim.hillPointData.outputDataName = "att_ref_output"
    # inertial3DPoint Data:
    TheAVSSim.inertial3DData.outputDataName = "att_ref_output"
    # velocityPoint Data:
    TheAVSSim.velocityPointData.mu = TheAVSSim.VehOrbElemObject.mu
    # axisScan Data:
    TheAVSSim.axisScanData.psiDot = 0.2
    #TheAVSSim.axisScanData.psi0 = 0.1
    # cel2BdyPoint Data:
    TheAVSSim.celTwoBodyPointData.inputCelMessName = "mars_display_frame_data"
    #TheAVSSim.celTwoBodyPointData.inputSecMessName = "sun_display_frame_data"
    # orbitAxisSpin Data:
    TheAVSSim.orbitAxisSpinData.o_spin = 2
    TheAVSSim.orbitAxisSpinData.b_spin = 0
    TheAVSSim.orbitAxisSpinData.omega_spin = 0.1

    # Initialize SIM:
    TheAVSSim.InitializeSimulation()
    TheAVSSim.ConfigureStopTime(int(1 * 1E9))
    TheAVSSim.ExecuteSimulation()

    #singleTest('inertial3DSpin')
    #singleTest('inertial3DPoint')
    #doubleTest('inertial3DPoint', 'inertial3DSpin')
    #doubleTest('hillPoint', 'velocityPoint')
    #singleTest('orbitAxisSpin')
    #doubleTest('velocityPoint', 'orbitAxisSpin')
    #singleTest('hillPoint')
    #singleTest('velocityPoint')
    #singleTest('celTwoBodyPoint')
    #doubleTest('hillPoint', 'celTwoBodyPoint')
    #singleTest('singleAxisSpin')
    #singleTest('axisScan')
    singleTest('singleAxisSpin')

if __name__ == "__main__":
    TheAVSSim = AVSSim.AVSSim()
    TheAVSSim.TotalSim.logThisMessage("att_ref_output_stage1", int(1E9))
    TheAVSSim.TotalSim.logThisMessage("OrbitalElements", int(1E9))
    TheAVSSim.TotalSim.logThisMessage("simple_nav_output", int(1E9))
    TheAVSSim.TotalSim.logThisMessage("att_ref_output", int(1E9))
    TheAVSSim.TotalSim.logThisMessage("nom_att_guid_out", int(1E9))

    TheAVSSim.VehDynObject.GravData[0].IsCentralBody = False
    TheAVSSim.VehDynObject.GravData[0].IsDisplayBody = False
    TheAVSSim.VehDynObject.GravData[2].IsCentralBody = True
    TheAVSSim.VehDynObject.GravData[2].IsDisplayBody = True
    TheAVSSim.SpiceObject.zeroBase = "mars"
    TheAVSSim.SpiceObject.referenceBase = "MARSIAU"
    TheAVSSim.VehOrbElemObject.mu = TheAVSSim.MarsGravBody.mu

    TheAVSSim.VehOrbElemObject.CurrentElem.a = af.M_radius * 2.8 * 1000.0
    TheAVSSim.VehOrbElemObject.CurrentElem.e = 0.0
    TheAVSSim.VehOrbElemObject.CurrentElem.i = 0.0 * math.pi / 180.0
    TheAVSSim.VehOrbElemObject.CurrentElem.Omega = 0.0
    TheAVSSim.VehOrbElemObject.CurrentElem.omega = 0.0
    TheAVSSim.VehOrbElemObject.CurrentElem.f = 70.0 * math.pi / 180.0

    # Convert those OEs to cartesian
    TheAVSSim.VehOrbElemObject.Elements2Cartesian()
    PosVec = ctypes.cast(TheAVSSim.VehOrbElemObject.r_N.__long__(),
                         ctypes.POINTER(ctypes.c_double))
    VelVec = ctypes.cast(TheAVSSim.VehOrbElemObject.v_N.__long__(),
                         ctypes.POINTER(ctypes.c_double))
    TheAVSSim.VehDynObject.PositionInit = sim_model.DoubleVector([PosVec[0], PosVec[1], PosVec[2]])
    TheAVSSim.VehDynObject.VelocityInit = sim_model.DoubleVector([VelVec[0], VelVec[1], VelVec[2]])

    executeGuidance(TheAVSSim)

    P = af.orbitalPeriod(TheAVSSim.VehOrbElemObject.CurrentElem.a, TheAVSSim.VehOrbElemObject.mu)
    n = 2 * np.pi / P
    print '\n'
    print 'Orbital Period [days] = ', P * af.SEC2DAY
    print 'Orbital Mean Motiom [rad/s]', n
    print 'Mars Orbit Eccentricity = ', TheAVSSim.VehOrbElemObject.CurrentElem.e
    print 'Mars Orbit Inclination = ', TheAVSSim.VehOrbElemObject.CurrentElem.i
    print '\n'

    r_BN_N = TheAVSSim.pullMessageLogData("simple_nav_output.r_BN_N", range(3))
    v_BN_N = TheAVSSim.pullMessageLogData("simple_nav_output.v_BN_N", range(3))
    #plotRV_mag(r_BN_N, v_BN_N)

    sigma_BN = TheAVSSim.pullMessageLogData("simple_nav_output.sigma_BN", range(3))
    omega_BN_B = TheAVSSim.pullMessageLogData("simple_nav_output.omega_BN_B", range(3))
    #plotRotNav(sigma_BN, omega_BN_B)


    sigma_RN = TheAVSSim.pullMessageLogData("att_ref_output.sigma_RN", range(3))
    omega_RN_N = TheAVSSim.pullMessageLogData("att_ref_output.omega_RN_N", range(3))
    domega_RN_N = TheAVSSim.pullMessageLogData("att_ref_output.domega_RN_N", range(3))
    plotReference(sigma_RN, omega_RN_N)

    if TheAVSSim.modeRequest == 'orbitAxisSpin' or TheAVSSim.modeRequest == 'axisScan':
        sigma_R0N = TheAVSSim.pullMessageLogData("att_ref_output_stage1.sigma_RN", range(3))
        omega_R0N_N = TheAVSSim.pullMessageLogData("att_ref_output_stage1.omega_RN_N", range(3))
        domega_R0N_N = TheAVSSim.pullMessageLogData("att_ref_output_stage1.domega_RN_N", range(3))
        plotBaseReference(sigma_R0N, omega_R0N_N)

    sigma_BR = TheAVSSim.pullMessageLogData("nom_att_guid_out.sigma_BR", range(3))
    omega_BR_B = TheAVSSim.pullMessageLogData("nom_att_guid_out.omega_BR_B", range(3))
    omega_RN_B = TheAVSSim.pullMessageLogData("nom_att_guid_out.omega_RN_B", range(3))
    domega_RN_B = TheAVSSim.pullMessageLogData("nom_att_guid_out.domega_RN_B", range(3))
    plotTrackingError(sigma_BR, omega_BR_B)

    plt.show()