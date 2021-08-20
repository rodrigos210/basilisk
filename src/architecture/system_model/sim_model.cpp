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

#include "sim_model.h"
#include <cstring>
#include <iostream>

void activateNewThread(void *threadData)
{

    SimThreadExecution *theThread = static_cast<SimThreadExecution*> (threadData);

    //std::cout << "Starting thread yes" << std::endl;
    theThread->lockMaster();
    theThread->postInit();

    while(theThread->threadValid())
    {
        theThread->lockThread();
        if(theThread->selfInitNow){
            theThread->selfInitProcesses();
            theThread->selfInitNow = false;
        }
        else if(theThread->crossInitNow){
            theThread->crossInitProcesses();
            theThread->crossInitNow = false;
        }
        else if(theThread->resetNow){
            theThread->resetProcesses();
            theThread->resetNow = false;
        }
        else{
            theThread->StepUntilStop();
        }
        //std::cout << "Stepping thread"<<std::endl;
        theThread->unlockMaster();

    }
    //std::cout << "Killing thread" << std::endl;

}

SimThreadExecution::SimThreadExecution(uint64_t threadIdent, uint64_t currentSimNanos) : SimThreadExecution(){

    currentThreadNanos = currentSimNanos;
    threadID = threadIdent;
}

SimThreadExecution::~SimThreadExecution() {

}

SimThreadExecution::SimThreadExecution() {
    currentThreadNanos = 0;
    threadRunning = false;
    terminateThread = false;
    selfInitNow = false;
    crossInitNow = false;
    threadID = 0;
    CurrentNanos = 0;
    NextTaskTime = 0;
    stopThreadNanos=0;
    nextProcPriority = -1;
    threadContext = nullptr;

}

void SimThreadExecution::lockThread() {
    this->selfThreadLock.lock();
}

void SimThreadExecution::lockMaster() {
    this->masterThreadLock.lock();
}

void SimThreadExecution::unlockThread() {
    this->selfThreadLock.unlock();
}

void SimThreadExecution::unlockMaster() {
    this->masterThreadLock.unlock();
}

/*! This method steps all of the processes forward to the current time.  It also
    increments the internal simulation time appropriately as the simulation
    processes are triggered
    @param int64_t stopPri The priority level below which the sim won't go
    @return void
*/
void SimThreadExecution::SingleStepProcesses(int64_t stopPri)
{
    uint64_t nextCallTime = ~((uint64_t) 0);
    std::vector<SysProcess *>::iterator it = this->processList.begin();
    this->CurrentNanos = this->NextTaskTime;
    while(it!= this->processList.end())
    {
        SysProcess *localProc = (*it);
        if(localProc->processEnabled())
        {
            while(localProc->nextTaskTime < this->CurrentNanos ||
                  (localProc->nextTaskTime == this->CurrentNanos &&
                   localProc->processPriority >= stopPri))
            {
                localProc->singleStepNextTask(this->CurrentNanos);
            }
            if(localProc->getNextTime() < nextCallTime)
            {
                nextCallTime = localProc->getNextTime();
                this->nextProcPriority = localProc->processPriority;
            }
            else if(localProc->getNextTime() == nextCallTime &&
                    localProc->processPriority > this->nextProcPriority)
            {
                this->nextProcPriority = localProc->processPriority;
            }
        }
        it++;
    }
    this->NextTaskTime = nextCallTime != ~((uint64_t) 0) ? nextCallTime : this->CurrentNanos;
    
}

/*! This method steps the simulation until the specified stop time and
 stop priority have been reached.
 @return void
 */
void SimThreadExecution::StepUntilStop()
{
    /*! - Note that we have to step until both the time is greater and the next
     Task's start time is in the future. If the NextTaskTime is less than
     SimStopTime, then the inPri shouldn't come into effect, so set it to -1
     (that's less than all process priorities, so it will run through the next
     process)*/
    int64_t inPri = stopThreadNanos == this->NextTaskTime ? stopThreadPriority : -1;
    while(this->NextTaskTime < stopThreadNanos || (this->NextTaskTime == stopThreadNanos &&
                                               this->nextProcPriority >= stopThreadPriority) )
    {
        this->SingleStepProcesses(inPri);
        inPri = stopThreadNanos == this->NextTaskTime ? stopThreadPriority : -1;
    }
}

void SimThreadExecution::moveProcessMessages() {
    std::vector<SysProcess *>::iterator it;
    for(it = this->processList.begin(); it != this->processList.end(); it++)
    {
        //(*it)->routeInterfaces(this->CurrentNanos);
    }

}

void SimThreadExecution::waitOnInit() {
    std::unique_lock<std::mutex> lck(this->initReadyLock);
    while(!this->threadActive())
    {
        (this)->initHoldVar.wait(lck);
    }
}

