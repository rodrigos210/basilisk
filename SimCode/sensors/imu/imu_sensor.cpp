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
#include "sensors/imu/imu_sensor.h"
#include "architecture/messaging/system_messaging.h"
#include "utilities/rigidBodyKinematics.h"
#include "utilities/linearAlgebra.h"
#include <math.h>
#include <iostream>
#include <cstring>
#include <random>
#include "utilities/gauss_markov.h"

ImuSensor::ImuSensor()
{
    CallCounts = 0;
    this->InputStateID = -1;
    this->InputStateMsg = "inertial_state_output";
    this->OutputDataMsg = "imu_meas_data";
    this->setBodyToPlatformDCM(0.0, 0.0, 0.0);
    this->OutputBufferCount = 2;
    memset(&this->StatePrevious, 0x0, sizeof(SCPlusStatesSimMsg));
    memset(&this->StateCurrent, 0x0, sizeof(SCPlusStatesSimMsg));
    this->PreviousTime = 0;
    this->NominalReady = false;
    memset(&this->senRotBias[0], 0x0, 3*sizeof(double));
    memset(&this->senTransBias[0], 0x0, 3*sizeof(double));
    memset(&this->sensedValues, 0x0, sizeof(IMUSensorIntMsg));
    memset(&this->trueValues, 0x0, sizeof(IMUSensorIntMsg));
    this->accelLSB = 0.;
    this->gyroLSB = 0.;
    this->senRotMax = 1e6;
    this->senTransMax = 1e6;
    

    return;
}

void ImuSensor::setBodyToPlatformDCM(double yaw, double pitch, double roll)
{
    double q[3] = {yaw, pitch, roll};
    Euler3212C(q, this->dcm_PB);
}

ImuSensor::~ImuSensor()
{
    return;
}

void ImuSensor::SelfInit()
{

    OutputDataID = SystemMessaging::GetInstance()->
        CreateNewMessage( OutputDataMsg, sizeof(IMUSensorIntMsg),
        OutputBufferCount, "IMUSensorIntMsg", moduleID);

	uint64_t numStates = 3;

	AMatrixAccel.clear();
	AMatrixAccel.insert(AMatrixAccel.begin(), numStates*numStates, 0.0);
	mSetIdentity(AMatrixAccel.data(), numStates, numStates);
	for(uint32_t i=0; i<3; i++)
	{
		AMatrixAccel.data()[i * 3 + i] = 1.0;
	}
	//! - Alert the user if the noise matrix was not the right size.  That'd be bad.
	if(PMatrixAccel.size() != numStates*numStates)
	{
		std::cerr << __FILE__ <<": Your process noise matrix (PMatrix) is not 3*3.";
		std::cerr << "  You should fix that.  Popping zeros onto end"<<std::endl;
		PMatrixAccel.insert(PMatrixAccel.begin()+PMatrixAccel.size(), numStates*numStates - PMatrixAccel.size(),
					   0.0);
	}
	errorModelAccel.setNoiseMatrix(PMatrixAccel);
	errorModelAccel.setRNGSeed(RNGSeed);
	errorModelAccel.setUpperBounds(walkBoundsAccel);

	AMatrixGyro.clear();
	AMatrixGyro.insert(AMatrixGyro.begin(), numStates*numStates, 0.0);
	mSetIdentity(AMatrixGyro.data(), numStates, numStates);
	for(uint32_t i=0; i<3; i++)
	{
		AMatrixGyro.data()[i * 3 + i] = 1.0;
	}
	//! - Alert the user if the noise matrix was not the right size.  That'd be bad.
	if(PMatrixGyro.size() != numStates*numStates)
	{
		std::cerr << __FILE__ <<": Your process noise matrix (PMatrix) is not 3*3.";
		std::cerr << "  You should fix that.  Popping zeros onto end"<<std::endl;
		PMatrixGyro.insert(PMatrixGyro.begin()+PMatrixGyro.size(), numStates*numStates - PMatrixGyro.size(),
							0.0);
	}
	errorModelGyro.setNoiseMatrix(PMatrixGyro);
	errorModelGyro.setRNGSeed(RNGSeed);
	errorModelGyro.setUpperBounds(walkBoundsGyro);

}

void ImuSensor::CrossInit()
{
    InputStateID = SystemMessaging::GetInstance()->subscribeToMessage(InputStateMsg,
        sizeof(SCPlusStatesSimMsg), moduleID);
    if(InputStateID < 0 )
    {
        std::cerr << "WARNING: Failed to link an imu input message: ";
        std::cerr << std::endl << "State: "<<InputStateID;
    }
    return;
}

