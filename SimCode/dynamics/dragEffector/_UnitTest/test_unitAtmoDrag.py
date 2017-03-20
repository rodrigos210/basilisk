''' '''
'''
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

'''

#
# Basilisk Scenario Script and Integrated Test
#
# Purpose:  Test the validity of a simple exponential atmosphere model.
# Author:   Andrew Harris
# Creation Date:  Jan 18, 2017
#

import sys, os, inspect
import matplotlib
import numpy as np
import ctypes
import math
import csv
import logging
import pytest


# @cond DOXYGEN_IGNORE
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
bskName = 'Basilisk'
splitPath = path.split(bskName)
bskPath = splitPath[0] + '/' + bskName + '/'
# if this script is run from a custom folder outside of the Basilisk folder, then uncomment the
# following line and specify the absolute bath to the Basilisk folder
#bskPath = '/Users/hp/Documents/Research/' + bskName + '/'
sys.path.append(bskPath + 'modules')
sys.path.append(bskPath + 'PythonModules')
# @endcond

# import general simulation support files
import SimulationBaseClass
import unitTestSupport                  # general support file with common unit test functions
import matplotlib.pyplot as plt
import macros
import orbitalMotion

# import simulation related support
import spacecraftPlus
import gravityEffector
import simIncludeGravity
import exponentialAtmosphere
import dragDynamicEffector
import unitTestSupport
#print dir(exponentialAtmosphere)


def test_unitAtmosphere():
    '''This function is called by the py.test environment.'''
    # each test method requires a single assert method to be called

    #   Initialize new atmosphere and drag model, add them to task
    newDrag = dragDynamicEffector.dragDynamicEffector()
    showVal = False
    testResults = []
    testMessage = []

    planetRes, planetMsg = testSetDensityMsg(newDrag)
    testMessage.append(planetMsg)
    testResults.append(planetRes)

    testSum = sum(testResults)
    assert testSum < 1, testMessage

def testSetDensityMsg(dragEffector):
    testFailCount = 0
    testMessages = []

    # create the dynamics task and specify the integration update time
    scObject = spacecraftPlus.SpacecraftPlus()
    scObject.ModelTag = "spacecraftBody"
    scObject.hub.useTranslation = True
    scObject.hub.useRotation = False

    scObject.addDynamicEffector(dragEffector)

    # add spacecraftPlus object to the simulation process
    dragEffector.SetDensityMessage("testDensMsgName")

    if dragEffector.atmoDensInMsgName != "testDensMsgName":
        testFailCount += 1
        testMessages.append(
            "FAILED: DragEffector does not correctly set message names.")
    return testFailCount, testMessages



