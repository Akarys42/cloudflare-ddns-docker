import re

DURATION_REGEX = re.compile(
    r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
    r"((?P<hours>\d+?) ?(hours|hour|H|h) ?)?"
    r"((?P<minutes>\d+?) ?(minutes|minute|min|M|m) ?)?"
    r"((?P<seconds>\d+?) ?(seconds|second|sec|S|s))?"
)
UNIT_TO_SECONDS = {
    "days": 86400,
    "hours": 3600,
    "minutes": 60,
    "seconds": 1
}


def parse_duration(duration: str) -> int:
    """
    Parameter type for durations.

    The converter supports the following symbols for each unit of time:
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `M`, `m`, `minute`, `minutes`, `min`
        - seconds: `S`, `s`, `second`, `seconds`, `sec`
        The units need to be provided in descending order of magnitude.
    """
    match = DURATION_REGEX.fullmatch(duration)
    if not match:
        raise ValueError(f"{duration} isn't a valid duration.")

    duration = 0
    for unit, time_value in match.groupdict().items():
        if time_value:
            duration += int(time_value) * UNIT_TO_SECONDS[unit]

    return duration


def validate_bearer(bearer: str) -> None:
    ...
