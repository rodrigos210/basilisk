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
#define SWIGPYTHON_BUILTIN

%pythoncode %{
    from Basilisk.simulation.swig_common_model import *
%}
%include "swig_conly_data.i"
%include "std_vector.i"
%module message
%pythoncode %{
    import numpy as np
%};
%{
#include "../../_GeneralModuleFiles/sys_model.h"
#include "message.h"
#include <vector>
%}
%template(TimeVector) std::vector<uint64_t>;
%include "std_vector.i"
%include "../../_GeneralModuleFiles/sys_model.h"
%include "message.h"
%rename(__subscribe_to) subscribeTo;  // we want the users to have a unified "subscribeTo" interface
%rename(__subscribe_to_C) subscribeToC;  // we want the users to have a unified "subscribeTo" interface
%define INSTANTIATE_TEMPLATES(messageType)
%{
#include "architecture/messaging2/cMsgDefinition/messageType.h"
%}
%include "architecture/messaging2/cMsgDefinition/messageType.h"

%template(messageType ## Reader) ReadFunctor<messageType>;
%extend ReadFunctor<messageType> {
        %pythoncode %{
            def subscribeTo(self, source):
                from Basilisk.simulation.c_messages import messageType ## _C
                if type(source) == messageType ## Class:
                    self.__subscribe_to(source)
                elif type(source) == messageType ## _C:
                    self.__subscribe_to_C(source)
                else:
                    raise Exception('tried to subscribe ReadFunctor<messageType> to another message type')
        %}
};

%template(messageType ## Writer) WriteFunctor<messageType>;

%template(messageType ## Class) SimMessage<messageType>;

%template(messageType ## Logger) Log<messageType>;
%rename(__time_vector) times;  // It's not really useful to give the user back a time vector
%rename(__record_vector) record;
%extend Log<messageType> {
    %pythoncode %{
        def times(self):
            return np.array(self.__time_vector())

        # This __getattr__ is written in message.i.
        # It lets us return message struct attribute record as lists for plotting, etc.
        def __getattr__(self, name):
            data = self.__record_vector()
            data_log = []
            for rec in data.iterator():
                data_log.append(rec.__getattribute__(name))
            return np.array(data_log)

        def record(self):
            return self.__record_vector
    %}
};

typedef struct messageType;

%template(messageType ## Vector) std::vector<messageType>;
%extend std::vector<messageType>{
    %pythoncode %{
        # This __getattr__ is written in message.i.
        # It lets us return message struct attribute record as lists for plotting, etc.
        def __getattr__(self, name):
            data_log = []
            for rec in self.iterator():
                data_log.append(rec.__getattribute__(name))
            return np.array(data_log)
    %}
};
%enddef

//sim messages
INSTANTIATE_TEMPLATES(SpicePlanetStateMsg)
INSTANTIATE_TEMPLATES(SCPlusStatesMsg)
INSTANTIATE_TEMPLATES(SCPlusMassPropsMsg)

//fsw interface messages
INSTANTIATE_TEMPLATES(NavAttMsg)
INSTANTIATE_TEMPLATES(NavTransMsg)
INSTANTIATE_TEMPLATES(CmdTorqueBodyMsg)
INSTANTIATE_TEMPLATES(CmdForceBodyMsg)
INSTANTIATE_TEMPLATES(CmdForceInertialMsg)

//fsw messages
INSTANTIATE_TEMPLATES(AttRefMsg)
INSTANTIATE_TEMPLATES(AttGuidMsg)
INSTANTIATE_TEMPLATES(VehicleConfigMsg)

%include "message.h"
