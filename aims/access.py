#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup # type: ignore
from aims.mytypes import *
import sys

REQUEST_TIMEOUT=60

_session = requests.Session()
_aims_url = None

def fprint(str_: str) -> None:
    """Send str to stderr then immediately flush.

    Args:
        str: The string to send.
    """
    sys.stderr.write(str_)
    sys.stderr.flush()


def _check_response(r: requests.Response, *args, **kwargs) -> None:
    """Checks the response from a request; raises exceptions as required.
    """
    fprint(".")
    r.raise_for_status()


def connect(username:str, password:str) -> None:
    """Connects to AIMS server.

    Args:
        username: AIMS username (e.g. 001234)
        password: AIMS password

    Raises:
        requests.ConnectionError:
            A network problem occured.
        requests.HTTPError:
            Request returned unsuccessful status code.
        requests.Timeout:
            No response from server within REQUEST_TIMEOUT seconds.
        mytypes.CaptchaOn:
            Captcha was detected on the login page
        mytypes.LogonError:
            Logon failed

    This function mimics the sign on procedure that a web browser
    would carry out. The first step is to populate the session cookies
    by getting connected.easyjet.com. The password and username are
    then sent to authorise the session. If no CAPTCHA is in play, a
    SAML handshake takes place (something to do with single sign on I
    think) and finally the ecrew page is accessed. This is actually
    the "Please Wait" page, but accessing it auto logs on to AIMS
    meaning that session cookies and the base URL are sufficient to
    access any other AIMS page. These are stored on the global
    _session object and in the global _aims_url variable respectively.
    """
    global _session, _aims_url
    _session.hooks['response'].append(_check_response)
    _session.headers.update({
        "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) "
        "Gecko/20100101 Firefox/64.0"})
    fprint("Connecting ")
    r = _session.get("https://connected.easyjet.com")
    if r.text.find("g-recaptcha") != -1: raise CaptchaOn()
    r = _session.post("https://connected.easyjet.com/my.policy",
               {"username": username,
                "password": password,
                "vhost": "standard"},
                      timeout=REQUEST_TIMEOUT)
    del password #to help with auditing
    soup = BeautifulSoup(r.text, 'html.parser')
    url = soup.form.get("action", None)
    if not url: raise LogonError()
    saml_request = soup.input['value']
    r = _session.post(url, {"SAMLRequest": saml_request}, timeout=REQUEST_TIMEOUT)
    soup = BeautifulSoup(r.text, 'html.parser')
    url = soup.form["action"]
    saml_response = soup.input['value']
    r = _session.post(url, {"SAMLResponse": saml_response}, timeout=REQUEST_TIMEOUT)
    autologin_url = r.url + "cms/f5-h-$$/portal/cms/redirect/ecrew"
    r = _session.get(autologin_url, timeout=REQUEST_TIMEOUT)
    _aims_url = r.url.split("wtouch.exe")[0]
    # fix for session behaviour introduced by 2019-03-14 AIMS update
    if r.text.find("Please log out and try again.") != -1:
        _session.post(_aims_url + "perinfo.exe/AjAction?LOGOUT=1",
                      {"AjaxOperation": "0"}, timeout=REQUEST_TIMEOUT)
        r = _session.get(autologin_url, timeout=REQUEST_TIMEOUT)
        _aims_url = r.url.split("wtouch.exe")[0]
    fprint(" Done\n")


def get_brief_roster(offset: int = 0) -> str:
    """Downloads and returns the html of a  brief roster.

    Args:
        offset:
           The 'current' brief roster is offset 0. A positive integer
           steps forward that number of rosters. A negative integer
           similarly steps backwards.

    Returns:
        The raw html of the brief roster is returned as a string.

    Unfortunately, as far as I can tell the "brief roster"
    functionality of AIMS can only move from one roster to either the
    next or previous roster. This means if the absolute value of the
    offset is greater than 1, all intermediary rosters have to be
    downloaded. This makes the process of stepping to a distant roster
    very slow.
    """
    global _session, _aims_url
    assert _aims_url, "Must connect before calling get_brief_roster"
    fprint("Getting roster ")
    r = _session.post(_aims_url + "perinfo.exe/schedule",
               {
                   "eReferrer": "touchgo.europe.easyjet.local",
                   "_flagy": "2",
                   "DoVac": "0",
                   "Oper": "1",
                   "eCrewIsLockedDuetoPendingNotifs": "0",
               },
                      timeout=REQUEST_TIMEOUT)
    if offset:
        direc = "2" if offset > 0 else "1"
        for _ in range(abs(offset)):
            r = _session.post(_aims_url + "perinfo.exe/schedule",
                             {
                                 "Direc": direc,
                                 "FltInf": "0",
                                 "_flagy": "2",
                                 "OtherId": "0",
                                 "_NotOne": "0",
                                 "ORGDAY": "0",
                                 "DISPLAY_DAY": "0",
                                 "CROUTE": "0",
                                 "ground_code": "0",
                                 "trip_switch": "0",
                                 "rightClickArray": "0",
                             },
                              timeout=REQUEST_TIMEOUT)
    fprint(" Done\n")
    return r.text


def get_trip(aims_day: str, trip: str) -> str:
    """Downloads and returns the html of a trip sheet.

    Args:
        aims_day: The number of days since 1/1/1980 as a string.
        trip: The identifier that AIMS uses to define a trip. Usually a
        letter or two followed by three or four numbers.

    Returns:
        The html of an AIMS trip sheet. This is the sheet you get
        if you click a trip identifier on "Crew Schedule - Brief"
        (e.g. B089) then click the "Trip Details in UTC button".
    """
    global _session, _aims_url
    assert _aims_url, "Must connect before calling get_trip."
    r = _session.get(_aims_url + "perinfo.exe/schedule",
                    params={
                        "FltInf": "1",
                        "ORGDAY": aims_day,
                        "CROUTE": trip,
                    },
                     timeout=REQUEST_TIMEOUT)
    return r.text


def get_crewlist(id_: str) -> str:
    """Downloads and returns the html of a crewlist.

    Args:
        id_: The id attribute of the <tr> containing the details of a
            sector on an AIMS trip sheet. It looks something like:

            '14262,138549409849,14262,401,brs,1, ,gla,320'

    Returns:
        The HTML of a crew sheet. This is the page you get when you
        click a sector on an AIMS duty sheet.
    """
    global _session, _aims_url
    assert _aims_url, "Must connect before calling get_crewlist."
    r = _session.get(_aims_url + "perinfo.exe/getlegmem",
                    params={
                        "LegInfo": id_,
                    },
                     timeout=REQUEST_TIMEOUT)
    return r.text


def get_index_page() -> str:
    """Downloads and returns the AIMS index page.

    The AIMS index page is of interest because it is where "red
    writing" occurs.

    Args: None

    Returns:
        The HTML of the AIMS index page.
    """
    global _session, _aims_url
    assert _aims_url, "Must connect before calling get_index_page."
    r = _session.get(_aims_url + "perinfo.exe/index", timeout=REQUEST_TIMEOUT)
    return r.text
