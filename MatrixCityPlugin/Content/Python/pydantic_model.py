import json
from typing import List, Tuple, Dict, Union
from pathlib import Path
from pydantic import BaseModel as PydanticBaseModel
from pydantic import validate_model


PathLike = Union[Path, str]
Tuple3 = Tuple[float, float, float]


class BaseModel(PydanticBaseModel):
    def check(self):
        """Call this method for manual validation."""
        *_, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error

    class Config:
        # allow_mutation = False
        # Automatically validate values for each assignment.
        validate_assignment = True
        # Forbid to use extra values who aren't defined in models.
        extra = 'forbid'

    def dump_json(self, path: PathLike) -> None:
        # validate before dump
        self.check()
        # dump json
        with open(path, 'w') as f:
            json.dump(self.dict(), f, indent=2, sort_keys=True)


class SequenceKey(BaseModel):
    frame: int
    location: Tuple3
    rotation: Tuple3