void ImuSensor::readInputMessages()
{
    SingleMessageHeader LocalHeader;
    
    memset(&this->StateCurrent, 0x0, sizeof(SCPlusStatesSimMsg));
    if(InputStateID >= 0)
    {
        SystemMessaging::GetInstance()->ReadMessage(InputStateID, &LocalHeader,
                                                    sizeof(SCPlusStatesSimMsg), reinterpret_cast<uint8_t*> (&this->StateCurrent), moduleID);
    }
}

void ImuSensor::writeOutputMessages(uint64_t Clock)
{
    IMUSensorIntMsg LocalOutput;
    memcpy(LocalOutput.DVFramePlatform, this->sensedValues.DVFramePlatform, 3*sizeof(double));
    memcpy(LocalOutput.AccelPlatform, this->sensedValues.AccelPlatform, 3*sizeof(double));
    memcpy(LocalOutput.DRFramePlatform, this->sensedValues.DRFramePlatform, 3*sizeof(double));
    memcpy(LocalOutput.AngVelPlatform, this->sensedValues.AngVelPlatform, 3*sizeof(double));
    SystemMessaging::GetInstance()->WriteMessage(OutputDataID, Clock,
                                                 sizeof(IMUSensorIntMsg), reinterpret_cast<uint8_t*> (&LocalOutput), moduleID);
}

void ImuSensor::applySensorDiscretization(uint64_t CurrentTime)
{
    double scaledMeas[3];
    double intMeas[3];
    double dt;
    
    dt = (CurrentTime - PreviousTime)*1.0E-9;
    
    if(accelLSB > 0.0) //If accelLSB has been set.
    {
        v3Scale(1.0/accelLSB, sensedValues.AccelPlatform, scaledMeas);
        for(uint32_t i=0; i<3; i++) //Discretize each part of the acceleration
        {
            scaledMeas[i] = fabs(scaledMeas[i]);
            scaledMeas[i] = floor(scaledMeas[i]);
            scaledMeas[i] = scaledMeas[i]*accelLSB;
            scaledMeas[i] = copysign(scaledMeas[i], sensedValues.AccelPlatform[i]);
        }
        v3Subtract(sensedValues.AccelPlatform, scaledMeas, intMeas);
        v3Copy(scaledMeas, sensedValues.AccelPlatform);
        v3Scale(dt, intMeas, intMeas);
        v3Subtract(sensedValues.DVFramePlatform, intMeas, sensedValues.DVFramePlatform); //Account for acceleration discretization in velocity output
        v3Scale(1.0/accelLSB, sensedValues.DVFramePlatform, scaledMeas);
        for(uint32_t i=0; i<3; i++) //Then discretize each part of the velocity measurement b/c the work above doesn't guarantee that DV landed on a discretized value.
        {
            scaledMeas[i] = fabs(scaledMeas[i]);
            scaledMeas[i] = floor(scaledMeas[i]);
            scaledMeas[i] = scaledMeas[i]*accelLSB;
            scaledMeas[i] = copysign(scaledMeas[i], sensedValues.DVFramePlatform[i]);
        }
        v3Copy(scaledMeas, sensedValues.DVFramePlatform);
    }
    
    if(gyroLSB > 0.0) //If gyroLSB has been set
    {
        v3Scale(1.0/gyroLSB, sensedValues.AngVelPlatform, scaledMeas);
        for(uint32_t i=0; i<3; i++) //Discretize each part of the angular rate
        {
            scaledMeas[i] = fabs(scaledMeas[i]);
            scaledMeas[i] = floor(scaledMeas[i]);
            scaledMeas[i] = scaledMeas[i]*gyroLSB;
            scaledMeas[i] = copysign(scaledMeas[i], sensedValues.AngVelPlatform[i]);
        }
        v3Subtract(sensedValues.AngVelPlatform, scaledMeas, intMeas);
        v3Copy(scaledMeas, sensedValues.AngVelPlatform);
        v3Scale(dt, intMeas, intMeas);
        v3Subtract(sensedValues.DRFramePlatform, intMeas, sensedValues.DRFramePlatform); //account for angular rate discretization in PRV output.
        v3Scale(1.0/gyroLSB, sensedValues.DRFramePlatform, scaledMeas);
        for(uint32_t i=0; i<3; i++) //Discretize each part of the angular rate b/c the work above doesn't guarantee that DR will land on a discretized value
        {
            scaledMeas[i] = fabs(scaledMeas[i]);
            scaledMeas[i] = floor(scaledMeas[i]);
            scaledMeas[i] = scaledMeas[i]*gyroLSB;
            scaledMeas[i] = copysign(scaledMeas[i], sensedValues.DRFramePlatform[i]);
        }
        v3Copy(scaledMeas, sensedValues.DRFramePlatform);
    }
    
}

