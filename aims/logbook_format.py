
from typing import List, Dict
from aims.mytypes import *
import datetime as dt

from aims.approx_night import approx_night


reg_dict = {
    "G-EZEB": "A319", "G-EZEG": "A319", "G-EZEH": "A319",
    "G-EZEN": "A319", "G-EZEY": "A319", "G-EZEZ": "A319",
    "G-EZMK": "A319", "G-EZPG": "A319", "G-EZNM": "A319",
    "G-EJAR": "A319", "G-EZIH": "A319", "G-EZII": "A319",
    "G-EZIM": "A319", "G-EZIO": "A319", "G-EZIP": "A319",
    "G-EZIR": "A319", "G-EZIS": "A319", "G-EZIT": "A319",
    "G-EZIV": "A319", "G-EZIW": "A319", "G-EZIX": "A319",
    "G-EZIY": "A319", "G-EZIZ": "A319", "G-EZAA": "A319",
    "G-EZAB": "A319", "G-EZAC": "A319", "G-EZAF": "A319",
    "G-EZAG": "A319", "G-EZAI": "A319", "G-EZAJ": "A319",
    "G-EZAK": "A319", "G-EZAL": "A319", "G-EZAN": "A319",
    "G-EZAO": "A319", "G-EZAP": "A319", "G-EZAS": "A319",
    "G-EZAT": "A319", "G-EZAU": "A319", "G-EZAV": "A319",
    "G-EZAW": "A319", "G-EZAX": "A319", "OE-LKH": "A319",
    "OE-LKI": "A319", "G-EZBB": "A319", "G-EZBA": "A319",
    "G-EZBC": "A319", "G-EZBD": "A319", "G-EZBE": "A319",
    "G-EZBF": "A319", "OE-LKJ": "A319", "G-EZBH": "A319",
    "OE-IZV": "A320", "G-EZBI": "A319", "OE-LKN": "A319",
    "G-EZBK": "A319", "OE-LQT": "A319", "OE-IZW": "A320",
    "OE-LQZ": "A319", "OE-LKQ": "A319", "G-EZBO": "A319",
    "G-EZBR": "A319", "OE-LKE": "A319", "G-EZBU": "A319",
    "G-EZBV": "A319", "G-EZBW": "A319", "G-EZBX": "A319",
    "OE-LQH": "A319", "G-EZBZ": "A319", "OE-LQI": "A319",
    "G-EZDA": "A319", "OE-LKK": "A319", "G-EZDF": "A319",
    "G-EZDD": "A319", "G-EZDH": "A319", "G-EZDI": "A319",
    "G-EZDJ": "A319", "G-EZDK": "A319", "G-EZDL": "A319",
    "G-EZDM": "A319", "G-EZDN": "A319", "OE-LQX": "A319",
    "OE-LKM": "A319", "OE-LQY": "A319", "OE-LKP": "A319",
    "OE-LKD": "A319", "OE-LQN": "A319", "G-EZDV": "A319",
    "OE-LKF": "A319", "OE-LQO": "A319", "OE-LQD": "A319",
    "OE-LQL": "A319", "OE-LQC": "A319", "OE-LQA": "A319",
    "G-EZTA": "A320", "OE-LQB": "A319", "OE-LQP": "A319",
    "OE-LQM": "A319", "G-EZTB": "A320", "OE-LQF": "A319",
    "OE-LQQ": "A319", "OE-LQR": "A319", "G-EZTC": "A320",
    "OE-LQK": "A319", "G-EZTD": "A320", "G-EZTE": "A320",
    "OE-IJO": "A320", "OE-IZS": "A320", "G-EZTG": "A320",
    "G-EZTH": "A320", "OE-IJR": "A320", "OE-IVO": "A320",
    "G-EZTK": "A320", "OE-IZT": "A320", "HB-JYE": "A320",
    "OE-IVX": "A320", "OE-IZU": "A320", "G-EZTM": "A320",
    "OE-IZC": "A320", "HB-JZR": "A320", "OE-LQS": "A319",
    "OE-LKL": "A319", "G-EZFL": "A319", "OE-LKO": "A319",
    "OE-LQG": "A319", "OE-LQJ": "A319", "OE-LQU": "A319",
    "OE-LQV": "A319", "OE-LQW": "A319", "G-EZFT": "A319",
    "HB-JZX": "A320", "G-EZTR": "A320", "HB-JZY": "A320",
    "G-EZTT": "A320", "HB-JZZ": "A320", "OE-IJP": "A320",
    "HB-JYA": "A320", "OE-IVH": "A320", "OE-LKG": "A319",
    "OE-IZB": "A320", "G-EZFV": "A319", "G-EZFW": "A319",
    "G-EZFX": "A319", "G-EZFY": "A319", "G-EZFZ": "A319",
    "G-EZGA": "A319", "G-EZGB": "A319", "G-EZGC": "A319",
    "OE-LQE": "A319", "G-EZTY": "A320", "G-EZTZ": "A320",
    "OE-IZD": "A320", "G-EZUA": "A320", "OE-IVK": "A320",
    "OE-IZE": "A320", "G-EZGE": "A319", "G-EZGF": "A319",
    "OE-IJE": "A320", "HB-JYN": "A319", "HB-JYD": "A320",
    "HB-JYM": "A319", "G-EZUF": "A320", "OE-IJL": "A320",
    "HB-JYL": "A319", "HB-JYK": "A319", "G-EZUH": "A320",
    "HB-JYJ": "A319", "HB-JXI": "A320", "G-EZUJ": "A320",
    "HB-JYI": "A319", "G-EZUK": "A320", "HB-JYF": "A319",
    "HB-JYG": "A319", "HB-JYC": "A319", "HB-JYH": "A319",
    "G-EZGR": "A319", "G-EZUL": "A320", "OE-ICK": "A320",
    "G-EZUN": "A320", "G-EZUO": "A320", "G-EZUP": "A320",
    "G-EZUR": "A320", "G-EZUS": "A320", "HB-JXB": "A320",
    "G-EZUT": "A320", "G-EZUW": "A320", "HB-JXA": "A320",
    "HB-JXC": "A320", "HB-JXD": "A320", "G-EZUZ": "A320",
    "G-EZWA": "A320", "G-EZWB": "A320", "G-EZWC": "A320",
    "G-EZWD": "A320", "G-EZWE": "A320", "G-EZWG": "A320",
    "G-EZWF": "A320", "OE-IZO": "A320", "G-EZWH": "A320",
    "G-EZWI": "A320", "G-EZWJ": "A320", "OE-IZP": "A320",
    "OE-IVJ": "A320", "G-EZWL": "A320", "G-EZWM": "A320",
    "OE-IJQ": "A320", "HB-JXE": "A320", "G-EZWP": "A320",
    "G-EZWR": "A320", "G-EZWS": "A320", "OE-ICJ": "A320",
    "G-EZWU": "A320", "G-EZWV": "A320", "OE-IVL": "A320",
    "G-EZWX": "A320", "G-EZWY": "A320", "G-EZWZ": "A320",
    "G-EZOA": "A320", "G-EZOB": "A320", "OE-IVZ": "A320",
    "OE-IJZ": "A320", "OE-IJI": "A320", "G-EZOF": "A320",
    "OE-IJY": "A320", "OE-IJJ": "A320", "OE-ICT": "A320",
    "G-EZOI": "A320", "OE-IJK": "A320", "G-EZOK": "A320",
    "OE-IJB": "A320", "G-EZOM": "A320", "G-EZON": "A320",
    "OE-ICB": "A320", "G-EZOP": "A320", "OE-IJF": "A320",
    "OE-ICC": "A320", "OE-ICG": "A320", "OE-IJG": "A320",
    "OE-IZF": "A320", "OE-IJN": "A320", "G-EZOX": "A320",
    "OE-IZG": "A320", "OE-IZQ": "A320", "G-EZOY": "A320",
    "OE-IZH": "A320", "OE-IZJ": "A320", "G-EZOZ": "A320",
    "OE-IZL": "A320", "OE-IZN": "A320", "OE-IVA": "A320",
    "G-EZPB": "A320", "OE-IVV": "A320", "G-EZPD": "A320",
    "G-EZPE": "A320", "OE-IVW": "A320", "OE-IVB": "A320",
    "G-EZPI": "A320", "OE-IVE": "A320", "OE-IVF": "A320",
    "OE-IVD": "A320", "OE-IVQ": "A320", "OE-IVS": "A320",
    "OE-IVR": "A320", "HB-JXF": "A320", "OE-IVC": "A320",
    "OE-IJS": "A320", "OE-IJU": "A320", "OE-IVI": "A320",
    "OE-IVM": "A320", "OE-IJX": "A320", "OE-IVN": "A320",
    "OE-IJW": "A320", "OE-IJV": "A320", "OE-IVT": "A320",
    "OE-IVU": "A320", "G-UZHA": "A320", "OE-IJA": "A320",
    "OE-IJD": "A320", "OE-IJH": "A320", "G-EZRG": "A320",
    "G-UZHB": "A320", "G-EZRH": "A320", "G-EZRI": "A320",
    "G-EZRJ": "A320", "HB-JXJ": "A320", "G-EZRL": "A320",
    "G-EZRM": "A320", "G-UZHC": "A320", "G-UZHD": "A320",
    "OE-INH": "A320", "OE-INI": "A320", "G-EZRP": "A320",
    "G-EZRR": "A320", "G-UZHE": "A320", "OE-ING": "A320",
    "G-EZRT": "A320", "G-EZRU": "A320", "G-UZHF": "A320",
    "G-UZHG": "A320", "G-EZRV": "A320", "G-UZHH": "A320",
    "G-EZRW": "A320", "G-UZHI": "A320", "G-UZMA": "A321",
    "G-EZRX": "A320", "G-UZHJ": "A320", "G-EZRY": "A320",
    "G-UZHK": "A320", "G-EZRZ": "A320", "G-UZMB": "A321",
    "G-UZHL": "A320", "G-EZGX": "A320", "G-EZGY": "A320",
    "G-UZMC": "A321", "G-EZGZ": "A320", "G-UZHM": "A320",
    "G-UZHN": "A320", "G-UZHO": "A320", "G-UZMD": "A321",
    "G-UZHP": "A320", "G-UZME": "A321", "G-UZHR": "A320",
    "G-UZHS": "A320", "OE-ICM": "A320", "OE-INP": "A320",
}


