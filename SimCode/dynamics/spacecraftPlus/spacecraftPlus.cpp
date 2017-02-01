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

#include "spacecraftPlus.h"
#include "utilities/simMacros.h"
#include "../_GeneralModuleFiles/svIntegratorRK4.h"
#include "utilities/avsEigenSupport.h"
#include "utilities/avsEigenMRP.h"
#include <iostream>

/*! This is the constructor, setting variables to default values */
SpacecraftPlus::SpacecraftPlus()
{
    // - Set default names
    this->sysTimePropertyName = "systemTime";
    this->scStateOutMsgName = "inertial_state_output";
    this->scMassStateOutMsgName = "mass_state_output";
    this->struct2BdyPropertyName = "dcm_BS";

    // - Set values to either zero or default values
	this->currTimeStep = 0.0;
	this->timePrevious = 0.0;
    this->simTimePrevious = 0;
    this->MRPSwitchCount = 0;
    this->scStateOutMsgId = -1;
	this->numOutMsgBuffers = 2;
    this->dcm_BS.setIdentity();
    this->dvAccum_B.setZero();

    // - Set integrator as RK4 by default
    this->integrator = new svIntegratorRK4(this);

    return;
}

/*! This is the destructor, nothing to report here */
SpacecraftPlus::~SpacecraftPlus()
{
    return;
}

/*! This method creates the messages for s/c output data and initializes the gravity field*/
void SpacecraftPlus::SelfInit()
{
    // - Create the message for the spacecraft state
    this->scStateOutMsgId = SystemMessaging::GetInstance()->CreateNewMessage(this->scStateOutMsgName,
                                                                             sizeof(SCPlusOutputStateData),
                                                                             this->numOutMsgBuffers,
                                                                             "SCPlusOutputStateData", this->moduleID);
    // - Create the message for the spacecraft mass state
    this->scMassStateOutMsgId = SystemMessaging::GetInstance()->CreateNewMessage(this->scMassStateOutMsgName,
                                                                             sizeof(SCPlusMassPropsData),
                                                                                 this->numOutMsgBuffers,
                                                                                 "SCPlusMassPropsData", this->moduleID);
    // - Call the gravity fields selfInit method
    this->gravField.SelfInit();

    return;
}

/*! This method is used to cross link the messages and to initialize the dynamics */
void SpacecraftPlus::CrossInit()
{
    // - Call gravity field cross initialization
    this->gravField.CrossInit();
    // - Call method for initializing the dynamics of spacecraftPlus
    this->initializeDynamics();

    return;
}

/*! This is the method where the messages of the state of vehicle are written */
void SpacecraftPlus::writeOutputMessages(uint64_t clockTime)
{
    // - Populate state output message
    SCPlusOutputStateData stateOut;
    eigenMatrixXd2CArray(*this->inertialPositionProperty, stateOut.r_BN_N);
    eigenMatrixXd2CArray(*this->inertialVelocityProperty, stateOut.v_BN_N);
    eigenMatrixXd2CArray(this->hubSigma->getState(), stateOut.sigma_BN);
    eigenMatrixXd2CArray(this->hubOmega_BN_B->getState(), stateOut.omega_BN_B);
    eigenMatrix3d2CArray(this->dcm_BS, (double *)stateOut.dcm_BS);
    eigenMatrixXd2CArray(this->dvAccum_B, stateOut.TotalAccumDVBdy);
    stateOut.MRPSwitchCount = this->MRPSwitchCount;
    SystemMessaging::GetInstance()->WriteMessage(this->scStateOutMsgId, clockTime, sizeof(SCPlusOutputStateData),
                                                 reinterpret_cast<uint8_t*> (&stateOut), this->moduleID);

    // - Populate mass state output message
    SCPlusMassPropsData massStateOut;
    massStateOut.massSC = (*this->m_SC)(0,0);
    eigenMatrixXd2CArray(*this->c_B, massStateOut.c_B);
    eigenMatrixXd2CArray(*this->ISCPntB_B, (double *)massStateOut.ISC_PntB_B);
    SystemMessaging::GetInstance()->WriteMessage(this->scMassStateOutMsgId, clockTime, sizeof(SCPlusMassPropsData),
                                                 reinterpret_cast<uint8_t*> (&massStateOut), this->moduleID);

    return;
}

