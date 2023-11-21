// Fill out your copyright notice in the Description page of Project Settings.


#include "CustomMoviePipelineDeferredPass.h"
#include "CustomMoviePipelineOutput.h"

void UCustomMoviePipelineDeferredPass::SetupImpl(const MoviePipeline::FMoviePipelineRenderPassInitSettings& InPassInitSettings)
{
	
	UCustomMoviePipelineOutput* OutputSettings = GetPipeline()->GetPipelineMasterConfig()->FindSetting<UCustomMoviePipelineOutput>();
	check(OutputSettings);

	AdditionalPostProcessMaterials.Empty();
	for (FCustomMoviePipelineRenderPass& Pass : OutputSettings->AdditionalRenderPasses)
	{
		if (Pass.Material.IsNull() || Pass.bEnabled == false) 
		{
			continue;
		}
		FMoviePipelinePostProcessPass NewPass;
		NewPass.bEnabled = Pass.bEnabled;
		NewPass.Material = Pass.Material;
		AdditionalPostProcessMaterials.Add(NewPass);

		FString PassName = Pass.Material.LoadSynchronous()->GetName();
		Pass.SPassName = PassIdentifier.Name + PassName;  // set identifier pass name
		if (Pass.RenderPassName.IsEmpty())
		{
			Pass.RenderPassName = PassName;
		}
	}
	
	UE_LOG(LogMovieRenderPipeline, Log, TEXT("Custom Movie Pipeline Finised, %d ppm materials."), AdditionalPostProcessMaterials.Num());
	
	Super::SetupImpl(InPassInitSettings);
}
