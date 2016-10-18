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
%module vehicleConfigData
%{
   #include "vehicleConfigData.h"
%}

%include "swig_conly_data.i"
%array_functions(RWConfigurationElement, RWConfigArray);
%array_functions(ThrusterPointData, ThrustConfigArray);
STRUCTASLIST(CSSConfigurationElement)
%constant void Update_vehicleConfigData(void*, uint64_t, uint64_t);
%ignore Update_vehicleConfigData;
%constant void SelfInit_vehicleConfigData(void*, uint64_t);
%ignore SelfInit_vehicleConfigData;
%constant void CrossInit_vehicleConfigData(void*, uint64_t);
%ignore CrossInit_vehicleConfigData;
GEN_SIZEOF(vehicleConfigData);
GEN_SIZEOF(RWConfigurationElement);
GEN_SIZEOF(RWConstellation);
GEN_SIZEOF(ThrusterPointData);
GEN_SIZEOF(ThrusterCluster);
GEN_SIZEOF(VehConfigInputData);
GEN_SIZEOF(CSSConfigurationElement);
GEN_SIZEOF(CSSConstConfig);

%include "vehicleConfigData.h"

%pythoncode %{
import sys
protectAllClasses(sys.modules[__name__])
%}
