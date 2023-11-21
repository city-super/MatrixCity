// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "MoviePipelineDeferredPasses.h"
#include "Misc/StringFormatArg.h"
#include "Runtime/Launch/Resources/Version.h"

#if WITH_UNREALEXR
#if ENGINE_MAJOR_VERSION == 4
THIRD_PARTY_INCLUDES_START
#include "OpenEXR/include/ImfIO.h"
#include "OpenEXR/include/ImathBox.h"
#include "OpenEXR/include/ImfChannelList.h"
#include "OpenEXR/include/ImfInputFile.h"
#include "OpenEXR/include/ImfOutputFile.h"
#include "OpenEXR/include/ImfArray.h"
#include "OpenEXR/include/ImfHeader.h"
#include "OpenEXR/include/ImfStdIO.h"
#include "OpenEXR/include/ImfChannelList.h"
#include "OpenEXR/include/ImfRgbaFile.h"
#include "OpenEXR/include/ImfChannelList.h"
THIRD_PARTY_INCLUDES_END

#elif ENGINE_MAJOR_VERSION == 5
THIRD_PARTY_INCLUDES_START
#include "Imath/ImathBox.h"
#include "OpenEXR/ImfArray.h"
#include "OpenEXR/ImfChannelList.h"
#include "OpenEXR/ImfHeader.h"
#include "OpenEXR/ImfIO.h"
#include "OpenEXR/ImfInputFile.h"
#include "OpenEXR/ImfOutputFile.h"
#include "OpenEXR/ImfRgbaFile.h"
#include "OpenEXR/ImfStdIO.h"
#include "OpenEXR/ImfChannelList.h"
THIRD_PARTY_INCLUDES_END
#endif

#endif // WITH_UNREALEXR

#include "ImageWriteTask.h"
#include "ImagePixelData.h"

#include "HAL/PlatformFilemanager.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Async/Async.h"
#include "Misc/Paths.h"
#include "HAL/PlatformTime.h"
#include "Math/Float16.h"
#include "MovieRenderPipelineCoreModule.h"
#include "MoviePipelineOutputSetting.h"
#include "ImageWriteQueue.h"
#include "MoviePipeline.h"
#include "MoviePipelineImageQuantization.h"
#include "MoviePipelineMasterConfig.h"
#include "IOpenExrRTTIModule.h"
#include "Modules/ModuleManager.h"
#include "MoviePipelineUtils.h"


#include "CoreMinimal.h"
#include "Async/Future.h"
// #include "MovieRenderPipelineRenderPasses/Public/MoviePipelineImageSequenceOutput.h"
// #include "MovieRenderPipelineRenderPasses/Private/MoviePipelineEXROutput.h"
#include "MoviePipelineImageSequenceOutput.h"
#include "CustomMoviePipelineOutput.generated.h"


UENUM(BlueprintType)
enum class ECustomImageFormat : uint8
{
	/** Portable Network Graphics. */
	PNG = 0,
	/** Joint Photographic Experts Group. */
	JPEG,
	/** Windows Bitmap. */
	BMP,
	/** OpenEXR (HDR) image file format. */
	EXR
};
	
USTRUCT(BlueprintType)
struct XRFEITORIAGEAR_API FCustomMoviePipelineRenderPass
{
	GENERATED_BODY()
	
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Render Pass")
	bool bEnabled = true;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Render Pass")
	FString RenderPassName;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Render Pass")
	TSoftObjectPtr<UMaterialInterface> Material;
	// UMaterialInterface* Material;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Render Pass")
	ECustomImageFormat Extension;
	
	FString SPassName;

};

/**
 * 
 */
UCLASS()
class XRFEITORIAGEAR_API UCustomMoviePipelineOutput : public UMoviePipelineImageSequenceOutputBase
{
	GENERATED_BODY()
public:
#if WITH_EDITOR
	virtual FText GetDisplayText() const override { return NSLOCTEXT("MovieRenderPipeline", "ImgSequenceEXTSettingDisplayName", ".ext(custom) Sequence [8/16bit]"); }
#endif
public:
	UCustomMoviePipelineOutput(): UMoviePipelineImageSequenceOutputBase()
	{
		OutputFormat = EImageFormat::PNG;
	}
	virtual void OnReceiveImageDataImpl(FMoviePipelineMergerOutputFrame* InMergedOutputFrame) override;
	
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RenderPasses|RGB")
	bool bEnableRenderPass_RGB = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RenderPasses|RGB")
	FString RenderPassName_RGB;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RenderPasses|RGB")
	ECustomImageFormat Extension_RGB = ECustomImageFormat::PNG;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RenderPasses|Additional")
	TArray<FCustomMoviePipelineRenderPass> AdditionalRenderPasses;
};
