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

#include <stdio.h>
#include <stdarg.h>
#include "utilities/bskPrint.h"

int global_;
int global_c;

BSKPrint::BSKPrint()
{
  this->_msgLevel = MSG_DEBUG;
}

BSKPrint::BSKPrint(msgLevel_t msgLevel)
{
  this->_msgLevel = msgLevel;
}

void BSKPrint::setPrintLevel(msgLevel_t msgLevel)
{
  this->_msgLevel = msgLevel;
}

void BSKPrint::readPrintLevel()
{
  const char* currLevelStr = this->msgLevelMap[this->_msgLevel];
  printf("Current Message Level: %s\n", currLevelStr);
}

void BSKPrint::printMessage(msgLevel_t targetLevel, const char* message, ...)
{
  if(targetLevel >= this->_msgLevel)
  {
    const char* targetLevelStr = this->msgLevelMap[targetLevel];
    char formatMessage[255];
    va_list args;
    va_start (args, message);
    vsnprintf(formatMessage, sizeof(formatMessage), message, args);
    printf("Message Level: %s, Message: %s\n", targetLevelStr, formatMessage);
  }
}