/*! This method is a part of sysModel and is used to integrate the state and update the state in the messaging system */
void SpacecraftPlus::UpdateState(uint64_t CurrentSimNanos)
{
    // - Convert current time to seconds
    double newTime = CurrentSimNanos*NANO2SEC;

    // - Update the gravity field
    this->gravField.UpdateState(CurrentSimNanos);

    // - Integrate the state forward in time
    this->integrateState(newTime);
    this->gravField.updateInertialPosAndVel();

    // - Write the state of the vehicle into messages
    this->writeOutputMessages(CurrentSimNanos);
    this->simTimePrevious = CurrentSimNanos;

    return;
}

/*! This method allows the spacecraftPlus to have access to the current state of the hub for MRP switching, writing 
 messages, and calculating energy and momentum */
void SpacecraftPlus::linkInStates(DynParamManager& statesIn)
{
    // - Get access to all hub states
	this->hubR_N = statesIn.getStateObject("hubPosition");
	this->hubV_N = statesIn.getStateObject("hubVelocity");
    this->hubSigma = statesIn.getStateObject("hubSigma");   /* Need sigmaBN for MRP switching */
	this->hubOmega_BN_B = statesIn.getStateObject("hubOmega");

    // - Get access to the hubs position and velocity in the property manager
    this->inertialPositionProperty = statesIn.getPropertyReference("r_BN_N");
    this->inertialVelocityProperty = statesIn.getPropertyReference("v_BN_N");

    return;
}

/*! This method is used to initialize the simulation by registering all of the states, linking the dynamicEffectors,
 stateEffectors, and the hub, initialize gravity, and initialize the sim with the initial conditions specified in python
 for the simulation */
void SpacecraftPlus::initializeDynamics()
{
    // - SpacecraftPlus initiates all of the spaceCraft mass properties
    Eigen::MatrixXd initM_SC(1,1);
    Eigen::MatrixXd initC_B(3,1);
    Eigen::MatrixXd initISCPntB_B(3,3);
    Eigen::MatrixXd initCPrime_B(3,1);
    Eigen::MatrixXd initISCPntBPrime_B(3,3);
    Eigen::MatrixXd systemTime(2,1);
    systemTime.setZero();
    // - Create the properties
    this->m_SC = this->dynManager.createProperty("m_SC", initM_SC);
    this->c_B = this->dynManager.createProperty("centerOfMassSC", initC_B);
    this->ISCPntB_B = this->dynManager.createProperty("inertiaSC", initISCPntB_B);
    this->ISCPntBPrime_B = this->dynManager.createProperty("inertiaPrimeSC", initISCPntBPrime_B);
    this->cPrime_B = this->dynManager.createProperty("centerOfMassPrimeSC", initCPrime_B);
    this->property_dcm_BS = this->dynManager.createProperty(this->struct2BdyPropertyName, this->dcm_BS);
    this->sysTime = this->dynManager.createProperty(this->sysTimePropertyName, systemTime);
    
    // - Register the gravity properties with the dynManager, 'erbody wants g_N!
    this->gravField.registerProperties(this->dynManager);
    
    // - Register the hub states
    this->hub.registerStates(this->dynManager);
    
    // - Loop through stateEffectors to register their states
    std::vector<StateEffector*>::iterator stateIt;
    for(stateIt = this->states.begin(); stateIt != this->states.end(); stateIt++)
    {
        (*stateIt)->registerStates(this->dynManager);
    }
    
    // - Link in states for the spaceCraftPlus, gravity and the hub
    this->linkInStates(this->dynManager);
    this->gravField.linkInStates(this->dynManager);
    this->hub.linkInStates(this->dynManager);
    
    // - Loop through the stateEffectros to link in the states needed
    for(stateIt = this->states.begin(); stateIt != this->states.end(); stateIt++)
    {
        (*stateIt)->linkInStates(this->dynManager);
    }
    
    // - Loop through the dynamicEffectors to link in the states needed
    std::vector<DynamicEffector*>::iterator dynIt;
    for(dynIt = this->dynEffectors.begin(); dynIt != this->dynEffectors.end(); dynIt++)
    {
        (*dynIt)->linkInStates(this->dynManager);
    }

    // - Call equations of motion at time zero
	this->equationsOfMotion(0.0);
    
    return;
}

/*! This method is solving Xdot = F(X,t) for the system. The hub needs to calculate its derivatives, along with all of 
 the stateEffectors. The hub also has gravity and dynamicEffectors acting on it and these relationships are controlled 
 in this method. At the end of this method all of the states will have their corresponding state derivatives set in the 
 dynParam Manager thus solving for Xdot*/
