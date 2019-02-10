#!/usr/bin/python3

import datetime
import unittest
from pathlib import Path

import aims.access
import aims.parse
from aims.mytypes import *

here = Path(__file__).parent

class TestBriefRosterParsing(unittest.TestCase):

    def test_brief_roster_parse(self):
        data = """\
<html><head></head><body><div id="main_div">

<div id="myday_14146"><table class="duties_table">
<tr><td>CSBE</td><td>3:00</td></tr>
<tr><td>&nbsp;</td><td>5:00</td></tr>
<tr><td>B006D</td><td></td></tr>
</table></div>

<div id="myday_14147"><table class="duties_table">
<tr><td>B086</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
</table></div>

<div id="myday_14150"><table class="duties_table">
<tr><td>D/O</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
</table></div>

<div id="myday_14153"><table class="duties_table">
<tr><td>LVE</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
</table></div>

<div id="myday_14157"><table class="duties_table">
<tr><td>==&gt;</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
<tr><td>B253</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
</table></div>

<div id="myday_14162"><table class="duties_table">
<tr><td>ADTY</td><td>5:00</td></tr>
<tr><td>&nbsp;</td><td>11:00</td></tr>
</table></div>

<div id="myday_14174"><table class="duties_table">
<tr><td>FTGD</td><td></td></tr>
</table></div>

<div id="myday_13869"><table class="duties_table">
<tr><td>FIRE</td><td>8:00</td></tr>
<tr><td>&nbsp;</td><td>9:30</td></tr>
<tr><td>DOOR</td><td>9:30</td></tr>
<tr><td>&nbsp;</td><td>10:45</td></tr>
<tr><td>G/S</td><td>10:45</td></tr>
<tr><td>&nbsp;</td><td>11:30</td></tr>
<tr><td>ASEC</td><td>11:30</td></tr>
<tr><td>&nbsp;</td><td>13:00</td></tr>
<tr><td>CRM</td><td>13:00</td></tr>
<tr><td>&nbsp;</td><td>14:00</td></tr>
<tr><td>SEP</td><td>14:00</td></tr>
<tr><td>&nbsp;</td><td>16:00</td></tr>
<tr><td>89</td><td></td></tr>
<tr><td>&nbsp;</td><td></td></tr>
</table></div>

<div id="myday_14036"><table class="duties_table">
<tr><td>B001T</td><td></td></tr>
<tr><td>&nbsp;6</td><td></td></tr>
</table></div>

</div></body></html>
"""
        entries = aims.parse.parse_brief_roster(data)
        self.assertEqual(entries, [
            RosterEntry(aims_day='14146',
                        items=['CSBE', '3:00', '5:00', 'B006D']),
            RosterEntry(aims_day='14147', items=['B086']),
            RosterEntry(aims_day='14150', items=['D/O']),
            RosterEntry(aims_day='14153', items=['LVE']),
            RosterEntry(aims_day='14157', items=['==>', 'B253']),
            RosterEntry(aims_day='14162', items=['ADTY', '5:00', '11:00']),
            RosterEntry(aims_day='14174', items=['FTGD']),
            RosterEntry(aims_day='13869',
                        items = ['FIRE', '8:00', '9:30',
                                 'DOOR', '9:30', '10:45',
                                 'G/S', '10:45', '11:30',
                                 'ASEC', '11:30', '13:00',
                                 'CRM', '13:00', '14:00',
                                 'SEP', '14:00', '16:00',
                                 '89']),
            RosterEntry(aims_day='14036', items=['B001T', '6']),
            ])


    def test_bad_brief_roster(self):
        data = "<html><head></head><body><p>No main div</p></body></html>"
        with self.assertRaises(BadBriefRoster) as cm:
            aims.parse.parse_brief_roster(data)
        data = ("<html><head></head><body><div id='main_div'>"
                "No class=duties_tables tables</div></body></html>")
        with self.assertRaises(BadBriefRoster) as cm:
            aims.parse.parse_brief_roster(data)
        data = "Not even HTML"
        with self.assertRaises(BadBriefRoster) as cm:
            aims.parse.parse_brief_roster(data)


