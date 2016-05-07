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
/*
    Inertial 3D Spin Module
 
 * University of Colorado, Autonomous Vehicle Systems (AVS) Lab
 * Unpublished Copyright (c) 2012-2015 University of Colorado, All Rights Reserved

 */


#include "attGuidance/hillPoint/hillPoint.h"
#include <string.h>
#include "ADCSUtilities/ADCSDefinitions.h"
#include "ADCSUtilities/ADCSAlgorithmMacros.h"

/* Support files.  Be sure to use the absolute path relative to Basilisk directory. */
#include "SimCode/utilities/linearAlgebra.h"
#include "SimCode/utilities/rigidBodyKinematics.h"



void SelfInit_hillPoint(hillPointConfig *ConfigData, uint64_t moduleID)
{
    /*! - Create output message for module */
    ConfigData->outputMsgID = CreateNewMessage(ConfigData->outputDataName,
                                               sizeof(attRefOut),
                                               "attRefOut",
                                               moduleID);
}

void CrossInit_hillPoint(hillPointConfig *ConfigData, uint64_t moduleID)
{
    /*! - Get the control data message ID*/
    ConfigData->inputCelID = subscribeToMessage(ConfigData->inputCelMessName,
                                                sizeof(SpicePlanetState), moduleID);
    ConfigData->inputNavID = subscribeToMessage(ConfigData->inputNavDataName,
                                                sizeof(NavStateOut), moduleID);
}

void Reset_hillPoint(hillPointConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    
}


void Update_hillPoint(hillPointConfig *ConfigData, uint64_t callTime, uint64_t moduleID)
{
    /*! - Read input message */
    uint64_t            writeTime;
    uint32_t            writeSize;
    NavStateOut         navData;
    SpicePlanetState    primPlanet;
    
    ReadMessage(ConfigData->inputCelID, &writeTime, &writeSize,
                sizeof(SpicePlanetState), &primPlanet);
    ReadMessage(ConfigData->inputNavID, &writeTime, &writeSize,
                sizeof(NavStateOut), &navData);
    
    
    /*! - Compute and store output message */
    computeHillPointingReference(navData.r_BN_N,
                                 navData.v_BN_N,
                                 primPlanet.PositionVector,
                                 primPlanet.VelocityVector,
                                 ConfigData->attRefOut.sigma_RN,
                                 ConfigData->attRefOut.omega_RN_N,
                                 ConfigData->attRefOut.domega_RN_N);
    
    WriteMessage(ConfigData->outputMsgID, callTime, sizeof(attRefOut),   /* update module name */
                 (void*) &(ConfigData->attRefOut), moduleID);
    
    return;
}


void computeHillPointingReference(double r_BN_N[3],
                                  double v_BN_N[3],
                                  double celBdyPositonVector[3],
                                  double celBdyVelocityVector[3],
                                  double sigma_RN[3],
                                  double omega_RN_N[3],
                                  double domega_RN_N[3])
{
    
    double  relPosVector[3];
    double  relVelVector[3];
    double  RN[3][3];                /*!< DCM from inertial to reference frame */
    double  temp33[3][3];
    
    double  rm;                      /*!< orbit radius */
    double  h[3];                    /*!< orbit angular momentum vector */
    double  hm;                      /*!< module of the orbit angular momentum vector */
    
    double  dfdt;                    /*!< rotational rate of the orbit frame */
    double  ddfdt2;                  /*!< rotational acceleration of the frame */
    double  omega_RN_R[3];           /*!< reference angular velocity vector in Reference frame R components */
    double  domega_RN_R[3];          /*!< reference angular acceleration vector in Reference frame R components */
    
    /* Compute relative position and velocity of the spacecraft with respect to the main celestial body */
    v3Subtract(r_BN_N, celBdyPositonVector, relPosVector);
    v3Subtract(v_BN_N, celBdyVelocityVector, relVelVector);
    
    /* Compute RN */
    v3Normalize(relPosVector, RN[0]);
    v3Cross(relPosVector, relVelVector, h);
    v3Normalize(h, RN[2]);
    v3Cross(RN[2], RN[0], RN[1]);
    
    /* Compute R-frame orientation */
    C2MRP(RN, sigma_RN);
    
    /* Compute R-frame inertial rate and acceleration */
    rm = v3Norm(relPosVector);
    hm = v3Norm(h);
    if(rm > 1.) {
        dfdt = hm / (rm * rm);  /* true anomaly rate */
        ddfdt2 = - 2.0 * v3Dot(relVelVector, RN[0]) / rm * dfdt; /* derivative of true anomaly rate */
    } else {
        /* an error has occured, radius shouldn't be less than 1km #WHY?? */
        dfdt   = 0.;
        ddfdt2 = 0.;
    }
    v3SetZero(omega_RN_R);
    v3SetZero(domega_RN_R);
    omega_RN_R[2]  = dfdt;
    domega_RN_R[2] = ddfdt2;

    m33Transpose(RN, temp33);
    m33MultV3(temp33, omega_RN_R, omega_RN_N);
    m33MultV3(temp33, domega_RN_R, domega_RN_N);
    
}