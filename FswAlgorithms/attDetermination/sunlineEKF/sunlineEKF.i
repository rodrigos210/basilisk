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
%module sunlineEKF
%{
   #include "sunlineEKF.h"
   #include "../_GeneralModuleFiles/ukfUtilities.h"
%}

%include "swig_conly_data.i"
%constant void Update_sunlineEKF(void*, uint64_t, uint64_t);
%ignore Update_sunlineEKF;
%constant void SelfInit_sunlineEKF(void*, uint64_t);
%ignore SelfInit_sunlineEKF;
%constant void CrossInit_sunlineEKF(void*, uint64_t);
%ignore CrossInit_sunlineEKF;
%constant void Reset_sunlineEKF(void*, uint64_t, uint64_t);
%ignore Reset_sunlineEKF;
//%constant void sunlineDynMatrix(double*, double*);
//%ignore sunlineDynMatrix;
STRUCTASLIST(CSSConfigFswMsg)
GEN_SIZEOF(CSSConfigFswMsg)
GEN_SIZEOF(SunlineFilterFswMsg);
GEN_SIZEOF(sunlineEKFConfig);
GEN_SIZEOF(VehicleConfigFswMsg);
%include "../_GeneralModuleFiles/ukfUtilities.h"
%include "../../fswMessages/cssConfigFswMsg.h"
%include "../../fswMessages/vehicleConfigFswMsg.h"
%include "../../fswMessages/sunlineFilterFswMsg.h"
%typemap(in) double (*A)[6][6] {
    void *dataPtr;
    SWIG_ConvertPtr($input, &dataPtr, $descriptor(double *), 0 |  0);
    double *actData = (double*) dataPtr;
    $1 = actData;
}
%typemap(in) double (*STM)[6][6] {
    void *dataPtr;
    SWIG_ConvertPtr($input, &dataPtr, $descriptor(double *), 0 |  0);
    double *actData = (double*) dataPtr;
    $1 = actData;
}
%include "sunlineEKF.h"

%pythoncode %{
import sys
protectAllClasses(sys.modules[__name__])
%}

