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
#include "environment/ephemeris_converter/ephemeris_converter.h"
#include "architecture/messaging/system_messaging.h"
#include "utilities/linearAlgebra.h"
#include <string.h>

EphemerisConverter::EphemerisConverter()
{
    CallCounts = 0;
    numOutputBuffers = 2;
    return;
}

EphemerisConverter::~EphemerisConverter()
{
    return;
}

bool EphemerisConverter::LinkMessages()
{
    int64_t sourceID;
    int64_t destID;
    bool messagesFound = true;
    std::map<std::string, std::string>::iterator it;
    std::map<int64_t, IDEphemerisOutputContainer>::iterator mapIt;
    for(it=messageNameMap.begin(); it!= messageNameMap.end(); it++)
    {
        sourceID = SystemMessaging::GetInstance()->subscribeToMessage(it->first,
            sizeof(SpicePlanetStateMessage), moduleID);
        destID = SystemMessaging::GetInstance()->FindMessageID(it->second);
        messagesFound &= (sourceID >= 0 && destID >= 0);
        mapIt = messageIDMap.find(destID);
        mapIt->second.inputID = sourceID;
    }
    
    return(true);
}

void EphemerisConverter::SelfInit()
{
    IDEphemerisOutputContainer ephemContainer;
    std::map<std::string, std::string>::iterator it;
    int64_t destID;
 
    memset(&ephemContainer, 0x0, sizeof(IDEphemerisOutputContainer));
    messageIDMap.clear();
    
    for(it=messageNameMap.begin(); it!= messageNameMap.end(); it++)
    {
        destID = SystemMessaging::GetInstance()->CreateNewMessage(it->second,
            sizeof(EphemerisOutputData), numOutputBuffers, "EphemerisOutputData",
            moduleID);
        messageIDMap.insert(std::pair<int64_t, IDEphemerisOutputContainer>
            (destID, ephemContainer));
        
    }
}

void EphemerisConverter::CrossInit()
{
    messagesLinked = LinkMessages();
}

void EphemerisConverter::convertEphemData(uint64_t clockNow)
{
    std::map<int64_t, IDEphemerisOutputContainer>::iterator it;
    for(it=messageIDMap.begin(); it!=messageIDMap.end(); it++)
    {
        v3Copy(it->second.messageData.PositionVector,
               it->second.outputData.r_BdyZero_N);
        v3Copy(it->second.messageData.VelocityVector,
               it->second.outputData.v_BdyZero_N);
        it->second.outputData.timeTag = it->second.clockTime*1.0E-9;
        
    }
    
}

void EphemerisConverter::readInputMessages()
{
    SingleMessageHeader localHeader;
    std::map<int64_t, IDEphemerisOutputContainer>::iterator it;
    
    if(!this->messagesLinked)
    {
        this->messagesLinked = LinkMessages();
    }
    
    for(it=messageIDMap.begin(); it!=messageIDMap.end(); it++)
    {
        SystemMessaging::GetInstance()->ReadMessage(it->second.inputID,
            &localHeader, sizeof(SpicePlanetStateMessage),
            (uint8_t *) (&(it->second.messageData)));
        it->second.clockTime = localHeader.WriteClockNanos;
    }
    
}

void EphemerisConverter::writeOutputMessages(uint64_t CurrentSimNanos)
{

    std::map<int64_t, IDEphemerisOutputContainer>::iterator it;
    for(it=messageIDMap.begin(); it!=messageIDMap.end(); it++)
    {
        SystemMessaging::GetInstance()->WriteMessage(it->first,
            CurrentSimNanos, sizeof(EphemerisOutputData),
            reinterpret_cast<uint8_t *>(&it->second.outputData));
    }
    

}

void EphemerisConverter::UpdateState(uint64_t CurrentSimNanos)
{
    readInputMessages();
    convertEphemData(CurrentSimNanos);
    writeOutputMessages(CurrentSimNanos);
}
