from aims.mytypes import *
from bs4 import BeautifulSoup # type: ignore
import re
import aims.access


def parse_brief_roster(html: str) -> List[RosterEntry]:
    """Convert an HTML brief roster to a list of roster entries.

    Args:
        html: The HTML of an AIMS Brief Roster

    Returns:
        A list of RosterEntry objects. A RosterEntry object is a tuple
        consisting of an aims_day and a list of strings. An aims_day
        is an integer representing the number of elapsed days since
        1st January 1980 that is used internally by AIMS. The list of
        strings is the strings that AIMS allocated to that day of the
        brief roster in reading order.

    There appear to be four categories of strings published on an
    AIMS brief roster:

    1. Strings indicating some form of day off. These include D/O,
    D/OR, WD/O, LVE, P/T, REST, FTGD and SICK. There may be others.

    2. Strings indicating some form of standby ot training duty. These
    can be identified as a group of three strings, the latter two of
    which are times in the form h:mm or hh:mm.

    3. A single digit number. These seem to be associated with long
    duties that have additional rest limitations associated with them.

    4. Trip identifiers and continuation markers. A trip identifier is
    a string consisting of a mix of letters and numbers. They seem to
    generally be a letter or two, some numbers and maybe another
    letter, but I have come across trip identifiers that are just two
    digit numbers. It is easiest to identify them as strings that do
    not belong to any of the other groups, although not having a
    guaranteed complete set of category 1 strings complicates
    this. Continuation markers are "==>", indicating that the previous
    day's trip crosses midnight.

    """
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", id="main_div")
    if not main_div: raise BadBriefRoster
    duties_tables = main_div.find_all("table", class_="duties_table")
    if not duties_tables: raise BadBriefRoster
    roster_entries: List[RosterEntry] = []
    for table in duties_tables:
        roster_entries.append(RosterEntry(
            table.parent["id"].replace("myday_", ""),
            [X for X in table.stripped_strings]))
    return roster_entries


def parse_trip_details(html:str) -> List[AimsDuty]:
    """Parse trip details out of a AIMS trip sheet.

    Args:
        html: The HTML of an AIMS trip sheet

    Returns:
        List[AimsDuty]:

        An AimsDuty is a list of AimsSectors. An AimsSector is a list of
        strings found in an AIMS trip sheet. The first six fields always
        exist. They are:

        [0]: Sector identifier (used as input to find crew list)
        [1]: Flight number
        [2]: Departure aerodrome (3 letter code)
        [3]: Arrival aerodrome (3 letter code)
        [4]: Scheduled departure time (HHMM format) in UTC
        [5]: Scheduled arrival time (HHMM format) in UTC

        Field 0 may be None in the case that a standby duty occurred
        before a flight duty, and the standby duty got included on the
        trip sheet as a quasi sector.

        The last field of the last AimsSector is the AimsDuty end
        time. If there is more than one sector, the last field of the
        first sector is the AimsDuty start time. If there is only one
        sector it is the second to last field.

        Other fields of interest occur in the following order, although
        their exact position is not defined:

        [?]: Trip day number (single digit)
        [?]: Actual departure time (Adddd where dddd are digits)
        [?]: Actual arrival time (Adddd where dddd are digits)
        [?]: Tail number. Either XX-XXX or X-XXXX where X are capital
        letters. This may change in the future, although it is likely that
        there will still be a dash either as the 2nd or 3rd character.

        Other fields that are not of interest will be in the mix. They
        mostly have the form HH:MM, although the departure date is of the
        form Fri18Jan.

    """
    if html.find("Unable to find the trip details") != -1:
        raise NoTripDetails
    soup = BeautifulSoup(html, "html.parser")
    first_sector = soup.find("tr", class_="mono_rows_ctrl_f3")
    if not first_sector:
        raise BadTripDetails("tr.mono_rows_ctrl_f3 not found")
    id_ = first_sector.get("id", None)
    aims_sector = [id_] + first_sector.text.split()
    aims_duty = [aims_sector] #type: AimsDuty
    aims_duties = [aims_duty]
    for sibling in first_sector.find_next_siblings("tr"):
        if "mono_rows_ctrl_f3" in sibling["class"]:
            id_ = sibling.get("id", None)
            sector = [id_] + sibling.text.split()
            if len(sector) < 6: #gross error check
                raise BadTripDetails(sibling.text)
            aims_duty.append(sector)
        elif aims_duty != []:
            aims_duty = []
            aims_duties.append(aims_duty)
    if aims_duties[-1] == []: del aims_duties[-1]
    return aims_duties


def parse_crewlist(html: str) -> List[Crewmember]:
    """Convert an AIMS HTML crew list into a crew list.

    Args:
        html: The HTML of the AIMS crew list.

    Returns:
        A list of Crewmember objects. A Crewmember object is a named
        tuple consisting of a name and a role.
    """
    html = html.replace("\n</tr><tr class=", "\n<tr class=") #fix buggy html
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("tr", class_="sub_table_header")
    if not header:
        raise BadCrewList
    crewlist = []
    for sibling in header.find_next_siblings("tr"):
        crew_strings = [X.text for X in sibling.find_all("td")]
        if crew_strings[8] == "*": continue #ignore positioning crew
        crewlist.append(Crewmember(crew_strings[1].title(), crew_strings[5]))
    return crewlist
