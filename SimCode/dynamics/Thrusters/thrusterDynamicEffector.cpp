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


#include "thrusterDynamicEffector.h"
#include "architecture/messaging/system_messaging.h"
#include "utilities/linearAlgebra.h"
#include "utilities/astroConstants.h"
#include "../ADCSAlgorithms/effectorInterfaces/errorConversion/vehEffectorOut.h"
#include "../ADCSAlgorithms/ADCSUtilities/ADCSAlgorithmMacros.h"
#include <cstring>
#include <iostream>
#include <cmath>

ThrusterDynamicEffector::ThrusterDynamicEffector()
    : stepsInRamp(30) 
    , InputCmds("acs_thruster_cmds")
    , thrusterOutMsgNameBufferCount(2)
    , prevFireTime(0.0)
    , CmdsInMsgID(-1)
    , IncomingCmdBuffer(NULL)
    , prevCommandTime(0xFFFFFFFFFFFFFFFF)
{
    CallCounts = 0;
    return;
}

/*! The destructor.*/
ThrusterDynamicEffector::~ThrusterDynamicEffector()
{
    return;
}

/*! This method is used to clear out the current thruster states and make sure
 that the overall model is ready for firing
 @return void
 */
void ThrusterDynamicEffector::SelfInit()
{
    //! Begin method steps
    //! - Clear out any currently firing thrusters and re-init cmd array
    NewThrustCmds.clear();
    NewThrustCmds.insert(NewThrustCmds.begin(), ThrusterData.size(), 0.0);
    //! - Clear out the incoming command buffer and resize to max thrusters
    if(IncomingCmdBuffer != NULL)
    {
        delete [] IncomingCmdBuffer;
    }
    IncomingCmdBuffer = new ThrustCmdStruct[ThrusterData.size()];
    
    std::vector<ThrusterConfigData>::iterator it;
    uint64_t tmpThrustMsgId;
    std::string tmpThrustMsgName;
    int thrustIdx = 0;
    for (it = ThrusterData.begin(); it != ThrusterData.end(); it++)
    {
        /* # TODO: The string comparison is a provisional way to get only the ACS thruster data into the Message System.
         In the future a better way to handle this distinction should be implemented - Mar Cols */
        if (std::strcmp(this->ModelTag.c_str(), "ACSThrusterDynamics") == 0)
        {
            tmpThrustMsgName = "acs_thruster_" + std::to_string(thrustIdx) + "_data";
            tmpThrustMsgId = SystemMessaging::GetInstance()->
            CreateNewMessage(tmpThrustMsgName, sizeof(ThrusterOutputData), this->thrusterOutMsgNameBufferCount, "ThrusterOutputData", moduleID);
            
            this->thrusterOutMsgNames.push_back(tmpThrustMsgName);
            this->thrusterOutMsgIds.push_back(tmpThrustMsgId);
            
            thrustIdx++;
        }
    }
}

/*! This method is used to connect the input command message to the thrusters.
 It sets the message ID based on what it finds for the input string.  If the
 message is not successfully linked, it will warn the user.
 @return void
 */
void ThrusterDynamicEffector::CrossInit()
{
 /*   MassPropsData localProps;*/
    SingleMessageHeader localHeader;
    //! Begin method steps
    //! - Find the message ID associated with the InputCmds string.
    //! - Warn the user if the message is not successfully linked.
    CmdsInMsgID = SystemMessaging::GetInstance()->subscribeToMessage(InputCmds,
                                                                     MAX_EFF_CNT*sizeof(ThrustCmdStruct), moduleID);
    
/*    propsInID = SystemMessaging::GetInstance()->subscribeToMessage(inputProperties,
                                                                   sizeof(MassPropsData), moduleID);
    SystemMessaging::GetInstance()->ReadMessage(propsInID, &localHeader,
                                                sizeof(MassPropsData), reinterpret_cast<uint8_t *>(&localProps)); */
    std::vector<ThrusterConfigData>::iterator it;
    for (it = ThrusterData.begin(); it != ThrusterData.end(); it++)
    {
/*        m33MultV3(RECAST3X3 localProps.T_str2Bdy, it->inputThrDir_S,
                  it->thrDir_B);
        m33MultV3(RECAST3X3 localProps.T_str2Bdy, it->inputThrLoc_S,
                  it->thrLoc_B);*/
    }
    
}


/*! This method is here to write the output message structure into the specified
 message.  It is currently blank but we will certainly have an output message
 soon.  If it is already here, bludgeon whoever added it and didn't fix the
 comment.sizeof(ThrusterOutputData)
 @param CurrentClock The current time used for time-stamping the message
 @return void
 */
