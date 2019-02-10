# Overview #

This is a small command line program that accesses your account on the
easyJet AIMS server and outputs data in a number of hopefully useful
formats.

Your password is not stored anywhere; indeed it is expunged as soon as
it has been sent to the easyJet servers. The program is open source
(licenced under GPLv3), short and simple, so anyone with any
experience of the Python language can easily verify this.

# Audience #

If you are not an easyJet employee, you should probably stop reading
now.

This program is designed to be used as part of a workflow. It is
tightly focussed on retrieving data from the easyJet AIMS server and
presenting it in a selection of output formats that will be usable by
other software. Roster data is available in both an iCalendar and a
simple text format. Logbook data is presented in a simple batch format
that can be converted using [a logbook entry
generator](https://hursts.org.uk/logbook-entry-generator/index.html
"logbook entry generator") into three CSV files suitable for importing
into spreadsheets, databases or proprietary electronic logbooks,
assuming they have the facility. A JSON format provides easily
accessible data for most programming languages. Finally, a changes
format simply tells you whether you have red writing without even
having to open a browser.

You are not required to give anyone your authentication details so you
won't contravene company acceptable use policy in that regard, and it
won't continue if you have "red writing", so you don't have to worry
about accidentally accepting changes that you are not aware of. If you
are hoping to get details of roster changes without accepting them
through the normal company channels, this tool is not for you.

This is a command line interface (CLI) program. This means that it
must be run in a terminal emulator of some description on Linux and
Mac, and in the “Command Prompt” program on Windows. I do not intend
to give a tutorial on how to use CLI programs: there is plenty of
information on the Internet on the subject. If you are not comfortable
with the command line and do not feel that you could become so, this
tool is not for you.

If you are an easyJet IT manager and are about to get upset about yet
another third party app scraping data from AIMS, please spend a few
moments auditing the source code, which is licensed under GPLv3. You
should be able to quickly verify that handling of authentication
details is fully compliant with company policy. In terms of server
load, the interactions with the servers are much lighter than those of
a regular browser: it is accessing the same sequence of pages but is
not downloading any non-HTML resources. Significant effort has also
been made to cache duty data, so that in general it will be downloaded
once on roster publication and once after the duty has been completed.

# On brittleness #

This program was originally written to replace the slot in my workflow
that consisted of downloading the “Detailed Roster” and processing it
with other software, a workflow rendered non viable by the switch from
HTML to PDF.

Processing the “Detailed Roster” robustly was reasonably brittle,
since the format had to be reverse engineered and was subject to
change without notice, but at least it was just the one format. This
program uses the “Brief Roster”, the trip pages accessible from it by
selecting a link and clicking “Trip Details in UTC” and the crew
sheets available from that by clicking on sectors. It also has to deal
with all the Crew Portal pages involved in the single sign on
procedure. All of these have also had to be reverse engineered and all
of them are subject to change without notice. That makes this program
substantially more brittle. While every effort has been made to handle
errors gracefully, it is vital that any information is checked against
official sources before being used.

On top of all this, there is a possibility that permanent CAPTCHA or
multi-factor authentication will be deployed in order to prevent third
party apps accessing AIMS. Since this program is already acting in
almost exactly the same way as a user with a browser, in this
eventuality it should be possible to switch to driving an actual
Chromium based web browser to complete whatever authentication is
required. This is not guaranteed to be successful, however.

# On performance #

Scraping data in this manner is not a particularly efficient thing to
do. While the program is working it will output a `.` every time that
it accesses a file on the server. When processing a newly released
roster or subsequent to a block with a lot of sectors, a fair number
of files need to be accessed, and this can take a minute or
so. Subsequent visits to the same roster will be much quicker, since
trip details are cached.

In general, you will only be interested in the current and next
rosters. The `--past` and `--future` switches can be used to access
any other roster, but this is done by stepping through rosters (as you
have to in the Brief Roster on AIMS), and one file must be accessed
per step. Again this can be slightly slow.

# Installation #

There are two possible types of installation: installation via the
Python Package index (PyPI), available for any operating system, or,
on Windows only, installation of a self contained executable. The
reason Windows gets special treatment is that Linux users almost
certainly already have the requisite Python infrastructure in place,
allowing an installation of under 100KB. Windows users looking to
install from PyPI, on the other hand, are likely to need to manually
download and install a Python interpreter and do some manual
setup. The Windows executable bundles the Python interpreter, which
makes for a much simpler installation at the cost of a much larger
download. Mac users have Python pre-installed, but it is version 2.7
and this program runs under version 3.6 or newer. I don't have access
to a Mac to make an equivalent to the Windows executable, so you will
need to [read these
instructions](https://docs.python.org/3/using/mac.html) on python.org
to update to a suitably modern version.

Installation of the Windows executable does not give you access to the
source code, whereas installation via PyPI will let you audit it
before running. If you install the Windows executable, you are
implying sufficient trust in me to run arbitrary code on your machine.

## Self Contained Executable (Windows only) ##

Download [this zip file](https://hursts.org.uk/aimsextract/latest.zip
"Windows Executable") and unzip it. This will give you a file named
aims.exe.  Place this file somewhere that is accessible to your
system's PATH. Typing "path" at the command prompt will give you a list
of suitable directories. If in doubt, dropping it into `C:\Windows`
will probably work.

## From PyPI using pip (all OS) ##

You need a Python interpreter newer than version 3.6. This is likely
pre-installed on Linux. Many Linux distributions have both a version
2.x interpreter and a version 3.x interpreter installed: if this is
the case, replace `python` with `python3` and `pip` with `pip3` in the
instructions below. Windows users will likely need to download an
installer suitable for their version of Windows from
<https://python.org> (make sure you tick the “Add Python to PATH”
box).

