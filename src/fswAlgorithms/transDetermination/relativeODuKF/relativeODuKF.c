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
#include "transDetermination/relativeODuKF/relativeODuKF.h"
#include "transDetermination/_GeneralModuleFiles/ukfUtilities.h"
#include "simulation/utilities/linearAlgebra.h"
#include "simulation/utilities/rigidBodyKinematics.h"
#include "simFswInterfaceMessages/macroDefinitions.h"
#include "simulation/utilities/bsk_Print.h"

/*! This method creates the two moduel output messages.
 @return void
 @param configData The configuration data associated with the CSS WLS estimator
 */
void SelfInit_relODuKF(InertialUKFConfig *configData, uint64_t moduleId)
{
    /*! - Create output message for module */
    configData->navStateOutMsgId = CreateNewMessage(configData->navStateOutMsgName,
                                                    sizeof(NavAttIntMsg), "NavAttIntMsg", moduleId);
    /*! - Create filter states output message which is mostly for debug*/
    configData->filtDataOutMsgId = CreateNewMessage(configData->filtDataOutMsgName,
                                                    sizeof(OpnavFswMsg), "InertialFilterFswMsg", moduleId);
    
}

/*! This method performs the second stage of initialization for the OD filter.  It's primary function is to link the input messages that were created elsewhere.
 @return void
 @param configData The configuration data associated with the CSS interface
 */
void CrossInit_relODuKF(InertialUKFConfig *configData, uint64_t moduleId)
{
    configData->massPropsInMsgId = subscribeToMessage(configData->massPropsInMsgName,
                                                      sizeof(VehicleConfigFswMsg), moduleId);
    /*! - Find the message Id for the vehicle mass properties configuration message */
    configData->circlesInMsgId = subscribeToMessage(configData->circlesInMsgName,
                                                     sizeof(CameraImageMsg), moduleId);
    
}

/*! This method resets the relative OD filter to an initial state and
 initializes the internal estimation matrices.
 @return void
 @param configData The configuration data associated with the CSS estimator
 @param callTime The clock time at which the function was called (nanoseconds)
 */
void Reset_relODuKF(InertialUKFConfig *configData, uint64_t callTime,
                       uint64_t moduleId)
{
    
    int32_t i;
    int32_t badUpdate=0; /* Negative badUpdate is faulty, */
    uint64_t timeOfMsgWritten;
    uint32_t sizeOfMsgWritten;
    double tempMatrix[ODUKF_N_STATES*ODUKF_N_STATES];
    
    /*! - Zero the local configuration data structures and outputs */
    memset(&(configData->localConfigData), 0x0, sizeof(VehicleConfigFswMsg));
    /*! - Read static RW config data message and store it in module variables */
    ReadMessage(configData->massPropsInMsgId, &timeOfMsgWritten, &sizeOfMsgWritten,
                sizeof(VehicleConfigFswMsg), &(configData->localConfigData), moduleId);
    
    /*! - Initialize filter parameters to max values */
    configData->timeTag = callTime*NANO2SEC;
    configData->dt = 0.0;
    configData->numStates = ODUKF_N_STATES;
    configData->countHalfSPs = ODUKF_N_STATES;
    configData->numObs = 3;
    configData->firstPassComplete = 0;
    
    /*! - Ensure that all internal filter matrices are zeroed*/
    vSetZero(configData->obs, configData->numObs);
    vSetZero(configData->wM, configData->countHalfSPs * 2 + 1);
    vSetZero(configData->wC, configData->countHalfSPs * 2 + 1);
    mSetZero(configData->sBar, configData->numStates, configData->numStates);
    mSetZero(configData->SP, configData->countHalfSPs * 2 + 1,
             configData->numStates);
    mSetZero(configData->sQnoise, configData->numStates, configData->numStates);
    
    /*! - Set lambda/gamma to standard value for unscented kalman filters */
    configData->lambdaVal = configData->alpha*configData->alpha*
    (configData->numStates + configData->kappa) - configData->numStates;
    configData->gamma = sqrt(configData->numStates + configData->lambdaVal);
    
    
    /*! - Set the wM/wC vectors to standard values for unscented kalman filters*/
    configData->wM[0] = configData->lambdaVal / (configData->numStates +
                                                 configData->lambdaVal);
    configData->wC[0] = configData->lambdaVal / (configData->numStates +
                                                 configData->lambdaVal) + (1 - configData->alpha*configData->alpha + configData->beta);
    for (i = 1; i<configData->countHalfSPs * 2 + 1; i++)
    {
        configData->wM[i] = 1.0 / 2.0*1.0 / (configData->numStates +
                                             configData->lambdaVal);
        configData->wC[i] = configData->wM[i];
    }
    
    vCopy(configData->stateInit, configData->numStates, configData->state);
    
    /*! - User a cholesky decomposition to obtain the sBar and sQnoise matrices for use in filter at runtime*/
    mCopy(configData->covarInit, configData->numStates, configData->numStates,
          configData->sBar);
    mCopy(configData->covarInit, configData->numStates, configData->numStates,
          configData->covar);
    mSetZero(tempMatrix, configData->numStates, configData->numStates);
    badUpdate += ukfCholDecomp(configData->sBar, configData->numStates,
                               configData->numStates, tempMatrix);
    
    badUpdate += ukfCholDecomp(configData->qNoise, configData->numStates,
                               configData->numStates, configData->sQnoise);
    
    mCopy(tempMatrix, configData->numStates, configData->numStates,
          configData->sBar);
    mTranspose(configData->sQnoise, configData->numStates,
               configData->numStates, configData->sQnoise);
    
    v3Copy(configData->state, configData->sigma_BNOut);
    v3Copy(&(configData->state[3]), configData->omega_BN_BOut);
    configData->timeTagOut = configData->timeTag;
    
    if (badUpdate <0){
        BSK_PRINT(MSG_WARNING, "Reset method contained bad update");
    }
    return;
}