void ThrusterDynamicEffector::WriteOutputMessages(uint64_t CurrentClock)
{
    int idx = 0;
    std::vector<ThrusterConfigData>::iterator it;
    //    std::vector<ThrusterOutputData>acsThrusters;
    ThrusterOutputData tmpThruster;
    for (it = ThrusterData.begin(); it != ThrusterData.end(); it++)
    {
        /* # TODO: The string comparison is a provisional way to get only the ACS thruster data into the Message System.
         In the future a better way to handle this distinction should be implemented - Mar Cols */
        if (std::strcmp(this->ModelTag.c_str(), "ACSThrusterDynamics") == 0)
        {
            tmpThruster.thrusterLocation[0] = it->thrLoc_B[0];
            tmpThruster.thrusterLocation[1] = it->thrLoc_B[1];
            tmpThruster.thrusterLocation[2] = it->thrLoc_B[2];
            tmpThruster.thrusterDirection[0] = it->thrDir_B[0];
            tmpThruster.thrusterDirection[1] = it->thrDir_B[1];
            tmpThruster.thrusterDirection[2] = it->thrDir_B[2];
            tmpThruster.maxThrust = it->MaxThrust;
            tmpThruster.thrustFactor = it->ThrustOps.ThrustFactor;
            //            if (it->ThrustOps.ThrustFactor > 0.0)
            //            {
            //                std::cout << it->ThrustOps.ThrustFactor <<std::endl;
            //            }
            
            SystemMessaging::GetInstance()->WriteMessage(this->thrusterOutMsgIds.at(idx),
                                                         CurrentClock,
                                                         sizeof(ThrusterOutputData),
                                                         reinterpret_cast<uint8_t*>(&tmpThruster),
                                                         moduleID);
            //            acsThrusters.push_back(tempThruster);
            idx ++;
        }
    }
}


/*! This method is used to read the incoming command message and set the
 associated command structure for operating the thrusters.
 @return void
 */
bool ThrusterDynamicEffector::ReadInputs()
{
    
    std::vector<double>::iterator CmdIt;
    uint64_t i;
    bool dataGood;
    //! Begin method steps
    
    //! - Zero the command buffer and read the incoming command array
    SingleMessageHeader LocalHeader;
    memset(IncomingCmdBuffer, 0x0, ThrusterData.size()*sizeof(ThrustCmdStruct));
    memset(&LocalHeader, 0x0, sizeof(LocalHeader));
    dataGood = SystemMessaging::GetInstance()->ReadMessage(CmdsInMsgID, &LocalHeader,
                                                           ThrusterData.size()*sizeof(ThrustCmdStruct),
                                                           reinterpret_cast<uint8_t*> (IncomingCmdBuffer), moduleID);
    
    //! - Check if message has already been read, if stale return
    if(prevCommandTime==LocalHeader.WriteClockNanos || !dataGood) {
        return(false);
    }
    prevCommandTime = LocalHeader.WriteClockNanos;
    
    //! - Set the NewThrustCmds vector.  Using the data() method for raw speed
    double *CmdPtr;
    for(i=0, CmdPtr = NewThrustCmds.data(); i<ThrusterData.size();
        CmdPtr++, i++)
    {
        *CmdPtr = IncomingCmdBuffer[i].OnTimeRequest;
    }
    return(true);
    
}

/*! This method is used to read the new commands vector and set the thruster
 firings appropriately.  It assumes that the ReadInputs method has already been
 run successfully.  It honors all previous thruster firings if they are still
 active.  Note that for unit testing purposes you can insert firings directly
 into NewThrustCmds.
 @return void
 @param CurrentTime The current simulation time converted to a double
 */
void ThrusterDynamicEffector::ConfigureThrustRequests(double CurrentTime)
{
    //! Begin method steps
    std::vector<ThrusterConfigData>::iterator it;
    std::vector<double>::iterator CmdIt;
    std::vector<ThrusterTimePair>::iterator PairIt;
    //! - Iterate through the list of thruster commands that we read in.
    for(CmdIt=NewThrustCmds.begin(), it=ThrusterData.begin();
        it != ThrusterData.end(); it++, CmdIt++)
    {
        if(*CmdIt >= it->MinOnTime) /// - Check to see if we have met minimum for each thruster
        {
            //! - For each case where we are above the minimum firing request, reset the thruster
            it->ThrustOps.ThrustOnCmd = *CmdIt;
            it->ThrustOps.fireCounter += it->ThrustOps.ThrustFactor > 0.0
            ? 0 : 1;
        }
        else
        {
            //! - Will ensure that thruster shuts down once this cmd expires
            it->ThrustOps.ThrustOnCmd = it->ThrustOps.ThrustFactor > 0.0
            ? *CmdIt : 0.0;
        }
        it->ThrustOps.ThrusterStartTime = CurrentTime;
        it->ThrustOps.PreviousIterTime = CurrentTime;
        it->ThrustOps.ThrustOnRampTime = 0.0;
        it->ThrustOps.ThrustOnSteadyTime = 0.0;
        it->ThrustOps.ThrustOffRampTime = 0.0;
        //! After we have assigned the firing to the internal thruster, zero the command request.
        *CmdIt = 0.0;
    }
    
}

