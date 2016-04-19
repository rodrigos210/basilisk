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
OR  IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

*/

#ifndef ALG_CONTAIN_H
#define ALG_CONTAIN_H

#include "utilities/sys_model.h"

typedef void (*AlgPtr)(void*, uint64_t);
typedef void (*AlgUpdatePtr)(void*, uint64_t, uint64_t);

class AlgContain: public SysModel {
public:
    AlgContain();
    ~AlgContain();
    AlgContain(void *DataIn, void(*UpPtr) (void*, uint64_t, uint64_t),
        void (*SelfPtr)(void*, uint64_t)=NULL,
        void (*CrossPtr)(void*, uint64_t)=NULL,
		void(*ResetPtr)(void*, uint64_t, uint64_t) = NULL);
    
    void UseData(void *IncomingData) {DataPtr = IncomingData;}
    void UseUpdate(void (*LocPtr)(void*, uint64_t, uint64_t)) {AlgUpdate = LocPtr;}
    void UseSelfInit(void (*LocPtr)(void*, uint64_t)) {AlgSelfInit = LocPtr;}
    void UseCrossInit(void (*LocPtr)(void*, uint64_t)) {AlgCrossInit = LocPtr;}
	void UseReset(void(*LocPtr)(void*, uint64_t, uint64_t)) { AlgReset = LocPtr; }
    void CrossInit();
    void SelfInit();
    void UpdateState(uint64_t CurrentSimNanos);
	void Reset(uint64_t CurrentSimNanos);
    
private:
    void *DataPtr;
    AlgPtr AlgSelfInit;
    AlgPtr AlgCrossInit;
	AlgUpdatePtr AlgReset;
    AlgUpdatePtr AlgUpdate;
};

#endif
