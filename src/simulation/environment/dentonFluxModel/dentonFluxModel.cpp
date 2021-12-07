/*
 ISC License

 Copyright (c) 2021, Autonomous Vehicle Systems Lab, University of Colorado Boulder

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

#include "simulation/environment/dentonFluxModel/dentonFluxModel.h"
#include "architecture/utilities/linearAlgebra.h"
#include "architecture/utilities/astroConstants.h"

#include <iostream>
#include <cstring>
#include <fstream>
#include <cmath> // trig

/*! This is the constructor for the module class.  It sets default variable
    values and initializes the various parts of the model */

 // Final Desired Constructor
DentonFluxModel::DentonFluxModel()
{
}

/*! Module Destructor */
DentonFluxModel::~DentonFluxModel()
{
    
}

/*! This method is used to reset the module and checks that required input messages are connect.
    @return void
*/
void DentonFluxModel::Reset(uint64_t CurrentSimNanos)
{
    // Check that required input messages are connected
    if (!this->scStateInMsg.isLinked())
    {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.scStateInMsg was not linked.");
    }

    if (!this->earthStateInMsg.isLinked())
    {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.earthStateInMsg was not linked.");
    }

    if (!this->sunStateInMsg.isLinked())
    {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.sunStateInMsg was not linked.");
    }
    
    if (this->kpIndex < 0) {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.kpIndex was not set to a proper value.");
    }

    // Check the disired array size is not larger than the maximum value
    if (this->numOutputEnergies > MAX_PLASMA_FLUX_SIZE)
    {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel: Maximum denton space weather array size exceeded.");
    }
    if (this->numOutputEnergies < 0)
    {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.numEnergies was not set.");
    }
    if (this->dataPath == "") {
        bskLogger.bskLog(BSK_ERROR, "DentonFluxModel.dataPath was not set.");
    }
    
    // convert energies to log10 values
    for (int k = 0; k < MAX_NUM_ENERGIES; k++)
    {
        this->logEnElec[k] = log(this->enElec[k]);
        this->logEnProt[k] = log(this->enProt[k]);
    }

    // Define Energy Array
    double step = (40000 - 1)/this->numOutputEnergies;
 
    this->inputEnergies[0] = 1;
    for (int i = 1; i < numOutputEnergies; i++)
    {
        this->inputEnergies[i] = this->inputEnergies[i-1] + step;
    }


}


