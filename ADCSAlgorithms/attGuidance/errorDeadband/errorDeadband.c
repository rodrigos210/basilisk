/*
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

*/
/*
    Attitude Tracking Error Module
 
 */

/* modify the path to reflect the new module names */
#include "attGuidance/errorDeadband/errorDeadband.h"
#include <string.h>
#include <math.h>
#include "ADCSUtilities/ADCSDefinitions.h"
#include "ADCSUtilities/ADCSAlgorithmMacros.h"

/* update this include to reflect the required module input messages */
#include "attGuidance/attTrackingError/attTrackingError.h"



/*
 Pull in support files from other modules.  Be sure to use the absolute path relative to Basilisk directory.
 */
#include "SimCode/utilities/linearAlgebra.h"
#include "SimCode/utilities/rigidBodyKinematics.h"


/*! This method initializes the ConfigData for this module.
 It checks to ensure that the inputs are sane and then creates the
 output message
 @return void
 @param ConfigData The configuration data associated with this module
 */
void SelfInit_errorDeadband(errorDeadbandConfig *ConfigData, uint64_t moduleID)
{
    
    /*! Begin method steps */
    /*! - Create output message for module */
    ConfigData->outputGuidID = CreateNewMessage(ConfigData->outputDataName,
                                               sizeof(attGuidOut),
                                               "attGuidOut",
                                               moduleID);
    ConfigData->boolWasControlOff = 0;
    v3Set(-1, -1, -1, ConfigData->sigma_BR);
}

/*! This method performs the second stage of initialization for this module.
 It's primary function is to link the input messages that were created elsewhere.
 @return void
 @param ConfigData The configuration data associated with this module
 */
void CrossInit_errorDeadband(errorDeadbandConfig *ConfigData, uint64_t moduleID)
{
    /*! - Get the control data message ID*/
    ConfigData->inputGuidID = subscribeToMessage(ConfigData->inputGuidName,
                                                sizeof(attGuidOut),
                                                moduleID);
}

/*! This method performs a complete reset of the module.  Local module variables that retain
 time varying states between function calls are reset to their default values.
 @return void
 @param ConfigData The configuration data associated with the MRP steering control
 */
void Reset_errorDeadband(errorDeadbandConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    ConfigData->boolWasControlOff = 0;
    v3Set(-1, -1, -1, ConfigData->sigma_BR);

}

/*! Add a description of what this main Update() routine does for this module
 @return void
 @param ConfigData The configuration data associated with the attitude tracking error module
 @param callTime The clock time at which the function was called (nanoseconds)
 */
void Update_errorDeadband(errorDeadbandConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    /*! - Read the input message and set it as the output by default */
    uint64_t    clockTime;
    uint32_t    readSize;
    ReadMessage(ConfigData->inputGuidID, &clockTime, &readSize,
                sizeof(attGuidOut), (void*) &(ConfigData->attGuidOut), moduleID);
    /*! - Evaluate current error in attitude and rates */
    computeAbsoluteError(ConfigData);
    /*! - Check whether control should be ON or OFF */
    applyDeadband(ConfigData);
    /*! - Write output guidance message */
    writeOutputMessages(ConfigData, callTime, moduleID);
    return;
}


void writeOutputMessages(errorDeadbandConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    WriteMessage(ConfigData->outputGuidID, callTime, sizeof(attGuidOut),
                 (void*) &(ConfigData->attGuidOut), moduleID);
    v3Copy(ConfigData->attGuidOut.sigma_BR, ConfigData->sigma_BR);
    v3Copy(ConfigData->attGuidOut.omega_BR_B, ConfigData->omega_BR_B);
}

void computeAbsoluteError(errorDeadbandConfig *ConfigData)
{
    double attError;
    double rateError;
    attError = 4 * atan(v3Norm(ConfigData->attGuidOut.sigma_BR));
    rateError = v3Norm(ConfigData->attGuidOut.omega_BR_B);
    ConfigData->error = sqrt(attError * attError + rateError * rateError);
}

void applyDeadband(errorDeadbandConfig *ConfigData)
{
    if (ConfigData->error < ConfigData->outerThresh)
    {
        if (ConfigData->error < ConfigData->innerThresh || (ConfigData->error > ConfigData->innerThresh && ConfigData->boolWasControlOff))
        {
            /* Set errors to zero in order to turn off control */
            v3SetZero(ConfigData->attGuidOut.sigma_BR);
            v3SetZero(ConfigData->attGuidOut.omega_BR_B);
            ConfigData->boolWasControlOff = 1;
        } else {
            ConfigData->boolWasControlOff = 0;
        }
    }
    else
    {
        ConfigData->boolWasControlOff = 0;
    }
    
}

//void applyDeadband(errorDeadbandConfig *ConfigData)
//{
//    if (ConfigData->error < ConfigData->outerThresh)
//    {
//        if (ConfigData->error < ConfigData->innerThresh || (ConfigData->error > ConfigData->innerThresh && wasControlOff(ConfigData)))
//        {
//            /* Set errors to zero in order to turn off control */
//            v3SetZero(ConfigData->attGuidOut.sigma_BR);
//            v3SetZero(ConfigData->attGuidOut.omega_BR_B);
//        }
//    }
//}

uint32_t wasControlOff(errorDeadbandConfig *ConfigData)
{
    double zeroVec[3];
    v3SetZero(zeroVec);
    //ConfigData->boolWasControlOff = v3IsEqual(ConfigData->sigma_BR, zeroVec, 1E-12) && v3IsEqual(ConfigData->omega_BR_B, zeroVec, 1E-12);
    return v3IsEqual(ConfigData->sigma_BR, zeroVec, 1E-12) && v3IsEqual(ConfigData->omega_BR_B, zeroVec, 1E-12);
}


