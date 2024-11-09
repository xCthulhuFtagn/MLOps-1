import errors_pb2 as _errors_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TrainRequest(_message.Message):
    __slots__ = ("modelClass", "hyperParams", "token")
    class HyperParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MODELCLASS_FIELD_NUMBER: _ClassVar[int]
    HYPERPARAMS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    modelClass: str
    hyperParams: _containers.ScalarMap[str, str]
    token: str
    def __init__(self, modelClass: _Optional[str] = ..., hyperParams: _Optional[_Mapping[str, str]] = ..., token: _Optional[str] = ...) -> None: ...

class TrainResponse(_message.Message):
    __slots__ = ("modelClass", "error")
    MODELCLASS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    modelClass: str
    error: _errors_pb2.Error
    def __init__(self, modelClass: _Optional[str] = ..., error: _Optional[_Union[_errors_pb2.Error, _Mapping]] = ...) -> None: ...

class ListAvailableModelsRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class ListAvailableModelsResponse(_message.Message):
    __slots__ = ("modelClasses", "error")
    MODELCLASSES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    modelClasses: _containers.RepeatedScalarFieldContainer[str]
    error: _errors_pb2.Error
    def __init__(self, modelClasses: _Optional[_Iterable[str]] = ..., error: _Optional[_Union[_errors_pb2.Error, _Mapping]] = ...) -> None: ...

class GetPredictionRequest(_message.Message):
    __slots__ = ("modelClass", "token", "fileData")
    MODELCLASS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    FILEDATA_FIELD_NUMBER: _ClassVar[int]
    modelClass: str
    token: str
    fileData: bytes
    def __init__(self, modelClass: _Optional[str] = ..., token: _Optional[str] = ..., fileData: _Optional[bytes] = ...) -> None: ...

class GetPredictionResponse(_message.Message):
    __slots__ = ("prediction", "error")
    PREDICTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    prediction: _containers.RepeatedScalarFieldContainer[float]
    error: _errors_pb2.Error
    def __init__(self, prediction: _Optional[_Iterable[float]] = ..., error: _Optional[_Union[_errors_pb2.Error, _Mapping]] = ...) -> None: ...
