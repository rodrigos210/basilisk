/*
 ISC License

 Copyright (c) 2023, Autonomous Vehicle Systems Lab, University of Colorado at Boulder

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

#ifndef _PRESCRIBEDTRANS_
#define _PRESCRIBEDTRANS_

#include "architecture/_GeneralModuleFiles/sys_model.h"
#include "architecture/messaging/messaging.h"
#include "architecture/utilities/bskLogging.h"
#include "architecture/msgPayloadDefC/PrescribedTranslationMsgPayload.h"
#include "architecture/msgPayloadDefC/LinearTranslationRigidBodyMsgPayload.h"
#include <cstdint>

/*! @brief Prescribed Linear Translation Profiler Class */
class PrescribedTranslation: public SysModel {
public:
    PrescribedTranslation() = default;                                      //!< Constructor
    ~PrescribedTranslation() = default;                                     //!< Destructor

    void Reset(uint64_t CurrentSimNanos) override;                          //!< Reset member function
    void UpdateState(uint64_t CurrentSimNanos) override;                    //!< Update member function

    /* User-configurable variables */
    double transAccelMax;                                          //!< [m/s^2] Maximum acceleration magnitude
    double transAxis_M[3];                                          //!< Axis along the direction of translation
    double r_FM_M[3];                                               //!< [m] Position of the frame F origin with respect to the M frame origin expressed in M frame components
    double rPrime_FM_M[3];                                          //!< [m/s] B frame time derivative of r_FM_M expressed in M frame components
    double rPrimePrime_FM_M[3];                                     //!< [m/s^] B frame time derivative of rPrime_FM_M expressed in M frame components

    /* Private variables */
    bool convergence;                                           //!< Boolean variable is true when the translation is complete
    double tInit;                                               //!< [s] Simulation time at the beginning of the translation
    double transPosInit;                                        //!< [m] Initial translational body position from M to F frame origin along transAxis_M
    double transVelInit;                                        //!< [m/s] Initial translational body velocity
    double transPosRef;                                         //!< [m] Reference translational body position from M to F frame origin along transAxis_M
    double transPos;                                            //!< [m] Current translational body position along transAxis_M
    double transVel;                                            //!< [m] Current translational body velocity along transAxis_M
    double transAccel;                                          //!< [m] Current translational body acceleration along transAxis_M
    double ts;                                                  //!< [s] The simulation time halfway through the translation
    double tf;                                                  //!< [s] The simulation time when the translation is complete
    double a;                                                   //!< Parabolic constant for the first half of the translation
    double b;                                                   //!< Parabolic constant for the second half of the translation

    ReadFunctor<LinearTranslationRigidBodyMsgPayload> linearTranslationRigidBodyInMsg;    //!< Input msg for the translational reference position and velocity
    Message<PrescribedTranslationMsgPayload> prescribedTranslationOutMsg;                 //!< Output msg for the translational body prescribed states

    BSKLogger *bskLogger;                                           //!< BSK Logging
};

#endif
