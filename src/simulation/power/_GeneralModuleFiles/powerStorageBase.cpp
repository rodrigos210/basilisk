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

#include "architecture/utilities/astroConstants.h"
#include "architecture/utilities/linearAlgebra.h"
#include "architecture/utilities/macroDefinitions.h"
#include "powerStorageBase.h"


/*! This method initializes some basic parameters for the module.
 @return void
 */
PowerStorageBase::PowerStorageBase()
{
    this->previousTime = 0;
    this->nodePowerUseInMsgs.clear();

    this->storedCharge = 0.0;
    this->storedCharge_Init = 0.0;

    return;
}

/*! Destructor.
 @return void
 */
PowerStorageBase::~PowerStorageBase()
{
    return;
}


/*! Adds a PowerNodeUsageMsgPayload input message to iterate over
 @return void
 @param tmpNodeMsg Message name corresponding to a PowerNodeUsageMsgPayload.
 */
void PowerStorageBase::addPowerNodeToModel(Message<PowerNodeUsageMsgPayload> *tmpNodeMsg){
    this->nodePowerUseInMsgs.push_back(tmpNodeMsg->addSubscriber());
    return;
}

/*! SelfInit creates one PowerStorageMsgPayload for the simPowerStorageBase instance.
  @return void
*/
void PowerStorageBase::SelfInit()
{
    //! - call the custom SelfInit() method to add addtional self initialization steps
    customSelfInit();

    return;
}

/*! Subscribes to messages with the names provided by addPowerNodeToModel. Also calls customCrossInit.
 @return void
 */
void PowerStorageBase::CrossInit()
{
    //!- call the custom CrossInit() method to all additional cross initialization steps
    customCrossInit();

    return;
}

/*! This method is used to reset the module.
 @return void
 */
void PowerStorageBase::Reset(uint64_t CurrentSimNanos)
{
    this->previousTime = 0;
    if (this->storedCharge_Init >= 0.0) {
    this->storedCharge = this->storedCharge_Init;
    } else {
        bskLogger.bskLog(BSK_ERROR, "The storedCharge_Init variable must be set to a non-negative value.");
    }

    //! - call the custom environment module reset method
    customReset(CurrentSimNanos);

    return;
}

/*! Writes out one PowerStorageStatusMsgPayload
 @param CurrentClock The current time used for time-stamping the message
 @return void
 */
void PowerStorageBase::writeMessages(uint64_t CurrentClock)
{
    this->batPowerOutMsg.write(&this->storageStatusMsg, this->moduleID, CurrentClock);

    //! - call the custom method to perform additional output message writing
    customWriteMessages(CurrentClock);

    return;
}

/*! This method is used to read the incoming power supply/usage messages and store them for future use.
 @return void
 */
bool PowerStorageBase::readMessages()
{
    PowerNodeUsageMsgPayload nodeMsg;

    this->nodeWattMsgs.clear();

    //! - read in the power node use/supply messages
    bool powerRead = true;
    bool tmpPowerRead;
    if(this->nodePowerUseInMsgs.size() > 0)
    {
        for(int c=0; c<this->nodePowerUseInMsgs.size(); c++)
        {
            nodeMsg = this->nodePowerUseInMsgs.at(c)();
            tmpPowerRead = this->nodePowerUseInMsgs.at(c).isWritten();
            powerRead = powerRead && tmpPowerRead;

            this->nodeWattMsgs.push_back(nodeMsg);
        }
    }
    else {
        bskLogger.bskLog(BSK_WARNING, "Power storage has no power node messages to read.");
        powerRead = false;
    }

    //! - call the custom method to perform additional input reading
    bool customRead = customReadMessages();

    return(powerRead && customRead);
}

/*! This method sums over the power used/generated by the attached simPowerNodes.
  @return double currentSum: current net power in Watts
 */
double PowerStorageBase::sumAllInputs(){
    double currentSum = 0.0;

    std::vector<PowerNodeUsageMsgPayload>::iterator it;
    for(it = nodeWattMsgs.begin(); it != nodeWattMsgs.end(); it++) {

        currentSum += (*it).netPower;
    }

    return currentSum;
}

/*! This method integrates the power use provided by the attached modules.
  @return void
 */
void PowerStorageBase::integratePowerStatus(double currentTime)
{
    this->currentTimestep = currentTime - this->previousTime;
    //! - loop over all the power nodes and sum their contributions
    this->currentPowerSum = this->sumAllInputs();
    this->evaluateBatteryModel(&(this->storageStatusMsg)); // Computes the battery charge status, if applicable.
    this->previousTime = currentTime;
    return;
}


/*! Implements readMessages, integratePowerStatus, and writeMessages for the rest of the sim.
 @return void
 @param currentSimNanos The current simulation time in nanoseconds
 */
void PowerStorageBase::UpdateState(uint64_t currentSimNanos)
{
    //! - update net power information
    if(this->readMessages())
    {
        this->integratePowerStatus(currentSimNanos*NANO2SEC);
    } else {
        /* zero the output message if no input messages were received. */
        this->storageStatusMsg = this->batPowerOutMsg.zeroMsgPayload();
    }

    //! - write out neutral density message
    this->writeMessages(currentSimNanos);

    return;
}


/*! Custom SelfInit() method.  This allows a child class to add additional functionality to the SelfInit() method
 @return void
 */
void PowerStorageBase::customSelfInit()
{
    return;
}

/*! Custom CrossInit() method.  This allows a child class to add additional functionality to the CrossInit() method
 @return void
 */
void PowerStorageBase::customCrossInit()
{
    return;
}

/*! Custom Reset() method.  This allows a child class to add additional functionality to the Reset() method
 @return void
 */
void PowerStorageBase::customReset(uint64_t CurrentClock)
{
    return;
}

/*! custom Write method, similar to customSelfInit.
 @return void
 */
void PowerStorageBase::customWriteMessages(uint64_t CurrentClock)
{
    return;
}

/*! Custom read method, similar to customSelfInit; returns `true' by default.
 @return void
 */
bool PowerStorageBase::customReadMessages()
{
    return true;
}
