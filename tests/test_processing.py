#!/usr/bin/python3

import unittest
import datetime
import os
import pickle

from aims.mytypes import *
import aims.access as access
import aims.parse as parse
import aims.process as process


class TestBriefRosterProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_get_trip_duties = process.get_trip_duties
        process.get_trip_duties = cls.get_trip_duties_patch


    @classmethod
    def tearDownClass(cls):
        process.get_trip_duties = cls.orig_get_trip_duties


    @staticmethod
    def get_trip_duties_patch(aims_day: str,
                    trip_id: str,
                    date: datetime.date,
                    cache: dict) -> List[Duty]:
        if aims_day == '14158' and trip_id == '89':
            return [Duty(datetime.datetime.combine(date, dt.time(7)),
                     datetime.datetime.combine(date, dt.time(20)),
                     aims_day + trip_id,
                         None)]
        return [Duty(datetime.datetime.combine(date, dt.time(0)),
                     datetime.datetime.combine(date, dt.time(1)),
                     aims_day + trip_id,
                     None)]


    def test_roster_processing(self):
        duties = process.process_roster_entries(
            [
                RosterEntry(aims_day='14146', items=['CSBE', '3:00', '5:00', 'B006D']),
                RosterEntry(aims_day='14147', items=['B086']),
                RosterEntry(aims_day='14152', items=['D/O']),
                RosterEntry(aims_day='14153', items=['LVE']),
                RosterEntry(aims_day='14157', items=['==>', 'B253']),
                RosterEntry(aims_day='14158',
                            items = ['FIRE', '8:00', '9:30',
                                     'DOOR', '9:30', '10:45',
                                     'G/S', '10:45', '11:30',
                                     'ASEC', '11:30', '13:00',
                                     'CRM', '13:00', '14:00',
                                     'SEP', '14:00', '16:00',
                                     '89']),
            ])
        self.assertEqual(duties, [
            Duty(on=datetime.datetime(2018, 9, 24, 0, 0),
                 off=datetime.datetime(2018, 9, 24, 1, 0),
                 text='14146B006D', sectors=None),
            Duty(on=datetime.datetime(2018, 9, 24, 3, 0),
                 off=datetime.datetime(2018, 9, 24, 5, 0),
                 text='CSBE', sectors=None),
            Duty(on=datetime.datetime(2018, 9, 25, 0, 0),
                 off=datetime.datetime(2018, 9, 25, 1, 0),
                 text='14147B086', sectors=None),
            Duty(on=datetime.datetime(2018, 10, 5, 0, 0),
                 off=datetime.datetime(2018, 10, 5, 1, 0),
                 text='14157B253', sectors=None),
            Duty(on=datetime.datetime(2018, 10, 6, 7, 0),
                 off=datetime.datetime(2018, 10, 6, 20, 0),
                 text='1415889', sectors=None),
        ])


class TestSectorProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_get_crewlist = access.get_crewlist
        cls.orig_parse_crewlist = parse.parse_crewlist
        access.get_crewlist = lambda x: ""
        parse.parse_crewlist = lambda x: [Crewmember("c", "CP")]


    @classmethod
    def tearDownClass(cls):
        access.get_crewlist = cls.orig_get_crewlist
        parse.parse_crewlist = cls.orig_parse_crewlist


    def test_flight_sector_future(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '1235', '1450', 'Wed20Feb', '1',
                'G-EZDL', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 12, 35),
                   dt.datetime(2000, 1, 1, 14, 50),
                   None, None,
                   'G-EZDL',
                   False, []))


    def test_flight_sector_over_midnight(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '2300', '0030+1', 'Wed20Feb', '1',
                'A2300', 'A0035', 'G-EZDL', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 23, 0),
                   dt.datetime(2000, 1, 2, 0, 30),
                   dt.datetime(2000, 1, 1, 23, 0),
                   dt.datetime(2000, 1, 2, 0, 35),
                   'G-EZDL',
                   False, [Crewmember("c", "CP")]))


    def test_flight_sector_over_midnight_future(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '2300', '0030+1', 'Wed20Feb', '1',
                'G-EZDL', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 23, 0),
                   dt.datetime(2000, 1, 2, 0, 30),
                   None, None,
                   'G-EZDL',
                   False, []))


    def test_air_positioning_future(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '1235', '1450', 'Wed20Feb', '3',
                'PAX', 'G-EZDL', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 12, 35),
                   dt.datetime(2000, 1, 1, 14, 50),
                   None, None,
                   'G-EZDL',
                   True, []))


    def test_air_positioning_past(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '1235', '1450', 'Wed20Feb', '3',
                'PAX', 'A1230', 'A1445', 'G-EZDL', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 12, 35),
                   dt.datetime(2000, 1, 1, 14, 50),
                   dt.datetime(2000, 1, 1, 12, 30),
                   dt.datetime(2000, 1, 1, 14, 45),
                   'G-EZDL',
                   True, []))


    def test_ground_positioning(self):
        data = ['14293,353365012537,14295,8496,opo,1, ,lgw,319',
                '8496', 'OPO', 'LGW', '1235', '1450', 'Wed20Feb', '3',
                'PAX', '11:35']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('8496', 'OPO', 'LGW',
                   dt.datetime(2000, 1, 1, 12, 35),
                   dt.datetime(2000, 1, 1, 14, 50),
                   None, None,
                   None,
                   True, []))


    def test_quasi_sector(self):
        data = [None,
                'LSBY', 'BRS', 'BRS', '0600', '0910', 'Fri18Jan', '1',
                '09:10', '09:10', '06:00']
        result = process.process_aims_sector(data, dt.date(2000, 1, 1))
        self.assertEqual(
            result,
            Sector('[LSBY]', 'BRS', 'BRS',
                   dt.datetime(2000, 1, 1, 6, 0),
                   dt.datetime(2000, 1, 1, 9, 10),
                   None, None,
                   None,
                   False, []))


    def test_bad_aims_sector(self):
        with self.assertRaises(BadAIMSSector) as cm:
            process.process_aims_sector(1, dt.date(2000, 1, 1))
        with self.assertRaises(BadAIMSSector) as cm:
            process.process_aims_sector(["test"] * 7, dt.date(2000, 1, 1))
        data = [None,
                'LSBY', 'BRS', 'BRS', '0600', '0910', 'Fri18Jan', '1',
                '09:10', '09:10', '06:00']
        with self.assertRaises(BadAIMSSector) as cm:
            process.process_aims_sector(data, None)


class TestDutyProcessing(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.old_process_aims_sector = process.process_aims_sector
        process.process_aims_sector = lambda s, d: Sector(
            "test", "a", "b",
            dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 1, 1),
            dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 1, 1),
            "G-TEST", False, [])


    @classmethod
    def tearDownClass(cls):
        process.process_aims_sector = cls.old_process_aims_sector


    def test_duty_processing(self):
        data = [
            ['14262,138549409849,14262,401,brs,1, ,gla,320',
             '401', 'BRS', 'GLA', '0855', '1010', 'Fri1Jan', '1',
             'A0900', 'A1009', 'OE-IVK', '1:09', '08:45'],
            ['14262,138549409849,14262,402,gla,1, ,brs,320',
             '402', 'GLA', 'BRS', '1035', '1145',
             'A1040', 'A1145', 'OE-IVK', '1:05', '12:15']]
        result = process.process_aims_duty(data, dt.date(2000, 1, 1), "test")
        self.assertEqual(
            result,
            Duty(on=datetime.datetime(2000, 1, 1, 8, 45),
                 off=datetime.datetime(2000, 1, 1, 12, 15), text='test',
                 sectors=[
                     Sector(flightnum='test', from_='a', to='b',
                            sched_off=datetime.datetime(2000, 1, 1, 0, 0),
                            sched_on=datetime.datetime(2000, 1, 1, 1, 0),
                            off=datetime.datetime(2000, 1, 1, 0, 0),
                            on=datetime.datetime(2000, 1, 1, 1, 0),
                            reg='G-TEST', pax=False,
                            crewlist=[])] * 2))


    def test_single_sector_duty(self):
        data = [
            ['14262,138549409849,14262,401,brs,1, ,gla,320',
             '401', 'BRS', 'GLA', '0855', '1010', 'Fri1Jan', '1',
             'A0900', 'A1009', 'OE-IVK', '1:09', '07:55', '10:40']]
        result = process.process_aims_duty(data, dt.date(2000, 1, 1), "test")
        self.assertEqual(
            result,
            Duty(on=datetime.datetime(2000, 1, 1, 7, 55),
                 off=datetime.datetime(2000, 1, 1, 10, 40), text='test',
                 sectors=[
                     Sector(flightnum='test', from_='a', to='b',
                            sched_off=datetime.datetime(2000, 1, 1, 0, 0),
                            sched_on=datetime.datetime(2000, 1, 1, 1, 0),
                            off=datetime.datetime(2000, 1, 1, 0, 0),
                            on=datetime.datetime(2000, 1, 1, 1, 0),
                            reg='G-TEST', pax=False,
                            crewlist=[])]))


    def test_bad_duty(self):
        with self.assertRaises(BadAIMSDuty):
            result = process.process_aims_duty(
                [1, 2], dt.date(2000, 1, 1), "test")


