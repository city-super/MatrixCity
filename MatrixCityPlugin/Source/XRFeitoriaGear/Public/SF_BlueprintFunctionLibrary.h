// Fill out your copyright notice in the Description page of Project Settings.

#pragma once
#include "Serialization/Archive.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/ArchiveSaveCompressedProxy.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/PostProcessComponent.h"

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SF_BlueprintFunctionLibrary.generated.h"

DECLARE_LOG_CATEGORY_EXTERN(LogSF, Log, All);

/**
 * 
 */
UCLASS()
class XRFEITORIAGEAR_API USF_BlueprintFunctionLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

	UFUNCTION(BlueprintCallable, Category="SF_BPLibrary")
		static bool SaveFloatToByteFile(float f, FString Path);
	UFUNCTION(BlueprintCallable, Category="SF_BPLibrary")
		static bool SaveFloatArrayToByteFile(TArray<float> FloatArray, FString Path);
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static void EmptyPostProcessMaterial(UPostProcessComponent* postprocessComponent);
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static void ModifyPostProcessMaterial(UMaterialInterface * mat, UPostProcessComponent* postprocessComponent);

	/** Saves text to filename of your choosing, make sure include whichever file extension you want in the filename, ex: SelfNotes.txt . Make sure to include the entire file path in the save directory, ex: C:\MyGameDir\BPSavedTextFiles */
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static bool FileIO__SaveStringTextToFile(FString SaveDirectory, FString JoyfulFileName, FString SaveText, bool AllowOverWriting = false, bool AllowAppend = false);

	UFUNCTION(BlueprintPure, Category = "SF_BPLibrary")
		static bool FileIO__GetFiles(TArray<FString>& Files, FString RootFolderFullPath, FString Ext);

	/** Takes in an Static Mesh Component and return an array of Vectors of all the vertices locations. Locations are in World Space. Returns: false if the operation could not occur. */
	UFUNCTION(BlueprintPure, Category = "SF_BPLibrary")
		static bool GetStaticMeshVertexLocations(UStaticMeshComponent* Comp, TArray<FVector>& VertexPositions, int32 LodIndex);

	/** Takes in an Skeletal Mesh Component and return an array of Vectors of all of the current bone locations and an array of corresponding bone name in each index. Locations are in World Space. Returns: false if the operation could not occur. */
	UFUNCTION(BlueprintPure, Category = "SF_BPLibrary")
		static bool GetSkeletalMeshBoneLocations(USkeletalMeshComponent* Comp, TArray<FVector>& BoneLocations, TArray<FName>& BoneNames);

	/** Takes in an Skeletal Mesh Component and return an array of Vectors of all the vertices locations. Locations are in World Space. Returns: false if the operation could not occur. */
	UFUNCTION(BlueprintPure, Category = "SF_BPLibrary")
		static bool GetSkeletalMeshVertexLocationsByLODIndex(USkeletalMeshComponent* Comp, int32 LODIndex, TArray<FVector>& VertexPositions);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static void MessageDialog(FText const Content);
	
	/** Set persistent level for world object. **/
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static bool SetLevel(UWorld* world, ULevel* level);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static UPhysicsAsset* GeneratePhysicsAsset(USkeletalMesh* SkeletalMesh, float MinBoneSize = 5.);

	/** Detect Occlusion from Camera. Return: hit_rate, self_occlusion_rate, inter_occlusion_rate **/
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static bool DetectOcclusionSkeletalMesh(
			USkeletalMeshComponent* Comp,
			ACameraActor* Camera,
			int32 LODIndex,
			bool bDebug,
			float& hit_rate,
			float& self_occlusion_rate,
			float& inter_occlusion_rate);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary")
		static bool GetSkeletalMeshValidFaceCentersByLODIndex(
			FRotator ActorRotator,
			FVector CameraForward,
			USkeletalMeshComponent* Comp,
			int32 LODIndex,
			TArray<FVector>& Centers);

	
	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary",
		meta = (AdvancedDisplay=5, WorldContext="WorldContext"))
	static void DivideSceneViaBoxTrace(
		const UObject* WorldContext,
		bool EnableTrace = true,
		int BoxHalfSize = 20,
		FVector StartPoint = FVector(0, 0, 2000),
		bool UseRandomStartPointXAndY = false,
		float MaxXExtend = 1500,
		float MinXExtend = -1500,
		float MaxYExtend = 1500,
		float MinYExtend = -1500,
		float HitEndZ = -2000,
		FString PathToSaveResults = TEXT("../HitBoxes.txt"),
		bool VisualizeBoxes = false);

	UFUNCTION(BlueprintPure, Category = "SF_BPLibrary",
		meta = (WorldContext="WorldContext"))
	static bool TestInside(
		const UObject* WorldContext, const FVector LocStart,
		const float Extend,	FHitResult& UpHitResult);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary",
		meta = (WorldContext="WorldContext"))
	static bool TestVisible(
		const UObject* WorldContext, const FVector TestLoc,
		const FVector CamLoc, FHitResult& OutHitResult);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary",
		meta = (AdvancedDisplay=4, WorldContext="WorldContext"))
	static void DivideSceneViaBoxTraceBatch(
		const UObject* WorldContext,
		TArray<FVector> StartPoints,
		bool EnableTrace = true,
		int BoxHalfSize = 20,
		float MaxXExtend = 1500,
		float MinXExtend = -1500,
		float MaxYExtend = 1500,
		float MinYExtend = -1500,
		float ZExtend = 2000,
		FString PathToSaveResults = TEXT("../HitBoxes.txt"),
		bool VisualizeBoxes = false);

	UFUNCTION(BlueprintCallable, Category = "SF_BPLibrary",
		meta = (WorldContext="WorldContext"))
	static bool GetCameraVisualCenterLocation(
		const UObject* WorldContext,
		const FVector CameraLoc, const FRotator CameraRot,
		FVector& CenterLoc,
		bool& bIsHit);

private:
	static void SaveTextToFile(
		const FString StringToWrite,
		FString PathToSave = TEXT("../HitBoxes.txt"));
};
