
#ifndef _MRP_FEEDBACK_CONTROL_H_
#define _MRP_FEEDBACK_CONTROL_H_

#include "messaging/static_messaging.h"
#include "../_GeneralModuleFiles/vehControlOut.h"
#include <stdint.h>

/*! \addtogroup ADCSAlgGroup
 * @{
 */

/*! @brief Top level structure for the MRP Steering attitude control routine. */
typedef struct {
    /* declare module private variables */
    double K;                   /*!< [rad/sec] Proportional gain applied to MRP errors */
    double omega_max;           /*!< [rad/sec] Maximum rate command of steering control */
    double P;                   /*!< [N*m*s]   Rate error feedback gain applied  */
    double Ki;                  /*!< [N*m]     Integration feedback error on rate error  */
    double integralLimit;       /*!< [N*m]     Integration limit to avoid wind-up issue */
    uint64_t priorTime;         /*!< [ns]      Last time the attitude control is called */
    double z[3];                /*!< [rad]     integral state of delta_omega */
    double int_sigma[3];        /*!< [s]       integral of the MPR attitude error */
    double domega0[3];          /*!< [rad/sec] initial omega tracking error */

    /* declare module IO interfaces */
    char outputDataName[MAX_STAT_MSG_LENGTH]; /*!< The name of the output message*/
    char inputGuidName[MAX_STAT_MSG_LENGTH];  /*!< The name of the Input message*/
    char inputNavName[MAX_STAT_MSG_LENGTH];   /*!< The name of the Navigation 6Input message*/
    char inputVehicleConfigDataName[MAX_STAT_MSG_LENGTH]; /*!< The name of the Input message*/
    int32_t outputMsgID;        /*!< [] ID for the outgoing body accel requests*/
    int32_t inputGuidID;        /*!< [] ID for the incoming guidance errors*/
    int32_t inputVehicleConfigDataID;/*!< -- ID for the incoming static vehicle data */
    int32_t inputNavID;         /*!< [] ID for the incoming navigation message */
    vehControlOut controlOut;   /*!< -- Control output requests */
}MRP_FeedbackConfig;

#ifdef __cplusplus
extern "C" {
#endif
    
    void SelfInit_MRP_Feedback(MRP_FeedbackConfig *ConfigData, uint64_t moduleID);
    void CrossInit_MRP_Feedback(MRP_FeedbackConfig *ConfigData, uint64_t moduleID);
    void Update_MRP_Feedback(MRP_FeedbackConfig *ConfigData, uint64_t callTime, uint64_t moduleID);
    void Reset_MRP_Feedback(MRP_FeedbackConfig *ConfigData);

    
#ifdef __cplusplus
}
#endif

/*! @} */

#endif