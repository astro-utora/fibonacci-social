from enum import Enum
from pydantic import BaseModel, ConfigDict

class StructuredMorphismType(Enum):
    Project = 0
    Edge = 1
    Decomposition = 2
    Substitution = 3
    Product = 4
    Coproduct = 5

class StructuredMorphism(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra = "allow")

    id: int
    type: StructuredMorphismType
    sourceId: int
    targetId: int
    content: str | None

class StructuredProjectViewType(Enum):
    Collapsed = 0
    Ports = 1
    Full = 2

class StructuredProject(StructuredMorphism):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    morphisms: list[StructuredMorphism]
    viewType: StructuredProjectViewType
    type: StructuredMorphismType = StructuredMorphismType.Project

class StructuredEdge(StructuredMorphism):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    type: StructuredMorphismType = StructuredMorphismType.Edge

class Composition(StructuredMorphism):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    subProject: StructuredProject

class HorizontalComposition(StructuredMorphism):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    subProjects: list[StructuredProject]

class Decomposition(Composition):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    type: StructuredMorphismType = StructuredMorphismType.Decomposition

class Substitution(Composition):
    model_config = ConfigDict(from_attributes=True, extra = "allow")
    type: StructuredMorphismType = StructuredMorphismType.Substitution

class Product(HorizontalComposition):
    type: StructuredMorphismType = StructuredMorphismType.Product

class Coproduct(HorizontalComposition):
    type: StructuredMorphismType = StructuredMorphismType.Coproduct