class TestTripParsing(unittest.TestCase):

    def test_trip_parsing(self):
        html = "<html><body><table>{}</table><body></html>".format("""\
<tr class="mono_rows_ctrl_f3">
<td>LSBY BRS BRS 0600 0910 Fri18Jan 1 09:10 09:10 06:00 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14262,138549409849,14262,401,brs,1, ,gla,320">
<td>401  BRS GLA 0855 1010 A0900 A1009 OE-IVK 1:09 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14262,138549409849,14262,402,gla,1, ,brs,320">
<td>402 GLA BRS 1035 1145 A1040 A1145 OE-IVK 1:05 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14262,138549409849,14262,6085,brs,1, ,bsl,320">
<td>6085 BRS BSL 1215 1350 A1216 A1356 OE-IVK 1:40 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14262,138549409849,14262,6086,bsl,1, ,brs,320">
<td>6086 BSL BRS 1415 1600 A1425 A1603 OE-IVK 1:38 16:03 16:03 16:33 </td></tr>""")
        dutylist = aims.parse.parse_trip_details(html)
        self.assertEqual(dutylist, [
            [
                [None,
                 'LSBY', 'BRS', 'BRS', '0600', '0910', 'Fri18Jan', '1',
                 '09:10', '09:10', '06:00'],
                ['14262,138549409849,14262,401,brs,1, ,gla,320',
                 '401', 'BRS', 'GLA', '0855', '1010',
                 'A0900', 'A1009', 'OE-IVK', '1:09'],
                ['14262,138549409849,14262,402,gla,1, ,brs,320',
                 '402', 'GLA', 'BRS', '1035', '1145',
                 'A1040', 'A1145', 'OE-IVK', '1:05'],
                ['14262,138549409849,14262,6085,brs,1, ,bsl,320',
                 '6085', 'BRS', 'BSL', '1215', '1350',
                 'A1216', 'A1356', 'OE-IVK', '1:40'],
                ['14262,138549409849,14262,6086,bsl,1, ,brs,320',
                 '6086', 'BSL', 'BRS', '1415', '1600',
                 'A1425', 'A1603', 'OE-IVK', '1:38',
                 '16:03', '16:03', '16:33']]])


    def test_trip_parsing_mulitday(self):
        data = """\
<html><body><table>
<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14293,209,brs,8, ,lgw,">
<td>TAXI209 BRS LGW 0435 0820 Mon18Feb 1 PAX 4:35 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14293,8495,lgw,1, ,opo,319">
<td>8495 LGW OPO 0935 1200 PAX G-EZBC 12:15 </td></tr>

<tr class="sub_table_header_blue_courier">
<td> 17:00 Rest OPERATIONAL HOTEL 7:40 </td></tr>
<tr class="sub_table_header_blue_courier">
<td> (18/02/19 12:35) </td></tr>

<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14294,7585,opo,1, ,fnc,320">
<td>7585 OPO FNC 0615 0820 Tue19Feb 2 G-UZHP 2:05 5:15 5:15 5:15 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14294,7586,fnc,1, ,opo,320">
<td>7586 FNC OPO 0850 1050 G-UZHP 2:00 10:50 10:50 11:20 </td></tr>

<tr class="sub_table_header_blue_courier">
<td> 24:15 Rest OPERATIONAL HOTEL 4:05 OPO B 5:35 10:45 6:05 </td></tr>
<tr class="sub_table_header_blue_courier">
<td> (19/02/19 11:40) </td></tr>

<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14295,8496,opo,1, ,lgw,319">
<td>8496 OPO LGW 1235 1450 Wed20Feb 3 PAX G-EZDL 11:35 </td></tr>
<tr class="mono_rows_ctrl_f3" id="14293,353365012537,14295,209,lgw,8, ,brs,">
<td>TAXI209 LGW BRS 1505 1805 PAX 18:05 </td></tr>
</table></body></html>
"""
        dutylist = aims.parse.parse_trip_details(data)
        self.assertEqual(dutylist, [
            [
                ['14293,353365012537,14293,209,brs,8, ,lgw,',
                 'TAXI209', 'BRS', 'LGW', '0435', '0820', 'Mon18Feb', '1',
                 'PAX', '4:35'],
                ['14293,353365012537,14293,8495,lgw,1, ,opo,319',
                 '8495', 'LGW', 'OPO', '0935', '1200',
                 'PAX', 'G-EZBC', '12:15']
            ],
            [
                ['14293,353365012537,14294,7585,opo,1, ,fnc,320',
                 '7585', 'OPO', 'FNC', '0615', '0820', 'Tue19Feb', '2',
                 'G-UZHP', '2:05', '5:15', '5:15', '5:15'],
                ['14293,353365012537,14294,7586,fnc,1, ,opo,320',
                 '7586', 'FNC', 'OPO', '0850', '1050',
                 'G-UZHP', '2:00', '10:50', '10:50', '11:20']
            ],
            [
                ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                 '8496', 'OPO', 'LGW', '1235', '1450', 'Wed20Feb', '3',
                 'PAX', 'G-EZDL', '11:35'],
                ['14293,353365012537,14295,209,lgw,8, ,brs,',
                 'TAXI209', 'LGW', 'BRS', '1505', '1805',
                 'PAX', '18:05']
            ]])


    def test_bad_trip_details(self):
        with self.assertRaises(BadTripDetails) as cm:
            aims.parse.parse_trip_details("Not even html")
        self.assertEqual(cm.exception.str_,
                         "tr.mono_rows_ctrl_f3 not found")
        with self.assertRaises(BadTripDetails) as cm:
            aims.parse.parse_trip_details(
                "<html><body>"
                "<table><tr><td>Not right</td></tr></table>"
                "</body></html>")