void SpacecraftPlus::equationsOfMotion(double t)
{
    // - Update time to the current time
    uint64_t CurrentSimNanos;
    CurrentSimNanos = this->simTimePrevious + (t-this->timePrevious)/NANO2SEC;
    (*this->sysTime) << CurrentSimNanos, t;

    // - Zero all Matrices and vectors for back-sub and the dynamics
    this->hub.matrixA.setZero();
    this->hub.matrixB.setZero();
    this->hub.matrixC.setZero();
    this->hub.matrixD.setZero();
    this->hub.vecTrans.setZero();
    this->hub.vecRot.setZero();
    this->hub.sumForceExternal_B.setZero();
    this->hub.sumForceExternal_N.setZero();
    this->hub.sumTorquePntB_B.setZero();

    // - Zero the properties which will get populated in this method
    (*this->m_SC).setZero();
    (*this->c_B).setZero();
    (*this->ISCPntB_B).setZero();
    (*this->cPrime_B).setZero();
    (*this->ISCPntBPrime_B).setZero();

    // Add in hubs mass props to the spacecraft mass props
    this->hub.updateEffectorMassProps(t);
    (*this->m_SC)(0,0) += this->hub.effProps.mEff;
    (*this->ISCPntB_B) += this->hub.effProps.IEffPntB_B;
    (*this->c_B) += this->hub.effProps.mEff*this->hub.effProps.rEff_CB_B;

    // - Loop through state effectors to get mass props
    std::vector<StateEffector*>::iterator it;
    for(it = this->states.begin(); it != this->states.end(); it++)
    {
        (*it)->updateEffectorMassProps(t);
        // - Add in effectors mass props into mass props of spacecraft
        (*this->m_SC)(0,0) += (*it)->effProps.mEff;
        (*this->ISCPntB_B) += (*it)->effProps.IEffPntB_B;
        (*this->c_B) += (*it)->effProps.mEff*(*it)->effProps.rEff_CB_B;
        (*this->ISCPntBPrime_B) += (*it)->effProps.IEffPrimePntB_B;
        (*this->cPrime_B) += (*it)->effProps.mEff*(*it)->effProps.rEffPrime_CB_B;
    }

    // Divide c_B and cPrime_B by the total mass of the spaceCraft to finalize c_B and cPrime_B
    (*this->c_B) = (*this->c_B)/(*this->m_SC)(0,0);
    (*this->cPrime_B) = (*this->cPrime_B)/(*this->m_SC)(0,0);

    // - This is where gravity is computed (gravity needs to know c_B to calculated gravity about r_CN_N)
    this->gravField.computeGravityField();

    // - Loop through state effectors to get contributions for back-substitution
    for(it = this->states.begin(); it != this->states.end(); it++)
    {
        /* - Set the contribution matrices to zero (just in case a stateEffector += on the matrix or the stateEffector
         doesn't have a contribution for a matrix and doesn't set the matrix to zero */
        this->matrixAContr.setZero();
        this->matrixBContr.setZero();
        this->matrixCContr.setZero();
        this->matrixDContr.setZero();
        this->vecTransContr.setZero();
        this->vecRotContr.setZero();

        // - Call the update contributions method for the stateEffectors and add in contributions to the hub matrices
        (*it)->updateContributions(t, this->matrixAContr, this->matrixBContr, this->matrixCContr, this->matrixDContr,
                                   this->vecTransContr, this->vecRotContr);
        this->hub.matrixA += this->matrixAContr;
        this->hub.matrixB += this->matrixBContr;
        this->hub.matrixC += this->matrixCContr;
        this->hub.matrixD += this->matrixDContr;
        this->hub.vecTrans += this->vecTransContr;
        this->hub.vecRot += this->vecRotContr;
    }

    // - Loop through dynEffectors to compute force and torque on the s/c
    std::vector<DynamicEffector*>::iterator dynIt;
    for(dynIt = this->dynEffectors.begin(); dynIt != this->dynEffectors.end(); dynIt++)
    {
        // - Compute the force and torque contributions from the dynamicEffectors
        (*dynIt)->computeBodyForceTorque(t);
        this->hub.sumForceExternal_N += (*dynIt)->forceExternal_N;
        this->hub.sumForceExternal_B += (*dynIt)->forceExternal_B;
        this->hub.sumTorquePntB_B += (*dynIt)->torqueExternalPntB_B;
    }

    // - Compute the derivatives of the hub states before looping through stateEffectors
    this->hub.computeDerivatives(t);

    // - Loop through state effectors for compute derivatives
    for(it = states.begin(); it != states.end(); it++)
    {
        (*it)->computeDerivatives(t);
    }

    return;
}

