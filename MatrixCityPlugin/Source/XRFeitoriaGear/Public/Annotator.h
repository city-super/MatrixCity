// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Annotator.generated.h"

UENUM(BlueprintType)
enum class ECustomPPMType : uint8
{
	None,
	SemanticSegmentation,
	DepthMap,
	NormalMap,
	Roughtness,
	Specular,
	Tangent,
	OpticaFlow,
	Metallic,
	Diffuse,
	Basecolor,
	Custom
};


UCLASS()
class XRFEITORIAGEAR_API AAnnotator : public AActor
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Annotations|Stencil Value")
		bool bSignStencilValue = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Annotations|Stencil Value",
		meta = (EditCondition = "bSignStencilValue", EditConditionHides))
		bool bManualSignStencilValue = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Annotations|Stencil Value",
		meta = (EditCondition = "bManualSignStencilValue", EditConditionHides))
		TArray<AActor*> SegmentObjects;


	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Annotations")
		ECustomPPMType PreviewAnnotationType = ECustomPPMType::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Annotations", 
		meta = (EditCondition = "PreviewAnnotationType == ECustomPPMType::Custom", EditConditionHides))
		UMaterialInterface* CustomPostprocessMaterial;
	
public:	
	// Sets default values for this actor's properties
	AAnnotator();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

};
