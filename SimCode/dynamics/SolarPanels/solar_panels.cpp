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
#include "dynamics/SolarPanels/solar_panels.h"
#include "architecture/messaging/system_messaging.h"
#include "utilities/linearAlgebra.h"
#include <cstring>
#include <iostream>
#include <cmath>

/*! This is the constructor.  It sets some default initializers that can be
 overriden by the user.*/
SolarPanels::SolarPanels()
{
}

/*! The destructor.  Nothing of note is performed here*/
SolarPanels::~SolarPanels()
{
    return;
}

void SolarPanels::SelfInit()
{
}

void SolarPanels::CrossInit()
{
}

/*! This method is used to compute all the dynamical effects for the SP set.
 It is an inherited method from the DynEffector class and is designed to be called
 by the dynamics plant for the simulation.
 @return void
 @param Props Current mass properties of the vehicle (using center of mass and str2bdy transformation
 @param Bstate Current state of the vehicle (not used by RW dynamics)
 @param CurrentTime Current simulation time converted to double precision
 */
void SolarPanels::ComputeDynamics(MassPropsData *Props, OutputStateData *Bstate, double CurrentTime)
{}