void ImuSensor::applySensorErrors(uint64_t CurrentTime)
{
    double OmegaErrors[3] = {0, 0, 0};
    double AccelErrors[3]= {0, 0, 0};
    double dt;
    
    dt = (CurrentTime - PreviousTime)*1.0E-9;
    
    for(uint32_t i=0; i<3; i++)
    {
		OmegaErrors[i] = navErrorsGyro[i] + senRotBias[i];
        this->sensedValues.AngVelPlatform[i] =  this->trueValues.AngVelPlatform[i] + OmegaErrors[i];
        this->sensedValues.DRFramePlatform[i] = this->trueValues.DRFramePlatform[i] +  OmegaErrors[i]*dt;
		AccelErrors[i] = navErrorsAccel[i] + senTransBias[i];
        this->sensedValues.AccelPlatform[i] = this->trueValues.AccelPlatform[i] + AccelErrors[i];
        this->sensedValues.DVFramePlatform[i] = this->trueValues.DVFramePlatform[i] + AccelErrors[i]*dt;
    }
    
}

void ImuSensor::computeSensorErrors()
{
	this->errorModelAccel.setPropMatrix(AMatrixAccel);
	this->errorModelAccel.computeNextState();
	this->navErrorsAccel = this->errorModelAccel.getCurrentState();
	this->errorModelGyro.setPropMatrix(AMatrixGyro);
	this->errorModelGyro.computeNextState();
	this->navErrorsGyro = this->errorModelGyro.getCurrentState();
}


void ImuSensor::applySensorSaturation(uint64_t CurrentTime)
{
	double dt;
    
	dt = (CurrentTime - PreviousTime)*1.0E-9;

	for(uint32_t i=0; i<3; i++)
	{
		if(this->sensedValues.AngVelPlatform[i] > this->senRotMax) {
			this->sensedValues.AngVelPlatform[i] = this->senRotMax;
			this->sensedValues.DRFramePlatform[i] = this->senRotMax * dt;
		} else if (this->sensedValues.AngVelPlatform[i] < -this->senRotMax) {
			this->sensedValues.AngVelPlatform[i] = -this->senRotMax;
			this->sensedValues.DRFramePlatform[i] = -this->senRotMax * dt;
		}
		if(this->sensedValues.AccelPlatform[i] > this->senTransMax) {
			this->sensedValues.AccelPlatform[i] = this->senTransMax;
			this->sensedValues.DVFramePlatform[i] = this->senTransMax * dt;
		} else if (this->sensedValues.AccelPlatform[i] < -this->senTransMax) {
			this->sensedValues.AccelPlatform[i] = -this->senTransMax;
			this->sensedValues.DVFramePlatform[i] = -this->senTransMax * dt;
		}
	}

}

void ImuSensor::computePlatformDR()
//This function gathers actual spacecraft attitude from the spacecraftPlus output message.
//It then differences the state attitude between this time and the last time the IMU was called
//to get a DR (delta radians or delta rotation)
//The angular rate is retrieved directly from the spacecraftPlus output message and passed through to the
//other IMU functions which add noise, etc.
{
    
    double sigma_BN_2[3];    // MRP from body to inertial frame last time the IMU was called
    double sigma_BN_1[3];         // MRP from body to inertial frame now.
    double dcm_BN_1[3][3];
    double dcm_BN_2[3][3];
    double dcm_PN_1[3][3];
    double dcm_PN_2[3][3];
    double dcm_NP_1[3][3];
    double dcm_P2P1[3][3];

    //Calculated time averaged cumulative rotation
    v3Copy(StatePrevious.sigma_BN, sigma_BN_1);
    v3Copy(StateCurrent.sigma_BN, sigma_BN_2);
    MRP2C(sigma_BN_1, dcm_BN_1);
    MRP2C(sigma_BN_2, dcm_BN_2);
    m33MultM33(dcm_PB, dcm_BN_1, dcm_PN_1);
    m33MultM33(dcm_PB, dcm_BN_2, dcm_PN_2);
    m33Transpose(dcm_PN_1, dcm_NP_1);
    m33MultM33(dcm_PN_2, dcm_NP_1, dcm_P2P1);
    C2MRP(dcm_P2P1, trueValues.DRFramePlatform);
    MRP2PRV(trueValues.DRFramePlatform, trueValues.DRFramePlatform);
    
    //calculate "instantaneous" angular rate
    m33MultV3(this->dcm_PB, StateCurrent.omega_BN_B, this->trueValues.AngVelPlatform); //returns instantaneous angular rate of imu sensor in imu platform frame coordinates
}