/*! This method takes the parsed CSS sensor data and outputs an estimate of the
 sun vector in the ADCS body frame
 @return void
 @param configData The configuration data associated with the CSS estimator
 @param callTime The clock time at which the function was called (nanoseconds)
 */
void Update_relODuKF(InertialUKFConfig *configData, uint64_t callTime,
                        uint64_t moduleId)
{
    double newTimeTag = 0.0;  /* [s] Local Time-tag variable*/
    uint64_t timeOfMsgWritten; /* [ns] Read time for the message*/
    uint32_t sizeOfMsgWritten = 0;  /* [-] Non-zero size indicates we received ST msg*/
    uint32_t otherSize; /* [-] Size of messages that are assumed to be good*/
    int32_t trackerValid; /* [-] Indicates whether the star tracker was valid*/
    OpnavFswMsg opNavOutBuffer; /* [-] Output filter info*/
    NavAttIntMsg outputRelOD;
    
    // Reset update check to zero
    if (v3Norm(configData->state) > configData->switchMag) //Little extra margin
    {
        MRPswitch(configData->state, configData->switchMag, configData->state);
    }
    memset(&(outputRelOD), 0x0, sizeof(NavAttIntMsg));
    memset(&opNavOutBuffer, 0x0, sizeof(OpnavFswMsg));
    memset(&(configData->localConfigData), 0x0, sizeof(VehicleConfigFswMsg));
    ReadMessage(configData->massPropsInMsgId, &timeOfMsgWritten, &otherSize,
                sizeof(VehicleConfigFswMsg), &(configData->localConfigData), moduleId);
    ReadMessage(configData->circlesInMsgId, &timeOfMsgWritten, &otherSize,
                sizeof(OpnavFswMsg), &outputRelOD, moduleId);
    
    m33Inverse(RECAST3X3 configData->localConfigData.ISCPntB_B, configData->IInv);
    /*! - Handle initializing time in filter and discard initial messages*/
    
    trackerValid = 0;
    /*! - If the star tracker has provided a new message compared to last time,
     update the filter to the new measurement*/
    if(newTimeTag >= configData->timeTag && sizeOfMsgWritten == sizeof(CameraImageMsg))
    {
        trackerValid = 1;
        if((newTimeTag - configData->timeTag) > configData->maxTimeJump
           && configData->maxTimeJump > 0)
        {
            configData->timeTag = newTimeTag - configData->maxTimeJump;
            BSK_PRINT(MSG_WARNING, "Large jump in state time that was set to max\n");
        }
        trackerValid += relODuKFTimeUpdate(configData, newTimeTag);
        trackerValid += relODuKFMeasUpdate(configData);
    }
    
   
    /*! - Write the relative OD estimate into the copy of the navigation message structure*/
//    v3Copy(configData->sigma_BNOut, outputInertial.sigma_BN);
//    v3Copy(configData->omega_BN_BOut, outputInertial.omega_BN_B);
//    outputInertial.timeTag = configData->timeTagOut;
    
    WriteMessage(configData->navStateOutMsgId, callTime, sizeof(NavAttIntMsg),
                 &(opNavOutBuffer), moduleId);
    
    /*! - Populate the filter states output buffer and write the output message*/
    opNavOutBuffer.timeTag = configData->timeTag;
    memmove(opNavOutBuffer.covar, configData->covar,
            ODUKF_N_STATES*ODUKF_N_STATES*sizeof(double));
    memmove(opNavOutBuffer.state, configData->state, ODUKF_N_STATES*sizeof(double));
    WriteMessage(configData->filtDataOutMsgId, callTime, sizeof(OpnavFswMsg),
                 &opNavOutBuffer, moduleId);
    
    return;
}

