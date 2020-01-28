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

#
#   Simulation Setup Utilities for RW
#

import sys
import numpy

from . import macros
from Basilisk.simulation import simMessages
from Basilisk.fswAlgorithms import fswMessages
try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict

class rwFactory(object):
    def __init__(self):
        self.BalancedWheels = 0
        self.JitterSimple = 1
        self.JitterFullyCoupled = 2
        self.rwList = OrderedDict()
        self.maxMomentum = 0.0

    def create(self, rwType, gsHat_B, **kwargs):
        """
            This function is called to setup a RW device in python, and adds it to the RW factory
            list rwList{}.  The function returns a copy of the device that can be changed if needed.
            The first 2 arguments are required, the remaining arguments are optional with:

            Parameters
            ----------
            rwType : string
                RW manufacturing name.
            gsHat_B : list
                Spin axis unit vector gsHat in B-frame components
            kwargs :
                Omega : initial RW speed in RPM
                rWB_B : 3x1 list of RW center of mass position coordinates
                RWModel : RW model type such as BalancedWheels, JitterSimple and JitterFullyCoupled
                useRWfriction : BOOL to turn on RW internal wheel friction
                useMinTorque : BOOL to clip any torque below a minimum torque value
                useMaxTorque : BOOL to clip any torque value above a maximum torque value
                maxMomentum : maximum RW wheel momentum in Nms.  This is a required variable for some wheels.
                label : string with the unique device name, must be 5 characters or less
                fCoulomb: double for the Coulomb friction torque model
                fStatic: double for Static friction torque magnitude
                betaStatic: double for Stribeck friction coefficient, positive turns Stribeck friction on, negative turns this friction off
                cViscous: double for Viscous friction coefficient
            Returns
            -------
            RWConfigSimMsg : message structure
                A handle to the RW configuration message
        """

        # create the blank RW object
        RW = simMessages.RWConfigSimMsg()

        # process optional input arguments
        if 'RWModel' in kwargs:
            varRWModel =  kwargs['RWModel']
            if not isinstance(varRWModel, (int)):
                print('ERROR: RWModel must be a INT argument')
                exit(1)
        else:
            varRWModel = self.BalancedWheels    # default value

        if 'useRWfriction' in kwargs:
            varUseRWfriction = kwargs['useRWfriction']
            if not isinstance(varUseRWfriction, (bool)):
                print('ERROR: useRWfriction must be a BOOL argument')
                exit(1)
        else:
            varUseRWfriction = False            # default value

        if 'useMinTorque' in kwargs:
            varUseMinTorque =  kwargs['useMinTorque']
            if not isinstance(varUseMinTorque, (bool)):
                print('ERROR: useMinTorque must be a BOOL argument')
                exit(1)
        else:
            varUseMinTorque = False             # default value

        if 'useMaxTorque' in kwargs:
            varUseMaxTorque =  kwargs['useMaxTorque']
            if not isinstance(varUseMaxTorque, (bool)):
                print('ERROR: useMaxTorque must be a BOOL argument')
                exit(1)
        else:
            varUseMaxTorque = True              # default value

        if 'maxMomentum' in kwargs:
            varMaxMomentum =  kwargs['maxMomentum']
            if not isinstance(varMaxMomentum, (float)):
                print('ERROR: maxMomentum must be a FLOAT argument')
                exit(1)
        else:
            varMaxMomentum = 0.0              # default value
        self.maxMomentum = varMaxMomentum

        if 'fCoulomb' in kwargs:
            varfCoulomb =  kwargs['fCoulomb']
            if not isinstance(varfCoulomb, (float)):
                print('ERROR: fCoulomb must be a FLOAT argument')
                exit(1)
        else:
            varfCoulomb = 0.0       # default value
        RW.fCoulomb = varfCoulomb

        if 'fStatic' in kwargs:
            varfStatic =  kwargs['fStatic']
            if not isinstance(varfStatic, (float)):
                print('ERROR: fStatic must be a FLOAT argument')
                exit(1)
        else:
            varfStatic = 0.0       # default value
        RW.fStatic = varfStatic

        if 'betaStatic' in kwargs:
            varbetaStatic =  kwargs['betaStatic']
            if not isinstance(varbetaStatic, (float)):
                print('ERROR: betaStatic must be a FLOAT argument')
                exit(1)
            if varbetaStatic == 0:
                print('ERROR: betaStatic cannot be set to zero.  Positive turns it on, negative turns it off')
                exit(1)
        else:
            varbetaStatic = -1.0       # default value turns off Stribeck friction model
        RW.betaStatic = varbetaStatic

        if 'cViscous' in kwargs:
            varcViscous =  kwargs['cViscous']
            if not isinstance(varcViscous, (float)):
                print('ERROR: cViscous must be a FLOAT argument')
                exit(1)
        else:
            varcViscous = 0.0       # default value
        RW.cViscous = varcViscous


        # set device label name
        if 'label' in kwargs:
            varLabel = kwargs['label']
            if not isinstance(varLabel, (str)):
                print('ERROR: label must be a string')
                exit(1)
            if len(varLabel) > 5:
                print('ERROR: RW label string is longer than 5 characters')
                exit(1)
        else:
            varLabel = 'RW' + str(len(self.rwList)+1)        # default device labeling
        RW.label = varLabel

        # populate the RW object with the type specific parameters
        try:
            eval('self.' + rwType + '(RW)')
        except:
            print('ERROR: RW type ' + rwType + ' is not implemented')
            exit(1)

        # spin axis gs inertia [kg*m^2]
        RW.Js = self.maxMomentum / (RW.Omega_max)
        RW.Jt = 0.5 * RW.Js
        RW.Jg = RW.Jt

        # set RW axes
        self.setGsHat(RW,gsHat_B)

        # set RW position vector
        if 'rWB_B' in kwargs:
            varrWB_B =  kwargs['rWB_B']
            if not isinstance(varrWB_B, list):
                print('ERROR: rWB_B must be a 3x1 list argument')
                exit(1)
            if not len(varrWB_B) == 3:
                print('ERROR: rWB_B has dimension ' + str(len(varrWB_B)) + ', must be a 3x1 list argument')
                exit(1)
        else:
            varrWB_B = [0., 0., 0.]             # default value
        RW.rWB_B = varrWB_B

        # set initial RW states
        if 'Omega' in kwargs:
            varOmega =  kwargs['Omega']
            if not isinstance(varOmega, (float)):
                print('ERROR: Omega must be a FLOAT argument')
                exit(1)
        else:
            varOmega = 0.0                      # default value
        RW.Omega = varOmega * macros.RPM
        RW.theta = 0.0 * macros.D2R

        # enforce some RW options
        RW.RWModel = varRWModel
        if not varUseRWfriction:
            RW.fCoulomb = 0.0
        if not varUseMaxTorque:
            RW.u_max = -1  # a negative value turns off RW torque saturation
        if not varUseMinTorque:
            RW.u_min = 0.0

        # add RW to the list of RW devices
        self.rwList[varLabel] = RW
        return RW

    def setGsHat(self, RW, gsHat_B):
        """
            Function to set the gsHat_B RW spin axis vector.  This function
            automatically computes to companion transfer axes to complete a
            wheel reference frame.

        :param RW:
        :param gsHat_B:
        """
        # set RW spin axis gsHat
        norm = numpy.linalg.norm(gsHat_B)
        if norm > 1e-10:
            gsHat_B = gsHat_B / norm
        else:
            print('Error: RW gsHat input must be non-zero 3x1 vector')
            exit(1)
        RW.gsHat_B = [[gsHat_B[0]], [gsHat_B[1]], [gsHat_B[2]]]

        # set RW t and g unit axes
        w2Hat0_B = numpy.cross(gsHat_B, [1, 0, 0])
        norm = numpy.linalg.norm(w2Hat0_B)
        if norm < 0.01:
            w2Hat0_B = numpy.cross(gsHat_B, [0, 1, 0])
            norm = numpy.linalg.norm(w2Hat0_B)
        w2Hat0_B = w2Hat0_B / norm
        w3Hat0_B = numpy.cross(gsHat_B, w2Hat0_B)
        RW.w2Hat0_B = [[w2Hat0_B[0]], [w2Hat0_B[1]], [w2Hat0_B[2]]]
        RW.w3Hat0_B = [[w3Hat0_B[0]], [w3Hat0_B[1]], [w3Hat0_B[2]]]

        return

    def addToSpacecraft(self, modelTag, rwStateEffector, scPlus):
        """
            This function should be called after all RW devices are created with createRW()
            It creates the C-class container for the array of RW devices, and attaches
            this container to the spacecraft object

            Parameters
            ----------
            :param modelTag:  string with the model tag
            :param rwStateEffector:
            :param scPlus:
        """

        rwStateEffector.ModelTag = modelTag

        for key, rw in list(self.rwList.items()):
            rwStateEffector.addReactionWheel(rw)

        scPlus.addStateEffector(rwStateEffector)

        return



    def getNumOfDevices(self):
        """
            Returns the number of RW devices setup.

            Returns
            -------
            :return: int
        """
        return len(self.rwList)

    def getConfigMessage(self):
        """
        Returns a RWArrayConfigFswMsg instance based on the current setup.

        :return: rwConfigParams
        """

        GsMatrix_B = []
        JsList = []
        uMaxList = []
        for rw in self.rwList.values():
            
            flatGsHat = [element for sublist in rw.gsHat_B for element in sublist]
            
            GsMatrix_B.extend(flatGsHat)
            JsList.extend([rw.Js])
            uMaxList.extend([rw.u_max])

        rwConfigParams = fswMessages.RWArrayConfigFswMsg()
        rwConfigParams.GsMatrix_B = GsMatrix_B
        rwConfigParams.JsList = JsList
        rwConfigParams.uMax = uMaxList
        rwConfigParams.numRW = len(self.rwList)

        return rwConfigParams

    #
    #   Honeywell HR16 (100Nm, 75Nm, 50Nm)
    #
    #   RW Information Source:
    #   http://www51.honeywell.com/aero/common/documents/Constellation_Series_Reaction_Wheels.pdf
    #
    #   There are 3 momentum capacity options for this RW type.  The maximum momentum
    #   capacity must be set prior to creating the HR16 RW type using
    #       maxMomentum = 100, 75 or 50
    #
    def Honeywell_HR16(self, RW):

        # maximum allowable wheel speed
        RW.Omega_max = 6000.0*macros.RPM
        # maximum RW torque [Nm]
        RW.u_max = 0.200
        # minimum RW torque [Nm]
        RW.u_min = 0.00001
        # static friction torque [Nm]
        RW.fCoulomb = 0.0005
        # RW rotor mass [kg]
        # Note: the rotor mass here is set equal to the RW mass of the above spec sheet.
        # static RW imbalance [kg*m]
        # dynamic RW imbalance [kg*m^2]
        large = 100
        medium = 75
        small = 50

        if self.maxMomentum == large:
            RW.mass = 12.0
            RW.U_s = 4.8E-6
            RW.U_d = 15.4E-7
        elif self.maxMomentum == medium:
            RW.mass = 10.4
            RW.U_s = 3.8E-6
            RW.U_d = 11.5E-7
        elif self.maxMomentum == small:
            RW.mass = 9.0
            RW.U_s = 2.8E-6
            RW.U_d = 7.7E-7
        else:
            if self.maxMomentum > 0:
                print('ERROR: ' + sys._getframe().f_code.co_name + '() does not have a correct wheel momentum of '\
                      +str(large)+', '+str(medium)+' or '+str(small)+' Nm. Provided ' + str(self.maxMomentum) + ' Nm')
            else:
                print('ERROR: ' + sys._getframe().f_code.co_name \
                      + '() maxMomentum option must be set prior to calling createRW()')
            exit(1)

        return


    #
    #   Honeywell HR14 (25Nm, 50Nm, 75Nm)
    #
    #   RW Information Source:
    #   http://www51.honeywell.com/aero/common/documents/Constellation_Series_Reaction_Wheels.pdf
    #
    #   There are 3 momentum capacity options for this RW type.  The maximum momentum
    #   capacity must be set prior to creating the HR14 RW type using
    #       options.maxMomentum = 75, 50 or 25
    #
    def Honeywell_HR14(self, RW):
        # maximum allowable wheel speed
        RW.Omega_max = 6000.0*macros.RPM
        # maximum RW torque [Nm]
        RW.u_max = 0.200
        # minimum RW torque [Nm]
        RW.u_min = 0.00001
        # static friction torque [Nm]
        RW.fCoulomb = 0.0005
        # RW rotor mass [kg]
        # Note: the rotor mass here is set equal to the RW mass of the above spec sheet.
        # static RW imbalance [kg*m]
        # dynamic RW imbalance [kg*m^2]
        large = 75
        medium = 50
        small = 25
        if self.maxMomentum == large:
            RW.mass = 10.6
            RW.U_s = 4.8E-6
            RW.U_d = 13.7E-7
        elif self.maxMomentum == medium:
            RW.mass = 8.5
            RW.U_s = 3.5E-6
            RW.U_d = 9.1E-7
        elif self.maxMomentum == small:
            RW.mass = 7.5
            RW.U_s = 2.2E-6
            RW.U_d = 4.6E-7
        else:
            if self.maxMomentum > 0:
                print('ERROR: ' + sys._getframe().f_code.co_name + '() does not have a correct wheel momentum of '\
                      +str(large)+', '+str(medium)+' or '+str(small)+' Nm. Provided ' + str(self.maxMomentum) + ' Nm')
            else:
                print('ERROR: ' + sys._getframe().f_code.co_name \
                      + '() maxMomentum option must be set prior to calling createRW()')
            exit(1)

        return


    #
    #   Honeywell HR12 (12Nm, 25Nm, 50Nm)
    #
    #   RW Information Source:
    #   http://www51.honeywell.com/aero/common/documents/Constellation_Series_Reaction_Wheels.pdf
    #
    #   There are 3 momentum capacity self for this RW type.  The maximum momentum
    #   capacity must be set prior to creating the HR12 RW type using
    #       maxMomentum = 12, 25 or 50
    #
    def Honeywell_HR12(self, RW):

        # maximum allowable wheel speed
        RW.Omega_max = 6000.0*macros.RPM
        # maximum RW torque [Nm]
        RW.u_max = 0.200
        # minimum RW torque [Nm]
        RW.u_min = 0.00001
        # static friction torque [Nm]
        RW.fCoulomb = 0.0005
        # RW rotor mass [kg]
        # Note: the rotor mass here is set equal to the RW mass of the above spec sheet.
        # static RW imbalance [kg*m]
        # dynamic RW imbalance [kg*m^2]
        large = 50
        medium = 25
        small = 12
        if self.maxMomentum == large:
            RW.mass = 9.5
            RW.U_s = 4.4E-6
            RW.U_d = 9.1E-7
        elif self.maxMomentum == medium:
            RW.mass = 7.0
            RW.U_s = 2.4E-6
            RW.U_d = 4.6E-7
        elif self.maxMomentum == small:
            RW.maxx = 6.0
            RW.U_s = 1.5E-6
            RW.U_d = 2.2E-7
        else:
            if self.maxMomentum > 0:
                print('ERROR: ' + sys._getframe().f_code.co_name + '() does not have a correct wheel momentum of '\
                      +str(large)+', '+str(medium)+' or '+str(small)+' Nm. Provided ' + str(self.maxMomentum) + ' Nm')
            else:
                print('ERROR: ' + sys._getframe().f_code.co_name \
                      + '() maxMomentum option must be set prior to calling createRW()')
            exit(1)

        return


    #
    #   BCT RWP015
    #
    #   RW Information Source:
    #   https://storage.googleapis.com/blue-canyon-tech-news/1/2019/10/BCT_DataSheet_Components_ReactionWheels_F2.pdf
    #
    #   Not complete; fields not listed are estimates.

    def BCT_RWP015(self, RW):

        # maximum allowable wheel speed
        RW.Omega_max = 6000.0*macros.RPM
        # maximum RW torque [Nm]
        RW.u_max = 0.004
        # minimum RW torque [Nm]
        RW.u_min = 0.00001
        # static friction torque [Nm]
        RW.fCoulomb = 0.00005
        # RW rotor mass [kg]
        # Note: the rotor mass here is set equal to the RW mass of the above spec sheet.
        # static RW imbalance [kg*m]
        # dynamic RW imbalance [kg*m^2]

        large = 0.130
        medium = 25
        small = 12
        RW.mass = 0.130
        RW.U_s = 1E-7 # Guestimate
        RW.U_d = 1E-8 # Guestimate

        return
