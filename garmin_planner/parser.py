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
    

def parse_bracket(string):
    match = re.match(r'([\w@]+)(?:\(([^()]+)\))?', string.lower())
    if match:
        key = match.group(1)  
        value = match.group(2)      
        return key, value
    return None, None

def parse_time_to_minutes(time_string):
    minutes, sec = map(int, time_string.split(":"))
    time_in_min = minutes + (sec / 60)
    return time_in_min

def parse_stepdetail(string):
    stepDetails = {}
    details = string.split(" ")
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

   

        except Exception as e:
            logger.error(e)
            continue

    return stepDetails