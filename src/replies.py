from enum import Enum


# inherit from str first to convert enum values to str automatically
# https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
class CommandReplies(str, Enum):
    START: str = "Hello, <strong>World</strong>!"