/*! This is the main method that gets called every time the module is updated.  Provide an appropriate description.
    @return void
*/
void DentonFluxModel::UpdateState(uint64_t CurrentSimNanos)
{
    // Make local copies of messages
    SCStatesMsgPayload scStateInMsgBuffer;  //!< local copy of spacecraft states
    PlasmaFluxMsgPayload fluxOutMsgBuffer; //!< local copy of the plasma flux output message content
    SpicePlanetStateMsgPayload sunSpiceInMsgBuffer;  //!< local copy of the sun state input message payload
    SpicePlanetStateMsgPayload earthSpiceInMsgBuffer;  //!< local copy of the earth state input message payload

    // Always zero the output message buffers before assigning values
    fluxOutMsgBuffer = this->fluxOutMsg.zeroMsgPayload;

    // Read in the input messages
    scStateInMsgBuffer = this->scStateInMsg();  //!< populating local copy
    sunSpiceInMsgBuffer = this->sunStateInMsg();
    earthSpiceInMsgBuffer = this->earthStateInMsg();
    
    // Set parameters
    
    
    // Electron: All F10.7
    double mean_e_all[MAX_NUM_KPS][MAX_NUM_ENERGIES][MAX_NUM_LOCAL_TIMES];
    
    // Ion: All F10.7
    double mean_i_all[MAX_NUM_KPS][MAX_NUM_ENERGIES][MAX_NUM_LOCAL_TIMES];
    
    // HPS: why is this done in update and note in Reset()??
    
    // Input file stream object
    std::ifstream inputFile1;
    
    // Read data from file 1: electron all F10.7
    inputFile1.open(this->dataPath + "model_e_array_all.txt");
    
    // Read information into arrays: MEAN
    if (inputFile1.is_open()) {
        for (int i = 0; i < MAX_NUM_KPS; i++)
        {   for (int j = 0; j < MAX_NUM_ENERGIES; j++)
            {   for (int k = 0; k < MAX_NUM_LOCAL_TIMES; k++)
                {   inputFile1 >> mean_e_all[i][j][k];
//                    std::cout << mean_e_all[i][j][k] << std::endl;
                }
            }
        }
    } else {
        bskLogger.bskLog(BSK_ERROR, ("Could not open " + this->dataPath + "model_e_array_all.txt").c_str());
    }
    
    // Close file
    inputFile1.close();
    
    // Input file stream object
    std::ifstream inputFile2;
    
    // Read data from file 2: ion all F10.7
    inputFile2.open(this->dataPath + "model_i_array_all.txt");
    
    // Read information into arrays: MEAN
    if (inputFile2.is_open()) {
        for (int i = 0; i < MAX_NUM_KPS; i++)
        {   for (int j = 0; j < MAX_NUM_ENERGIES; j++)
            {   for (int k = 0; k < MAX_NUM_LOCAL_TIMES; k++)
                {   inputFile2 >> mean_i_all[i][j][k];
//                    std::cout << mean_i_all[i][j][k] << std::endl;
                }
            }
        }
    } else {
        bskLogger.bskLog(BSK_ERROR, ("Could not open " + this->dataPath + "model_i_array_all.txt").c_str());
    }
    
    
    // Close file
    inputFile2.close();
    
    
    // Define output (array if we open more than 2 files)
    double finalElecAll;
    double finalIonAll;
    //double finalElecAll[7]; //!< Desired end result for all F10.7
    //double finalIonAll[7];

    //  Calculate both Sun snd spacecraft B position vectors from Earth in ECI frame
    double r_BE_N[3];       /* satellite position relative to Earth in N frame components */
    double r_SE_N[3];       /* sun position relative to Earth in N frame components */
    v3Subtract(scStateInMsgBuffer.r_BN_N, earthSpiceInMsgBuffer.PositionVector, r_BE_N);
    v3Subtract(sunSpiceInMsgBuffer.PositionVector, earthSpiceInMsgBuffer.PositionVector, r_SE_N);

    // Find local lime from spacecraft and Earth state messages
    calcLocalTime(r_BE_N, r_SE_N);
    
    // For loop to calculate each element of output flux vectors
    for (int i = 0; i < numOutputEnergies; i++)
    {
        // Convert energies to log10
        double logInputEnergy = log(inputEnergies[i]);
                
        // ELECTRONS: Find nearest neighbors in energy
        double eHigher = 0.0;
        double eLower = 0.0;
        int eHigherIndex = 0;
        int eLowerIndex = 0;
        
        for (int j = 0; j < MAX_NUM_ENERGIES; j++)
        {
            if (logEnElec[j] > logInputEnergy)
            {
                eHigher = logEnElec[j];
                eLower = logEnElec[j-1];
                eHigherIndex = j;
                eLowerIndex = j-1;
                break;
            }
            else
            {
            }
        }
        
        // IONS: Find nearest neighbors in energy
        double iHigher = 0.0;
        double iLower = 0.0;
        int iHigherIndex = 0;
        int iLowerIndex = 0;
        
        for (int m = 0; m < MAX_NUM_ENERGIES; m++)
        {
            if (logEnProt[m] > logInputEnergy)
            {
                iHigher = logEnProt[m];
                iLower = logEnProt[m-1];
                iHigherIndex = m;
                iLowerIndex = m-1;
                break;
            }
            else
            {
            }
        }
        
        int localTimeFloor = floor(this->localTime + 1);
        int localTimeCeil = ceil(this->localTime + 1);
        
        // Initialize flux variables
        double flux11 = 0.0;
        double flux12 = 0.0;
        double flux13 = 0.0;
        double flux14 = 0.0;
        
        // ELECTRON: Gather four nearest *MEAN* flux values for *ALL F10.7*
        flux11 = mean_e_all[this->kpIndex][eLowerIndex][localTimeFloor];
        flux12 = mean_e_all[this->kpIndex][eHigherIndex][localTimeFloor];
        flux13 = mean_e_all[this->kpIndex][eLowerIndex][localTimeCeil];
        flux14 = mean_e_all[this->kpIndex][eHigherIndex][localTimeCeil];
        
        // ELECTRON: Find flux
        finalElecAll = bilinear((localTimeFloor - 1), (localTimeCeil-1), logEnElec[eLowerIndex], logEnElec[eHigherIndex], logInputEnergy, flux11, flux12, flux13, flux14);
        
        // ION: Gather four nearest *MEAN* flux values for *ALL F10.7*
        flux11 = mean_i_all[this->kpIndex][iLowerIndex][localTimeFloor];
        flux12 = mean_i_all[this->kpIndex][iHigherIndex][localTimeFloor];
        flux13 = mean_i_all[this->kpIndex][iLowerIndex][localTimeCeil];
        flux14 = mean_i_all[this->kpIndex][iHigherIndex][localTimeCeil];
        
        // ION: Find flux
        finalIonAll = bilinear(localTimeFloor, localTimeCeil, logEnProt[iHigherIndex], logEnProt[iLowerIndex], logInputEnergy, flux11, flux12, flux13, flux14);
        
        // Store the output message
        fluxOutMsgBuffer.meanElectronFlux[i] = finalElecAll;
        fluxOutMsgBuffer.meanIonFlux[i] = finalIonAll;
        fluxOutMsgBuffer.energies[i] = inputEnergies[i];
    }
    
    // Write to the output message
    this->fluxOutMsg.write(&fluxOutMsgBuffer, this->moduleID, CurrentSimNanos);
}

