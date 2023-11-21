import unreal

@unreal.uenum()
class MyPythonEnum(unreal.EnumBase):
    FIRST = unreal.uvalue(0)
    SECOND = unreal.uvalue(1)
    FOURTH = unreal.uvalue(3)

@unreal.ustruct()
class PythonUnrealStruct(unreal.StructBase):
    some_string = unreal.uproperty(str)
    some_number = unreal.uproperty(float)
    array_of_string = unreal.uproperty(unreal.Array(str))

@unreal.uclass()
class PythonTestClass(unreal.BlueprintFunctionLibrary):

    @unreal.ufunction(static = True, params = [int], ret = PythonUnrealStruct)
    def MyPythonFunction(integer_argument1):
        struct = PythonUnrealStruct()
        struct.some_string = "5"
        struct.some_number = integer_argument1 + 1
        struct.array_of_string = ["a", "b", "c"]
        return struct
    
    @unreal.ufunction(static = True, params = [str], ret = bool)
    def MyPythonFunction2(string_argument1):
        print(string_argument1)
        return True