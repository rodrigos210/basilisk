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

#include <string.h>
#include <math.h>
#include "attGuidance/opNavPoint/opNavPoint.h"
#include "simulation/utilities/linearAlgebra.h"
#include "simulation/utilities/rigidBodyKinematics.h"
#include "simulation/utilities/astroConstants.h"
#include "simulation/utilities/bsk_Print.h"

/*! This method initializes the configData for the opNav attitude guidance.
 It checks to ensure that the inputs are sane and then creates the
 output message
 @return void
 @param configData The configuration data associated with the opNav guidance
 */
void SelfInit_opNavPoint(OpNavPointConfig *configData, int64_t moduleID)
{
    /*! - Create output message for module */
    configData->attGuidanceOutMsgID = CreateNewMessage(configData->attGuidanceOutMsgName,
        sizeof(AttGuidFswMsg), "AttGuidFswMsg", moduleID);
    memset(configData->attGuidanceOutBuffer.omega_RN_B, 0x0, 3*sizeof(double));
    memset(configData->attGuidanceOutBuffer.domega_RN_B, 0x0, 3*sizeof(double));
    
}

/*! This method performs the second stage of initialization for the opNav attitude
 interface.  It's primary function is to link the input messages that were
 created elsewhere.
 @return void
 @param configData The configuration data associated with the opNav attitude guidance
 */
void CrossInit_opNavPoint(OpNavPointConfig *configData, int64_t moduleID)
{
    /*! - Loop over the number of sensors and find IDs for each one */
    configData->opnavDataInMsgId = subscribeToMessage(configData->opnavDataInMsgName,
                                                      sizeof(OpNavFswMsg), moduleID);
    configData->imuInMsgID = subscribeToMessage(configData->imuInMsgName,
        sizeof(NavAttIntMsg), moduleID);
    configData->cameraConfigMsgID = subscribeToMessage(configData->cameraConfigMsgName,sizeof(CameraConfigMsg),moduleID);
    
}

/*! This method performs a complete reset of the module.  Local module variables that retain
 time varying states between function calls are reset to their default values.
 @return void
 @param configData The configuration data associated with the guidance module
 */
void Reset_opNavPoint(OpNavPointConfig *configData, uint64_t callTime, int64_t moduleID)
{
    double v1[3];

    /* compute an Eigen axis orthogonal to alignAxis_C */
    if (v3Norm(configData->alignAxis_C)  < 0.1) {
        BSK_PRINT(MSG_ERROR,"The module vector alignAxis_C is not setup as a unit vector [%f, %f %f]",
                  configData->alignAxis_C[0], configData->alignAxis_C[1], configData->alignAxis_C[2]);
    } else {
        v3Set(1., 0., 0., v1);
        v3Normalize(configData->alignAxis_C, configData->alignAxis_C);    /* ensure that this vector is a unit vector */
        v3Cross(configData->alignAxis_C, v1, configData->eHat180_B);
        if (v3Norm(configData->eHat180_B) < 0.1) {
            v3Set(0., 1., 0., v1);
            v3Cross(configData->alignAxis_C, v1, configData->eHat180_B);
        }
        v3Normalize(configData->eHat180_B, configData->eHat180_B);
    }
    configData->lastTime = 0;
    v3SetZero(configData->currentHeading_N);
    memset(configData->attGuidanceOutBuffer.omega_RN_B, 0x0, 3*sizeof(double));
    memset(configData->attGuidanceOutBuffer.domega_RN_B, 0x0, 3*sizeof(double));

    return;
}

/*! This method takes the estimated camera-observed target vector and computes the
 current attitude/attitude rate errors to pass on to control.
 @return void
 @param configData The configuration data associated with the opNav attitude guidance
 @param callTime The clock time at which the function was called (nanoseconds)
 */
