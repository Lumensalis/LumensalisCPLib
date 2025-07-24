from typing import TypeVar

def GenericT[T](cls:T) -> T:  # pylint: disable=invalid-name
    T2 = TypeVar('T2' ) # type: ignore
    return cls[T2] # type: ignore