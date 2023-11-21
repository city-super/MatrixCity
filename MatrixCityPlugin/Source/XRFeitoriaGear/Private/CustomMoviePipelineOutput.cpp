// Fill out your copyright notice in the Description page of Project Settings.


#include "CustomMoviePipelineOutput.h"
#include "ImageWriteTask.h"
#include "ImagePixelData.h"
#include "Modules/ModuleManager.h"
#include "ImageWriteQueue.h"
#include "MoviePipeline.h"
#include "ImageWriteStream.h"
#include "MoviePipelineMasterConfig.h"
#include "MovieRenderTileImage.h"
#include "MovieRenderOverlappedImage.h"
#include "MovieRenderPipelineCoreModule.h"
#include "Misc/FrameRate.h"
#include "MoviePipelineOutputSetting.h"
#include "MoviePipelineBurnInSetting.h"
#include "Containers/UnrealString.h"
#include "Misc/StringFormatArg.h"
#include "MoviePipelineOutputBase.h"
#include "MoviePipelineImageQuantization.h"
#include "MoviePipelineWidgetRenderSetting.h"
#include "MoviePipelineUtils.h"
#include "HAL/PlatformTime.h"
#include "Misc/Paths.h"

DECLARE_CYCLE_STAT(TEXT("ImgSeqOutput_RecieveImageData"), STAT_ImgSeqRecieveImageData, STATGROUP_MoviePipeline);

