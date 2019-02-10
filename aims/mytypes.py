from typing import Tuple, NamedTuple, List, Optional
import datetime as dt

class RosterEntry(NamedTuple):
    aims_day: str
    items: List[str]

class Crewmember(NamedTuple):
    name: str
    role: str

class Sector(NamedTuple):
    flightnum: str
    from_: str
    to: str
    sched_off: dt.datetime
    sched_on: dt.datetime
    off: Optional[dt.datetime]
    on: Optional[dt.datetime]
    reg: Optional[str]
    pax: bool
    crewlist: List[Crewmember]

class Duty(NamedTuple):
    on: dt.datetime
    off: dt.datetime
    text: str
    sectors: Optional[List[Sector]]

AimsSector = List[str]
AimsDuty = List[AimsSector]

class AIMSException(Exception):
    def __init__(self, str_: str ="") -> None:
        self.str_ = str_

class CaptchaOn(AIMSException):
    """CAPTCHA was found."""
    pass

class LogonError(AIMSException):
    """Logon failed."""
    pass

class BadBriefRoster(AIMSException):
    """Brief Roster parse failed."""

class BadTripDetails(AIMSException):
    """Error parsing trip details."""
    pass

class NoTripDetails(AIMSException):
    """AIMS unable to find trip details"""
    pass

class BadCrewList(AIMSException):
    """Crew list parse failed."""
    pass

class BadAIMSSector(AIMSException):
    """Failed to process AIMS sector"""
    pass

class BadAIMSDuty(AIMSException):
    """Failed to process AIMS duty"""
