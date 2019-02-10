#!/usr/bin/python3

import unittest
import datetime
from pathlib import Path

from aims.mytypes import *
import aims.ical_format as ical_format

DT = datetime.datetime
here = Path(__file__).parent

class PatchedDatetime(datetime.datetime):

    @classmethod
    def utcnow(cls):
        return cls(2019, 1, 1)



class TestIcalFormat(unittest.TestCase):

    sectors = [
            Sector("1", "BRS", "NCL",
                   DT(2019, 1, 1, 8), DT(2019, 1, 1, 9),
                   DT(2019, 1, 1, 8), DT(2019, 1, 1, 9),
                   "G-TEST", pax=False, crewlist=[]),
            Sector("2", "NCL", "BRS",
                   DT(2019, 1, 1, 10), DT(2019, 1, 1, 11),
                   DT(2019, 1, 1, 10), DT(2019, 1, 1, 11),
                   "G-TEST", pax=False, crewlist=[]),
            Sector("3", "BRS", "NCL",
                   DT(2019, 1, 2, 8), DT(2019, 1, 2, 9),
                   DT(2019, 1, 2, 8), DT(2019, 1, 2, 9),
                   "G-TEST", pax=False, crewlist=[]),
            Sector("4", "NCL", "BRS",
                   DT(2019, 1, 2, 10), DT(2019, 1, 2, 11),
                   DT(2019, 1, 2, 10), DT(2019, 1, 2, 11),
                   "G-TEST", pax=False, crewlist=[]),
    ]

    duties_1 = [
            Duty(DT(2019, 1, 1, 7), DT(2019, 1, 1, 12), None, sectors[:2]),
            Duty(DT(2019, 1, 2, 7), DT(2019, 1, 2, 12), None, sectors[2:]),
    ]

    dict_1 = {
            '2019-01-01T07:00:00BRSNCLBRS@HURSTS.ORG.UK': {
                'start': '20190101T070000Z', 'end': '20190101T120000Z',
                'sectors': 'DESCRIPTION:08:00-09:00 1 BRS/NCL G-TEST\\n\r\n'
                ' 10:00-11:00 2 NCL/BRS G-TEST\r\n',
                'uid': '2019-01-01T07:00:00BRSNCLBRS@HURSTS.ORG.UK',
                'route': 'BRS-NCL-BRS',
                'modified': '20190101T000000Z', 'seq': '0', 'status': 'TENTATIVE'
            },
            '2019-01-02T07:00:00BRSNCLBRS@HURSTS.ORG.UK': {
                'start': '20190102T070000Z', 'end': '20190102T120000Z',
                'sectors': 'DESCRIPTION:08:00-09:00 3 BRS/NCL G-TEST\\n\r\n'
                ' 10:00-11:00 4 NCL/BRS G-TEST\r\n',
                'uid': '2019-01-02T07:00:00BRSNCLBRS@HURSTS.ORG.UK',
                'route': 'BRS-NCL-BRS', 'modified': '20190101T000000Z',
                'seq': '0', 'status': 'TENTATIVE'}}


    @classmethod
    def setUpClass(cls):
        cls.orig_datetime = datetime.datetime
        datetime.datetime = PatchedDatetime


    @classmethod
    def tearDownClass(cls):
        datetime.datetime = cls.orig_datetime


    def test_new_dict(self):
        result = ical_format.new_dict(self.duties_1)
        self.assertEqual(result, self.dict_1)


    def test_output(self):
        result = ical_format.output(self.dict_1)
        with open(here/"test-files/icaltest_1.ics", newline='') as f:
            expected_result = f.read()
        self.assertEqual(result, expected_result)


    def test_old_dict(self):
        result = ical_format.old_dict(here/"test-files/icaltest_1.ics")
        self.assertEqual(result, self.dict_1)


    def test_update_cancelled(self):
        test = self.dict_1.copy()
        del test['2019-01-01T07:00:00BRSNCLBRS@HURSTS.ORG.UK']
        result = ical_format.update(test, self.dict_1)
        expected_result = self.dict_1.copy()
        expected_result[
            '2019-01-01T07:00:00BRSNCLBRS@HURSTS.ORG.UK'][
                'status'] = "CANCELLED"
        expected_result[
            '2019-01-01T07:00:00BRSNCLBRS@HURSTS.ORG.UK'][
                'seq'] = "1"
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
