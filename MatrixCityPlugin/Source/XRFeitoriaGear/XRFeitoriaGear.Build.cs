// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class XRFeitoriaGear : ModuleRules
{
	public XRFeitoriaGear(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicIncludePaths.AddRange(
			new string[] {
				// ... add public include paths required here ...
			}
			);
				
		
		PrivateIncludePaths.AddRange(
			new string[] {
				// ... add other private include paths required here ...
			}
			);
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"UnrealEd",
				"ImageWriteQueue",
				"SignalProcessing", // Needed for wave writer.
				"AudioMixer",
				"UEOpenExr", // Needed for multilayer EXRs
				"UEOpenExrRTTI", // Needed for EXR metadata
				"ImageWrapper",				
				"CinematicCamera", // For metadata
				"MovieRenderPipelineSettings", // For settings
				"MovieRenderPipelineRenderPasses",
				"MovieRenderPipelineEditor",
				"MeshDescription",
			}
			);

#if UE_5_0_OR_LATER
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"Imath",
				"PhysicsUtilities",
			}
			);
#endif
		

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"MovieRenderPipelineCore",
				"Renderer",
				"RenderCore",
				"RHI",
				"OpenColorIO",
				"ActorLayerUtilities", // For Layering
				// ... add other public dependencies that you statically link with here ...
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);
		
		// Required for UEOpenExr
		AddEngineThirdPartyPrivateStaticDependencies(Target, "zlib");
	}
}