Check your python version with:

`$ python --version`

If it is not 3.6 or newer, it will need to be updated.

Check that you have pip installed with:

`$ pip --version`

If you have not, you need to install it. This is most likely on Linux,
where you will find it in your distribution's repositories.

To install:

`$ pip install --user aims_extract`

# Usage #

## Example workflows ##

### Loading roster changes into Google Calendar ###

The evening before a standby, you decide to check for changes. Your
easyJet username is 001234:

Linux/Mac:

`$ aims changes 001234`

Windows:

`> aims.exe changes 001234`

You are asked for your password, which you type in. You get:

    Password:
    Connecting .............. Done
    Checking for changes . Done
    You have changes

You log onto AIMS to check what the changes are. It turns out that it
wasn't for tomorrow, it was for next month's roster. You want to
upload the changes to your Google Calendar, so you get yourself an
iCalendar file:

Linux/Mac:

`$ aims ical 001234 --future 1 -l 2019-02-r1.ical >2019-02-r2.ical`

Windows:

`> aims.exe ical 001234 --future 1 -l 2019-02-r1.ical >2019-02-r2.ical`

`2019-02-r1.ical` is the last iCalendar file that you uploaded to
Google calendar. By using the `-l` switch you add entries to the
iCalendar file that cancel entries in your Google Calendar that are
no longer valid. `>2019-02-r2.ical` causes output to be placed in a
file of this name rather than be output to the screen. Again you will
be asked for a password, and you will end up with:

    Password:
    Connecting .............. Done
    Checking for changes . Done
    Getting roster .. Done
    Processing roster  Done

The `2019-02-r2.ical` file is in your current directory. You open
Google Calendar and click the 3 vertical dots next to “Add calendar”
and choose “Import”. The ical file can now be uploaded and the result
checked against AIMS.

### Filling in your Google Sheets logbook after a block ###

Following a block of work, you decide to update your logbook:

Linux/Mac:

`$ aims logbook 001234 >logbook`

Windows:

`> aims.exe logbook 001234 >logbook`

You get:

    Password:
    Connecting .............. Done
    Checking for changes . Done
    Getting roster . Done
    Processing roster  Done

The file `logbook` is in your current directory. You go to
<https://hursts.org.uk> and open the Logbook Entry Generator. Using
the button on the left, you upload `logbook`, edit it as required then
click “Run Parser”. Three CSV blocks are generated. You copy the
sectors block and paste it into your Google Sheets spreadsheet.

## Documentation ##

    usage: aims [-h] [--future FUTURE] [--past PAST] [--quiet]
                [--last_ics LAST_ICS] [--force]
                {roster,logbook,ical,changes,json} username

    Access AIMS data from easyJet servers.

    positional arguments:
        {roster,logbook,ical,changes,json}
        username

    optional arguments:
        -h, --help            show this help message and exit
        --future FUTURE
        --past PAST
        --quiet, -q
        --last_ics LAST_ICS, -l LAST_ICS
        --force, -f

Windows users should replace `aims` with `aims.exe`.

There are 5 output formats:

1. **roster**: A simple text representation of a roster that includes
   total block and total duty times at the end of each duty string.

2. **logbook**: An intermediate logbook format that is designed to be
   easy to edit so that it can be processed into a final form by other
   tools. One such tool may be found at <https://hursts.org.uk>.

3. **ical**: An iCalendar file suitable for loading into many calendar
   programs including Google Calendar.

4. **changes**: Responds with either “No changes” or “You have
   changes”.

5. **json**: A JSON file suitable for loading and processing with
    other software.

By default, your current Brief Roster is used, i.e. the roster you get
if you access AIMS and click on “Crew Schedule - Brief”. There are
buttons marked “Previous period” and “Next period” on this page. The
`--past` switch is used with an integer (e.g. `--past 2`) which has
the same effect as clicking the “Previous period” button that number
of times. `--future` is the equivalent with the “Next period” button.

`--quiet` silences the progress and error messages.

`--last_ics` is used with the filename of the last iCalendar file that
was loaded into a calendar program. It has the effect of introducing
cancellation events where a duty that was previously uploaded is no
longer valid.

`--force` forces trips to be downloaded directly from AIMS rather than
loaded from cache.
