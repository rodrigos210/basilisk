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
 Inertial 3D Spin Module
 
 * University of Colorado, Autonomous Vehicle Systems (AVS) Lab
 * Unpublished Copyright (c) 2012-2015 University of Colorado, All Rights Reserved
 
 */

#include "attGuidance/rasterManager/rasterManager.h"
#include <string.h>
#include <stdio.h>
#include <math.h>
#include "fswUtilities/fswDefinitions.h"
#include "simFswInterfaceMessages/macroDefinitions.h"

/* Support files.  Be sure to use the absolute path relative to Basilisk directory. */
#include "simulation/utilities/linearAlgebra.h"
#include "simulation/utilities/rigidBodyKinematics.h"




void SelfInit_rasterManager(rasterManagerConfig *configData, int64_t moduleID)
{
    configData->bskPrint = _BSKPrint();
    /*! - Create output message for module */
    configData->AttStateOutMsgID = CreateNewMessage(configData->AttStateOutMsgName,
                                                 sizeof(AttStateFswMsg),
                                                 "AttStateFswMsg",
                                                 moduleID);
    configData->mnvrActive = 0;
    configData->scanSelector = 0;
    
}

void CrossInit_rasterManager(rasterManagerConfig *configData, int64_t moduleID)
{
    /*! - Get the control data message ID*/
}

void Reset_rasterManager(rasterManagerConfig *configData, uint64_t callTime, int64_t moduleID)
{
    configData->mnvrActive = 0;
    configData->scanSelector = 0;
}


void Update_rasterManager(rasterManagerConfig *configData, uint64_t callTime, int64_t moduleID)
{
    uint64_t currentMnvrTime;
    configData->scanSelector = configData->scanSelector % configData->numRasters;
    if (configData->mnvrActive == 0)
    {
        configData->mnvrStartTime = callTime;
        configData->mnvrActive = 1;
    }
    currentMnvrTime = (callTime - configData->mnvrStartTime) * 1E-9;
    if (currentMnvrTime < configData->rasterTimes[configData->scanSelector])
    {
        v3Copy(&configData->scanningAngles[3 * configData->scanSelector], configData->attOutSet.state);
        v3Copy(&configData->scanningRates[3 * configData->scanSelector], configData->attOutSet.rate);
    } else {
        configData->mnvrActive = 0.0;
        configData->scanSelector += 1;

        char msg[255];
        sprintf(msg, "Raster: %i. AngleSet = [%f, %f, %f], RateSet = [%f, %f, %f] ", configData->scanSelector,
               configData->attOutSet.state[0],
               configData->attOutSet.state[1],
               configData->attOutSet.state[2],
               configData->attOutSet.rate[0],
               configData->attOutSet.rate[1],
               configData->attOutSet.rate[2]);
        _printMessage(configData->bskPrint, MSG_INFORMATION, msg);
    }
    
    
    WriteMessage(configData->AttStateOutMsgID, callTime, sizeof(AttStateFswMsg),
                 (void*) &(configData->attOutSet), moduleID);
    return;
}




