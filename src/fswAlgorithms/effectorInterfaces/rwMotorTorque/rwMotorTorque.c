/*
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

 */
/*
    Mapping required attitude control torque Lr to RW motor torques

 */

/* modify the path to reflect the new module names */
#include "effectorInterfaces/rwMotorTorque/rwMotorTorque.h"

/* update this include to reflect the required module input messages */
#include "simFswInterfaceMessages/macroDefinitions.h"
#include <string.h>


/*
 Pull in support files from other modules.  Be sure to use the absolute path relative to Basilisk directory.
 */
#include "simulation/utilities/linearAlgebra.h"
#include "simulation/utilities/bsk_Print.h"

/*! This method initializes the ConfigData for this module.
 It checks to ensure that the inputs are sane and then creates the
 output message
 @return void
 @param ConfigData The configuration data associated with this module
 @param moduleID The Basilisk module identifier
 */
void SelfInit_rwMotorTorque(rwMotorTorqueConfig *ConfigData, uint64_t moduleID)
{
    /*! Begin method steps */
    /*! - Create output message for module */
    ConfigData->outputMsgID = CreateNewMessage(ConfigData->outputDataName,
                                               sizeof(RWArrayTorqueIntMsg),
                                               "RWArrayTorqueIntMsg",          /* add the output structure name */
                                               moduleID);
}

/*! This method performs the second stage of initialization for this module.
 It's primary function is to link the input messages that were created elsewhere.
 @return void
 @param ConfigData The configuration data associated with this module
 @param moduleID The Basilisk module identifier
 */
void CrossInit_rwMotorTorque(rwMotorTorqueConfig *ConfigData, uint64_t moduleID)
{
    /*! - Get the input message ID's */
    ConfigData->inputVehControlID = subscribeToMessage(ConfigData->inputVehControlName,
                                                       sizeof(CmdTorqueBodyIntMsg), moduleID);
    ConfigData->rwParamsInMsgID = subscribeToMessage(ConfigData->rwParamsInMsgName,
                                                     sizeof(RWArrayConfigFswMsg), moduleID);
    ConfigData->rwAvailInMsgID = -1;
    if (strlen(ConfigData->rwAvailInMsgName) > 0){
        ConfigData->rwAvailInMsgID = subscribeToMessage(ConfigData->rwAvailInMsgName,
                                                         sizeof(RWAvailabilityFswMsg), moduleID);
    }

}

/*! This method performs a complete reset of the module.  Local module variables that retain
 time varying states between function calls are reset to their default values.
 @return void
 @param ConfigData The configuration data associated with the module
 @param moduleID The Basilisk module identifier
 */
void Reset_rwMotorTorque(rwMotorTorqueConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    uint64_t timeOfMsgWritten;
    uint32_t sizeOfMsgWritten;
    int i;
    
    /* configure the number of axes that are controlled */
    double *pAxis; /*!< pointer to the current control axis */
    ConfigData->numControlAxes = 0;
    for (i = 0; i < 3; i++)
    {
        pAxis = ConfigData->controlAxes_B + 3 * ConfigData->numControlAxes;
        if (v3Norm(pAxis) > 0.0) {
            ConfigData->numControlAxes += 1;
        }
    }
    if (ConfigData->numControlAxes == 0) {
        BSK_PRINT(MSG_WARNING,"rwMotorTorque() is not setup to control any axes!\n"); // Should this be a hard fail?
    }
    
    /*! - Read static RW config data message and store it in module variables */
    ReadMessage(ConfigData->rwParamsInMsgID, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(RWArrayConfigFswMsg), &(ConfigData->rwConfigParams), moduleID);
    
    if (ConfigData->rwAvailInMsgID < 0){
        /* If no info is provided about RW availability we'll assume that all are available */
        ConfigData->numAvailRW =ConfigData->rwConfigParams.numRW;
        for (i = 0; i < ConfigData->rwConfigParams.numRW; i++){
            v3Copy(&ConfigData->rwConfigParams.GsMatrix_B[i * 3], &ConfigData->GsMatrixAvail_B[i * 3]);
        }
    }
}

/*! Add a description of what this main Update() routine does for this module
 @return void
 @param ConfigData The configuration data associated with the module
 @param callTime The clock time at which the function was called (nanoseconds)
 @param moduleID The Basilisk module identifier
 */