void UCustomMoviePipelineOutput::OnReceiveImageDataImpl(FMoviePipelineMergerOutputFrame* InMergedOutputFrame)
{
	SCOPE_CYCLE_COUNTER(STAT_ImgSeqRecieveImageData);

	check(InMergedOutputFrame);

	// Special case for extracting Burn Ins and Widget Renderer 
	TArray<MoviePipeline::FCompositePassInfo> CompositedPasses;
	MoviePipeline::GetPassCompositeData(InMergedOutputFrame, CompositedPasses);

	UMoviePipelineOutputSetting* OutputSettings = GetPipeline()->GetPipelineMasterConfig()->FindSetting<UMoviePipelineOutputSetting>();
	check(OutputSettings);

	UMoviePipelineColorSetting* ColorSetting = GetPipeline()->GetPipelineMasterConfig()->FindSetting<UMoviePipelineColorSetting>();

	FString OutputDirectory = OutputSettings->OutputDirectory.Path;

	for (TPair<FMoviePipelinePassIdentifier, TUniquePtr<FImagePixelData>>& RenderPassData : InMergedOutputFrame->ImageOutputData)
	{
		// Don't write out a composited pass in this loop, as it will be merged with the Final Image and not written separately. 
		bool bSkip = false;
		for (const MoviePipeline::FCompositePassInfo& CompositePass : CompositedPasses)
		{
			if (CompositePass.PassIdentifier == RenderPassData.Key)
			{
				bSkip = true;
				break;
			}
		}

		if (bSkip)
		{
			continue;
		}

		// Get the output file extension via the output setting
		EImageFormat PreferredOutputFormat = OutputFormat;
		FString RenderPassName;
		if (RenderPassData.Key.Name == FString("FinalImage"))
		{
			if (!bEnableRenderPass_RGB)
			{
				continue;
			}
			switch (Extension_RGB)
			{
			case ECustomImageFormat::PNG: PreferredOutputFormat = EImageFormat::PNG; break;
			case ECustomImageFormat::JPEG: PreferredOutputFormat = EImageFormat::JPEG; break;
			case ECustomImageFormat::BMP: PreferredOutputFormat = EImageFormat::BMP; break;
			case ECustomImageFormat::EXR: PreferredOutputFormat = EImageFormat::EXR; break;
			}

			if (RenderPassName_RGB.IsEmpty())
			{
				RenderPassName_RGB = FString("rgb");
			}

			RenderPassName = RenderPassName_RGB;
		}

		for (FCustomMoviePipelineRenderPass DefinedRenderPass: AdditionalRenderPasses)
		{
			if (DefinedRenderPass.SPassName == RenderPassData.Key.Name)
			{
				if (!DefinedRenderPass.bEnabled)
				{
					continue;
				}
				switch (DefinedRenderPass.Extension)
				{
				case ECustomImageFormat::PNG: PreferredOutputFormat = EImageFormat::PNG; break;
				case ECustomImageFormat::JPEG: PreferredOutputFormat = EImageFormat::JPEG; break;
				case ECustomImageFormat::BMP: PreferredOutputFormat = EImageFormat::BMP; break;
				case ECustomImageFormat::EXR: PreferredOutputFormat = EImageFormat::EXR; break;
				}
				
				RenderPassName = DefinedRenderPass.RenderPassName;
			}
		}

		FImagePixelDataPayload* Payload = RenderPassData.Value->GetPayload<FImagePixelDataPayload>();

		// If the output requires a transparent output (to be useful) then we'll on a per-case basis override their intended
		// filetype to something that makes that file useful.
		if (Payload->bRequireTransparentOutput)
		{
			if (PreferredOutputFormat == EImageFormat::BMP ||
				PreferredOutputFormat == EImageFormat::JPEG)
			{
				PreferredOutputFormat = EImageFormat::PNG;
			}
		}

		const TCHAR* Extension = TEXT("");
		switch (PreferredOutputFormat)
		{
		case EImageFormat::PNG: Extension = TEXT("png"); break;
		case EImageFormat::JPEG: Extension = TEXT("jpeg"); break;
		case EImageFormat::BMP: Extension = TEXT("bmp"); break;
		case EImageFormat::EXR: Extension = TEXT("exr"); break;
		}

		TUniquePtr<FImagePixelData> QuantizedPixelData = nullptr;
		

		switch (PreferredOutputFormat)
		{
		case EImageFormat::PNG:
		case EImageFormat::JPEG:
		case EImageFormat::BMP:
		{
			// All three of these formats only support 8 bit data, so we need to take the incoming buffer type,
			// copy it into a new 8-bit array and optionally apply a little noise to the data to help hide gradient banding.
			QuantizedPixelData = UE::MoviePipeline::QuantizeImagePixelDataToBitDepth(RenderPassData.Value.Get(), 8, nullptr, !(ColorSetting && ColorSetting->OCIOConfiguration.bIsEnabled));
			break;
		}
		case EImageFormat::EXR:
			// No quantization required, just copy the data as we will move it into the image write task.
			QuantizedPixelData = RenderPassData.Value->CopyImageData();
			break;
		default:
			check(false);
		}

		// We need to resolve the filename format string. We combine the folder and file name into one long string first
		MoviePipeline::FMoviePipelineOutputFutureData OutputData;
		OutputData.Shot = GetPipeline()->GetActiveShotList()[Payload->SampleState.OutputState.ShotIndex];
		OutputData.PassIdentifier = RenderPassData.Key;

		struct FXMLData
		{
			FString ClipName;
			FString ImageSequenceFileName;
		};
		
		FXMLData XMLData;
		{
			FString FileNameFormatString = OutputSettings->FileNameFormat;

			// If we're writing more than one render pass out, we need to ensure the file name has the format string in it so we don't
			// overwrite the same file multiple times. Burn In overlays don't count if they are getting composited on top of an existing file.
			const bool bIncludeRenderPass = InMergedOutputFrame->ImageOutputData.Num() - CompositedPasses.Num() > 1;
			const bool bTestFrameNumber = true;

			UE::MoviePipeline::ValidateOutputFormatString(FileNameFormatString, bIncludeRenderPass, bTestFrameNumber);

			// Create specific data that needs to override 
			TMap<FString, FString> FormatOverrides;
			// FormatOverrides.Add(TEXT("render_pass"), RenderPassData.Key.Name);
			FormatOverrides.Add(TEXT("render_pass"), RenderPassName);
			FormatOverrides.Add(TEXT("ext"), Extension);
			FMoviePipelineFormatArgs FinalFormatArgs;

			// Resolve for XMLs
			{
				GetPipeline()->ResolveFilenameFormatArguments(FileNameFormatString, FormatOverrides, XMLData.ImageSequenceFileName, FinalFormatArgs, &InMergedOutputFrame->FrameOutputState, -InMergedOutputFrame->FrameOutputState.ShotOutputFrameNumber);
			}
			
			// Resolve the final absolute file path to write this to
			{
				FString FormatString = OutputDirectory / FileNameFormatString;
				GetPipeline()->ResolveFilenameFormatArguments(FormatString, FormatOverrides, OutputData.FilePath, FinalFormatArgs, &InMergedOutputFrame->FrameOutputState);

				if (FPaths::IsRelative(OutputData.FilePath))
				{
					OutputData.FilePath = FPaths::ConvertRelativePathToFull(OutputData.FilePath);
				}
			}

			// More XML resolving. Create a deterministic clipname by removing frame numbers, file extension, and any trailing .'s
			{
				UE::MoviePipeline::RemoveFrameNumberFormatStrings(FileNameFormatString, true);
				GetPipeline()->ResolveFilenameFormatArguments(FileNameFormatString, FormatOverrides, XMLData.ClipName, FinalFormatArgs, &InMergedOutputFrame->FrameOutputState);
				XMLData.ClipName.RemoveFromEnd(Extension);
				XMLData.ClipName.RemoveFromEnd(".");
			}
		}

		TUniquePtr<FImageWriteTask> TileImageTask = MakeUnique<FImageWriteTask>();
		TileImageTask->Format = PreferredOutputFormat;
		TileImageTask->CompressionQuality = 100;
		TileImageTask->Filename = OutputData.FilePath;

		// We composite before flipping the alpha so that it is consistent for all formats.
		if (RenderPassData.Key == FMoviePipelinePassIdentifier(TEXT("FinalImage")))
		{
			for (const MoviePipeline::FCompositePassInfo& CompositePass : CompositedPasses)
			{
				// We don't need to copy the data here (even though it's being passed to a async system) because we already made a unique copy of the
				// burn in/widget data when we decided to composite it.
				switch (QuantizedPixelData->GetType())
				{
				case EImagePixelType::Color:
					TileImageTask->PixelPreProcessors.Add(TAsyncCompositeImage<FColor>(CompositePass.PixelData->MoveImageDataToNew()));
					break;
				case EImagePixelType::Float16:
					TileImageTask->PixelPreProcessors.Add(TAsyncCompositeImage<FFloat16Color>(CompositePass.PixelData->MoveImageDataToNew()));
					break;
				case EImagePixelType::Float32:
					TileImageTask->PixelPreProcessors.Add(TAsyncCompositeImage<FLinearColor>(CompositePass.PixelData->MoveImageDataToNew()));
					break;
				}
			}
		}


		TileImageTask->PixelData = MoveTemp(QuantizedPixelData);
		
#if WITH_EDITOR
		GetPipeline()->AddFrameToOutputMetadata(XMLData.ClipName, XMLData.ImageSequenceFileName, InMergedOutputFrame->FrameOutputState, Extension, Payload->bRequireTransparentOutput);
#endif

		GetPipeline()->AddOutputFuture(ImageWriteQueue->Enqueue(MoveTemp(TileImageTask)), OutputData);
	}
}