void ImuSensor::computePlatformDV(uint64_t CurrentTime)
//This functions gathers actual spacecraft velocity from the spacecraftPlus output message.
//It then differences the velocity between this time and the last time the IMU was called to get a
//DV (delta velocity).
//The acceleration of the spacecraft in the body frame is gathered directly from the spacecraftPlus
//output message. Then, it is converted to the platform frame and rotational terms are added to it
//to account for CoM offset of the platform frame.
{
    
    //double CmRelPos[3];
    double omega[3];            //omega_BN_B from scPlus
    double omega_x_r[3];        //omega_BN_B x r_SB_B
    double omega_x_r_prev[3];   //omega_BN_B x r_SB_B last time the IMU was called
    double omega_x_omega_x_r[3];//omega_BN_B x (omega_BN_B x r_SB_B)
    double omegaDot_x_r[3];     //(time derivative of omega_BN_B) x r_SB_B
    double rotationalTerms[3];  //(time derivative of omega_BN_B) x r_SB_B + omega_BN_B x (omega_BN_B x r_SB_B)
    double rotationalDelta_B[3];//delta in rotationl velocity term of sensor motion in B frame
    double r_SB_B[3];           //sensor position relative to B frame origin in B frame coordinates
    double rDotDot_BN_B[3];     //non-conservative acceleration of body frame relative to inertial frame in body frame coordinates
    double rDotDot_SN_B[3];     //sensor non conservative acceleration relative to inertial frame in body frame coordinates
    double rDotDot_SN_P[3];     //sensor non conservative acceleration relative to inertial frame in sensor platform frame
    double drDot_BN_B[3];       //change in velocity of body frame relative to inertial in body frame coordinates between IMU calls. This does not include delta-v from conservative accelerations.
    double dvSensor_B[3];       //sensor delta v between IMU calls in body frame coordinates
    
    //Calculate "instantaneous" linear acceleration
    v3Copy(StateCurrent.nonConservativeAccelpntB_B, rDotDot_BN_B);
    v3Copy(sensorPos_B.data(), r_SB_B);
    v3Copy(StateCurrent.omega_BN_B, omega);
    v3Cross(StateCurrent.omegaDot_BN_B, r_SB_B, omegaDot_x_r);
    v3Cross(omega, r_SB_B, omega_x_r);
    v3Cross(omega, omega_x_r, omega_x_omega_x_r);
    v3Add(omegaDot_x_r, omega_x_omega_x_r, rotationalTerms);
    v3Add(rDotDot_BN_B, rotationalTerms, rDotDot_SN_B);
    m33MultV3(this->dcm_PB, rDotDot_SN_B, rDotDot_SN_P);
    v3Copy(rDotDot_SN_P, this->trueValues.AccelPlatform); //returns linear non-conservative acceleration of the imu in imu platform frame coordinates
    
    //Calculate time-average cumulative delta v
    v3Subtract(StateCurrent.TotalAccumDV_BN_B, StatePrevious.TotalAccumDV_BN_B, drDot_BN_B);
    v3Cross(StatePrevious.omega_BN_B, r_SB_B, omega_x_r_prev);
    v3Subtract(omega_x_r, omega_x_r_prev, rotationalDelta_B);
    v3Add(drDot_BN_B, rotationalDelta_B, dvSensor_B);
    m33MultV3(this->dcm_PB, dvSensor_B, this->trueValues.DVFramePlatform); //returns the accumulated deltaV experienced by the sensor in imu platform frame coordinates. This does not include delta-v from conservative accelerations.
    
}

void ImuSensor::UpdateState(uint64_t CurrentSimNanos)
{
    readInputMessages();

    if(NominalReady)
    {
        /* Compute true data */
        computePlatformDR();
        computePlatformDV(CurrentSimNanos);
        /* Compute sensed data */
		computeSensorErrors();
		applySensorErrors(CurrentSimNanos);
        applySensorDiscretization(CurrentSimNanos);
		applySensorSaturation(CurrentSimNanos);
        /* Output sensed data */
        writeOutputMessages(CurrentSimNanos);
    }
    memcpy(&StatePrevious, &StateCurrent, sizeof(SCPlusStatesSimMsg));
    PreviousTime = CurrentSimNanos;
    NominalReady = true;
}