void Update_rwMotorTorque(rwMotorTorqueConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    /*! - Read the input messages */
    uint64_t timeOfMsgWritten;
    uint32_t sizeOfMsgWritten;
    
    /*! Begin method steps*/
    int i,j,k;
    int numAvailRW = 0;
    double us[MAX_EFF_CNT];
    double Lr_B[3]; /*!< [Nm]    commanded ADCS control torque */
    double Lr_C[3]; /*!< [Nm]    commanded ADCS control torque in the control frame */
    double CGs[3][MAX_EFF_CNT]; /*!< Mapping matrix between control and wheel frame */
    
    RWAvailabilityFswMsg wheelsAvailability;

    vSetZero(us, MAX_EFF_CNT);
    
    v3SetZero(Lr_B);
    ReadMessage(ConfigData->inputVehControlID, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(CmdTorqueBodyIntMsg), (void*) &(Lr_B), moduleID);
    
    /* Lr is assumed to be a positive torque onto the body */
    v3Scale(-1.0, Lr_B, Lr_B);
    
    if (ConfigData->rwAvailInMsgID >= 0){
        memset(&wheelsAvailability, 0x0, sizeof(RWAvailabilityFswMsg));
        ReadMessage(ConfigData->rwAvailInMsgID, &timeOfMsgWritten, &sizeOfMsgWritten,
                    sizeof(RWAvailabilityFswMsg), (void*) &wheelsAvailability, moduleID);
        
        for (i = 0; i < ConfigData->rwConfigParams.numRW; i++) {
            if (wheelsAvailability.wheelAvailability[i] == AVAILABLE){
                v3Copy(&ConfigData->rwConfigParams.GsMatrix_B[i * 3], &ConfigData->GsMatrixAvail_B[numAvailRW * 3]);
                numAvailRW += 1;
            }
            ConfigData->numAvailRW = numAvailRW;
        }
    }
    
    /* Compute minimum norm inverse for us = [CGs].T inv([CGs][CGs].T) [Lr_C] */
    /* Having at least the same # of RW as # of control axes is necessary condition to guarantee inverse matrix exists */
    /* If matrix to invert it not full rank, the control torque output is zero. */
    if (ConfigData->numAvailRW >= ConfigData->numControlAxes){
        double M[3][3];         /* [M] = [CGs][CGs].T */
        double v3_temp[3];      /* v3_temp = inv([M]) [Lr_C] */
        double us_avail[MAX_EFF_CNT];
        
        v3SetZero(v3_temp);
        vSetZero(us_avail, MAX_EFF_CNT);
        
        /* compute Lr_C = [C]Lr */
        /* compute [CGs] */
        for (i=0; i<ConfigData->numControlAxes; i++){
            Lr_C[i] = v3Dot(ConfigData->controlAxes_B + 3 * i, Lr_B);
            for (j=0; j<ConfigData->numAvailRW; j++) {
                CGs[i][j] = v3Dot(&ConfigData->GsMatrixAvail_B[j * 3], &ConfigData->controlAxes_B[3 * i]);
            }
        }

        if (ConfigData->numControlAxes > 0 && ConfigData->numControlAxes <= 3) // Uncertain if we need to impose the upper limit technically.
        {
            for (i=0; i<ConfigData->numControlAxes; i++) {
                for (j=0; j<ConfigData->numControlAxes; j++) {
                    M[i][j] = 0.0;
                    for (k=0; k < ConfigData->numAvailRW; k++) {
                        M[i][j] += CGs[i][k]*CGs[j][k];
                    }
                }
            }
            mInverse(M, ConfigData->numControlAxes, M);
            mMultV(M, ConfigData->numControlAxes, ConfigData->numControlAxes, Lr_C, v3_temp);
        }
        
        /* compute the RW motor torques */
        /* us = [CGs].T v3_temp */
        for (i=0; i<ConfigData->numAvailRW; i++) {
            for (j=0; j<ConfigData->numControlAxes; j++) {
                us_avail[i] += CGs[j][i] * v3_temp[j];
            }
        }
        
        int i_torque = 0;
        for (i = 0; i < ConfigData->rwConfigParams.numRW; i++) {
            if (wheelsAvailability.wheelAvailability[i] == AVAILABLE)
            {
                us[i] = us_avail[i_torque];
                i_torque += 1;
            }
        }
    }

    /* store the output message */
    mCopy(us, ConfigData->rwConfigParams.numRW, 1, ConfigData->rwMotorTorques.motorTorque);
    WriteMessage(ConfigData->outputMsgID, callTime, sizeof(RWArrayTorqueIntMsg),
                 (void*) &(ConfigData->rwMotorTorques), moduleID);

    return;
}


