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

#ifndef _HILL_POINT_
#define _HILL_POINT_

#include "messaging/static_messaging.h"
#include <stdint.h>
#include "../_GeneralModuleFiles/attGuidOut.h"

/* Required module input messages */
#include "attDetermination/_GeneralModuleFiles/navStateOut.h"
#include "SimCode/environment/spice/spice_planet_state.h"

/*! \addtogroup ADCSAlgGroup
 * @{
 */

/*! @brief Top level structure for the sub-module routines. */



typedef struct {
    
    /* declare module IO interfaces */
    char outputDataName[MAX_STAT_MSG_LENGTH];       /*!<        The name of the output message*/
    int32_t outputMsgID;                            /*!< (-)    ID for the outgoing message */
    char inputNavDataName[MAX_STAT_MSG_LENGTH];     /*<!        The name of the incoming attitude command*/
    int32_t inputNavID;                             /*!< (-)    ID for the incoming IMU data message*/
    char inputCelMessName[MAX_STAT_MSG_LENGTH];     /*<!        The name of the celestial body message */
    int32_t inputCelID;                             /*!< (-)    ID for the planet input message */
    
    /*  copy of the output message */
    attRefOut attRefOut;

}hillPointConfig;

#ifdef __cplusplus
extern "C" {
#endif
    
    void SelfInit_hillPoint(hillPointConfig *ConfigData, uint64_t moduleID);
    void CrossInit_hillPoint(hillPointConfig *ConfigData, uint64_t moduleID);
    void Update_hillPoint(hillPointConfig *ConfigData, uint64_t callTime, uint64_t moduleID);
    void Reset_hillPoint(hillPointConfig *ConfigData, uint64_t callTime, uint64_t moduleID);

    void computeHillPointingReference(hillPointConfig *ConfigData,
                                      double r_BN_N[3],
                                      double v_BN_N[3],
                                      double celBdyPositonVector[3],
                                      double celBdyVelocityVector[3]);

#ifdef __cplusplus
}
#endif

/*! @} */

#endif