void SimThreadExecution::postInit() {
    std::unique_lock<std::mutex> lck(this->initReadyLock);
    this->threadReady();
    this->initHoldVar.notify_one();
}

void SimThreadExecution::selfInitProcesses() {
    std::vector<SysProcess *>::iterator it;
    for(it=this->processList.begin(); it!= this->processList.end(); it++)
    {
        (*it)->selfInitProcess();
    }
}

void SimThreadExecution::crossInitProcesses() {
    std::vector<SysProcess *>::iterator it;
    for(it=this->processList.begin(); it!= this->processList.end(); it++)
    {
        //(*it)->crossInitProcess();
    }
}

void SimThreadExecution::resetProcesses() {
    std::vector<SysProcess *>::iterator it;
    this->currentThreadNanos = 0;
    this->CurrentNanos = 0;
    this->NextTaskTime = 0;
    for(it=this->processList.begin(); it!= this->processList.end(); it++)
    {
        (*it)->resetProcess(this->currentThreadNanos);
    }
}

/*! This Constructor is used to initialize the top-level sim model.
 */
SimModel::SimModel()
{

    this->threadList.clear();

    //Default to single-threaded runtime
    SimThreadExecution *newThread = new SimThreadExecution(0, 0);
    this->threadList.push_back(newThread);

    this->NextTaskTime = 0;

    this->CurrentNanos = 0;
    this->NextTaskTime = 0;
    this->nextProcPriority = -1;
}

/*! Nothing to destroy really */
SimModel::~SimModel()
{
    //this->deleteThreads();
}

/*! This method steps the simulation until the specified stop time and
 stop priority have been reached.
 @return void
 @param uint64_t SimStopTime Nanoseconds to step the simulation for
 @param int64_t stopPri The priority level below which the sim won't go
 */
void SimModel::StepUntilStop(uint64_t SimStopTime, int64_t stopPri)
{
    std::vector<SimThreadExecution*>::iterator thrIt;
    std::cout << std::flush;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->moveProcessMessages();
    }
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->stopThreadNanos = SimStopTime;
        (*thrIt)->stopThreadPriority = stopPri;
        (*thrIt)->unlockThread();
    }
    this->NextTaskTime = (uint64_t) ~0;
    this->CurrentNanos = (uint64_t) ~0;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->lockMaster();
        this->NextTaskTime = (*thrIt)->NextTaskTime < this->NextTaskTime ?
                             (*thrIt)->NextTaskTime : this->NextTaskTime;
        this->CurrentNanos = (*thrIt)->CurrentNanos < this->CurrentNanos ?
                             (*thrIt)->CurrentNanos : this->CurrentNanos;
    }
}


/*! This method allows the user to attach a process to the simulation for
    execution.  Note that the priority level of the process determines what
    order it gets called in: higher priorities are called before lower
    priorities. If priorities are the same, the proc added first goes first.
    @return void
    @param newProc the new process to be added
*/
void SimModel::addNewProcess(SysProcess *newProc)
{
    std::vector<SysProcess *>::iterator it;
    for(it = this->processList.begin(); it != this->processList.end(); it++)
    {
        if(newProc->processPriority > (*it)->processPriority)
        {
            this->processList.insert(it, newProc);
            return;
        }
    }
    this->processList.push_back(newProc);
}

/*! This method goes through all of the processes in the simulation,
 *  all of the tasks within each process, and all of the models within
 *  each task and self-inits them.
 @return void
 */
void SimModel::selfInitSimulation()
{
    std::vector<SimThreadExecution*>::iterator thrIt;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->selfInitNow = true;
        (*thrIt)->unlockThread();
    }
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++) {
        (*thrIt)->lockMaster();
    }
    this->NextTaskTime = 0;
    this->CurrentNanos = 0;

}

/*! This method goes through all of the processes in the simulation,
 *  all of the tasks within each process, and all of the models within
 *  each task and resets them.
 @return void
 */
void SimModel::resetInitSimulation()
{


    std::vector<SimThreadExecution*>::iterator thrIt;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->resetNow = true;
        (*thrIt)->unlockThread();
    }
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->lockMaster();

    }
}

/*! This method steps all of the processes forward to the current time.  It also
    increments the internal simulation time appropriately as the simulation
    processes are triggered
    @param stopPri The priority level below which the sim won't go
    @return void
*/

