from django.utils import termcolors


def colorize(value: str, is_warning: bool) -> str:
    if is_warning:
        return termcolors.make_style(fg="yellow")(value)
    return value
