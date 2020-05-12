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


#include "dataFileToViz.h"
#include "architecture/messaging/system_messaging.h"
#include "simMessages/scPlusStatesSimMsg.h"
#include "utilities/linearAlgebra.h"
#include <sstream>
#include <string>

/*! DataFileToViz Constructor
 */
DataFileToViz::DataFileToViz()
{
    this->dataFileName = "";
    this->numSatellites = 1;
    this->delimiter = " ";
    this->convertPosToMeters = 1000.;       /* convert km to meters */

    return;
}

/*! DataFileToViz Destructor
 */
DataFileToViz::~DataFileToViz()
{
    /* close the data file if it is open */
    if(this->fileHandle->is_open()) {
        this->fileHandle->close();
    }

    return;
}

/*! Initialization method
 */
void DataFileToViz::SelfInit()
{
    int64_t msgId;
    std::vector<std::string>::iterator it;

    //! - create all the environment output messages for each spacecraft
    for (it = this->scStateOutMsgNames.begin(); it!=this->scStateOutMsgNames.end(); it++) {
        msgId = SystemMessaging::GetInstance()->CreateNewMessage(*it,
                                                                sizeof(SCPlusStatesSimMsg),
                                                                this->OutputBufferCount,
                                                                "SCPlusStatesSimMsg",
                                                                moduleID);
        this->scStateOutMsgIds.push_back(msgId);
    }
    
    return;
}

/*! Cross initialization. This module does not subscribe to any other messages.
 */
void DataFileToViz::CrossInit()
{
    return;
}

/*! A Reset method to put the module back into a clean state
 @param CurrentSimNanos The current sim time in nanoseconds
 */
void DataFileToViz::Reset(uint64_t CurrentSimNanos)
{
    if (this->numSatellites < 1) {
        bskLogger.bskLog(BSK_ERROR, "DataFileToViz: numSatellites must be 1 or larger, not %d.", this->numSatellites);
    }
    if (this->dataFileName.length() == 0) {
        bskLogger.bskLog(BSK_ERROR, "DataFileToViz: dataFileName must be an non-empty string.");
    }
    if (this->numSatellites != this->scStateOutMsgNames.size()) {
        bskLogger.bskLog(BSK_ERROR, "DataFileToViz: numSatellites must the same size as scStateOutMsgNames vector.");
    }

    /* open the data file*/
    this->fileHandle = new std::ifstream(this->dataFileName);
    if (this->fileHandle->fail()) {
        bskLogger.bskLog(BSK_ERROR, "DataFileToViz: was not able to load the file %s.", this->dataFileName.c_str());
    }

    bskLogger.bskLog(BSK_INFORMATION, "DataFileToViz: loaded the file:\n %s.", this->dataFileName.c_str());


    return;
}


/*! Update this module at the task rate
 @param CurrentSimNanos The current sim time
 */
void DataFileToViz::UpdateState(uint64_t CurrentSimNanos)
{
    /* ensure that a file was opened */
    if (this->fileHandle->is_open()) {

        /* read in next line*/
        std::string line;
        if (getline(*this->fileHandle, line)) {

            std::istringstream iss(line);
            std::vector<int64_t>::iterator it;
            //! - create all the environment output messages for each spacecraft
            for (it = this->scStateOutMsgIds.begin(); it!=this->scStateOutMsgIds.end(); it++) {
                SCPlusStatesSimMsg scMsg;
                double x,y,z, vx, vy, vz;
                std::string item;
                const char delimiterString = *this->delimiter.c_str();

                /* zero output message */
                memset(&scMsg, 0x0, sizeof(SCPlusStatesSimMsg));

                /* get inertial position */
                getline(iss, item, delimiterString);
                x = stod(item);
                getline(iss, item, delimiterString);
                y = stod(item);
                getline(iss, item, delimiterString);
                z = stod(item);
                v3Set(x, y, z, scMsg.r_CN_N);
                v3Scale(this->convertPosToMeters, scMsg.r_CN_N, scMsg.r_CN_N);
                v3Copy(scMsg.r_CN_N, scMsg.r_BN_N);

                /* get inertial velocity */
                getline(iss, item, delimiterString);
                vx = stod(item);
                getline(iss, item, delimiterString);
                vy = stod(item);
                getline(iss, item, delimiterString);
                vz = stod(item);
                v3Set(vx, vy, vz, scMsg.v_CN_N);
                v3Scale(this->convertPosToMeters, scMsg.v_CN_N, scMsg.v_CN_N);
                v3Copy(scMsg.v_CN_N, scMsg.v_BN_N);

                /* write spacecraft state message */
                SystemMessaging::GetInstance()->WriteMessage(*it,
                                                          CurrentSimNanos,
                                                          sizeof(SCPlusStatesSimMsg),
                                                          reinterpret_cast<uint8_t*>(&scMsg),
                                                          moduleID);
            }
        } else {
            bskLogger.bskLog(BSK_INFORMATION, "DataFileToViz: reached end of file.");
//            exit(1);
        }
    }

    return;
}
