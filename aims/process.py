import re
import os
import pickle
import datetime as dt

from aims.mytypes import *
from aims import access, parse

CACHE_DIRECTORY = os.path.expanduser("~/.cache")
CACHE_FILE = os.path.join(CACHE_DIRECTORY, "aims.pickle.v1")

def get_cache() -> dict:
    try:
        os.mkdir(CACHE_DIRECTORY)
    except FileExistsError:
        pass
    try:
        with open(CACHE_FILE, "rb") as cachefile:
            return pickle.load(cachefile)
    except OSError:
        return {"trips": {}}


def save_cache(dict_: dict) -> None:
    with open(CACHE_FILE, "wb") as cachefile:
        pickle.dump(dict_, cachefile)


def process_roster_entries(entries: List[RosterEntry], force: bool = False
) -> List[Duty]:
    """Convert a list of RosterEntry objects into a list of Duty objects.

    Args:
        entries: A list of RosterEntry objects.
        force: Force cache update

    Returns:
        A list of Duty objects. There may be multiple Duty objects
        associated with each RosterEntry.
    """
    duty_list = []
    trip_cache = get_cache()
    access.fprint("Processing roster ")
    for entry in entries:
        date = (dt.datetime(1980, 1, 1) +
                dt.timedelta(int(entry.aims_day))).date()
        while len(entry.items):
            p = entry.items.pop()
            if p in ("==>", "D/O", "D/OR", "WD/O", "P/T",
                     "LVE", "FTGD", "REST", "SICK"):
                continue
            elif len(p) >= 4 and p[-3] == ":":
                end_time = dt.datetime.strptime(p, "%H:%M").time()
                start_time = dt.datetime.strptime(entry.items.pop(), "%H:%M").time()
                text = entry.items.pop()
                start, end = [dt.datetime.combine(date, X)
                              for X in (start_time, end_time)]
                if end < start:
                    end += dt.timedelta(days=1)
                duty_list.append(Duty(start, end, text, None))
            else:
                try:
                    duties = get_trip_duties(entry.aims_day, p, date, trip_cache, force)
                    duty_list.extend(duties)
                except AIMSException as e:
                    access.fprint("\nError while processing {} on {}\n".format(
                        p, entry.aims_day))
                    access.fprint("{} {}\n".format(e.__doc__, e.str_))
    access.fprint(" Done\n")
    save_cache(trip_cache)
    #AIMS sometimes records duties with times in the detailed roster,
    #then adds a trip that records the same duties. Since we're
    #popping duties off a stack, this means that duties that are
    #wholly contained by the previous filtered duty should be dropped.
    filtered_dutylist = []
    if duty_list:
        filtered_dutylist.append(duty_list[0])
        for duty in duty_list[1:]:
            last_duty = filtered_dutylist[-1]
            if duty.on < last_duty.on or duty.off > last_duty.off:
                filtered_dutylist.append(duty)
    return filtered_dutylist


def get_trip_duties(aims_day: str,
                    trip_id: str,
                    date: dt.date,
                    cache: dict,
                    force: bool = False
) -> List[Duty]:
    """Given a date and tripid, return a list of Duty objects.

    Args:
        aims_day: A date in the form of the number of days since 1st
            Jan 1980.
        trip_id: An AIMS trip identifier (e.g. B1234s)
        date: aims_day converted to a date object
        cache: A dictionary with a "trips" key that a dutylist can be
            cached in.
        force: If True, do not load trip details from cache

    Returns:
        A list of Duty objects.

    This function also handles caching of the duties associated with trips.
    """
    cache_key = (date, trip_id)
    duty_list = []
    cached_duties = cache["trips"].get(cache_key)
    if force or _requires_update(cached_duties):
        html = access.get_trip(aims_day, trip_id)
        try:
            aims_duties = parse.parse_trip_details(html)
            duties = [process_aims_duty(X, date, trip_id)
                      for X in aims_duties]
            duty_list.extend(duties)
            cache["trips"][cache_key] = duties
        except NoTripDetails:
            #if we get here, we tried to find a trip that
            #didn't exist. That probably means that our
            #list of day off codes is incomplete. Ho hum.
            access.fprint("\nNo trip details for {}:{}\n".format(
                aims_day, trip_id))
    else:
        duty_list.extend(cache["trips"][cache_key])
    return duty_list


def _requires_update(duties: Optional[List[Duty]]) -> bool:
    """Check whether cached duties are valid.

    Args:
        duties: The list of duties to check. Can be None.

    Returns:
        True if the duties require updating, otherwise False.
    """
    if not duties: return True
    now = dt.datetime.utcnow()
    for duty in duties:
        if not duty.sectors: continue
        for sector in duty.sectors:
            is_final = ((sector.off and sector.on) #have actual times
                or (sector.pax and not sector.reg) #ground positioning
                or (sector.flightnum[0] == "["))  #quasi sector
            if not is_final and duty.on < now:
                return True
    return False