void ThrusterDynamicEffector::linkInStates(const DynParamManager& states){
}


void ThrusterDynamicEffector::computeBodyForceTorque(){
}

/*! This method is used to get the current force for a thruster firing.  It uses
 the configuration data associated with a given thruster and the current clock
 time to determine what state and force the thruster should be in.
 @return void
 @param CurrentThruster Pointer to the configuration data for a given thruster
 @param CurrentTime The current simulation clock time converted to a double
 */
void ThrusterDynamicEffector::ComputeThrusterFire(ThrusterConfigData *CurrentThruster,
                                           double CurrentTime)
{
    //! Begin method steps
    std::vector<ThrusterTimePair>::iterator it;
    ThrusterOperationData *ops = &(CurrentThruster->ThrustOps);
    //! - Set the current ramp time for the thruster firing
    if(ops->ThrustOnRampTime == 0.0 &&
       CurrentThruster->ThrusterOnRamp.size() > 0)
    {
        ops->ThrustOnRampTime = thrFactorToTime(CurrentThruster,
                                                &(CurrentThruster->ThrusterOnRamp));
    }
    double LocalOnRamp = (CurrentTime - ops->PreviousIterTime) +
    ops->ThrustOnRampTime;
    double prevValidThrFactor = 0.0;
    double prevValidIspFactor = 0.0;
    double prevValidDelta = 0.0;
    
    //! - Iterate through the on-ramp for the thruster data to find where we are in ramp
    for(it = CurrentThruster->ThrusterOnRamp.begin();
        it != CurrentThruster->ThrusterOnRamp.end(); it++)
    {
        //! - If the current on-time is less than the ramp delta, set that ramp thrust factor
        if(LocalOnRamp < it->TimeDelta)
        {
            ops->ThrustFactor = (it->ThrustFactor - prevValidThrFactor)/
            (it->TimeDelta - prevValidDelta) *
            (LocalOnRamp - prevValidDelta) + prevValidThrFactor;
            ops->IspFactor = (it->IspFactor - prevValidIspFactor)/
            (it->TimeDelta - prevValidDelta) *
            (LocalOnRamp - prevValidDelta) + prevValidIspFactor;
            ops->ThrustOnRampTime = LocalOnRamp;
            ops->totalOnTime += (CurrentTime - ops->PreviousIterTime);
            ops->PreviousIterTime = CurrentTime;
            return;
        }
        prevValidThrFactor = it->ThrustFactor;
        prevValidIspFactor = it->IspFactor;
        prevValidDelta = it->TimeDelta;
    }
    //! - If we did not find the current time in the on-ramp, then we are at steady-state
    
    ops->ThrustOnSteadyTime += (CurrentTime - ops->PreviousIterTime);
    ops->totalOnTime += (CurrentTime - ops->PreviousIterTime);
    ops->PreviousIterTime = CurrentTime;
    ops->ThrustFactor = ops->IspFactor = 1.0;
    ops->ThrustOffRampTime = 0.0;
}


/*! This method is used to go through the process of shutting down a thruster
 once it has been commanded off.  It uses the configuration data associated with
 a given thruster and the current clock time to turn off the thruster according
 to the ramp profile.
 @return void
 @param CurrentThruster Pointer to the configuration data for a given thruster
 @param CurrentTime The current simulation clock time converted to a double
 */
