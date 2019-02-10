#!/usr/bin/python3

from typing import Dict, List
from  aims.mytypes import *
import datetime as dt


vcalendar = """\
BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:hursts.org.uk\r
{}\r
END:VCALENDAR\r
"""

vevent = """\
BEGIN:VEVENT\r
UID:{uid}\r
DTSTAMP:{modified}\r
DTSTART:{start}\r
DTEND:{end}\r
SUMMARY:{route}\r
{sectors}\
LAST-MODIFIED:{modified}\r
SEQUENCE:{seq}\r
STATUS:{status}\r
END:VEVENT"""

ical_datetime = "{:%Y%m%dT%H%M%SZ}"


def output(event_dict: Dict[str, Dict[str, str]]) -> str:
    events = []
    for k in sorted(event_dict):
        events.append(vevent.format(**event_dict[k]))
    return vcalendar.format("\r\n".join(events))


def new_dict(dutylist: List[Duty]) -> Dict[str, Dict[str, str]]:
    events = {}
    for duty in dutylist:
        event = {}
        event["start"], event["end"] = [ical_datetime.format(X)
                                        for X in (duty.on, duty.off)]
        if not duty.sectors:
            event["route"] = str(duty.text)
            event["sectors"] = ""
            event["uid"] = "{}{}@HURSTS.ORG.UK".format(
                duty.on.isoformat(), str(duty.text))
        else:
            sector_strings = []
            airports = [duty.sectors[0].from_]
            for sector in duty.sectors:
                off, on = sector.sched_off, sector.sched_on
                if sector.off and sector.on:
                    off, on = sector.off, sector.on
                sector_strings.append(
                    "{:%H:%M}-{:%H:%M} {} {}/{} {}".format(
                        off, on, sector.flightnum,
                        sector.from_, sector.to,
                        sector.reg if sector.reg else ""))
                if sector.flightnum[0] == "[":#quasi sector
                    airports.append(sector.flightnum)
                if sector.pax:
                    airports.append("[psn]")
                airports.append(sector.to)
            event["sectors"] = "DESCRIPTION:{}\r\n".format(
                "\\n\r\n ".join(sector_strings))
            event["uid"] = "{}{}@HURSTS.ORG.UK".format(
                duty.on.isoformat(), "".join(airports))
            event["route"] = "-".join(airports)
        event["modified"] = ical_datetime.format(dt.datetime.utcnow())
        event["seq"] = "0"
        event["status"] = "TENTATIVE"
        events[event["uid"]] = event
    return events


def old_dict(filename: str) -> Dict[str, Dict[str, str]]:
    events = {}
    vevent_mapping = {
        "UID": "uid",
        "DTSTAMP": "modified",
        "DTSTART": "start",
        "DTEND": "end",
        "SUMMARY": "route",
        "DESCRIPTION": "sectors",
        "SEQUENCE": "seq",
        "STATUS": "status",
    }
    lines = [] #type: List[str]
    with open(filename, newline='') as f:
        #do "unfolding"
        for line in f:
            if line[0] == " ":
                lines[-1] += line
            else:
                lines.append(line)
        for line in lines:
            if ":" not in line: continue
            label, field = [X.strip() for X in line.split(":", 1)]
            if label == "BEGIN" and field == "VEVENT":
                cur_event = {}
            elif label in vevent_mapping:
                cur_event[vevent_mapping[label]] = field
            elif label == "END" and field == "VEVENT":
                if "sectors" not in cur_event:
                    cur_event["sectors"] = ""
                else:
                    cur_event["sectors"] = "DESCRIPTION:{}\r\n".format(
                        cur_event["sectors"])
                events[cur_event["uid"]] = cur_event
    return events


def update(new: Dict[str, Dict[str, str]],
           old: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, str]]:
    new_uids = set(new.keys())
    old_uids = set(old.keys())
    #if in old and not in new, add events with incremented sequence
    #and status set to "CANCELLED"
    cancel = old_uids - new_uids
    for uid in cancel:
        new[uid] = old[uid]
        new[uid]["status"] = "CANCELLED"
        new[uid]["seq"] = str(1 + int(old[uid]["seq"]))
        new[uid]["modified"] = ical_datetime.format(dt.datetime.utcnow())
    #if in both old and new, check whether data matches. If it does,
    #copy old sequence number and timestamp, if it doesn't increment
    #old sequence number.
    both = old_uids & new_uids
    for uid in both:
        #note: "start" and "route" are coded into UID
        for label in ("end", "sectors"):
            if new[uid][label] != old[uid][label]:
                new[uid]["seq"] = str(1 + int(old[uid]["seq"]))
                break
        else:
            new[uid]["seq"] = old[uid]["seq"]
            new[uid]["modified"] = old[uid]["modified"]
    return new


def dump(dutylist: List[Duty], ics_file: str = None) -> str:
    old = {} # type: Dict[str, Dict[str, str]]
    if ics_file:
        old = old_dict(ics_file)
    new = new_dict(dutylist)
    new = update(new, old)
    if not new:
        return "No changes"
    else:
        return output(new)
