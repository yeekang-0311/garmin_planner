from garmin_planner.__init__ import logger
from garmin_planner.constant import *
import yaml
import os
import re

dir_path = os.path.dirname(__file__)

def parseYaml(filename: str):
    filepath = os.path.join(dir_path, filename)
    data = {}
    with open(filepath) as stream:
        try:
            data = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            logger.error(exc)
    return data
    

# def parse_bracket(string):
#     match = re.match(r'([\w@]+)(?:\(([^()]+)\))?', string.lower())
#     if match:
#         key = match.group(1)  
#         value = match.group(2)      
#         return key, value
#     return None, None
def parse_bracket(string):
    # cerca la prima occorrenza tipo TOKEN(...) o TOKEN nel testo, case-insensitive
    m = re.search(r'([\w@]+)(?:\(([^()]*)\))?', string, flags=re.IGNORECASE)
    if m:
        key = m.group(1).lower()
        value = m.group(2)
        return key, value
    return None, None

def parse_time_to_minutes(time_string):
    minutes, sec = map(int, time_string.split(":"))
    time_in_min = minutes + (sec / 60)
    return time_in_min

def parse_stepdetail(string, sport_type):
    stepDetails = {}
    details = string.split(" ")
    # sport_type = SportType.RUNNING if sport_type is None else sport_type
    for detail in details:
        try:
            # Duration
            ## Time
            if ("sec" in detail):
                detail = detail.replace("sec", "")
                durationInSec = int(detail)
                stepDetails.update({
                        'endCondition': ConditionType.TIME, 
                        'endConditionValue': durationInSec
                    })
                continue

            if ("min" in detail):
                detail = detail.replace("min", "")
                durationNum = int(detail)
                durationInSec = durationNum * 60
                stepDetails.update({
                        'endCondition': ConditionType.TIME, 
                        'endConditionValue': durationInSec
                    })
                continue
            
            ## Distance
            if ("m" in detail):
                detail = detail.replace("m", "")
                distanceInMeter = int(detail)
                stepDetails.update({
                        'endCondition': ConditionType.DISTANCE, 
                        'endConditionValue': distanceInMeter
                    })
                continue

            ## Lap button
            if ("lap" in detail):
                stepDetails.update({
                        'endCondition': ConditionType.LAP_BUTTON, 
                        'endConditionValue': 1
                    })
                continue

            # Target
            if ("@" in detail):
                target, value = parse_bracket(detail)
                print(f"Target: {target}, Value: {value}")
                if (target == None or value == None):
                    continue

                ## Pace
                if (target.upper() == "@P"):
                    floor, top = value.split("-")
                    floorMin = parse_time_to_minutes(floor)
                    topMin = parse_time_to_minutes(top)
                    stepDetails.update({
                        'targetType': TargetType.PACE,
                        'targetValueOne': PACE_CONST/floorMin,
                        'targetValueTwo': PACE_CONST/topMin
                    })
                    continue

                if (target.upper() == "@S"):
                    speedValueLowLimit = float(value)
                    speedValueHighLimit = float(value)
                    stepDetails.update({
                        'targetType': TargetType.SPEED,
                        'targetValueOne': speedValueLowLimit,
                        'targetValueTwo': speedValueHighLimit
                    })
                    continue

                if (target.upper() == "@C"):
                    cadenceValueLowLimit = int(value)
                    cadenceValueHighLimit = int(value)
                    stepDetails.update({
                        'targetType': TargetType.CADENCE,
                        'targetValueOne': cadenceValueLowLimit,
                        'targetValueTwo': cadenceValueHighLimit
                    })
                    continue

                ## Heart rate zone
                if (target.upper() == "@H"):
                    value = value.lower().replace("z", "")
                    rateZone = int(value)
                    stepDetails.update({
                        'targetType': TargetType.HEART_RATE_ZONE,
                        'zoneNumber': rateZone
                    })
                    continue
                if (target.upper() == "@W"):
                    value = value.lower().replace("z", "")
                    powerZone = int(value)
                    stepDetails.update({
                        'targetType': TargetType.POWER_ZONE,
                        'zoneNumber': powerZone
                    })
                    continue

                if (target.upper() == "@STYLE"):
                    swimStyleStr = value.lower()
                    match swimStyleStr:
                        case "free":
                            swimStyle = StrokeType.FREESTYLE.value
                        case "back":
                            swimStyle = StrokeType.BACKSTROKE.value
                        case "breast":
                            swimStyle = StrokeType.BREASTSTROKE.value
                        case _:
                            swimStyle = StrokeType.FREESTYLE.value
                    stepDetails.update({
                        'strokeType': swimStyle
                    })
                    continue
                if (target.upper() == "@EQUIP"):
                    equipmentStr = value.lower()
                    match equipmentStr:
                        case "fins":
                            equipmentType = EquipmentType.FINS.value
                        case "pull_buoy":
                            equipmentType = EquipmentType.PULL_BUOY.value
                        case "kickboard":
                            equipmentType = EquipmentType.KICKBOARD.value
                        case "snorkel":
                            equipmentType = EquipmentType.SNORKEL.value
                        case _:
                            raise ValueError(f"EQUIP selected but not a valid option {equipmentStr}")
                    stepDetails.update({
                        'equipmentType': equipmentType
                    })
                    continue
                if (target.upper() == "@EXECUTION"):
                    drillStr = value.lower()
                    match drillStr:
                        case "drill":
                            drillType = DrillType.DRILL.value
                        case "pull":
                            drillType = DrillType.PULL.value
                        case "kick":
                            drillType = DrillType.KICK.value
                    stepDetails.update({
                        'drillType': drillType
                    })
                    continue

   

        except Exception as e:
            logger.error(e)
            continue

    return stepDetails