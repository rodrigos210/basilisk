/*
 ISC License

 Copyright (c) 2016-2017, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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
    FSW MODULE: RW motor voltage command
 
 */

/* modify the path to reflect the new module names */
#include "effectorInterfaces/rwMotorVoltage/rwMotorVoltage.h"

/* update this include to reflect the required module input messages */
#include "SimFswInterfaceMessages/macroDefinitions.h"



/*
 Pull in support files from other modules.  Be sure to use the absolute path relative to Basilisk directory.
 */
#include "SimCode/utilities/linearAlgebra.h"
#include <string.h>


/*! This method initializes the ConfigData for this module.
 It checks to ensure that the inputs are sane and then creates the
 output message
 @return void
 @param ConfigData The configuration data associated with this module
 */
void SelfInit_rwMotorVoltage(rwMotorVoltageConfig *ConfigData, uint64_t moduleID)
{
    
    /*! Begin method steps */
    /*! - Create output message for module */
    ConfigData->voltageOutMsgID = CreateNewMessage(ConfigData->voltageOutMsgName,
                                               sizeof(RWArrayVoltageMessage),
                                               "RWArrayVoltageMessage",          /* add the output structure name */
                                               moduleID);
}

/*! This method performs the second stage of initialization for this module.
 It's primary function is to link the input messages that were created elsewhere.
 @return void
 @param ConfigData The configuration data associated with this module
 */
void CrossInit_rwMotorVoltage(rwMotorVoltageConfig *ConfigData, uint64_t moduleID)
{
    /*! - Get the control data message ID*/
    ConfigData->torqueInMsgID = subscribeToMessage(ConfigData->torqueInMsgName,
                                                sizeof(RWArrayTorqueMessage),
                                                moduleID);
    ConfigData->rwParamsInMsgID = -1;
    ConfigData->inputRWSpeedsInMsgID = -1;
    ConfigData->rwAvailInMsgID = -1;

    ConfigData->rwParamsInMsgID = subscribeToMessage(ConfigData->rwParamsInMsgName,
                                                     sizeof(RWArrayConfigFswMsg), moduleID);
    if (strlen(ConfigData->inputRWSpeedsInMsgName) > 0) {
        ConfigData->inputRWSpeedsInMsgID = subscribeToMessage(ConfigData->inputRWSpeedsInMsgName,
                                                         sizeof(RWSpeedMessage), moduleID);
    }
    if(strlen(ConfigData->rwAvailInMsgName) > 0) {
        ConfigData->rwAvailInMsgID = subscribeToMessage(ConfigData->rwAvailInMsgName,
                                                        sizeof(RWAvailabilityFswMsg), moduleID);
    }
}

/*! This method performs a complete reset of the module.  Local module variables that retain
 time varying states between function calls are reset to their default values.
 @return void
 @param ConfigData The configuration data associated with the module
 */
void Reset_rwMotorVoltage(rwMotorVoltageConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    uint64_t clockTime;
    uint32_t readSize;

    /*! - Read static RW config data message and store it in module variables*/
    ReadMessage(ConfigData->rwParamsInMsgID, &clockTime, &readSize,
                sizeof(RWArrayConfigFswMsg), &(ConfigData->rwConfigParams), moduleID);

    /* reset variables */
    memset(ConfigData->rwSpeedOld, 0, sizeof(double)*MAX_EFF_CNT);
    ConfigData->resetFlag = BOOL_TRUE;

    /* Reset the prior time flag state.
     If zero, control time step not evaluated on the first function call */
    ConfigData->priorTime = 0;

}

/*! Add a description of what this main Update() routine does for this module
 @return void
 @param ConfigData The configuration data associated with the module
 @param callTime The clock time at which the function was called (nanoseconds)
 */
