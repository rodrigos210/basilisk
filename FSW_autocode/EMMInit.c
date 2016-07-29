void dataInitialization(EMMConfigData *ConfigData) {
	ConfigData->cssSensorDecode.ChebyCount = 14;
	ConfigData->cssSensorDecode.KellyCheby[0] = -1734963.34695;
	ConfigData->cssSensorDecode.KellyCheby[1] = 3294117.1461;
	ConfigData->cssSensorDecode.KellyCheby[2] = -2816333.29462;
	ConfigData->cssSensorDecode.MaxSensorValue = 0.0005;
	ConfigData->cssSensorDecode.NumSensors = 8;
	strcpy(ConfigData->cssSensorDecode.OutputDataName,"css_data_aggregate");
	ConfigData->cssSensorDecode.OutputMsgID = 0;
	strcpy(ConfigData->cssSensorDecode.SensorListName,"css_sensors_data");
	ConfigData->cssSensorDecode.SensorMsgID = 0;
	strcpy(ConfigData->imuSensorDecode.InputDataName,"imu_meas_data");
	strcpy(ConfigData->imuSensorDecode.InputPropsName,"adcs_config_data");
	strcpy(ConfigData->imuSensorDecode.OutputDataName,"parsed_imu_data");
	ConfigData->imuSensorDecode.OutputMsgID = 0;
	ConfigData->imuSensorDecode.PropsMsgID = 0;
	ConfigData->imuSensorDecode.SensorMsgID = 0;
	ConfigData->imuSensorDecode.platform2BdyDCM[0] = 0.0;
	ConfigData->imuSensorDecode.platform2BdyDCM[1] = 0.0;
	ConfigData->imuSensorDecode.platform2BdyDCM[2] = 0.0;
	ConfigData->imuSensorDecode.platform2StrDCM[0] = 1.0;
	ConfigData->imuSensorDecode.platform2StrDCM[1] = 0.0;
	ConfigData->imuSensorDecode.platform2StrDCM[2] = 0.0;
	strcpy(ConfigData->stSensorDecode.InputDataName,"star_tracker_state");
	strcpy(ConfigData->stSensorDecode.InputPropsName,"adcs_config_data");
	strcpy(ConfigData->stSensorDecode.OutputDataName,"parsed_st_data");
	ConfigData->stSensorDecode.OutputMsgID = 0;
	ConfigData->stSensorDecode.PropsMsgID = 0;
	ConfigData->stSensorDecode.SensorMsgID = 0;
	ConfigData->stSensorDecode.T_BdyPlatform[0] = 0.0;
	ConfigData->stSensorDecode.T_BdyPlatform[1] = 0.0;
	ConfigData->stSensorDecode.T_BdyPlatform[2] = 0.0;
	ConfigData->stSensorDecode.T_StrPlatform[0] = 1.0;
	ConfigData->stSensorDecode.T_StrPlatform[1] = 0.0;
	ConfigData->stSensorDecode.T_StrPlatform[2] = 0.0;
	strcpy(ConfigData->inertial3D.outputDataName,"att_ref_output_stage1");
	ConfigData->inertial3D.outputMsgID = 0;
	ConfigData->inertial3D.sigma_R0N[0] = 0.0;
	ConfigData->inertial3D.sigma_R0N[1] = 0.0;
	ConfigData->inertial3D.sigma_R0N[2] = 0.0;
	ConfigData->hillPoint.inputCelID = 0;
	strcpy(ConfigData->hillPoint.inputCelMessName,"mars_display_frame_data");
	strcpy(ConfigData->hillPoint.inputNavDataName,"simple_nav_output");
	ConfigData->hillPoint.inputNavID = 0;
	strcpy(ConfigData->hillPoint.outputDataName,"att_ref_output_stage1");
	ConfigData->hillPoint.outputMsgID = 0;
	ConfigData->velocityPoint.inputCelID = 0;
	strcpy(ConfigData->velocityPoint.inputCelMessName,"mars_display_frame_data");
	strcpy(ConfigData->velocityPoint.inputNavDataName,"simple_nav_output");
	ConfigData->velocityPoint.inputNavID = 0;
	ConfigData->velocityPoint.mu = 1.32712440018e+20;
	strcpy(ConfigData->velocityPoint.outputDataName,"att_ref_output");
	ConfigData->velocityPoint.outputMsgID = 0;
	ConfigData->celTwoBodyPoint.R_P1[0] = 0.0;
	ConfigData->celTwoBodyPoint.R_P1[1] = 0.0;
	ConfigData->celTwoBodyPoint.R_P1[2] = 0.0;
	ConfigData->celTwoBodyPoint.R_P2[0] = 0.0;
	ConfigData->celTwoBodyPoint.R_P2[1] = 0.0;
	ConfigData->celTwoBodyPoint.R_P2[2] = 0.0;
	ConfigData->celTwoBodyPoint.a_P1[0] = 0.0;
	ConfigData->celTwoBodyPoint.a_P1[1] = 0.0;
	ConfigData->celTwoBodyPoint.a_P1[2] = 0.0;
	ConfigData->celTwoBodyPoint.a_P2[0] = 0.0;
	ConfigData->celTwoBodyPoint.a_P2[1] = 0.0;
	ConfigData->celTwoBodyPoint.a_P2[2] = 0.0;
	ConfigData->celTwoBodyPoint.inputCelID = 0;
	strcpy(ConfigData->celTwoBodyPoint.inputCelMessName,"mars_display_frame_data");
	strcpy(ConfigData->celTwoBodyPoint.inputNavDataName,"simple_nav_output");
	ConfigData->celTwoBodyPoint.inputNavID = 0;
	ConfigData->celTwoBodyPoint.inputSecID = 0;
	strcpy(ConfigData->celTwoBodyPoint.inputSecMessName,"");
	strcpy(ConfigData->celTwoBodyPoint.outputDataName,"att_ref_output");
	ConfigData->celTwoBodyPoint.outputMsgID = 0;
	ConfigData->celTwoBodyPoint.singularityThresh = 0.0174532925199;
	ConfigData->celTwoBodyPoint.v_P1[0] = 0.0;
	ConfigData->celTwoBodyPoint.v_P1[1] = 0.0;
	ConfigData->celTwoBodyPoint.v_P1[2] = 0.0;
	ConfigData->celTwoBodyPoint.v_P2[0] = 0.0;
	ConfigData->celTwoBodyPoint.v_P2[1] = 0.0;
	ConfigData->celTwoBodyPoint.v_P2[2] = 0.0;
	ConfigData->rasterManager.mnvrActive = 0;
	ConfigData->rasterManager.mnvrComplete = 0;
	ConfigData->rasterManager.mnvrStartTime = 0;
	ConfigData->rasterManager.numRasters = 12;
	ConfigData->rasterManager.outputEulerRatesID = 0;
	strcpy(ConfigData->rasterManager.outputEulerRatesName,"euler_angle_rates");
	ConfigData->rasterManager.outputEulerSetID = 0;
	strcpy(ConfigData->rasterManager.outputEulerSetName,"euler_angle_set");
	ConfigData->rasterManager.rasterTimes[0] = 720.0;
	ConfigData->rasterManager.rasterTimes[1] = 360.0;
	ConfigData->rasterManager.rasterTimes[2] = 360.0;
	ConfigData->rasterManager.scanSelector = 0;
	ConfigData->rasterManager.scanningAngles[0] = 0.0;
	ConfigData->rasterManager.scanningAngles[1] = 0.0;
	ConfigData->rasterManager.scanningAngles[2] = 0.0;
	ConfigData->rasterManager.scanningRates[0] = 0.0;
	ConfigData->rasterManager.scanningRates[1] = 0.0;
	ConfigData->rasterManager.scanningRates[2] = 0.000349065850399;
	ConfigData->eulerRotation.CallCounts = 0;
	ConfigData->eulerRotation.CrossInit = <bound method AlgContain.CrossInit of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.IntegratedInit = <bound method AlgContain.IntegratedInit of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	strcpy(ConfigData->eulerRotation.ModelTag,"eulerRotation");
	ConfigData->eulerRotation.RNGSeed = 464374481;
	ConfigData->eulerRotation.Reset = <bound method AlgContain.Reset of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.SelfInit = <bound method AlgContain.SelfInit of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UpdateState = <bound method AlgContain.UpdateState of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UseCrossInit = <bound method AlgContain.UseCrossInit of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UseData = <bound method AlgContain.UseData of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UseReset = <bound method AlgContain.UseReset of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UseSelfInit = <bound method AlgContain.UseSelfInit of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.UseUpdate = <bound method AlgContain.UseUpdate of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation._s = <class 'alg_contain.alg_contain.SysModel'>;
	ConfigData->eulerRotation.getSelfInitAddress = <bound method AlgContain.getSelfInitAddress of <alg_contain.alg_contain.AlgContain; proxy of <Swig Object of type 'AlgContain *' at 0x112c8dba0> >>;
	ConfigData->eulerRotation.moduleID = 92;
	ConfigData->TaskList_20_TaskModel_0.angleRates[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.angleRates[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.angleRates[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.angleSet[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.angleSet[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.angleSet[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdRates[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdRates[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdRates[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdSet[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdSet[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.cmdSet[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.dt = 0.0;
	ConfigData->TaskList_20_TaskModel_0.inputEulerRatesID = 0;
	strcpy(ConfigData->TaskList_20_TaskModel_0.inputEulerRatesName,"");
	ConfigData->TaskList_20_TaskModel_0.inputEulerSetID = 0;
	strcpy(ConfigData->TaskList_20_TaskModel_0.inputEulerSetName,"");
	ConfigData->TaskList_20_TaskModel_0.inputRefID = 0;
	strcpy(ConfigData->TaskList_20_TaskModel_0.inputRefName,"att_ref_output_stage1");
	strcpy(ConfigData->TaskList_20_TaskModel_0.outputDataName,"att_ref_output");
	ConfigData->TaskList_20_TaskModel_0.outputEulerRatesID = 0;
	strcpy(ConfigData->TaskList_20_TaskModel_0.outputEulerRatesName,"euler_rates_output");
	ConfigData->TaskList_20_TaskModel_0.outputEulerSetID = 0;
	strcpy(ConfigData->TaskList_20_TaskModel_0.outputEulerSetName,"euler_set_output");
	ConfigData->TaskList_20_TaskModel_0.outputMsgID = 0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdRates[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdRates[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdRates[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdSet[0] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdSet[1] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorCmdSet[2] = 0.0;
	ConfigData->TaskList_20_TaskModel_0.priorTime = 0;
	ConfigData->TaskList_22_TaskModel_0.inputNavID = 0;
	strcpy(ConfigData->TaskList_22_TaskModel_0.inputNavName,"simple_nav_output");
	ConfigData->TaskList_22_TaskModel_0.inputRefID = 0;
	strcpy(ConfigData->TaskList_22_TaskModel_0.inputRefName,"att_ref_output");
	strcpy(ConfigData->TaskList_22_TaskModel_0.outputDataName,"nom_att_guid_out");
	ConfigData->TaskList_22_TaskModel_0.outputMsgID = 0;
	ConfigData->TaskList_22_TaskModel_0.sigma_BcB = None;
	ConfigData->TaskList_22_TaskModel_0.sigma_R0R[0] = 0.0;
	ConfigData->TaskList_22_TaskModel_0.sigma_R0R[1] = 0.0;
	ConfigData->TaskList_22_TaskModel_0.sigma_R0R[2] = 0.0;
	ConfigData->errorDeadband.error = 0.0;
	ConfigData->errorDeadband.innerThresh = 0.0698131700798;
	ConfigData->errorDeadband.inputGuidID = 0;
	strcpy(ConfigData->errorDeadband.inputGuidName,"sun_safe_att_err");
	ConfigData->errorDeadband.omega_BR_B[0] = 0.0;
	ConfigData->errorDeadband.omega_BR_B[1] = 0.0;
	ConfigData->errorDeadband.omega_BR_B[2] = 0.0;
	ConfigData->errorDeadband.outerThresh = 0.305432619099;
	strcpy(ConfigData->errorDeadband.outputDataName,"db_att_guid_out");
	ConfigData->errorDeadband.outputGuidID = 0;
	ConfigData->errorDeadband.sigma_BR[0] = 0.0;
	ConfigData->errorDeadband.sigma_BR[1] = 0.0;
	ConfigData->errorDeadband.sigma_BR[2] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.GsMatrix[0] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.GsMatrix[1] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.GsMatrix[2] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.JsList[0] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.JsList[1] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.JsList[2] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.K1 = 0.3;
	ConfigData->TaskList_23_TaskModel_0.K3 = 1.0;
	ConfigData->TaskList_23_TaskModel_0.Ki = -1.0;
	ConfigData->TaskList_23_TaskModel_0.P = 150.0;
	ConfigData->TaskList_23_TaskModel_0.ignoreOuterLoopFeedforward = 0;
	ConfigData->TaskList_23_TaskModel_0.inputGuidID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_0.inputGuidName,"nom_att_guid_out");
	ConfigData->TaskList_23_TaskModel_0.inputRWConfID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_0.inputRWConfigData,"rwa_config_data");
	ConfigData->TaskList_23_TaskModel_0.inputRWSpeedsID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_0.inputRWSpeedsName,"reactionwheel_output_states");
	ConfigData->TaskList_23_TaskModel_0.inputVehicleConfigDataID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_0.inputVehicleConfigDataName,"adcs_config_data");
	ConfigData->TaskList_23_TaskModel_0.integralLimit = 0.0;
	ConfigData->TaskList_23_TaskModel_0.numRWAs = 4;
	ConfigData->TaskList_23_TaskModel_0.omega_max = 0.0261799387799;
	strcpy(ConfigData->TaskList_23_TaskModel_0.outputDataName,"controlTorqueRaw");
	ConfigData->TaskList_23_TaskModel_0.outputMsgID = 0;
	ConfigData->TaskList_23_TaskModel_0.priorTime = 0;
	ConfigData->TaskList_23_TaskModel_0.z[0] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.z[1] = 0.0;
	ConfigData->TaskList_23_TaskModel_0.z[2] = 0.0;
	strcpy(ConfigData->TaskList_23_TaskModel_1.inputControlName,"controlTorqueRaw");
	ConfigData->TaskList_23_TaskModel_1.inputMsgID = 0;
	ConfigData->TaskList_23_TaskModel_1.numThrGroups = 1;
	ConfigData->TaskList_23_TaskModel_2.GsInverse[0] = 0.0;
	ConfigData->TaskList_23_TaskModel_2.GsInverse[1] = 0.0;
	ConfigData->TaskList_23_TaskModel_2.GsInverse[2] = 0.0;
	ConfigData->TaskList_23_TaskModel_2.OmegaGain = 0.002;
	ConfigData->TaskList_23_TaskModel_2.inputRWCmdsID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_2.inputRWCommands,"reactionwheel_cmds_raw");
	ConfigData->TaskList_23_TaskModel_2.inputRWConfID = 0;
	strcpy(ConfigData->TaskList_23_TaskModel_2.inputRWConfigData,"rwa_config_data");
	strcpy(ConfigData->TaskList_23_TaskModel_2.inputRWSpeeds,"reactionwheel_output_states");
	ConfigData->TaskList_23_TaskModel_2.inputSpeedsID = 0;
	ConfigData->TaskList_23_TaskModel_2.numWheels = 4;
	strcpy(ConfigData->TaskList_23_TaskModel_2.outputControlName,"reactionwheel_cmds");
	ConfigData->TaskList_23_TaskModel_2.outputMsgID = 0;
	ConfigData->TaskList_24_TaskModel_0.inputNavID = 0;
	strcpy(ConfigData->TaskList_24_TaskModel_0.inputNavName,"simple_nav_output");
	ConfigData->TaskList_24_TaskModel_0.inputRefID = 0;
	strcpy(ConfigData->TaskList_24_TaskModel_0.inputRefName,"att_ref_output");
	strcpy(ConfigData->TaskList_24_TaskModel_0.outputDataName,"nom_att_guid_out");
	ConfigData->TaskList_24_TaskModel_0.outputMsgID = 0;
	ConfigData->TaskList_24_TaskModel_0.sigma_BcB = None;
	ConfigData->TaskList_24_TaskModel_0.sigma_R0R[0] = 0.0;
	ConfigData->TaskList_24_TaskModel_0.sigma_R0R[1] = 0.0;
	ConfigData->TaskList_24_TaskModel_0.sigma_R0R[2] = 0.0;
	ConfigData->MRP_SteeringRWA.GsMatrix[0] = 0.0;
	ConfigData->MRP_SteeringRWA.GsMatrix[1] = 0.0;
	ConfigData->MRP_SteeringRWA.GsMatrix[2] = 0.0;
	ConfigData->MRP_SteeringRWA.JsList[0] = 0.0;
	ConfigData->MRP_SteeringRWA.JsList[1] = 0.0;
	ConfigData->MRP_SteeringRWA.JsList[2] = 0.0;
	ConfigData->MRP_SteeringRWA.K1 = 0.3;
	ConfigData->MRP_SteeringRWA.K3 = 1.0;
	ConfigData->MRP_SteeringRWA.Ki = -1.0;
	ConfigData->MRP_SteeringRWA.P = 150.0;
	ConfigData->MRP_SteeringRWA.ignoreOuterLoopFeedforward = 0;
	ConfigData->MRP_SteeringRWA.inputGuidID = 0;
	strcpy(ConfigData->MRP_SteeringRWA.inputGuidName,"nom_att_guid_out");
	ConfigData->MRP_SteeringRWA.inputRWConfID = 0;
	strcpy(ConfigData->MRP_SteeringRWA.inputRWConfigData,"rwa_config_data");
	ConfigData->MRP_SteeringRWA.inputRWSpeedsID = 0;
	strcpy(ConfigData->MRP_SteeringRWA.inputRWSpeedsName,"reactionwheel_output_states");
	ConfigData->MRP_SteeringRWA.inputVehicleConfigDataID = 0;
	strcpy(ConfigData->MRP_SteeringRWA.inputVehicleConfigDataName,"adcs_config_data");
	ConfigData->MRP_SteeringRWA.integralLimit = 0.0;
	ConfigData->MRP_SteeringRWA.numRWAs = 4;
	ConfigData->MRP_SteeringRWA.omega_max = 0.0261799387799;
	strcpy(ConfigData->MRP_SteeringRWA.outputDataName,"controlTorqueRaw");
	ConfigData->MRP_SteeringRWA.outputMsgID = 0;
	ConfigData->MRP_SteeringRWA.priorTime = 0;
	ConfigData->MRP_SteeringRWA.z[0] = 0.0;
	ConfigData->MRP_SteeringRWA.z[1] = 0.0;
	ConfigData->MRP_SteeringRWA.z[2] = 0.0;
	strcpy(ConfigData->TaskList_24_TaskModel_2.inputControlName,"controlTorqueRaw");
	ConfigData->TaskList_24_TaskModel_2.inputMsgID = 0;
	ConfigData->TaskList_24_TaskModel_2.numThrGroups = 1;
	ConfigData->TaskList_24_TaskModel_3.GsInverse[0] = 0.0;
	ConfigData->TaskList_24_TaskModel_3.GsInverse[1] = 0.0;
	ConfigData->TaskList_24_TaskModel_3.GsInverse[2] = 0.0;
	ConfigData->TaskList_24_TaskModel_3.OmegaGain = 0.002;
	ConfigData->TaskList_24_TaskModel_3.inputRWCmdsID = 0;
	strcpy(ConfigData->TaskList_24_TaskModel_3.inputRWCommands,"reactionwheel_cmds_raw");
	ConfigData->TaskList_24_TaskModel_3.inputRWConfID = 0;
	strcpy(ConfigData->TaskList_24_TaskModel_3.inputRWConfigData,"rwa_config_data");
	strcpy(ConfigData->TaskList_24_TaskModel_3.inputRWSpeeds,"reactionwheel_output_states");
	ConfigData->TaskList_24_TaskModel_3.inputSpeedsID = 0;
	ConfigData->TaskList_24_TaskModel_3.numWheels = 4;
	strcpy(ConfigData->TaskList_24_TaskModel_3.outputControlName,"reactionwheel_cmds");
	ConfigData->TaskList_24_TaskModel_3.outputMsgID = 0;
	ConfigData->TaskList_25_TaskModel_0.inputNavID = 0;
	strcpy(ConfigData->TaskList_25_TaskModel_0.inputNavName,"simple_nav_output");
	ConfigData->TaskList_25_TaskModel_0.inputRefID = 0;
	strcpy(ConfigData->TaskList_25_TaskModel_0.inputRefName,"att_ref_output");
	strcpy(ConfigData->TaskList_25_TaskModel_0.outputDataName,"nom_att_guid_out");
	ConfigData->TaskList_25_TaskModel_0.outputMsgID = 0;
	ConfigData->TaskList_25_TaskModel_0.sigma_BcB = None;
	ConfigData->TaskList_25_TaskModel_0.sigma_R0R[0] = 0.0;
	ConfigData->TaskList_25_TaskModel_0.sigma_R0R[1] = 0.0;
	ConfigData->TaskList_25_TaskModel_0.sigma_R0R[2] = 0.0;
	ConfigData->MRP_FeedbackRWA.GsMatrix[0] = 0.0;
	ConfigData->MRP_FeedbackRWA.GsMatrix[1] = 0.0;
	ConfigData->MRP_FeedbackRWA.GsMatrix[2] = 0.0;
	ConfigData->MRP_FeedbackRWA.JsList[0] = 0.0;
	ConfigData->MRP_FeedbackRWA.JsList[1] = 0.0;
	ConfigData->MRP_FeedbackRWA.JsList[2] = 0.0;
	ConfigData->MRP_FeedbackRWA.K = 1.0;
	ConfigData->MRP_FeedbackRWA.Ki = -1.0;
	ConfigData->MRP_FeedbackRWA.P = 3.0;
	ConfigData->MRP_FeedbackRWA.domega0[0] = 0.0;
	ConfigData->MRP_FeedbackRWA.domega0[1] = 0.0;
	ConfigData->MRP_FeedbackRWA.domega0[2] = 0.0;
	ConfigData->MRP_FeedbackRWA.inputGuidID = 0;
	strcpy(ConfigData->MRP_FeedbackRWA.inputGuidName,"nom_att_guid_out");
	ConfigData->MRP_FeedbackRWA.inputRWConfID = 0;
	strcpy(ConfigData->MRP_FeedbackRWA.inputRWConfigData,"rwa_config_data");
	ConfigData->MRP_FeedbackRWA.inputRWSpeedsID = 0;
	strcpy(ConfigData->MRP_FeedbackRWA.inputRWSpeedsName,"reactionwheel_output_states");
	ConfigData->MRP_FeedbackRWA.inputVehicleConfigDataID = 0;
	strcpy(ConfigData->MRP_FeedbackRWA.inputVehicleConfigDataName,"adcs_config_data");
	ConfigData->MRP_FeedbackRWA.int_sigma[0] = 0.0;
	ConfigData->MRP_FeedbackRWA.int_sigma[1] = 0.0;
	ConfigData->MRP_FeedbackRWA.int_sigma[2] = 0.0;
	ConfigData->MRP_FeedbackRWA.integralLimit = 0.0;
	ConfigData->MRP_FeedbackRWA.numRWAs = 4;
	strcpy(ConfigData->MRP_FeedbackRWA.outputDataName,"controlTorqueRaw");
	ConfigData->MRP_FeedbackRWA.outputMsgID = 0;
	ConfigData->MRP_FeedbackRWA.priorTime = 0;
	ConfigData->MRP_FeedbackRWA.z[0] = 0.0;
	ConfigData->MRP_FeedbackRWA.z[1] = 0.0;
	ConfigData->MRP_FeedbackRWA.z[2] = 0.0;
	strcpy(ConfigData->TaskList_25_TaskModel_2.inputControlName,"controlTorqueRaw");
	ConfigData->TaskList_25_TaskModel_2.inputMsgID = 0;
	ConfigData->TaskList_25_TaskModel_2.numThrGroups = 1;
	ConfigData->TaskList_25_TaskModel_3.GsInverse[0] = 0.0;
	ConfigData->TaskList_25_TaskModel_3.GsInverse[1] = 0.0;
	ConfigData->TaskList_25_TaskModel_3.GsInverse[2] = 0.0;
	ConfigData->TaskList_25_TaskModel_3.OmegaGain = 0.002;
	ConfigData->TaskList_25_TaskModel_3.inputRWCmdsID = 0;
	strcpy(ConfigData->TaskList_25_TaskModel_3.inputRWCommands,"reactionwheel_cmds_raw");
	ConfigData->TaskList_25_TaskModel_3.inputRWConfID = 0;
	strcpy(ConfigData->TaskList_25_TaskModel_3.inputRWConfigData,"rwa_config_data");
	strcpy(ConfigData->TaskList_25_TaskModel_3.inputRWSpeeds,"reactionwheel_output_states");
	ConfigData->TaskList_25_TaskModel_3.inputSpeedsID = 0;
	ConfigData->TaskList_25_TaskModel_3.numWheels = 4;
	strcpy(ConfigData->TaskList_25_TaskModel_3.outputControlName,"reactionwheel_cmds");
	ConfigData->TaskList_25_TaskModel_3.outputMsgID = 0;
	ConfigData->inertial3DSpin.dt = 0.0;
	ConfigData->inertial3DSpin.inputRefID = 0;
	strcpy(ConfigData->inertial3DSpin.inputRefName,"att_ref_output_stage1");
	ConfigData->inertial3DSpin.omega_RN_N[0] = 0.00349065850399;
	ConfigData->inertial3DSpin.omega_RN_N[1] = 0.00349065850399;
	ConfigData->inertial3DSpin.omega_RN_N[2] = 0.00698131700798;
	strcpy(ConfigData->inertial3DSpin.outputDataName,"att_ref_output");
	ConfigData->inertial3DSpin.outputMsgID = 0;
	ConfigData->inertial3DSpin.priorCmdSigma_RN[0] = 0.0;
	ConfigData->inertial3DSpin.priorCmdSigma_RN[1] = 0.0;
	ConfigData->inertial3DSpin.priorCmdSigma_RN[2] = 0.0;
	ConfigData->inertial3DSpin.priorTime = 0;
	ConfigData->inertial3DSpin.sigma_RN[0] = 0.0;
	ConfigData->inertial3DSpin.sigma_RN[1] = 0.0;
	ConfigData->inertial3DSpin.sigma_RN[2] = 0.0;
	ConfigData->attTrackingError.inputNavID = 0;
	strcpy(ConfigData->attTrackingError.inputNavName,"simple_nav_output");
	ConfigData->attTrackingError.inputRefID = 0;
	strcpy(ConfigData->attTrackingError.inputRefName,"att_ref_output");
	strcpy(ConfigData->attTrackingError.outputDataName,"nom_att_guid_out");
	ConfigData->attTrackingError.outputMsgID = 0;
	ConfigData->attTrackingError.sigma_BcB = None;
	ConfigData->attTrackingError.sigma_R0R[0] = 0.0;
	ConfigData->attTrackingError.sigma_R0R[1] = 0.0;
	ConfigData->attTrackingError.sigma_R0R[2] = 0.0;
	ConfigData->PRV_SteeringRWA.GsMatrix[0] = 0.0;
	ConfigData->PRV_SteeringRWA.GsMatrix[1] = 0.0;
	ConfigData->PRV_SteeringRWA.GsMatrix[2] = 0.0;
	ConfigData->PRV_SteeringRWA.JsList[0] = 0.0;
	ConfigData->PRV_SteeringRWA.JsList[1] = 0.0;
	ConfigData->PRV_SteeringRWA.JsList[2] = 0.0;
	ConfigData->PRV_SteeringRWA.K1 = 0.3;
	ConfigData->PRV_SteeringRWA.K3 = 1.0;
	ConfigData->PRV_SteeringRWA.Ki = -1.0;
	ConfigData->PRV_SteeringRWA.P = 150.0;
	ConfigData->PRV_SteeringRWA.inputGuidID = 0;
	strcpy(ConfigData->PRV_SteeringRWA.inputGuidName,"nom_att_guid_out");
	ConfigData->PRV_SteeringRWA.inputRWConfID = 0;
	strcpy(ConfigData->PRV_SteeringRWA.inputRWConfigData,"rwa_config_data");
	ConfigData->PRV_SteeringRWA.inputRWSpeedsID = 0;
	strcpy(ConfigData->PRV_SteeringRWA.inputRWSpeedsName,"reactionwheel_output_states");
	ConfigData->PRV_SteeringRWA.inputVehicleConfigDataID = 0;
	strcpy(ConfigData->PRV_SteeringRWA.inputVehicleConfigDataName,"adcs_config_data");
	ConfigData->PRV_SteeringRWA.integralLimit = 0.0;
	ConfigData->PRV_SteeringRWA.numRWAs = 0;
	ConfigData->PRV_SteeringRWA.omega_max = 0.0261799387799;
	strcpy(ConfigData->PRV_SteeringRWA.outputDataName,"controlTorqueRaw");
	ConfigData->PRV_SteeringRWA.outputMsgID = 0;
	ConfigData->PRV_SteeringRWA.priorTime = 0;
	ConfigData->PRV_SteeringRWA.z[0] = 0.0;
	ConfigData->PRV_SteeringRWA.z[1] = 0.0;
	ConfigData->PRV_SteeringRWA.z[2] = 0.0;
	strcpy(ConfigData->RWAMappingData.inputControlName,"controlTorqueRaw");
	ConfigData->RWAMappingData.inputMsgID = 0;
	ConfigData->RWAMappingData.numThrGroups = 1;
	ConfigData->RWNullSpace.GsInverse[0] = 0.0;
	ConfigData->RWNullSpace.GsInverse[1] = 0.0;
	ConfigData->RWNullSpace.GsInverse[2] = 0.0;
	ConfigData->RWNullSpace.OmegaGain = 0.002;
	ConfigData->RWNullSpace.inputRWCmdsID = 0;
	strcpy(ConfigData->RWNullSpace.inputRWCommands,"reactionwheel_cmds_raw");
	ConfigData->RWNullSpace.inputRWConfID = 0;
	strcpy(ConfigData->RWNullSpace.inputRWConfigData,"rwa_config_data");
	strcpy(ConfigData->RWNullSpace.inputRWSpeeds,"reactionwheel_output_states");
	ConfigData->RWNullSpace.inputSpeedsID = 0;
	ConfigData->RWNullSpace.numWheels = 4;
	strcpy(ConfigData->RWNullSpace.outputControlName,"reactionwheel_cmds");
	ConfigData->RWNullSpace.outputMsgID = 0;
}