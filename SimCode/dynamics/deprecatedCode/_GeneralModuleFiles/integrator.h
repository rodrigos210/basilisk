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


#ifndef integrator_h
#define integrator_h

#include "dynObject.h"

/*!
 @brief Base clase for every integrator. For creating a new integrator, inherit this class and override the integrate() method. integrate() only needs to advance one time step. DO NOT CHANGE THIS CLASS, if possible.
 */
class integrator
{
	
public:
    integrator(dynObject* dyn);
    virtual ~integrator(void);
    virtual void integrate(double currentTime, double timeStep, double* currentState, double* nextState, unsigned int NStates) = 0;
    
protected:
    dynObject* _dyn; //!< This is an object that contains the method equationsOfMotion(), also known as the F function.
};

#endif /* integrator_h */