/*! This method is used to integrate the state forward in time, switch MRPs, calculate energy and momentum, and 
 calculate the accumulated deltaV */
void SpacecraftPlus::integrateState(double t)
{
    // - Find the time step
	double localTimeStep = t - timePrevious;

    // - Find v_CN_N before integration for accumulated DV
    Eigen::Vector3d oldV_BN_N;  // - V_BN_N before integration
    Eigen::Vector3d oldV_CN_N;  // - V_CN_N before integration
    Eigen::Vector3d oldC_B;     // - Center of mass offset before integration
    Eigen::MRPd oldSigma_BN;    // - Sigma_BN before integration
    Eigen::Matrix3d oldDcm_NB;  // - dcm_NB before integration
    // - Get center of mass, v_BN_N and dcm_NB from the dyn manager
    oldV_BN_N = this->hubV_N->getState();
    oldC_B = *this->c_B;
    oldSigma_BN = (Eigen::Vector3d) this->hubSigma->getState();
    // - Finally find v_CN_N
    oldDcm_NB = oldSigma_BN.toRotationMatrix();
    oldV_CN_N = oldV_BN_N + oldDcm_NB*((Eigen::Vector3d) this->hubOmega_BN_B->getState()).cross(oldC_B);

    // - Integrate the state forward in time
	this->integrator->integrate(t, localTimeStep);
	this->timePrevious = t;     // - copy the current time into previous time for next integrate state call
    
    // Lets switch those MRPs!!
    Eigen::Vector3d sigmaBNLoc;
    sigmaBNLoc = (Eigen::Vector3d) this->hubSigma->getState();
    if (sigmaBNLoc.norm() > 1) {
        sigmaBNLoc = -sigmaBNLoc/(sigmaBNLoc.dot(sigmaBNLoc));
        this->hubSigma->setState(sigmaBNLoc);
        this->MRPSwitchCount++;
    }

    // - Find v_CN_N after the integration for accumulated DV
    Eigen::Vector3d newV_BN_N;  // - V_BN_N after integration
    Eigen::Vector3d newV_CN_N;  // - V_CN_N after integration
    Eigen::Vector3d newC_B;     // - Center of mass offset after integration
    Eigen::MRPd newSigma_BN;    // - Sigma_BN after integration
    Eigen::Matrix3d newDcm_NB;  // - dcm_NB after integration
    // - Get center of mass, v_BN_N and dcm_NB
    newC_B = *this->c_B;
    newV_BN_N = this->hubV_N->getState();
    newSigma_BN = sigmaBNLoc;
    newDcm_NB = newSigma_BN.toRotationMatrix();
    newV_CN_N = newV_BN_N + newDcm_NB*((Eigen::Vector3d) this->hubOmega_BN_B->getState()).cross(newC_B);

    // - Find change in velocity
    Eigen::Vector3d dV_N;
    dV_N = newV_CN_N - oldV_CN_N;
    // - Subtract out gravity
    Eigen::Vector3d g_N;
    g_N = *(this->hub.g_N);
    dV_N -= g_N*localTimeStep;

    // - Find accumulated DV in the body frame
    Eigen::Matrix3d dcm_BN;
    dcm_BN = newDcm_NB.transpose();
    this->dvAccum_B += dcm_BN*dV_N;

    // - Compute Energy and Momentum
    this->computeEnergyMomentum(t);

    return;
}

/*! This method is used to find the total energy and momentum of the spacecraft. It finds the total orbital energy,
 total orbital angular momentum, total rotational energy and total rotational angular momentum. These values are used 
 for validation purposes. */
