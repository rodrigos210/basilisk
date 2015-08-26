
#include "architecture/system_model/message_logger.h"
#include <cstring>
#include <iostream>

/*! This constructor is used to initialize the message logging data.  It clears
 out the message log list and resets the logger to a clean state.
 */
messageLogger::messageLogger()
{
    logData.clear();
    allLogsLinked = true;
    initBufferSize = 5000000;
}

/*! Nothing to destroy really */
messageLogger::~messageLogger()
{
}

/*! This method inserts a new message onto the logging vector so that it gets
 logged out appropriately.  If the message has already been added once
 already it will just update the log period and return from there.
 @return void
 @param messageName -- The name of the message that we want to log
 @param messagePeriod ns The minimum time between messages that we want to allow
 */
void messageLogger::addMessageLog(std::string messageName, uint64_t messagePeriod)
{
    //! Begin  method steps
    //! - Check to see if we have already commanded a log for this message, if so just update the rate
    std::vector<messageLogContainer>::iterator it;
    for(it=logData.begin(); it != logData.end(); it++)
    {
        if(it->messageName ==  messageName)
        {
            it->writeDelta = messagePeriod;
            return;
        }
    }
    //! - If the message hasn't been added yet, allocate new container, init data, and add to log vector
    messageLogContainer newContainer;
    newContainer.messageName = messageName;
    newContainer.messageID = -1;
    newContainer.lastLogTime = 0;
    newContainer.logInstanceCount = 0;
    newContainer.lastWriteCheck = 0;
    newContainer.writeDelta = messagePeriod;
    newContainer.bufferOffset = 0;
    newContainer.storOff.clear();
    logData.push_back(newContainer);
    //! - Since we have a new message, note that we need to link it during run
    allLogsLinked = false;
}
/*! This method is used to find the appropriate messaged ID associated with
 each message name that has been added to logging.  It warns the user if any
 of the added messages have not been successfully linked.
 @return void
 */
void messageLogger::linkMessages()
{
    //! Begin  method steps
    //! - Since we are linking, go ahead and just relink all messages
    std::vector<messageLogContainer>::iterator it;
    //! - Set the linker indicator to good and only falsify it if we don't find a message
    allLogsLinked = true;
    for(it=logData.begin(); it != logData.end(); it++)
    {
        it->messageID = SystemMessaging::GetInstance()->
        FindMessageID(it->messageName);
        //! - Warn the user if linking failed and note that logging won't work for that message
        if(it->messageID < 0)
        {
            std::cout << "Warning, failed to find message: " << it->messageName;
            std::cout << std::endl << "Disabling logging for it"<<std::endl;
        }
        else
        {
            it->messageBuffer.IncreaseStorage(initBufferSize);
        }
    }
}
/*! This method executes the actual log generation activity.  It is focused on
 simplicity currently so there is room to speed things up if this
 functionality begins to consume significant parts of our runtime
 @return void
 */
void messageLogger::logAllMessages()
{
    //! Begin  method steps
    //! - Iterate through the message list and log any needed messages
    std::vector<messageLogContainer>::iterator it;
    for(it=logData.begin(); it != logData.end(); it++)
    {
        //! - Message ID is invalid if it is less than zero
        if(it->messageID <0)
        {
            continue;
        }
        //! - Get the current message header and check to see if it is new and if enough time has elapsed since the last log
        MessageHeaderData* localHeader = SystemMessaging::GetInstance()->
        FindMsgHeader(it->messageID);
        bool bufferNew = it->lastWriteCheck != localHeader->UpdateCounter;
        bufferNew = bufferNew ? (localHeader->CurrentReadTime - it->lastLogTime)
        >= it->writeDelta || it->lastWriteCheck == 0 : bufferNew;
        it->lastWriteCheck = localHeader->UpdateCounter;
        if(bufferNew)
        {
            //! - For valid message logging instance, increase storage buffer if necessary
            while((it->bufferOffset + sizeof(SingleMessageHeader) +
                   localHeader->CurrentReadSize) > it->messageBuffer.GetCurrentSize())
            {
                it->messageBuffer.IncreaseStorage(
                                                  it->messageBuffer.GetCurrentSize()*2+1);
            }
            //! - Read out current message and reset log parameter so that we grab the appropriate message next time
            uint8_t * localPtr =
            &(it->messageBuffer.StorageBuffer[it->bufferOffset]);
            SystemMessaging::GetInstance()->ReadMessage(it->messageID,
                                                        reinterpret_cast<SingleMessageHeader *> (localPtr),
                                                        localHeader->CurrentReadSize, &localPtr[sizeof(SingleMessageHeader)]);
            it->storOff.push_back(it->bufferOffset);
            it->bufferOffset += sizeof(SingleMessageHeader) +
            localHeader->CurrentReadSize;
            it->lastLogTime = localHeader->CurrentReadTime;
            it->logInstanceCount++;
        }
    }
}
bool messageLogger::readLog(int64_t messageID, SingleMessageHeader *dataHeader,
                            uint64_t maxBytes, uint8_t *msgPayload, uint64_t currentOffset)
{
    //! Begin  method steps
    //! - Iterate through the message list and find the requested ID
    std::vector<messageLogContainer>::iterator it;
    SingleMessageHeader *headPtr;
    for(it=logData.begin(); it != logData.end(); it++)
    {
        if(it->messageID != messageID)
        {
            continue;
        }
        int64_t currentIndex = it->logInstanceCount;
        currentIndex -= (1 + currentOffset);
        while(currentIndex < 0)
        {
            currentIndex += it->logInstanceCount;
        }
        std::vector<uint64_t>::iterator storIt;
        storIt = it->storOff.begin();
        storIt += currentIndex;
        uint8_t *dataPtr = &(it->messageBuffer.StorageBuffer[*storIt]);
        headPtr = reinterpret_cast<SingleMessageHeader*> (dataPtr);
        memcpy(dataHeader, headPtr, sizeof(SingleMessageHeader));
        dataPtr += sizeof(SingleMessageHeader);
        uint64_t bytesUse = maxBytes > headPtr->WriteSize ? headPtr->WriteSize : 
        maxBytes;
        memcpy(msgPayload, dataPtr, bytesUse);
        return(true);
    }
    
    return false;
}

