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

#include <iostream>
#include "dragDynamicEffector.h"
#include "../architecture/messaging/system_messaging.h"
#include "utilities/linearAlgebra.h"
#include "utilities/astroConstants.h"

DragDynamicEffector::DragDynamicEffector()
{
	this->coreParams.projectedArea = 0.0;
	this->coreParams.dragCoeff = 0.0;
    this->coreParams.comOffset.setZero();
	this->atmoDensInMsgName = "atmo_dens_0_data";
	this->modelType = "cannonball";
	this->forceExternal_B.fill(0.0);
	this->torqueExternalPntB_B.fill(0.0);
	this->v_B.fill(0.0);
	this->v_hat_B.fill(0.0);
	this->densInMsgId = -1;
	return;
}

/*! The destructor.*/
DragDynamicEffector::~DragDynamicEffector()
{
	return;
}

/*! This method currently does very little.
 @return void
 */
void DragDynamicEffector::SelfInit()
{
  return;
}

/*! This method is used to connect the input density message to the drag effector.
 It sets the message ID based on what it finds for the input string.
 @return void
 */
void DragDynamicEffector::CrossInit()
{
	//! - Find the message ID associated with the atmoDensInMsgName string.
	this->densInMsgId = SystemMessaging::GetInstance()->subscribeToMessage(this->atmoDensInMsgName,
																	 sizeof(AtmoPropsSimMsg), moduleID);
}

/*! This method is used to set the input density message produced by some atmospheric model.
@return void
*/
void DragDynamicEffector::setDensityMessage(std::string newDensMessage)
{
	this->atmoDensInMsgName = newDensMessage;
	return;
}

/*! The DragEffector does not write output messages to the rest of the sim.
@return void
 */
void DragDynamicEffector::WriteOutputMessages(uint64_t CurrentClock)
{
	return;
}


/*! This method is used to read the incoming density message and update the internal density/
atmospheric data.
 @return void
 */
bool DragDynamicEffector::ReadInputs()
{
	bool dataGood;
	//! - Zero the command buffer and read the incoming command array
	SingleMessageHeader localHeader;
    memset(&this->atmoInData, 0x0, sizeof(AtmoPropsSimMsg));
	memset(&localHeader, 0x0, sizeof(localHeader));
	dataGood = SystemMessaging::GetInstance()->ReadMessage(this->densInMsgId, &localHeader,
														  sizeof(AtmoPropsSimMsg),
														   reinterpret_cast<uint8_t*> (&this->atmoInData), moduleID);
	return(dataGood);

}

/*!
    This method is used to link the dragEffector to the hub attitude and velocity,
    which are required for calculating drag forces and torques.
    @return void
    @param states simulation states
 */
void DragDynamicEffector::linkInStates(DynParamManager& states){
    this->hubSigma = states.getStateObject("hubSigma");
	this->hubVelocity = states.getStateObject("hubVelocity");
}

/*! This method updates the internal drag direction based on the spacecraft velocity vector.
*/
void DragDynamicEffector::updateDragDir(){
    Eigen::MRPd sigmaBN;
    sigmaBN = (Eigen::Vector3d)this->hubSigma->getState();
    Eigen::Matrix3d dcm_BN = sigmaBN.toRotationMatrix().transpose();
    
	this->v_B = dcm_BN*this->hubVelocity->getState(); // [m/s] sc velocity
	this->v_hat_B = this->v_B / this->v_B.norm();
	
	return;
}

/*! This method implements a simple "cannnonball" (attitude-independent) drag model.
*/
void DragDynamicEffector::cannonballDrag(){
  	//! Begin method steps
  	//! - Zero out the structure force/torque for the drag set
  	this->forceExternal_B.setZero();
    this->torqueExternalPntB_B.setZero();
    
  	this->forceExternal_B  = 0.5 * this->coreParams.dragCoeff * pow(this->v_B.norm(), 2.0) * this->coreParams.projectedArea * this->atmoInData.neutralDensity * (-1.0)*this->v_hat_B;
  	this->torqueExternalPntB_B = this->coreParams.comOffset.cross(forceExternal_B);

  	return;
}

/*! This method computes the body forces and torques for the dragEffector in a simulation loop,
selecting the model type based on the settable attribute "modelType."
*/
void DragDynamicEffector::computeForceTorque(double integTime){
	updateDragDir();
	if(this->modelType == "cannonball"){
		cannonballDrag();
  	}
  	return;
}

/*! This method is called to update the local atmospheric conditions at each timestep.
Naturally, this means that conditions are held piecewise-constant over an integration step.
 @return void
 @param CurrentSimNanos The current simulation time in nanoseconds
 */
void DragDynamicEffector::UpdateState(uint64_t CurrentSimNanos)
{
	ReadInputs();
	return;
}
