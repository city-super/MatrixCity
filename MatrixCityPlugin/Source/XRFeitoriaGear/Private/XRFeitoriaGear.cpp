// Copyright Epic Games, Inc. All Rights Reserved.

#include "XRFeitoriaGear.h"
#include "Engine/RendererSettings.h"
#include "MovieRenderPipelineSettings.h"
#include "CustomMoviePipelineOutput.h"
#include "CustomMoviePipelineDeferredPass.h"

#define LOCTEXT_NAMESPACE "FXRFeitoriaGearModule"

void FXRFeitoriaGearModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
	UE_LOG(LogTemp, Log, TEXT( "XRFeitoriaGear Loaded. Doing initialization." ));
	URendererSettings* Settings = GetMutableDefault<URendererSettings>();

#if ENGINE_MAJOR_VERSION == 5
	
	Settings->CustomDepthStencil = ECustomDepthStencil::EnabledWithStencil;
	Settings->VelocityPass = EVelocityOutputPass::BasePass;
	Settings->SaveConfig();

#elif ENGINE_MAJOR_VERSION == 4
	
	Settings->CustomDepthStencil = ECustomDepthStencil::EnabledWithStencil;
	Settings->bBasePassOutputsVelocity = true;
	Settings->SaveConfig();

#endif

	UMovieRenderPipelineProjectSettings* MRQ_Settings = GetMutableDefault<UMovieRenderPipelineProjectSettings>();
	MRQ_Settings->DefaultClasses.Empty();
	MRQ_Settings->DefaultClasses.Add(UCustomMoviePipelineOutput::StaticClass());
	MRQ_Settings->DefaultClasses.Add(UCustomMoviePipelineDeferredPass::StaticClass());
	MRQ_Settings->SaveConfig();
}

void FXRFeitoriaGearModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FXRFeitoriaGearModule, XRFeitoriaGear)