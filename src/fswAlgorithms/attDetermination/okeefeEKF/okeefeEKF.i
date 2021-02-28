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
%module okeefeEKF
%{
   #include "okeefeEKF.h"
   #include "fswAlgorithms/attDetermination/_GeneralModuleFiles/ukfUtilities.h"
%}

%include "swig_conly_data.i"
%constant void Update_okeefeEKF(void*, uint64_t, uint64_t);
%ignore Update_okeefeEKF;
%constant void SelfInit_okeefeEKF(void*, uint64_t);
%ignore SelfInit_okeefeEKF;
%constant void Reset_okeefeEKF(void*, uint64_t, uint64_t);
%ignore Reset_okeefeEKF;

%include "fswAlgorithms/attDetermination/_GeneralModuleFiles/ukfUtilities.h"

%include "architecture/msgPayloadDefC/NavAttMsgPayload.h"
struct NavAttMsg_C;
%include "architecture/msgPayloadDefC/CSSArraySensorMsgPayload.h"
struct CSSArraySensorMsg_C;
%include "architecture/msgPayloadDefC/SunlineFilterMsgPayload.h"
struct SunlineFilterMsg_C;
%include "architecture/msgPayloadDefC/CSSConfigMsgPayload.h"
struct CSSConfigMsg_C;

%include "okeefeEKF.h"

%pythoncode %{
import sys
protectAllClasses(sys.modules[__name__])
%}

