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


#ifndef VSCMGSTATEEFFECTOR_H
#define VSCMGSTATEEFFECTOR_H

#include "../_GeneralModuleFiles/stateEffector.h"
#include "../_GeneralModuleFiles/dynParamManager.h"
#include "../_GeneralModuleFiles/dynamicEffector.h"
#include "../_GeneralModuleFiles/dynamicObject.h"
#include <Eigen/Dense>
#include "../SimFswInterfaceMessages/macroDefinitions.h"
#include "_GeneralModuleFiles/sys_model.h"
#include "../../../SimFswInterfaceMessages/vscmgSpeedIntMsg.h"
#include "../../simMessages/vscmgCmdSimMsg.h"
#include "../../simMessages/vscmgConfigSimMsg.h"
#include "../../SimFswInterfaceMessages/vscmgArrayTorqueIntMsg.h"
#include "../../SimFswInterfaceMessages/macroDefinitions.h"

#include "utilities/avsEigenMRP.h"
#include "utilities/avsEigenSupport.h"

/*! @brief Abstract class that is used to implement an effector impacting a dynamic body 
           that does not itself maintain a state or represent a changing component of
           the body (for example: gravity, thrusters, solar radiation pressure, etc.)
 */



class VSCMGStateEffector:  public SysModel, public StateEffector {
public:
    VSCMGStateEffector();
	~VSCMGStateEffector();
	void registerStates(DynParamManager& states);
	void linkInStates(DynParamManager& states);
	void updateContributions(double integTime, Eigen::Matrix3d & matrixAcontr, Eigen::Matrix3d & matrixBcontr, Eigen::Matrix3d & matrixCcontr, Eigen::Matrix3d & matrixDcontr, Eigen::Vector3d & vecTranscontr, Eigen::Vector3d & vecRotcontr);
    void computeDerivatives(double integTime);
    void updateEffectorMassProps(double integTime);
    void updateEnergyMomContributions(double integTime, Eigen::Vector3d & rotAngMomPntCContr_B, double & rotEnergyContr);
	void SelfInit();
	void CrossInit();
	void AddVSCMG(VSCMGConfigSimMsg *NewVSCMG) {VSCMGData.push_back(*NewVSCMG);}
	void UpdateState(uint64_t CurrentSimNanos);
	void WriteOutputMessages(uint64_t CurrentClock);
	void ReadInputs();
	void ConfigureVSCMGRequests(double CurrentTime);
    
public:
	std::vector<VSCMGConfigSimMsg> VSCMGData; 	//!< -- VSCMG data structure
    Eigen::MatrixXd *g_N; 						//!< [m/s^2] Gravitational acceleration in N frame components
	std::string InputCmds; 						//!< -- message used to read command inputs
	std::string OutputDataString; 				//!< -- port to use for output data
    uint64_t OutputBufferCount; 				//!< -- Count on number of buffers to output
	std::vector<VSCMGCmdSimMsg> NewVSCMGCmds; 	//!< -- Incoming torque commands
	VSCMGSpeedIntMsg outputStates; 				//!< (-) Output data from the VSCMGs
    std::string nameOfVSCMGOmegasState;
    std::string nameOfVSCMGThetasState;
	std::string nameOfVSCMGGammasState;
	std::string nameOfVSCMGGammaDotsState;
	int numVSCMG;
	int numVSCMGJitter;

private:
	std::vector<std::string> vscmgOutMsgNames;		//!< -- vector with the message names of each VSCMG
	std::vector<uint64_t> vscmgOutMsgIds;          //!< -- vector with the ID of each VSCMG
	int64_t CmdsInMsgID;                      	//!< -- Message ID for incoming data
	int64_t StateOutMsgID;                    	//!< -- Message ID for outgoing data
	VSCMGArrayTorqueIntMsg IncomingCmdBuffer; 	//!< -- One-time allocation for savings
	uint64_t prevCommandTime;                  	//!< -- Time for previous valid thruster firing

	StateData *hubSigma;
	StateData *hubOmega;
	StateData *hubVelocity;
	StateData *OmegasState;
	StateData *thetasState;
	StateData *gammasState;

};

#endif /* STATE_EFFECTOR_H */
