//
// Created by andrew on 7/12/19.
//

#ifndef BASILISK_POWERNODESTATUSMSG_H
#define BASILISK_POWERNODESTATUSMSG_H

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
/*! \defgroup simFswInterfaceMessages
 *  @{
 */

//! @brief Simulated IMU Sensor output message definition.
typedef struct{
    uint64_t powerStatus;      //!< Power status indicator; 0 is off, 1 is on, additional values
}PowerNodeStatusIntMsg;

/*! @} */


#endif //BASILISK_POWERNODESTATUSMSG_H
