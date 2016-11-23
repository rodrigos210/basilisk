'''
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

'''
# this is the initial version of the thruster unit test
#Very simple simulation.
import sys, os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy
import ctypes
import math
import inspect
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
splitPath = path.split('SimCode')
sys.path.append(splitPath[0] + '/modules')
sys.path.append(splitPath[0] + '/PythonModules')

#Import all of the modules that we are going to call in this simulation
import six_dof_eom
import MessagingAccess
import SimulationBaseClass
import sim_model
import thruster_dynamics

def executeSimulationRun(stopTime, stepTime, TotalSim, ACSThrusterDynObject, 
    massPropsData, outputState):
    newStop = TotalSim.TotalSim.CurrentNanos
    while(TotalSim.TotalSim.CurrentNanos < stopTime):
        ACSThrusterDynObject.ComputeDynamics(massPropsData, outputState,
            newStop*1.0E-9 - stepTime*1.0E-9)
        ACSThrusterDynObject.ComputeDynamics(massPropsData, outputState,
            newStop*1.0E-9 - stepTime/2*1.0E-9)
        ACSThrusterDynObject.ComputeDynamics(massPropsData, outputState,
            newStop*1.0E-9 - stepTime/2*1.0E-9)
        ACSThrusterDynObject.ComputeDynamics(massPropsData, outputState,
            newStop*1.0E-9)
        newStop += var1
        TotalSim.TotalSim.SingleStepProcesses()
        TotalSim.RecordLogVars()


#Instantiate a new set of thrusters using the thruster_dynamics module
ACSThrusterDynObject = thruster_dynamics.ThrusterDynamics()

#Configure a single thruster inside this thruster module
ACSThrusterDynObject.ModelTag = "ACSThrusterDynamics"
Thruster1 = thruster_dynamics.ThrusterConfigData()
Thruster1.ThrusterLocation = thruster_dynamics.DoubleVector([1.125, 0.0, 2.0])
Thruster1.ThrusterDirection = thruster_dynamics.DoubleVector([
    math.cos(30.0*math.pi/180.0), math.sin(30.0*math.pi/180.0), 0.0])
Thruster1.MaxThrust = 1.0
Thruster1.steadyIsp = 226.7
Thruster1.MinOnTime = 0.006
ACSThrusterDynObject.AddThruster(Thruster1)

ACSpropCM = [0.0, 0.0, 1.0]
ACSpropMass = 1.0 #Made up!!!!
ACSpropRadius = 46.0/2.0/3.2808399/12.0
sphereInerita = 2.0/5.0*ACSpropMass*ACSpropRadius*ACSpropRadius
ACSInertia = [sphereInerita, 0, 0, 0, sphereInerita, 0, 0, 0, sphereInerita]
ACSThrusterDynObject.objProps.Mass = ACSpropMass
SimulationBaseClass.SetCArray(ACSpropCM, 'double', 
    ACSThrusterDynObject.objProps.CoM)
SimulationBaseClass.SetCArray(ACSInertia, 'double', 
    ACSThrusterDynObject.objProps.InertiaTensor)

earthGrav = 9.80665
mDotExpect = Thruster1.MaxThrust/(Thruster1.steadyIsp*earthGrav)
print mDotExpect

#Set the test step (var1) and the various stop times (var2-var4)
var1 = int(1E7) # call the thread at 1000 Hz, let the thread do stuff at 10 Hz
var2 = int(60*1E9) # stop after 60 seconds
var3  = int(80*1E9) # next stop
var4  = int(100*1E9) # next stop
var5 = int(((110)*1E9)) #next stop
var6 = int((110 + 0.02)*1E9) #next stop
var7 = int(((120)*1E9)) #next stop
var8 = int(((120+0.04)*1E9)) #next stop
var9 = int(((130)*1E9)) #next stop
var10 = int(((140)*1E9)) #next stop

#Create a sim module as an empty container
TotalSim = SimulationBaseClass.SimBaseClass()
#Create a new process for the unit test task and add the module to tasking
testProc = TotalSim.CreateNewProcess("TestProcess")
testProc.addTask(TotalSim.CreateNewTask("thrusterbasic", var1))
TotalSim.AddModelToTask("thrusterbasic", ACSThrusterDynObject)

#Configure the vehicle mass properties to use in the simulation
massPropsData = six_dof_eom.MassPropsData()
CoMLoc = [1.0, 0.0, 0.0]
SimulationBaseClass.SetCArray(CoMLoc, 'double', massPropsData.CoM)
T_str2Bdy = [-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0]
SimulationBaseClass.SetCArray(T_str2Bdy, 'double', massPropsData.T_str2Bdy)
outputState = six_dof_eom.OutputStateData()

#Setup variables for logging
TotalSim.AddVectorForLogging('ACSThrusterDynamics.StrForce', 'double', 0, 2, int(1E2))
TotalSim.AddVectorForLogging('ACSThrusterDynamics.BodyForce', 'double', 0, 2, int(1E2))
TotalSim.AddVariableForLogging('ACSThrusterDynamics.ThrusterData[0].ThrustOps.ThrustFactor', int(1E2))
TotalSim.AddVariableForLogging('ACSThrusterDynamics.objProps.Mass', int(1E2))
TotalSim.AddVariableForLogging('ACSThrusterDynamics.mDotTotal', int(1E2))