/*! This method propagates a relative OD state vector forward in time.  Note
 that the calling parameter is updated in place to save on data copies.
 @return void
 @param stateInOut The state that is propagated
 */
void relODStateProp(InertialUKFConfig *configData, double *stateInOut, double dt)
{
    
    double sigmaDot[3];
    double BMatrix[3][3];
    double torqueTotal[3];
    double angAccelTotal[3];
    
    /*! - Convert the state derivative (body rate) to sigmaDot and propagate
     the attitude MRPs*/
    BmatMRP(stateInOut, BMatrix);
    m33Scale(0.25, BMatrix, BMatrix);
    m33MultV3(BMatrix, &(stateInOut[3]), sigmaDot);
    v3Scale(dt, sigmaDot, sigmaDot);
    v3Add(stateInOut, sigmaDot, stateInOut);
    
    
    /*! - Get the angular acceleration and propagate the state forward (euler prop)*/
    m33MultV3(configData->IInv, torqueTotal, angAccelTotal);
    v3Scale(dt, angAccelTotal, angAccelTotal);
    v3Add(&(stateInOut[3]), angAccelTotal, &(stateInOut[3]));
    return;
}

/*! This method performs the time update for the relative OD kalman filter.
 It propagates the sigma points forward in time and then gets the current
 covariance and state estimates.
 @return void
 @param configData The configuration data associated with the CSS estimator
 @param updateTime The time that we need to fix the filter to (seconds)
 */