def dump(dutylist: List[Duty]) -> str:
    output = []
    for duty in dutylist:
        if duty.on > dt.datetime.utcnow(): break
        output.append("{:%Y-%m-%d}".format(duty.on))
        if not duty.sectors:
            output.append("{:%H%M}/{:%H%M} #{}\n".format(
                duty.on, duty.off, duty.text))
            continue
        output.append("{:%H%M}/{:%H%M}".format(duty.on, duty.off))
        reg = None
        crewlist = None
        for sector in duty.sectors:
            if not (sector.on and sector.off) or sector.pax: continue
            if sector.crewlist and crewlist != sector.crewlist:
                crewstr = ", ".join(
                    ["{}:{}".format(X.role, X.name) for X in sector.crewlist])
                output.append(r"{{ {} }}".format(crewstr))
            crewlist = sector.crewlist
            sunset, sunrise = approx_night(sector.off)
            mid_duty_time = sector.off + (sector.off - sector.on) // 2
            night = ""
            if mid_duty_time.time() > sunset or mid_duty_time.time() < sunrise:
                night = " n"
            if sector.reg and reg != sector.reg:
                output.append("{}:{}".format(
                    sector.reg, reg_dict.get(sector.reg, "???")))
                reg = sector.reg
            output.append("{}/{} {:%H%M}/{:%H%M}{}".format(
                sector.from_, sector.to,
                sector.off, sector.on, night))
        output.append("")
    return "\n".join(output)