#Configure a single thruster firing, create a message for it
ThrustMessage = thruster_dynamics.ThrustCmdStruct()
ThrustMessage.OnTimeRequest = 10.0;
TotalSim.TotalSim.CreateNewMessage("TestProcess", "acs_thruster_cmds", 8, 2)

#Step the simulation for a bit to get clear of any init funnies
TotalSim.InitializeSimulation()
TotalSim.ConfigureStopTime(int(10*1E9-var1))
TotalSim.ExecuteSimulation()

#Write firing command message and step the simulation
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 0, ThrustMessage);
executeSimulationRun(var2, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)
   
#Configure a shorter firing command, execute it, and step simulation 
ThrustMessage.OnTimeRequest = 0.1;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, int(30E9), ThrustMessage);
executeSimulationRun(var3, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)
  
#Setup thruster ramp on and ramp off configuration
rampOnList = []
rampOffList = []
#Note that this ramp is totally linear and ramps up 30 ms using 30 steps
for i in range(30):
    newElement = thruster_dynamics.ThrusterTimePair()
    newElement.TimeDelta = (i+1)*0.001
    newElement.ThrustFactor = (i+1.0)/30.0
    newElement.IspFactor = (i+1.0)/30.0
    rampOnList.append(newElement)
    newElement = thruster_dynamics.ThrusterTimePair()
    newElement.TimeDelta = (i+1)*0.001
    newElement.ThrustFactor = 1.0-(i+1.0)/30.0
    newElement.IspFactor = newElement.ThrustFactor
    rampOffList.append(newElement)

#Set up the ramps 
ACSThrusterDynObject.ThrusterData[0].ThrusterOnRamp = \
    thruster_dynamics.ThrusterTimeVector(rampOnList)
ACSThrusterDynObject.ThrusterData[0].ThrusterOffRamp = \
    thruster_dynamics.ThrusterTimeVector(rampOffList)

#Execute a new firing that will use the thruster ramps
ThrustMessage.OnTimeRequest = 0.5;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 1, ThrustMessage);
executeSimulationRun(var4, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.015;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 2, ThrustMessage);
executeSimulationRun(var5, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.5;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 3, ThrustMessage);
executeSimulationRun(var6, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.005;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 4, ThrustMessage);
executeSimulationRun(var7, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.025;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 5, ThrustMessage);
executeSimulationRun(var8, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.2;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 6, ThrustMessage);
executeSimulationRun(var9, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

ThrustMessage.OnTimeRequest = 0.001;
TotalSim.TotalSim.WriteMessageData("acs_thruster_cmds", 8, 7, ThrustMessage);
executeSimulationRun(var10, var1, TotalSim, ACSThrusterDynObject,
    massPropsData, outputState)

#Extract log variables and plot the results
thrForce = TotalSim.GetLogVariableData('ACSThrusterDynamics.StrForce')
thrBodForce = TotalSim.GetLogVariableData('ACSThrusterDynamics.BodyForce')
thrFactor = TotalSim.GetLogVariableData('ACSThrusterDynamics.ThrusterData[0].ThrustOps.ThrustFactor')
thrMass = TotalSim.GetLogVariableData('ACSThrusterDynamics.objProps.Mass')
thrMDot = TotalSim.GetLogVariableData('ACSThrusterDynamics.mDotTotal')
plt.figure(1)
plt.plot(thrForce[:,0]*1.0E-9, thrForce[:,1], 'b', label='x Str')
plt.plot(thrBodForce[:,0]*1.0E-9, thrBodForce[:,1], 'b--', label='x Body')
plt.plot(thrForce[:,0]*1.0E-9, thrForce[:,2], 'g', label='y Str')  
plt.plot(thrBodForce[:,0]*1.0E-9, thrBodForce[:,2], 'g--', label='y Body')
plt.plot(thrForce[:,0]*1.0E-9, thrForce[:,3], 'r', label = 'z Str')
plt.plot(thrBodForce[:,0]*1.0E-9, thrBodForce[:,3], 'r--', label='z Body')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Thruster Force (N)')

plt.figure(2)
plt.plot(thrFactor[:,0]*1.0E-9, thrFactor[:,1])
plt.xlabel('Time(s)')
plt.ylabel('Thrust Factor (-)')

plt.figure(3)
plt.plot(thrMass[:,0]*1.0E-9, thrMass[:,1])
plt.xlabel('Time (s)')
plt.ylabel('Propellant Mass (kg)')

plt.figure(4)
plt.plot(thrMDot[:,0]*1.0E-9, thrMDot[:,1])
plt.xlabel('Time (s)')
plt.ylabel('Propellant Mass-Rate (kg/s)')

ACSThrusterDynObject.InputCmds = "dummy_fire_not_work"
TotalSim.InitializeSimulation()
TotalSim.ConfigureStopTime(int(2E6))
TotalSim.ExecuteSimulation()

if(len(sys.argv) > 1):
   if(sys.argv[1] == 'True'):
      plt.show()