/*! method to calculate the local time of the spacecraft within the GEO belt
    @return void
*/
void DentonFluxModel::calcLocalTime(double r_SE_N[3], double r_BE_N[3])
{
    double r_BE_N_hat[2];       /* unit vector from Earth to spacecraft */
    double r_SE_N_hat[2];       /* unit vector from Earth to Sun */
    v2Normalize(r_BE_N, r_BE_N_hat);
    v2Normalize(r_SE_N, r_SE_N_hat);
    
    // Determine Local Time: Using atan2()
    double x = v2Dot(r_BE_N_hat, r_SE_N_hat);
    double y = r_SE_N_hat[0]*r_BE_N_hat[1] - r_SE_N_hat[1]*r_BE_N_hat[0];
    
    double theta = atan2(y,x);

    if (x <= -1.0)
    {
        this->localTime = 0.0;    //!<  Data files are from 0-23 LT, this results in 24h being 0h
    }
    else
    {
        this->localTime = 12.00 + (theta / (2.*M_PI))*24;
    }
    
    return;
    
}

/*! Bilinear interpolation method
    @return void
*/
double DentonFluxModel::bilinear(int x1, int x2, double y1, double y2, double y, double f11, double f12, double f13, double f14)
{
    // Define variables
    double R1, R2, bilinear = 0.0;
    double x = this->localTime;

    if (x1 != x2)
    {
        R1 = ( (x2 - x) / (x2 - x1) ) * f11 + ( (x - x1) / (x2 - x1) ) * f13;
        R2 = ( (x2 - x) / (x2 - x1) ) * f12 + ( (x - x1) / (x2 - x1) ) * f14;
        bilinear = ( (y2 - y ) / (y2 - y1) ) * R1 + ( (y - y1) / (y2 - y1) ) * R2;
        return bilinear;
    }
    else
    {
        bilinear = ( (y2 - y ) / (y2 - y1) ) * f11 + ( (y - y1) / (y2 - y1) ) * f13;
        return bilinear;
    }

}

