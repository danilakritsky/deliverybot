from enum import Enum


# inherit from str first to convert enum values to str automatically
# https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
class CommandReplies(str, Enum):
    START: str = "Welcome to <strong>our restaurant</strong>!"
    ABOUT: str = """
        <strong>About us.</strong>\n
        Established in 2022.
    """.replace(
        " " * 4, ""
    )
    HELP: str = """
        <strong>Bot usage</strong>\n
        <em>Making an order:</em>\n
        1. select a meal\n
        2. use + and - to change quantity\n
        3. use -&gt and &lt- to navigate your cart\n
        If you feel stuck use <pre>help</pre> button or enter the
        <pre>/help</pre> command.
    """.replace(
        " " * 4, ""
    )