void Update_rwMotorVoltage(rwMotorVoltageConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    uint64_t            clockTime;
    uint32_t            readSize;
    uint32_t            rwArrayMemorySize;
    double              voltage[MAX_EFF_CNT];       /*!< [V]   RW voltage output commands */
    RWSpeedMessage      rwSpeed;                    /*!< [r/s] Reaction wheel speed estimates */
    RWAvailabilityFswMsg  rwAvailability;             /*!< []    Reaction wheel availability */
    double              dt;                         /*!< [s]   control update period */
    double              Omega_dot[MAX_EFF_CNT];     /*!< [r/s^2] RW angular acceleration */
    double              torqueCmd[MAX_EFF_CNT];     /*!< [Nm]   copy of RW motor torque input vector */
    int                 i;

    /* - Read the input messages */
    ReadMessage(ConfigData->torqueInMsgID, &clockTime, &readSize,
                sizeof(RWArrayTorqueMessage), (void*) torqueCmd, moduleID);
    if (ConfigData->inputRWSpeedsInMsgID >= 0) {
        ReadMessage(ConfigData->inputRWSpeedsInMsgID, &clockTime, &readSize,
                    sizeof(RWSpeedMessage), (void*) &(rwSpeed), moduleID);
    }
    memset(rwAvailability.wheelAvailability, 0x0, MAX_EFF_CNT * sizeof(int)); // wheelAvailability set to 0 (AVAILABLE) by default
    if (ConfigData->rwAvailInMsgID >= 0){
        ReadMessage(ConfigData->rwAvailInMsgID, &clockTime, &readSize,
                    sizeof(RWAvailabilityFswMsg), &rwAvailability, moduleID);
    }

    /* zero the output voltage vector */
    memset(voltage, 0, sizeof(double)*MAX_EFF_CNT);

    /* compute the often used double array size of RW double values */
    rwArrayMemorySize = ConfigData->rwConfigParams.numRW*sizeof(double);

    /* if the torque closed-loop is on, evaluate the feedback term */
    if (ConfigData->inputRWSpeedsInMsgID >= 0) {
        /* make sure the clock didn't just initialize, or the module was recently reset */
        if (ConfigData->priorTime != 0) {
            dt = (callTime - ConfigData->priorTime) * NANO2SEC;
            for (i=0;i<ConfigData->rwConfigParams.numRW;i++) {
                if (rwAvailability.wheelAvailability[i] == AVAILABLE && ConfigData->resetFlag == BOOL_FALSE) {
                    Omega_dot[i] = (rwSpeed.wheelSpeeds[i] - ConfigData->rwSpeedOld[i])/dt;
                    torqueCmd[i] -= ConfigData->K * (ConfigData->rwConfigParams.JsList[i] * Omega_dot[i] - torqueCmd[i]);
                }
                ConfigData->rwSpeedOld[i] = rwSpeed.wheelSpeeds[i];
            }
            ConfigData->resetFlag = BOOL_FALSE;
        }
        ConfigData->priorTime = callTime;
    }

    /* evaluate the feedforward mapping of torque into voltage */
    for (i=0;i<ConfigData->rwConfigParams.numRW;i++) {
        if (rwAvailability.wheelAvailability[i] == AVAILABLE) {
            voltage[i] = (ConfigData->VMax - ConfigData->VMin)/ConfigData->rwConfigParams.uMax[i]
                        * torqueCmd[i];
            if (voltage[i]>0.0) voltage[i] += ConfigData->VMin;
            if (voltage[i]<0.0) voltage[i] -= ConfigData->VMin;
        }
    }

    /* check for voltage saturation */
    for (i=0;i<ConfigData->rwConfigParams.numRW;i++) {
        if (voltage[i] > ConfigData->VMax) {
            voltage[i] = ConfigData->VMax;
        }
        if (voltage[i] < -ConfigData->VMax) {
            voltage[i] = -ConfigData->VMax;
        }
    }

    /*
     store the output message 
     */
    memcpy(ConfigData->voltageOut.voltage,
           voltage,
           rwArrayMemorySize);

    WriteMessage(ConfigData->voltageOutMsgID, callTime, sizeof(RWArrayVoltageMessage),
                 (void*) &(ConfigData->voltageOut), moduleID);

    return;
}
