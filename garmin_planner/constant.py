from enum import Enum
# docu for sports and activity IDshttps://developer.garmin.com/connect-iq/api-docs/Toybox/Activity.html#Sport-module
# A constant used to convert pace to certain value recognized by Garmin Connect
PACE_CONST = 16.66666

DATE_FORMAT = "%Y-%m-%d"

# Workout data 
class SportType(Enum):
    RUNNING = {
      "sportTypeId": 1,
      "sportTypeKey": "running",
      "displayOrder": 1
    }
    
    CYCLING = {
      "sportTypeId": 2,
      "sportTypeKey": "cycling",
      "displayOrder": 2
    }

    SWIMMING = {
      "sportTypeId": 4,
      "sportTypeKey": "swimming",
      "displayOrder": 3
    }
    def to_dict(self):
        return self.value


class DistanceUnit(Enum):
    KILOMETER = {
      "unitKey": "kilometer"
    }
    MILE = {
      "unitKey": "mile"
    },

    def to_dict(self):
        return self.value

class StepType(Enum):
    WARMUP = {
        "stepTypeId": 1,
        "stepTypeKey": "warmup",
        "displayOrder": 1
    }
    COOLDOWN = {
        "stepTypeId": 2,
        "stepTypeKey": "cooldown",
        "displayOrder": 2
    }
    INTERVAL = {
        "stepTypeId": 3,
        "stepTypeKey": "interval",
        "displayOrder": 3
    }
    RECOVERY = {
        "stepTypeId": 4,
        "stepTypeKey": "recovery",
        "displayOrder": 4
    }
    REPEAT = {
        "stepTypeId": 6,
        "stepTypeKey": "repeat",
        "displayOrder": 6
    }
    def to_dict(self):
        return self.value




class ConditionType(Enum):
    LAP_BUTTON = {
        "conditionTypeId": 1,
        "conditionTypeKey": "lap.button",
        "displayOrder": 1,
        "displayable": True
    }
    TIME = {
        "conditionTypeId": 2,
        "conditionTypeKey": "time",
        "displayOrder": 2,
        "displayable": True
    }
    DISTANCE = {
        "conditionTypeId": 3,
        "conditionTypeKey": "distance",
        "displayOrder": 3,
        "displayable": True
    }

    ITERATION_ENDS = {
        "conditionTypeId": 7,
        "conditionTypeKey": "iterations",
        "displayOrder": 7,
        "displayable": False
    }
    def to_dict(self):
        return self.value


class STROKE_TYPE(Enum):
    FREESTYLE = {
        "strokeTypeId": 6,
        "strokeTypeKey": "free",
        "displayOrder": 6
    }
    BACKSTROKE = {
        "strokeTypeId": 2,
        "strokeTypeKey": "backstroke",
        "displayOrder": 2
    }
    BREASTSTROKE = {
        "strokeTypeId": 3,
        "strokeTypeKey": "breaststroke",
        "displayOrder": 3
    }

    def to_dict(self):
        return self.value
    
class SWIM_EQUIPMENT(Enum):
    FINS = {
        "swimEquipmentId": 1,
        "swimEquipmentKey": "fins",
        "displayOrder": 1
    }
    KICKBOARD = {
        "swimEquipmentId": 2,
        "swimEquipmentKey": "kickboard",
        "displayOrder": 2
    }
    PULL_BUOY = {
        "swimEquipmentId": 4,
        "swimEquipmentKey": "pull_buoy",
        "displayOrder": 4
    }
    SNORKEL = {
        "swimEquipmentId": 5,
        "swimEquipmentKey": "snorkel",
        "displayOrder": 5
    }

    def to_dict(self):
        return self.value

class TargetType(Enum):
    NO_TARGET = {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1
    }
    # This need targetValueOne, Two
    PACE = {
        "workoutTargetTypeId": 6,
        "workoutTargetTypeKey": "pace.zone",
        "displayOrder": 6
    }
    CADENCE = {
        "workoutTargetTypeId": 3,
        "workoutTargetTypeKey": "cadence",
        "displayOrder": 3
    }
    HEART_RATE_ZONE = {
        "workoutTargetTypeId": 4,
        "workoutTargetTypeKey": "heart.rate.zone",
        "displayOrder": 4
    }
    POWER_ZONE = {
        "workoutTargetTypeId": 2,
        "workoutTargetTypeKey": "power.zone",
        "displayOrder": 2
    }
    def to_dict(self):
        return self.value

