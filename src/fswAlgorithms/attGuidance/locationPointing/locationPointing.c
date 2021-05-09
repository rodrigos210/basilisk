/*
 ISC License

 Copyright (c) 2021, Autonomous Vehicle Systems Lab, University of Colorado Boulder

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


#include "fswAlgorithms/attGuidance/locationPointing/locationPointing.h"
#include "string.h"
#include "architecture/utilities/linearAlgebra.h"
#include "architecture/utilities/rigidBodyKinematics.h"
#include "architecture/utilities/astroConstants.h"
#include "architecture/utilities/macroDefinitions.h"
#include <math.h>

/*!
    This method initializes the output messages for this module.
 @return void
 @param configData The configuration data associated with this module
 @param moduleID The module identifier
 */
void SelfInit_locationPointing(locationPointingConfig  *configData, int64_t moduleID)
{
    AttGuidMsg_C_init(&configData->attGuidOutMsg);
}


/*! This method performs a complete reset of the module.  Local module variables that retain
    time varying states between function calls are reset to their default values.
    Check if required input messages are connected.
 @return void
 @param configData The configuration data associated with the module
 @param callTime [ns] time the method is called
 @param moduleID The module identifier
*/
void Reset_locationPointing(locationPointingConfig *configData, uint64_t callTime, int64_t moduleID)
{

    // check if the required message has not been connected
    if (!SCStatesMsg_C_isLinked(&configData->scInMsg)) {
        _bskLog(configData->bskLogger, BSK_ERROR, "Error: locationPointing.SCInMsg was not connected.");
    }
    if (!GroundStateMsg_C_isLinked(&configData->locationInMsg)) {
        _bskLog(configData->bskLogger, BSK_ERROR, "Error: locationPointing.LocationInMsg was not connected.");
    }

    configData->init = 2;

    v3SetZero(configData->sigma_BR_old);
    v3SetZero(configData->omega_RN_N_old);
    configData->time_old = callTime;
    
    /* compute an Eigen axis orthogonal to sHatBdyCmd */
    if (v3Norm(configData->pHat_B)  < 0.1) {
      char info[MAX_LOGGING_LENGTH];
      sprintf(info, "locationPoint: vector pHat_B is not setup as a unit vector [%f, %f %f]",
                configData->pHat_B[0], configData->pHat_B[1], configData->pHat_B[2]);
      _bskLog(configData->bskLogger, BSK_ERROR, info);
    } else {
        double v1[3];
        v3Set(1., 0., 0., v1);
        v3Normalize(configData->pHat_B, configData->pHat_B);    /* ensure that this vector is a unit vector */
        v3Cross(configData->pHat_B, v1, configData->eHat180_B);
        if (v3Norm(configData->eHat180_B) < 0.1) {
            v3Set(0., 1., 0., v1);
            v3Cross(configData->pHat_B, v1, configData->eHat180_B);
        }
        v3Normalize(configData->eHat180_B, configData->eHat180_B);
    }
}