int relODuKFTimeUpdate(InertialUKFConfig *configData, double updateTime)
{
    int i, Index, k;
    double sBarT[ODUKF_N_STATES*ODUKF_N_STATES];
    double xComp[ODUKF_N_STATES], AT[(2 * ODUKF_N_STATES + ODUKF_N_STATES)*ODUKF_N_STATES];
    double aRow[ODUKF_N_STATES], rAT[ODUKF_N_STATES*ODUKF_N_STATES], xErr[ODUKF_N_STATES];
    double sBarUp[ODUKF_N_STATES*ODUKF_N_STATES];
    double *spPtr;
    double procNoise[ODUKF_N_STATES*ODUKF_N_STATES];
    int32_t badUpdate=0;
    
    configData->dt = updateTime - configData->timeTag;
    vCopy(configData->state, configData->numStates, configData->statePrev);
    mCopy(configData->sBar, configData->numStates, configData->numStates, configData->sBarPrev);
    mCopy(configData->covar, configData->numStates, configData->numStates, configData->covarPrev);
    
    mCopy(configData->sQnoise, ODUKF_N_STATES, ODUKF_N_STATES, procNoise);
    /*! - Copy over the current state estimate into the 0th Sigma point and propagate by dt*/
    vCopy(configData->state, configData->numStates,
          &(configData->SP[0 * configData->numStates + 0]));
    relODStateProp(configData, &(configData->SP[0]),
                      configData->dt);
    /*! - Scale that Sigma point by the appopriate scaling factor (Wm[0])*/
    vScale(configData->wM[0], &(configData->SP[0]),
           configData->numStates, configData->xBar);
    /*! - Get the transpose of the sBar matrix because it is easier to extract Rows vs columns*/
    mTranspose(configData->sBar, configData->numStates, configData->numStates,
               sBarT);
    /*! - For each Sigma point, apply sBar-based error, propagate forward, and scale by Wm just like 0th.
     Note that we perform +/- sigma points simultaneously in loop to save loop values.*/
    for (i = 0; i<configData->countHalfSPs; i++)
    {
        /*! - Adding covariance columns from sigma points*/
        Index = i + 1;
        spPtr = &(configData->SP[Index*configData->numStates]);
        vCopy(&sBarT[i*configData->numStates], configData->numStates, spPtr);
        vScale(configData->gamma, spPtr, configData->numStates, spPtr);
        vAdd(spPtr, configData->numStates, configData->state, spPtr);
        relODStateProp(configData, spPtr, configData->dt);
        vScale(configData->wM[Index], spPtr, configData->numStates, xComp);
        vAdd(xComp, configData->numStates, configData->xBar, configData->xBar);
        /*! - Subtracting covariance columns from sigma points*/
        Index = i + 1 + configData->countHalfSPs;
        spPtr = &(configData->SP[Index*configData->numStates]);
        vCopy(&sBarT[i*configData->numStates], configData->numStates, spPtr);
        vScale(-configData->gamma, spPtr, configData->numStates, spPtr);
        vAdd(spPtr, configData->numStates, configData->state, spPtr);
        relODStateProp(configData, spPtr, configData->dt);
        vScale(configData->wM[Index], spPtr, configData->numStates, xComp);
        vAdd(xComp, configData->numStates, configData->xBar, configData->xBar);
    }
    /*! - Zero the AT matrix prior to assembly*/
    mSetZero(AT, (2 * configData->countHalfSPs + configData->numStates),
             configData->countHalfSPs);
    /*! - Assemble the AT matrix.  Note that this matrix is the internals of
     the qr decomposition call in the source design documentation.  It is
     the inside of equation 20 in that document*/
    for (i = 0; i<2 * configData->countHalfSPs; i++)
    {
        vScale(-1.0, configData->xBar, configData->numStates, aRow);
        vAdd(aRow, configData->numStates,
             &(configData->SP[(i+1)*configData->numStates]), aRow);
        /*Check sign of wC to know if the sqrt will fail*/
        if (configData->wC[i+1]<=0){
            relODuKFCleanUpdate(configData);
            return -1;}
        vScale(sqrt(configData->wC[i+1]), aRow, configData->numStates, aRow);
        memcpy((void *)&AT[i*configData->numStates], (void *)aRow,
               configData->numStates*sizeof(double));
        
    }
    /*! - Scale sQNoise matrix depending on the dt*/
    for (k=0;k<3;k++){
        procNoise[k*ODUKF_N_STATES+k] *= configData->dt*configData->dt/2;
        procNoise[(k+3)*ODUKF_N_STATES+(k+3)] *= configData->dt;
    }
    /*! - Pop the sQNoise matrix on to the end of AT prior to getting QR decomposition*/
    memcpy(&AT[2 * configData->countHalfSPs*configData->numStates],
           procNoise, configData->numStates*configData->numStates
           *sizeof(double));
    /*! - QR decomposition (only R computed!) of the AT matrix provides the new sBar matrix*/
    ukfQRDJustR(AT, 2 * configData->countHalfSPs + configData->numStates,
                configData->countHalfSPs, rAT);
    
    mCopy(rAT, configData->numStates, configData->numStates, sBarT);
    mTranspose(sBarT, configData->numStates, configData->numStates,
               configData->sBar);
    
    /*! - Shift the sBar matrix over by the xBar vector using the appropriate weight
     like in equation 21 in design document.*/
    vScale(-1.0, configData->xBar, configData->numStates, xErr);
    vAdd(xErr, configData->numStates, &configData->SP[0], xErr);
    badUpdate += ukfCholDownDate(configData->sBar, xErr, configData->wC[0],
                                 configData->numStates, sBarUp);
    
    
    /*! - Save current sBar matrix, covariance, and state estimate off for further use*/
    mCopy(sBarUp, configData->numStates, configData->numStates, configData->sBar);
    mTranspose(configData->sBar, configData->numStates, configData->numStates,
               configData->covar);
    mMultM(configData->sBar, configData->numStates, configData->numStates,
           configData->covar, configData->numStates, configData->numStates,
           configData->covar);
    vCopy(&(configData->SP[0]), configData->numStates, configData->state);
    
    if (badUpdate<0){
        relODuKFCleanUpdate(configData);
        return(-1);}
    else{
        configData->timeTag = updateTime;
    }
    return(0);
}

/*! This method computes what the expected measurement vector is for each CSS
 that is present on the spacecraft.  All data is transacted from the main
 data structure for the model because there are many variables that would
 have to be updated otherwise.
 @return void
 @param configData The configuration data associated with the CSS estimator
 
 */
void relODuKFMeasModel(InertialUKFConfig *configData)
{
    int i;
    
    /*! - The measurement model is the same as the states since the star tracker
     measures the relative orbit directly.*/
    for(i=0; i<configData->countHalfSPs*2+1; i++)
    {
        v3Copy(&(configData->SP[i*ODUKF_N_STATES]), &(configData->yMeas[i*3]));
    }
    
}

