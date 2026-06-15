from pydantic import BaseModel


class Parameter(BaseModel):
    type: str


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Parameter]
    returns: Parameter


class PromptTest(BaseModel):
    prompt: str
