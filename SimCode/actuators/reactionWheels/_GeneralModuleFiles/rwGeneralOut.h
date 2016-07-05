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
#ifndef _GENERAL_RW_OUT_MESSAGE_
#define _GENERAL_RW_OUT_MESSAGE_

#include <stdint.h>
#include "SimCode/utilities/simDefinitions.h"

/*! \addtogroup SimGroup
 * @{
 */

/*! @brief Structure used to define the output definition for attitude guidance*/
typedef struct {

    DeviceConditionState_t speedState;      /*!<            if spin rate is > 6000 rpm */
    DeviceConditionState_t tempState;       /*!<            if temperature is above a threshold */
    double Omega                            /*!< [rad/s]    RW spin speed */
    double uRWc[3];                         /*!< [Nm]       Echo of the commanded RW torque command */
    int cmdCounter;                         /*!<            command ID counter */
    int current;                            /*!< [A]        rw motor current */
    int motorTemp1;                         /*!< [C]        motor temperature I */
    int motorTemp2;                         /*!< [C]        motor temperature II */
    int maxTorque;                          /*!< [micro-Nm] use set maximum torque value */

}rwGenearlOut;

/*! @} */

#endif