void Update_opNavPoint(OpNavPointConfig *configData, uint64_t callTime,
    int64_t moduleID)
{
    OpNavFswMsg opNavMsg;
    uint64_t timeOfMsgWritten;
    uint32_t sizeOfMsgWritten;
    double cthNormalized;
    double timeWithoutMeas;
    double currentHeading_C[3], alignAxis_B[3];
    double hNorm;                   /* Norm of measured direction vector */
    double e_hat[3];                /* Principal rotation Axis */
    double omega_BN_B[3];           /* r/s inertial body angular velocity vector in B frame components */
    double omega_RN_B[3];           /* r/s local copy of the desired reference frame rate */
    double dcm_BN[3][3], dcm_CB[3][3], dcm_CN[3][3];
    NavAttIntMsg localImuDataInBuffer;
    CameraConfigMsg cameraSpecs;
    /* zero the input message containers */
    memset(&(opNavMsg), 0x0, sizeof(OpNavFswMsg));
    memset(&(localImuDataInBuffer), 0x0, sizeof(NavAttIntMsg));
    /*! - Read the current target vector estimate*/
    ReadMessage(configData->opnavDataInMsgId, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(OpNavFswMsg), (void*) &(opNavMsg), moduleID);
    ReadMessage(configData->imuInMsgID, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(NavAttIntMsg), (void*) &(localImuDataInBuffer), moduleID);
    ReadMessage(configData->cameraConfigMsgID, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(CameraConfigMsg), &cameraSpecs, moduleID);
    
    if (configData->lastTime==0){
        configData->lastTime=callTime*1E-9;
        v3SetZero(configData->currentHeading_N);
    }
    timeWithoutMeas = callTime*1E-9 - configData->lastTime;

    v3Copy(localImuDataInBuffer.omega_BN_B, omega_BN_B);
    MRP2C(localImuDataInBuffer.sigma_BN, dcm_BN);
    MRP2C(cameraSpecs.sigma_CB, dcm_CB);
    m33MultM33(dcm_CB, dcm_BN, dcm_CN);
    /*! Compute the current error vector if it is valid. This checks for a valid, non-stale, previous message, or a new fresh measurement.*/
    if((opNavMsg.valid == 1 || v3IsZero(configData->currentHeading_N, 1E-10) == 0) && (timeWithoutMeas < configData->timeOut)){
        /*! - If a valid image is in save the heading direction for future use*/
        if (opNavMsg.valid == 1){
            configData->lastTime = callTime*1E-9;
            v3Copy(opNavMsg.r_BN_N, configData->currentHeading_N);
            v3Copy(opNavMsg.r_BN_C, currentHeading_C);
            v3Scale(-1, currentHeading_C, currentHeading_C);
            hNorm = v3Norm(currentHeading_C);
            v3Scale(1/hNorm, currentHeading_C, currentHeading_C);
        }
        else{
            /*! - Else use the previous direction in order to continue guidance */
            m33MultV3(dcm_CN, configData->currentHeading_N, currentHeading_C);
            v3Scale(-1, currentHeading_C, currentHeading_C);
            hNorm = v3Norm(currentHeading_C);
            v3Scale(1/hNorm, currentHeading_C, currentHeading_C);
        }
        cthNormalized = v3Dot(configData->alignAxis_C, currentHeading_C);
        cthNormalized = fabs(cthNormalized) > 1.0 ?
        cthNormalized/fabs(cthNormalized) : cthNormalized;
        configData->opNavAngleErr = acos(cthNormalized);

        /*
            Compute the opNav error relative to the opNav direction vector
         */
        if (configData->opNavAngleErr < configData->smallAngle) {
            /* opNav heading and desired camera axis are essentially aligned.  Set attitude error to zero. */
             v3SetZero(configData->attGuidanceOutBuffer.sigma_BR);
        } else {
            if (M_PI - configData->opNavAngleErr < configData->smallAngle) {
                /* the commanded camera vector nearly is opposite the opNav heading */
                v3Copy(configData->eHat180_B, e_hat);
            } else {
                /* normal case where opNav and commanded camera vectors are not aligned */
                v3Cross(currentHeading_C, configData->alignAxis_C, e_hat);
            }
            v3Normalize(e_hat, configData->opNavMnvrVec);
            v3Scale(tan(configData->opNavAngleErr*0.25), configData->opNavMnvrVec,
                    configData->attGuidanceOutBuffer.sigma_BR);
            MRPswitch(configData->attGuidanceOutBuffer.sigma_BR, 1.0, configData->attGuidanceOutBuffer.sigma_BR);
        }

        /* rate tracking error are the body rates to bring spacecraft to rest */
        m33tMultV3(dcm_CB, configData->alignAxis_C, alignAxis_B);
        v3Scale(configData->opNavAxisSpinRate, alignAxis_B, omega_RN_B);
        v3Subtract(omega_BN_B, omega_RN_B, configData->attGuidanceOutBuffer.omega_BR_B);
        v3Copy(omega_RN_B, configData->attGuidanceOutBuffer.omega_RN_B);

    } else {
        configData->lastTime=0;
        /* no proper opNav direction vector is available */
        v3SetZero(configData->attGuidanceOutBuffer.sigma_BR);

        /* specify a body-fixed constant search rotation rate */
        v3Subtract(omega_BN_B, configData->omega_RN_B, configData->attGuidanceOutBuffer.omega_BR_B);
        v3Copy(configData->omega_RN_B, configData->attGuidanceOutBuffer.omega_RN_B);
    }

    /* write the Guidance output message */
    WriteMessage(configData->attGuidanceOutMsgID, callTime, sizeof(AttGuidFswMsg),
                 (void*) &(configData->attGuidanceOutBuffer), moduleID);
    
    return;
}
