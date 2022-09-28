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
    HELP: str = "\n".join(
        [
            "<strong>Bot usage</strong>",
            "<em>Making an order:</em>",
            "1. select a meal",
            "2. use + and - to change quantity",
            "3. use -&gt and &lt- to navigate your cart",
            (
                "If you feel stuck use <pre>help</pre> button or enter the"
                "<pre>/help</pre> command."
            ),
        ]
    )