void ThrusterDynamicEffector::ComputeThrusterShut(ThrusterConfigData *CurrentThruster,
                                           double CurrentTime)
{
    //! Begin method steps
    std::vector<ThrusterTimePair>::iterator it;
    ThrusterOperationData *ops = &(CurrentThruster->ThrustOps);
    
    //! - Set the current off-ramp time based on the previous clock time and now
    if(ops->ThrustOffRampTime == 0.0 &&
       CurrentThruster->ThrusterOffRamp.size() > 0)
    {
        ops->ThrustOffRampTime = thrFactorToTime(CurrentThruster,
                                                 &(CurrentThruster->ThrusterOffRamp));
    }
    double LocalOffRamp = (CurrentTime - ops->PreviousIterTime) +
    ops->ThrustOffRampTime;
    double prevValidThrFactor = 1.0;
    double prevValidIspFactor = 1.0;
    double prevValidDelta = 0.0;
    //! - Iterate through the off-ramp to find the place where we are in the shutdown ramp
    for(it = CurrentThruster->ThrusterOffRamp.begin();
        it != CurrentThruster->ThrusterOffRamp.end(); it++)
    {
        //! - Once we find the location in the off-ramp, set that thrust factor to current
        if(LocalOffRamp < it->TimeDelta)
        {
            ops->ThrustFactor = (it->ThrustFactor - prevValidThrFactor)/
            (it->TimeDelta - prevValidDelta) *
            (LocalOffRamp - prevValidDelta) + prevValidThrFactor;
            ops->IspFactor = (it->IspFactor - prevValidIspFactor)/
            (it->TimeDelta - prevValidDelta) *
            (LocalOffRamp - prevValidDelta) + prevValidIspFactor;
            ops->ThrustOffRampTime = LocalOffRamp;
            ops->PreviousIterTime = CurrentTime;
            return;
        }
        prevValidThrFactor = it->ThrustFactor;
        prevValidIspFactor = it->IspFactor;
        prevValidDelta = it->TimeDelta;
    }
    //! - If we did not find the location in the off-ramp, we've reached the end state and zero thrust
    ops->ThrustFactor = ops->IspFactor = 0.0;
    ops->ThrustOnRampTime = 0.0;
}

/* */
void ThrusterDynamicEffector::updateMassProperties(double CurrentTime)
{
    double dt = CurrentTime - prevFireTime;
//    double oldMass = objProps.Mass;
//    objProps.Mass = oldMass - mDotTotal*dt;
//   vScale(objProps.Mass/oldMass, objProps.InertiaTensor, 9,
//           objProps.InertiaTensor);
    
}


/*! This method finds the location in the time in the specified ramp that
 corresponds to the current thruster thrust factor.  It is designed to
 initialize the ramp-up and ramp-down effects to the appropriate point in
 their respective ramps based on the initial force
 @return double The time in the ramp associated with the thrust factor
 @param thrData The data for the thruster that we are currently firing
 @param thrRamp This just allows us to avoid switching to figure out which ramp
 */
double ThrusterDynamicEffector::thrFactorToTime(ThrusterConfigData *thrData,
                                         std::vector<ThrusterTimePair> *thrRamp)
{
    //! Begin method steps
    std::vector<ThrusterTimePair>::iterator it;
    //! - Grab the last element in the ramp and determine if it goes up or down
    it = thrRamp->end();
    it--;
    double rampTime = it->TimeDelta;
    double rampDirection = std::copysign(1.0,
                                         it->ThrustFactor - thrData->ThrustOps.ThrustFactor);
    
    //! - Initialize the time computation functiosn based on ramp direction
    double prevValidThrFactor = rampDirection < 0 ? 1.0 : 0.0;
    double prevValidDelta = 0.0;
    for(it=thrRamp->begin(); it!=thrRamp->end(); it++)
    {
        //! - Determine if we haven't reached the right place in the ramp
        bool pointCheck = rampDirection > 0 ?
        it->ThrustFactor <= thrData->ThrustOps.ThrustFactor :
        it->ThrustFactor >= thrData->ThrustOps.ThrustFactor;
        //! - If we have not located the location in the ramp, continue
        if(pointCheck)
        {
            prevValidThrFactor = it->ThrustFactor;
            prevValidDelta = it->TimeDelta;
            continue;
        }
        
        //! - Linearly interpolate between the points, check for numerical garbage, and return clean interpolation
        rampTime = (it->TimeDelta - prevValidDelta)/(it->ThrustFactor -
                                                     prevValidThrFactor) * (thrData->ThrustOps.ThrustFactor -
                                                                            prevValidThrFactor) + prevValidDelta;
        rampTime = rampTime < 0.0 ? 0.0 : rampTime;
        break; 
    }
    
    return(rampTime);
}


/*! This method is the main cyclical call for the scheduled part of the thruster
 dynamics model.  It reads the current commands array and sets the thruster
 configuration data based on that incoming command set.  Note that the main
 dynamical method (ComputeDynamics()) is not called here and is intended to be
 called from the dynamics plant in the system
 @return void
 @param CurrentSimNanos The current simulation time in nanoseconds
 */
void ThrusterDynamicEffector::UpdateState(uint64_t CurrentSimNanos)
{
    //! Begin method steps
    //! - Read the inputs and then call ConfigureThrustRequests to set up dynamics
    if(ReadInputs())
    {
        ConfigureThrustRequests(CurrentSimNanos*1.0E-9);
    }
    WriteOutputMessages(CurrentSimNanos);
    
}