class TestCrewParsing(unittest.TestCase):

    def test_basic_crewlist(self):
        data = """\
<html><body><table>
<tr class="sub_table_header">
<td>ID</td><td>Name</td><td>Seniority</td><td>Base</td><td>AC</td>
<td>Pos</td><td>Trn Duty</td><td>Trip</td><td>PAX</td></tr>

<tr class="dual_rows"><td>9448</td><td>HURST JONATHAN SR</td><td></td>
<td>BRS</td><td>320</td><td>CP</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="mono_rows"><td>860579</td><td>WHITEHEAD MATTHEW</td><td></td>
<td>BRS</td><td>320</td><td>FO</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="dual_rows"><td>821015</td><td>SIMS GEORGIA</td><td></td>
<td>BRS</td><td>320</td><td>PU</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="mono_rows"><td>824591</td><td>WHITE SAMANTHA</td><td></td>
<td>BRS</td><td>320</td><td>FA</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="dual_rows"><td>830411</td><td>BANFIELD WENDY</td><td></td>
<td>BRS</td><td>320</td><td>FA</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="mono_rows"><td>820596</td><td>SALT BEVERLY</td><td></td>
<td>BRS</td><td>320</td><td>FA</td><td>&nbsp;</td><td>B036</td><td>&nbsp;</td></tr>
</tr><tr class="dual_rows"><td>820596</td><td>POSITIONER IAMA</td><td></td>
<td>BRS</td><td>320</td><td>FA</td><td>&nbsp;</td><td>B036</td><td>*</td></tr>
</tr></table>
</body></html>
"""
        crewlist = aims.parse.parse_crewlist(data)
        self.assertEqual(
            crewlist,
            [
                Crewmember(name='Hurst Jonathan Sr', role='CP'),
                Crewmember(name='Whitehead Matthew', role='FO'),
                Crewmember(name='Sims Georgia', role='PU'),
                Crewmember(name='White Samantha', role='FA'),
                Crewmember(name='Banfield Wendy', role='FA'),
                Crewmember(name='Salt Beverly', role='FA')])


    def test_bad_crewlist(self):
        with self.assertRaises(BadCrewList):
            aims.parse.parse_crewlist("Not HTML")
        with self.assertRaises(BadCrewList):
            aims.parse.parse_crewlist(
                "<html><body><p>Not crewlist</p></body></html>")


if __name__ == '__main__':
    unittest.main()
