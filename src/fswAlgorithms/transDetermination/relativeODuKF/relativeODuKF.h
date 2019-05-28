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

#ifndef _RELOD_UKF_H_
#define _RELOD_UKF_H_

#include <stdint.h>

#include "messaging/static_messaging.h"
#include "simFswInterfaceMessages/navTransIntMsg.h"
#include "simFswInterfaceMessages/macroDefinitions.h"
#include "fswMessages/opnavFswMsg.h"
#include "fswMessages/opNavFilterFswMsg.h"
#include "simulation/utilities/linearAlgebra.h"
#include "simulation/utilities/rigidBodyKinematics.h"
#include "simulation/utilities/bsk_Print.h"


/*! \defgroup relative orbit determination UKF
 @brief This module filters incoming star tracker measurements and reaction wheel data in order to get the best possible inertial attitude estimate. The filter used is an unscented Kalman filter using the Modified Rodrigues Parameters (MRPs) as a non-singular attitude measure.  Measurements can be coming in from several camera heads.
 
 * @{
 */


/*! @brief Top level structure for the Inertial unscented kalman filter.
 Used to estimate the spacecraft's inertial attitude. Measurements are StarTracker data and gyro data.
 */
typedef struct {
    char navStateOutMsgName[MAX_STAT_MSG_LENGTH]; //!< The name of the output message
    char filtDataOutMsgName[MAX_STAT_MSG_LENGTH]; //!< The name of the output filter data message
    char opNavInMsgName[MAX_STAT_MSG_LENGTH];  //!< [-] The name of the input RW speeds message
    
    int numStates;                //!< [-] Number of states for this filter
    int countHalfSPs;             //!< [-] Number of sigma points over 2
    int numObs;                   //!< [-] Number of measurements this cycle
    double beta;                  //!< [-] Beta parameter for filter
    double alpha;                 //!< [-] Alpha parameter for filter
    double kappa;                 //!< [-] Kappa parameter for filter
    double lambdaVal;             //!< [-] Lambda parameter for filter
    double gamma;                 //!< [-] Gamma parameter for filter
    double switchMag;             //!< [-] Threshold for where we switch MRP set
    
    double dt;                     //!< [s] seconds since last data epoch
    double timeTag;                //!< [s]  Time tag for statecovar/etc
    double gyrAggTimeTag;          //!< [s] Time-tag for aggregated gyro data
    double aggSigma_b2b1[3];       //!< [-] Aggregated attitude motion from gyros
    double dcm_BdyGyrpltf[3][3];   //!< [-] DCM for converting gyro data to body frame
    double wM[2 * ODUKF_N_STATES + 1]; //!< [-] Weighting vector for sigma points
    double wC[2 * ODUKF_N_STATES + 1]; //!< [-] Weighting vector for sigma points
    
    double stateInit[ODUKF_N_STATES];    //!< [-] State estimate to initialize filter to
    double state[ODUKF_N_STATES];        //!< [-] State estimate for time TimeTag
    double statePrev[ODUKF_N_STATES];        //!< [-] State estimate for time TimeTag at previous time
    double sBar[ODUKF_N_STATES*ODUKF_N_STATES];         //!< [-] Time updated covariance
    double sBarPrev[ODUKF_N_STATES*ODUKF_N_STATES];     //!< [-] Time updated covariance at previous time
    double covar[ODUKF_N_STATES*ODUKF_N_STATES];        //!< [-] covariance
    double covarPrev[ODUKF_N_STATES*ODUKF_N_STATES];    //!< [-] covariance at previous time
    double covarInit[ODUKF_N_STATES*ODUKF_N_STATES];    //!< [-] Covariance to init filter with
    double xBar[ODUKF_N_STATES];            //!< [-] Current mean state estimate
    
    double obs[3];          //!< [-] Observation vector for frame
    double yMeas[3*(2*ODUKF_N_STATES+1)];        //!< [-] Measurement model data
    
    double SP[(2*ODUKF_N_STATES+1)*ODUKF_N_STATES];          //!< [-]    sigma point matrix
    
    double qNoise[ODUKF_N_MEAS*ODUKF_N_STATES*ODUKF_N_STATES];       //!< [-] process noise matrix
    double sQnoise[ODUKF_N_MEAS*ODUKF_N_STATES*ODUKF_N_STATES];      //!< [-] cholesky of Qnoise
    double IInv[3][3];
    
    uint32_t firstPassComplete;
    double sigma_BNOut[3];   //!< [-] Output MRP
    double omega_BN_BOut[3]; //!< [r/s] Body rate output data
    double timeTagOut;       //!< [s] Output time-tag information
    double maxTimeJump;      //!< [s] Maximum time jump to allow in propagation
    
    OpnavFswMsg opNavInMsg; //!< [-] ST sensor data read in from message bus
    uint64_t ClockTimeCircles[ODUKF_N_MEAS]; //!< [-] All of the ClockTimes for the STs
    uint64_t ReadSizeCirlces[ODUKF_N_MEAS];  //!< [-] All of the ReadSizes for the STs
    

    int32_t navStateOutMsgId;     //!< -- Id for the outgoing body estimate message
    int32_t filtDataOutMsgId;     //!< [-] Id for the filter data output message
    int32_t opNavInMsgId;     //!< [-] Id for the incoming mass properties message
    
}InertialUKFConfig;


#ifdef __cplusplus
extern "C" {
#endif
    
    void SelfInit_relODuKF(InertialUKFConfig *configData, uint64_t moduleId);
    void CrossInit_relODuKF(InertialUKFConfig *configData, uint64_t moduleId);
    void Update_relODuKF(InertialUKFConfig *configData, uint64_t callTime,
                            uint64_t moduleId);
    void Reset_relODuKF(InertialUKFConfig *configData, uint64_t callTime,
                           uint64_t moduleId);
    int relODuKFTimeUpdate(InertialUKFConfig *configData, double updateTime);
    int relODuKFMeasUpdate(InertialUKFConfig *configData);
    void relODuKFCleanUpdate(InertialUKFConfig *configData);
    void inertialStateProp(InertialUKFConfig *configData, double *stateInOut, double dt);
    void relODuKFMeasModel(InertialUKFConfig *configData);
    
#ifdef __cplusplus
}
#endif

/*! @} */

#endif
