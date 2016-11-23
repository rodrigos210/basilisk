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

#include "eulerIntegrator.h"

eulerIntegrator::eulerIntegrator(dynObject* dyn) : integrator(dyn)
{
    dX = nullptr;
    return;
}

eulerIntegrator::~eulerIntegrator()
{
    if(dX)
    {
        delete [] dX;
    }
    return;
}

void eulerIntegrator::integrate(double currentTime, double timeStep, double* currentState, double* nextState, unsigned int NStates)
{
    if(statesAllocated != NStates)
    {
        if(dX)
        {
            delete [] dX;
        }
        dX = new double[NStates];
        statesAllocated = NStates;
    }
 
    unsigned int i;
    
    this->_dyn->equationsOfMotion(currentTime, currentState, dX);
    for(i = 0; i < NStates; i++) {
        nextState[i] = currentState[i] + timeStep * dX[i];
    }
    
    return;
}