/*! This method takes the estimated body states and position relative to the ground to compute the current attitude/attitude rate errors and pass them to control.
 @return void
 @param configData The configuration data associated with the module
 @param callTime The clock time at which the function was called (nanoseconds)
 @param moduleID The module identifier
*/
void Update_locationPointing(locationPointingConfig *configData, uint64_t callTime, int64_t moduleID)
{
    /* Local copies*/
    SCStatesMsgPayload scInMsgBuffer;  //!< local copy of input message buffer
    GroundStateMsgPayload locationInMsgBuffer;  //!< local copy of input message buffer
    AttGuidMsgPayload attGuidOutMsgBuffer;  //!< local copy of output message buffer

    double r_LS_N[3];                   /*!< Position vector of location w.r.t spacecraft CoM in inertial frame */
    double r_LS_B[3];                   /*!< Position vector of location w.r.t spacecraft CoM in body frame */
    double eHat_B[3];                   /*!< --- Eigen Axis */
    double dcmBN[3][3];                 /*!< inertial spacecraft orientation DCM */
    double phi;                         /*!< principal angle between pHat and heading to location */
    double sigma_BR_Dot[3];             /*!< time derivative of sigma_BR*/
    double sigma_BR[3];                 /*!< MRP of B relative to R */
    double omega_RN_N[3];               /*!< reference frame angular velocity relative to inertial frame, in N frame components */
    double omegaDot_RN_N[3];            /*!< inertial derivative of inertial reference frame angular velocity */
    double difference[3];
    double time_diff;                   /*!< module update time */
    double Binv[3][3];                  /*!< BinvMRP for dsigma_RB_R calculations*/
    double dum1;

    // zero output buffer
    attGuidOutMsgBuffer = AttGuidMsg_C_zeroMsgPayload();

    // read in the input messages
    scInMsgBuffer = SCStatesMsg_C_read(&configData->scInMsg);
    locationInMsgBuffer = GroundStateMsg_C_read(&configData->locationInMsg);

    /* calculate r_LS_N*/
    v3Subtract(locationInMsgBuffer.r_LN_N, scInMsgBuffer.r_CN_N, r_LS_N);

    /* principle rotation angle to point pHat at location */
    MRP2C(scInMsgBuffer.sigma_BN, dcmBN);
    m33MultV3(dcmBN, r_LS_N, r_LS_B);
    dum1 = v3Dot(configData->pHat_B, r_LS_B)/v3Norm(r_LS_B);
    if (fabs(dum1) > 1.0) {
        dum1 = dum1 / fabs(dum1);
    }
    phi = acos(dum1);

    /* calculate sigma_BR */
    if (phi < configData->smallAngle) {
        /* sun heading and desired body axis are essentially aligned.  Set attitude error to zero. */
         v3SetZero(sigma_BR);
    } else {
        if (M_PI - phi < configData->smallAngle) {
            /* the commanded body vector nearly is opposite the sun heading */
            v3Copy(configData->eHat180_B, eHat_B);
        } else {
            /* normal case where sun and commanded body vectors are not aligned */
            v3Cross(configData->pHat_B, r_LS_B, eHat_B);
        }
        v3Normalize(eHat_B, eHat_B);
        v3Scale(-tan(phi / 4.), eHat_B, sigma_BR);
    }
    v3Copy(sigma_BR, attGuidOutMsgBuffer.sigma_BR);
    
    /* use sigma_BR to compute d(sigma_BR)/dt if at least two data points */
    if (configData->init < 2) {
        // module update time
        time_diff = (callTime - configData->time_old)*NANO2SEC;

        // calculate d(sigma_BR)/dt
        v3Subtract(sigma_BR, configData->sigma_BR_old, difference);
        /* check for MRP switching */
        if (v3Norm(difference) > 0.3) {
            MRPswitch(configData->sigma_BR_old, 1.0, configData->sigma_BR_old);
            v3Subtract(sigma_BR, configData->sigma_BR_old, difference);
        }
        v3Scale(1.0/(time_diff), difference, sigma_BR_Dot);

        // calculate BinvMRP
        BinvMRP(sigma_BR, Binv);
        
        // compute omega_BR_B
        v3Scale(4.0, sigma_BR_Dot, sigma_BR_Dot);
        m33MultV3(Binv, sigma_BR_Dot, attGuidOutMsgBuffer.omega_BR_B);

        /* compute omega_BR_B (subtract as need omega_RB not omega_BR)*/
        v3Subtract(scInMsgBuffer.omega_BN_B, attGuidOutMsgBuffer.omega_BR_B, attGuidOutMsgBuffer.omega_RN_B);
           
        // if performed finite diff twice, then have enough for domega
        m33tMultV3(dcmBN, attGuidOutMsgBuffer.omega_RN_B, omega_RN_N);
        if (configData->init < 1) {
            // perform difference and compute reference angular acceleration
            v3Subtract(omega_RN_N, configData->omega_RN_N_old, difference);
            v3Scale(1. / (time_diff), difference, omegaDot_RN_N);
            m33MultV3(dcmBN, omegaDot_RN_N, attGuidOutMsgBuffer.domega_RN_B);
        } else {
            configData->init -= 1;
        }

        // copy current reference angular rate
        v3Copy(omega_RN_N, configData->omega_RN_N_old);

    } else {
        configData->init -= 1;
    }

    // copy current attitude states into prior state buffers
    v3Copy(sigma_BR, configData->sigma_BR_old);
    
    // update former module call time
    configData->time_old = callTime;

    // write to the output messages
    AttGuidMsg_C_write(&attGuidOutMsgBuffer, &configData->attGuidOutMsg, moduleID, callTime);
}