def process_aims_duty(
        aims_duty: List[AimsSector],
        start_date: dt.date,
        trip_id: str
) -> Duty:
    """Create a Duty object from a list of AimsSector objects.

    Args:
        aims_duty: A list of AimsSector objects, as described in the
            parse.parse_trip_details() documentation.
        start_date: The date of the duty.
        trip_id: The id of the trip that the duty belongs to.

    Returns:
        A Duty object.
    """
    try:
        trip_day = int(aims_duty[0][7]) - 1
        date = start_date + dt.timedelta(days=trip_day)
        duty_end_time = dt.datetime.strptime(aims_duty[-1][-1], "%H:%M").time()
        index = -2 if len(aims_duty) == 1 else -1
        duty_start_time = dt.datetime.strptime(aims_duty[0][index], "%H:%M").time()
    except:
        raise BadAIMSDuty(str(aims_duty))
    assert type(start_date) == dt.date
    duty_start, duty_end = (
        dt.datetime.combine(date, X)
        for X in (duty_start_time, duty_end_time))
    if duty_end < duty_start:
        duty_end += dt.timedelta(days=1)
    sectors = [] # type: List[Sector]
    for aims_sector in aims_duty:
        sectors.append(process_aims_sector(aims_sector, date))
    return Duty(duty_start, duty_end, trip_id, sectors)


def process_aims_sector(aims_sector: AimsSector, date: dt.date
) -> Sector:
    """Convert an AimsSector object into a Sector object.

    Args:
        aims_sector: An AimsSector object, as described in the
            documentation for parse.parse_trip_details().

    Returns:
        A Sector object.

    Standby and training duties that form part of a trip are recorded
    by AIMS as quasi-sectors. A quasi-sector is identified by its
    flight number being wrapped in square brackets, e.g. [esby]. AIMS
    does not update quasi-sectors with actual times.

    The pax flag indicates a postioning sector. If reg is None, it is
    ground positioning. AIMS does not update ground positioning
    sectors with actual times.

    Accessing AIMS crew member details is relatively slow and the
    planned crew for a sector tends to be in a continuous state of
    flux. Therefore, the crewlist field is only filled for sectors in
    the past; future sectors have an empty list.
    """
    try:
        id_, flightnum, from_, to, sched_off, sched_on = aims_sector[:6]
    except:
        raise BadAIMSSector(str(aims_sector))
    off, on, reg = (None,) * 3
    pax = False
    for field in aims_sector[6:]:
        if re.match(r"A\d{4}", field):
            if not off:
                off = field[1:]
            else:
                on = field[1:]
        elif re.match(r"\w{1,2}-\w{3,5}", field):
            reg = field
        elif field == "PAX":
            pax = True
    try:
        sched_off, sched_on = (X + "+0" if len(X) == 4 else X
                               for X in (sched_off, sched_on))
        sched_off_t, sched_on_t = (dt.datetime.strptime(X[:4], "%H%M").time()
                                   for X in (sched_off, sched_on))
        sched_off_dt = (dt.datetime.combine(date, sched_off_t)
                        + dt.timedelta(days=int(sched_off[5])))
        sched_on_dt = (dt.datetime.combine(date, sched_on_t)
                       + dt.timedelta(days=int(sched_on[5])))
        #actual times don't have +1 for after midnight, so use proximity to schedule
        off_dt, on_dt = None, None
        if on:
            off_t, on_t = (dt.datetime.strptime(X[:4], "%H%M").time()
                           for X in (off, on))
            off_dt, on_dt = (dt.datetime.combine(date, X)
                             for X in (off_t, on_t))
            if sched_off_dt - off_dt > dt.timedelta(days=1) / 2:
                off_dt += dt.timedelta(days=1)
            if sched_on_dt - on_dt > dt.timedelta(days=1) / 2:
                on_dt += dt.timedelta(days=1)
    except:
        raise BadAIMSSector(str(date) + ", " + str(aims_sector))
    #only get crewlist if we have actual times and were not positioning
    crewlist: List[Crewmember] = []
    if on and not pax:
        html = access.get_crewlist(id_)
        crewlist = parse.parse_crewlist(html)
    if not id_: #quasi sector
        flightnum = "[{}]".format(flightnum)
    return Sector(flightnum, from_, to, sched_off_dt, sched_on_dt,
                  off_dt, on_dt, reg, pax, crewlist)