/*! This method performs the measurement update for the kalman filter.
 It applies the observations in the obs vectors to the current state estimate and
 updates the state/covariance with that information.
 @return void
 @param configData The configuration data associated with the CSS estimator
 @param updateTime The time that we need to fix the filter to (seconds)
 */
int relODuKFMeasUpdate(InertialUKFConfig *configData)
{
    uint32_t i;
    double yBar[3], syInv[3*3];
    double kMat[ODUKF_N_STATES*3];
    double xHat[ODUKF_N_STATES], Ucol[ODUKF_N_STATES], sBarT[ODUKF_N_STATES*ODUKF_N_STATES], tempYVec[3];
    double AT[(2 * ODUKF_N_STATES + 3)*3], qChol[3*3];
    double rAT[3*3], syT[3*3];
    double sy[3*3];
    double updMat[3*3], pXY[ODUKF_N_STATES*3], Umat[ODUKF_N_STATES*3];
    int32_t badUpdate=0;
    
    vCopy(configData->state, configData->numStates, configData->statePrev);
    mCopy(configData->sBar, configData->numStates, configData->numStates, configData->sBarPrev);
    mCopy(configData->covar, configData->numStates, configData->numStates, configData->covarPrev);
    /*! - Compute the valid observations and the measurement model for all observations*/
    relODuKFMeasModel(configData);
    
    /*! - Compute the value for the yBar parameter (note that this is equation 23 in the
     time update section of the reference document*/
    vSetZero(yBar, configData->numObs);
    for(i=0; i<configData->countHalfSPs*2+1; i++)
    {
        vCopy(&(configData->yMeas[i*configData->numObs]), configData->numObs,
              tempYVec);
        vScale(configData->wM[i], tempYVec, configData->numObs, tempYVec);
        vAdd(yBar, configData->numObs, tempYVec, yBar);
    }
    
    /*! - Populate the matrix that we perform the QR decomposition on in the measurement
     update section of the code.  This is based on the differenence between the yBar
     parameter and the calculated measurement models.  Equation 24 in driving doc. */
    mSetZero(AT, configData->countHalfSPs*2+configData->numObs,
             configData->numObs);
    for(i=0; i<configData->countHalfSPs*2; i++)
    {
        vScale(-1.0, yBar, configData->numObs, tempYVec);
        vAdd(tempYVec, configData->numObs,
             &(configData->yMeas[(i+1)*configData->numObs]), tempYVec);
        if (configData->wC[i+1]<0){return -1;}
        vScale(sqrt(configData->wC[i+1]), tempYVec, configData->numObs, tempYVec);
        memcpy(&(AT[i*configData->numObs]), tempYVec,
               configData->numObs*sizeof(double));
    }
    
    /*! - This is the square-root of the Rk matrix which we treat as the Cholesky
     decomposition of the observation variance matrix constructed for our number
     of observations*/
    badUpdate += ukfCholDecomp(configData->sQnoise, configData->numObs, configData->numObs, qChol);
    memcpy(&(AT[2*configData->countHalfSPs*configData->numObs]),
           qChol, configData->numObs*configData->numObs*sizeof(double));
    /*! - Perform QR decomposition (only R again) of the above matrix to obtain the
     current Sy matrix*/
    ukfQRDJustR(AT, 2*configData->countHalfSPs+configData->numObs,
                configData->numObs, rAT);
    
    mCopy(rAT, configData->numObs, configData->numObs, syT);
    mTranspose(syT, configData->numObs, configData->numObs, sy);
    /*! - Shift the matrix over by the difference between the 0th SP-based measurement
     model and the yBar matrix (cholesky down-date again)*/
    vScale(-1.0, yBar, configData->numObs, tempYVec);
    vAdd(tempYVec, configData->numObs, &(configData->yMeas[0]), tempYVec);
    badUpdate += ukfCholDownDate(sy, tempYVec, configData->wC[0],
                                 configData->numObs, updMat);
    
    /*! - Shifted matrix represents the Sy matrix */
    mCopy(updMat, configData->numObs, configData->numObs, sy);
    mTranspose(sy, configData->numObs, configData->numObs, syT);
    
    /*! - Construct the Pxy matrix (equation 26) which multiplies the Sigma-point cloud
     by the measurement model cloud (weighted) to get the total Pxy matrix*/
    mSetZero(pXY, configData->numStates, configData->numObs);
    for(i=0; i<2*configData->countHalfSPs+1; i++)
    {
        vScale(-1.0, yBar, configData->numObs, tempYVec);
        vAdd(tempYVec, configData->numObs,
             &(configData->yMeas[i*configData->numObs]), tempYVec);
        vSubtract(&(configData->SP[i*configData->numStates]), configData->numStates,
                  configData->xBar, xHat);
        vScale(configData->wC[i], xHat, configData->numStates, xHat);
        mMultM(xHat, configData->numStates, 1, tempYVec, 1, configData->numObs,
               kMat);
        mAdd(pXY, configData->numStates, configData->numObs, kMat, pXY);
    }
    
    /*! - Then we need to invert the SyT*Sy matrix to get the Kalman gain factor.  Since
     The Sy matrix is lower triangular, we can do a back-sub inversion instead of
     a full matrix inversion.  That is the ukfUInv and ukfLInv calls below.  Once that
     multiplication is done (equation 27), we have the Kalman Gain.*/
    ukfUInv(syT, configData->numObs, configData->numObs, syInv);
    
    mMultM(pXY, configData->numStates, configData->numObs, syInv,
           configData->numObs, configData->numObs, kMat);
    ukfLInv(sy, configData->numObs, configData->numObs, syInv);
    mMultM(kMat, configData->numStates, configData->numObs, syInv,
           configData->numObs, configData->numObs, kMat);
    
    
    /*! - Difference the yBar and the observations to get the observed error and
     multiply by the Kalman Gain to get the state update.  Add the state update
     to the state to get the updated state value (equation 27).*/
    vSubtract(configData->obs, configData->numObs, yBar, tempYVec);
    mMultM(kMat, configData->numStates, configData->numObs, tempYVec,
           configData->numObs, 1, xHat);
    vAdd(configData->state, configData->numStates, xHat, configData->state);
    /*! - Compute the updated matrix U from equation 28.  Note that I then transpose it
     so that I can extract "columns" from adjacent memory*/
    mMultM(kMat, configData->numStates, configData->numObs, sy,
           configData->numObs, configData->numObs, Umat);
    mTranspose(Umat, configData->numStates, configData->numObs, Umat);
    /*! - For each column in the update matrix, perform a cholesky down-date on it to
     get the total shifted S matrix (called sBar in internal parameters*/
    for(i=0; i<configData->numObs; i++)
    {
        vCopy(&(Umat[i*configData->numStates]), configData->numStates, Ucol);
        badUpdate += ukfCholDownDate(configData->sBar, Ucol, -1.0, configData->numStates, sBarT);
        mCopy(sBarT, configData->numStates, configData->numStates,
              configData->sBar);
    }
    
    /*! - Compute equivalent covariance based on updated sBar matrix*/
    mTranspose(configData->sBar, configData->numStates, configData->numStates,
               configData->covar);
    mMultM(configData->sBar, configData->numStates, configData->numStates,
           configData->covar, configData->numStates, configData->numStates,
           configData->covar);
    
    if (badUpdate<0){
        relODuKFCleanUpdate(configData);
        return(-1);}
    return(0);
}