void SpacecraftPlus::computeEnergyMomentum(double t)
{
    // - Grab values from state Manager
    Eigen::Vector3d rLocal_BN_N;
    Eigen::Vector3d rDotLocal_BN_N;
    Eigen::MRPd sigmaLocal_BN;
    Eigen::Vector3d omegaLocal_BN_B;
    rLocal_BN_N = hubR_N->getState();
    rDotLocal_BN_N = hubV_N->getState();
    sigmaLocal_BN = (Eigen::Vector3d ) hubSigma->getState();
    omegaLocal_BN_B = hubOmega_BN_B->getState();

    // - Find DCM's
    Eigen::Matrix3d dcmLocal_NB;
    Eigen::Matrix3d dcmLocal_BN;
    dcmLocal_NB = sigmaLocal_BN.toRotationMatrix();
    dcmLocal_BN = dcmLocal_NB.transpose();

    // - Convert from inertial frame to body frame
    Eigen::Vector3d rBNLocal_B;
    Eigen::Vector3d rDotBNLocal_B;
    rBNLocal_B = dcmLocal_BN*rLocal_BN_N;
    rDotBNLocal_B = dcmLocal_BN*rDotLocal_BN_N;

    // - zero necessarry variables
    Eigen::Vector3d totOrbAngMomPntN_B;
    Eigen::Vector3d totRotAngMomPntC_B;
    Eigen::Vector3d cLocal_B;
    Eigen::Vector3d cPrimeLocal_B;
    Eigen::Vector3d cDotLocal_B;
    totOrbAngMomPntN_B.setZero();
    totRotAngMomPntC_B.setZero();
    cLocal_B.setZero();
    cPrimeLocal_B.setZero();
    cDotLocal_B.setZero();
    this->totOrbAngMomPntN_N.setZero();
    this->totRotAngMomPntC_N.setZero();
    this->rotAngMomPntCContr_B.setZero();
    this->totOrbKinEnergy = 0.0;
    this->totRotEnergy = 0.0;
    this->rotEnergyContr = 0.0;
    double mSCLocal = 0.0;

    // - Get the hubs contribution
    this->hub.updateEnergyMomContributions(t, this->rotAngMomPntCContr_B, this->rotEnergyContr);
    mSCLocal += this->hub.effProps.mEff;
    cLocal_B += this->hub.effProps.mEff*this->hub.effProps.rEff_CB_B;
    totRotAngMomPntC_B += this->rotAngMomPntCContr_B;
    this->totRotEnergy += this->rotEnergyContr;

    // - Loop over stateEffectors to get their contributions to energy and momentum
    std::vector<StateEffector*>::iterator it;
    for(it = this->states.begin(); it != this->states.end(); it++)
    {
        // - Set the matrices to zero
        this->rotAngMomPntCContr_B.setZero();
        this->rotEnergyContr = 0.0;

        // - Add in effectors mass props into mass props of spacecraft
        (*it)->updateEffectorMassProps(t);
        mSCLocal += (*it)->effProps.mEff;
        cLocal_B += (*it)->effProps.mEff*(*it)->effProps.rEff_CB_B;
        cPrimeLocal_B += (*it)->effProps.mEff*(*it)->effProps.rEffPrime_CB_B;

        // - Call energy and momentum calulations for stateEffectors
        (*it)->updateEnergyMomContributions(t, this->rotAngMomPntCContr_B, this->rotEnergyContr);
        totRotAngMomPntC_B += this->rotAngMomPntCContr_B;
        this->totRotEnergy += this->rotEnergyContr;
    }

    // - correct c_B and cPrime_B by 1/mSC
    cLocal_B = cLocal_B/mSCLocal;
    cPrimeLocal_B = cPrimeLocal_B/mSCLocal;

    // - Find cDot_B
    cDotLocal_B = cPrimeLocal_B + omegaLocal_BN_B.cross(cLocal_B);

    // - Find orbital kinetic energy for the spacecraft
    this->totOrbKinEnergy += 1.0/2.0*mSCLocal*(rDotBNLocal_B.dot(rDotBNLocal_B) + 2.0*rDotBNLocal_B.dot(cDotLocal_B)
                                               + cDotLocal_B.dot(cDotLocal_B));

    // - Find total rotational energy
    this->totRotEnergy += -1.0/2.0*mSCLocal*cDotLocal_B.dot(cDotLocal_B);

    // - Find orbital angular momentum for the spacecraft
    Eigen::Vector3d rCN_N;
    Eigen::Vector3d rDotCN_N;
    rCN_N = rLocal_BN_N + dcmLocal_NB*cLocal_B;
    rDotCN_N = rDotLocal_BN_N + dcmLocal_NB*cDotLocal_B;
    this->totOrbAngMomPntN_N = mSCLocal*(rCN_N.cross(rDotCN_N));

    // - Find rotational angular momentum for the spacecraft
    totRotAngMomPntC_B += -mSCLocal*cLocal_B.cross(cDotLocal_B);
    this->totRotAngMomPntC_N = dcmLocal_NB*totRotAngMomPntC_B;
    
    return;
}