class fakeDatetime(dt.datetime):

    now = dt.datetime(2000, 1, 1)

    @staticmethod
    def utcnow():
        return fakeDatetime.now


def _make_sector(sched_off, flightnum='test', reg='G-TEST', pax=False, no_actuals=False):
    return Sector(
        flightnum, 'a', 'b',
        sched_off, sched_off + dt.timedelta(seconds=3600),
        None if no_actuals else sched_off,
        None if no_actuals else sched_off + dt.timedelta(seconds=3660),
        reg, pax, [])


def _make_duty(sectors):
    return Duty(on=datetime.datetime(2000, 1, 1, 7, 55),
                off=datetime.datetime(2000, 1, 1, 12, 0),
                text='test',
                sectors=sectors)


class TestCaching(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.real_datetime = dt.datetime
        dt.datetime = fakeDatetime


    @classmethod
    def tearDown(cls):
        dt.datetime = cls.real_datetime


    def test_requires_update_past_with_actual(self):
        #past with actuals --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        data = [
            _make_duty([
                _make_sector(dt.datetime(2000, 1, 1, 8, 55)),
                _make_sector(dt.datetime(2000, 1, 1, 10, 30)),
            ])]
        self.assertEqual(process._requires_update(data), False)


    def test_requires_update_without_actual(self):
        #future with no actuals --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 1)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55), no_actuals=True),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30), no_actuals=True),
        ])]
        self.assertEqual(process._requires_update(data), False)
        #past with no actuals --> Update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        self.assertEqual(process._requires_update(data), True)


    def test_requires_update_air_positioning(self):
        #future air postioning --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 1)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55), no_actuals=True, pax=True),
            ])]
        self.assertEqual(process._requires_update(data), False)
        #past air positioning with no actuals --> Update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        self.assertEqual(process._requires_update(data), True)


    def test_requires_update_ground_positioning(self):
        #future ground positioning only --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 1)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55),
                         no_actuals=True, pax=True, reg=None),
            ])]
        self.assertEqual(process._requires_update(data), False)
        #past ground positioning only --> No update rqd (won't get actuals)
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        self.assertEqual(process._requires_update(data), False)
        #future ground positioning then a sector --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 1)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55),
                         no_actuals=True, pax=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30), no_actuals=True),
            ])]
        self.assertEqual(process._requires_update(data), False)
        #past ground positioning then a sector, with actuals --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55),
                         no_actuals=True, pax=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30)),
            ])]
        self.assertEqual(process._requires_update(data), False)
        #past ground positioning then a sector, no actuals --> Update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55),
                         no_actuals=True, pax=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30), no_actuals=True),
            ])]
        self.assertEqual(process._requires_update(data), True)


    def test_requires_update_quasi_then_sector(self):
        #past quasi then a sector with actuals --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55), flightnum="[test]",
                         no_actuals=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30)),
            ])]
        self.assertEqual(process._requires_update(data), False)
        #past quasi then a sector, no actuals --> Update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 2)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55), flightnum="[test]",
                         no_actuals=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30), no_actuals=True),
            ])]
        self.assertEqual(process._requires_update(data), True)
        #future quasi then a sector --> No update rqd
        fakeDatetime.now = dt.datetime(2000, 1, 1)
        data = [
            _make_duty([
            _make_sector(dt.datetime(2000, 1, 1, 8, 55), flightnum="[test]",
                         no_actuals=True, reg=None),
            _make_sector(dt.datetime(2000, 1, 1, 10, 30), no_actuals=True),
            ])]
        self.assertEqual(process._requires_update(data), False)



if __name__ == '__main__':
    unittest.main()