//void SimModel::SingleStepProcesses(int64_t stopPri)
//{
//    uint64_t nextCallTime = ~((uint64_t) 0);
//    std::vector<SysProcess *>::iterator it = this->processList.begin();
//    this->CurrentNanos = this->NextTaskTime;
//    while(it!= this->processList.end())
//    {
//        SysProcess *localProc = (*it);
//        if(localProc->processEnabled())
//        {
//            while(localProc->nextTaskTime < this->CurrentNanos ||
//                (localProc->nextTaskTime == this->CurrentNanos &&
//                  localProc->processPriority >= stopPri))
//            {
//                localProc->singleStepNextTask(this->CurrentNanos);
//            }
//            if(localProc->getNextTime() < nextCallTime)
//            {
//                nextCallTime = localProc->getNextTime();
//                this->nextProcPriority = localProc->processPriority;
//            }
//            else if(localProc->getNextTime() == nextCallTime &&
//                localProc->processPriority > this->nextProcPriority)
//            {
//                this->nextProcPriority = localProc->processPriority;
//            }
//        }
//        it++;
//    }
//
//    this->NextTaskTime = nextCallTime != ~((uint64_t) 0) ? nextCallTime : this->CurrentNanos;
//    //! - If a message has been added to logger, link the message IDs
//}

void SimModel::SingleStepProcesses(int64_t stopPri)
{
    uint64_t nextCallTime = ~((uint64_t) 0);
    std::vector<SysProcess *>::iterator it = this->processList.begin();
    this->CurrentNanos = this->NextTaskTime;
    while(it!= this->processList.end())
    {
        SysProcess *localProc = (*it);
        if(localProc->processEnabled())
        {
            while(localProc->nextTaskTime < this->CurrentNanos ||
                (localProc->nextTaskTime == this->CurrentNanos &&
                  localProc->processPriority >= stopPri))
            {
                localProc->singleStepNextTask(this->CurrentNanos);
            }
            if(localProc->getNextTime() < nextCallTime)
            {
                nextCallTime = localProc->getNextTime();
                this->nextProcPriority = localProc->processPriority;
            }
            else if(localProc->getNextTime() == nextCallTime &&
                localProc->processPriority > this->nextProcPriority)
            {
                this->nextProcPriority = localProc->processPriority;
            }
        }
        it++;
    }

    this->NextTaskTime = nextCallTime != ~((uint64_t) 0) ? nextCallTime : this->CurrentNanos;
    //! - If a message has been added to logger, link the message IDs
}

/*! This method is used to reset a simulation to time 0. It sets all process and
 * tasks back to the initial call times. It clears all message logs. However,
 * it does not clear all message buffers and does not reset individual models.
 @return void
 */
void SimModel::ResetSimulation()
{
    std::vector<SysProcess *>::iterator it;
    //! - Iterate through model list and call the Task model initializer
    for(it = this->processList.begin(); it != this->processList.end(); it++)
    {
        (*it)->reInitProcess();
    }
    std::vector<SimThreadExecution*>::iterator thrIt;
    this->NextTaskTime = 0;
    this->CurrentNanos = 0;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->NextTaskTime = 0;
        (*thrIt)->CurrentNanos = 0;
    }
}


///*! This method clears all messages.  Note that once you do this, the simulation
//    object itself is really dead.
//    @return void
//*/
//void SimModel::terminateSimulation()
//{
//}

void SimModel::clearProcsFromThreads() {

    std::vector<SimThreadExecution*>::iterator thrIt;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->clearProcessList();
    }

}

void SimModel::resetThreads(uint64_t threadCount)
{

    this->clearProcsFromThreads();
    this->deleteThreads();
    this->threadList.clear();
    for(uint64_t i=0; i<threadCount; i++)
    {
        SimThreadExecution *newThread = new SimThreadExecution(0, 0);
        this->threadList.push_back(newThread);
    }

}

void SimModel::deleteThreads() {
    std::vector<SimThreadExecution*>::iterator thrIt;
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->killThread();
        (*thrIt)->unlockThread();
        if((*thrIt)->threadContext && (*thrIt)->threadContext->joinable()) {
            (*thrIt)->threadContext->join();
        }
        delete (*thrIt);
    }
}

void SimModel::assignRemainingProcs() {

    std::vector<SysProcess *>::iterator it;
    std::vector<SimThreadExecution*>::iterator thrIt;
    for(it=this->processList.begin(), thrIt=threadList.begin(); it!= this->processList.end(); it++, thrIt++)
    {
        if(thrIt == threadList.end())
        {
            thrIt = threadList.begin();
        }
        (*thrIt)->addNewProcess((*it));
    }
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        it=this->processList.begin();
        (*thrIt)->nextProcPriority = (*it)->processPriority;
        (*thrIt)->NextTaskTime = 0;
        (*thrIt)->CurrentNanos = 0;
        (*thrIt)->lockThread();
        (*thrIt)->threadContext = new std::thread(activateNewThread, (*thrIt));
    }
    for(thrIt=this->threadList.begin(); thrIt != this->threadList.end(); thrIt++)
    {
        (*thrIt)->waitOnInit();
    }


}

