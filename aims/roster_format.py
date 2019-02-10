from typing import List
from  aims.mytypes import *
import datetime as dt
import re
from dateutil import tz

def dump(dutylist: List[Duty]) -> str:
    dutylist.sort()
    output = []
    for duty in dutylist:
        start, end = [X.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
                      for X in (duty.on, duty.off)]
        duration = int((end - start).total_seconds()) // 60
        if duty.sectors:
            airports = [duty.sectors[0].from_]
            block = 0
            for sector in duty.sectors:
                if sector.flightnum[0] == "[":#quasi sector
                    airports.append(sector.flightnum.lower())
                elif sector.pax:
                    airports.append("[psn]")
                else:
                    off, on = sector.sched_off, sector.sched_on
                    if sector.on and sector.off:
                        off, on = sector.off, sector.on
                    block += int((on - off).total_seconds()) // 60
                airports.append(sector.to)
            output.append("{:%d/%m/%Y %H:%M}-{:%H:%M} {} {:d}:{:02d}/{:d}:{:02d}".format(
                    start, end, "-".join(airports),
                    block // 60, block % 60,
                    duration // 60, duration % 60))
        else:
            output.append("{:%d/%m/%Y %H:%M}-{:%H:%M} {} 0:00/{:d}:{:02d}".format(
                start, end, duty.text, duration // 60, duration % 60))
    return "\n".join(output)