/*! This method cleans the filter states after a bad upadate on the fly.
 It removes the potentially corrupted previous estimates and puts the filter
 back to a working state.
 @return void
 @param configData The configuration data associated with the CSS estimator
 */
void relODuKFCleanUpdate(InertialUKFConfig *configData){
    int i;
    /*! - Reset the observations, state, and covariannces to a previous safe value*/
    vSetZero(configData->obs, configData->numObs);
    vCopy(configData->statePrev, configData->numStates, configData->state);
    mCopy(configData->sBarPrev, configData->numStates, configData->numStates, configData->sBar);
    mCopy(configData->covarPrev, configData->numStates, configData->numStates, configData->covar);
    
    /*! - Reset the wM/wC vectors to standard values for unscented kalman filters*/
    configData->wM[0] = configData->lambdaVal / (configData->numStates +
                                                 configData->lambdaVal);
    configData->wC[0] = configData->lambdaVal / (configData->numStates +
                                                 configData->lambdaVal) + (1 - configData->alpha*configData->alpha + configData->beta);
    for (i = 1; i<configData->countHalfSPs * 2 + 1; i++)
    {
        configData->wM[i] = 1.0 / 2.0*1.0 / (configData->numStates +
                                             configData->lambdaVal);
        configData->wC[i] = configData->wM[i];
    }
    
    return;
}

