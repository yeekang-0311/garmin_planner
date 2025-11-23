from garmin_planner.client import Client
from garmin_planner.__init__ import logger
from garmin_planner.model.workoutModel import WorkoutModel, WorkoutSegment, WorkoutStep, RepeatStep
from garmin_planner.constant import *
from garmin_planner.parser import *
import re
import json
import datetime
import sys
import argparse
import os

__version__ = "0.1.0"

def replace_variables(data, definitionsDict: dict):
    if isinstance(data, str):
        return re.sub(r'\$(\w+)', lambda m: definitionsDict.get(m.group(1), m.group(0)), data)
    elif isinstance(data, dict):
        return {k: replace_variables(v, definitionsDict) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_variables(item, definitionsDict) for item in data]
    return data  

# Serialize to JSON
def serialize(obj):
    if isinstance(obj, Enum):
        return obj.to_dict()
    return obj.__dict__

def createWorkoutList(steps: list, stepCount: list):
    workoutSteps = []
    for _, step in enumerate(steps):
        workoutStep = createWorkoutStep(step, stepCount)
        if workoutStep:
            workoutSteps.append(workoutStep)
    return workoutSteps

def createWorkoutStep(step: dict, stepCount: list):
    stepType = None
    for stepName in step:
        stepDetail = step[stepName]
        parsedStep, numIteration = parse_bracket(stepName)
        match parsedStep:
            case "run":
                stepType = StepType.WARMUP
            case "warmup":
                stepType = StepType.WARMUP
            case "cooldown":
                stepType = StepType.COOLDOWN
            case "recovery":
                stepType = StepType.RECOVERY
            case "repeat":
                stepType = StepType.REPEAT
                stepCount[0] += 1
                order = stepCount[0]
                workoutSteps = createWorkoutList(stepDetail, stepCount)
                return RepeatStep(
                    stepId=order, stepOrder=order, 
                    workoutSteps=workoutSteps,
                    numberOfIterations=int(numIteration))
            case _:
                logger.error("default in workout step")
                return None

        parsedStepDetailDict = parse_stepdetail(stepDetail)
        stepCount[0] += 1
        order = stepCount[0]
    return WorkoutStep(stepId=order, stepOrder=order, stepType=stepType, **parsedStepDetailDict)


def createWorkoutJson(workoutName: str, steps: list):
    stepCount = [0]
    sport_type = SportType.RUNNING
    # distance_unit = DistanceUnit.KILOMETER

    workoutSteps = createWorkoutList(steps, stepCount)

    # Create other steps and segments similarly, then create the workout model
    workout_segment = WorkoutSegment(
        segmentOrder=1,
        sportType=sport_type,
        workoutSteps=workoutSteps
    )

    workout_model = WorkoutModel(
        workoutName=workoutName,
        sportType=sport_type,
        subSportType=None,
        workoutSegments=[workout_segment],
        estimatedDistanceUnit=None,
        avgTrainingSpeed=None,
        estimatedDurationInSecs=None,
        estimatedDistanceInMeters=None,
        estimateType=None
    )

    return json.dumps(workout_model, default=serialize)

def importWorkouts(workouts: dict, toDeletePrevious: bool, conn: Client):
    # delete previous workout with the same workout name
    allWorkouts = []
    if toDeletePrevious:
        allWorkouts = conn.getAllWorkouts() 

    for name in workouts:
        if toDeletePrevious and (name in [wo['workoutName'] for wo in allWorkouts]):
            filtered = [wo for wo in allWorkouts if wo['workoutName'] == name]
            for toDelete in filtered:
                conn.deleteWorkout(toDelete)

        steps = workouts[name]
        jsonData = createWorkoutJson(name, steps)
        conn.importWorkout(jsonData)

def scheduleWorkouts(startfrom: datetime, workouts: list, conn: Client):
    # Check valid date
    isValidDate = isinstance(startfrom, datetime.date)
    if (not isValidDate):
        logger.error(f"""Invalid date {startfrom} format, example of proper date: 2024-10-06 """)
        return False

    # Get all workouts plan from garmin acc
    allWorkouts = conn.getAllWorkouts()
    workoutMap = {value['workoutName']: value['workoutId'] for _, value in enumerate(allWorkouts)}
    logger.debug(f"""Workouts on garmin: {workoutMap}""")

    toScheduleDate = startfrom

    # Schedule workouts
    for toScheduleWorkouts in workouts:
        currentDate = toScheduleDate
        toScheduleDate += datetime.timedelta(days=1)

        if not isinstance(toScheduleWorkouts, str):
            logger.error(f"Invalid workout entry: {toScheduleWorkouts}. Skipping.")
            continue
        # Split multiple workouts for a single day
        dailyWorkouts = [workout.strip() for workout in toScheduleWorkouts.split(",")]

        for workout in dailyWorkouts:
            if workout not in workoutMap:
                logger.warning(f"Workout '{workout}' not found on Garmin Connect. Skipping.")
                continue

            workoutId = workoutMap[workout]
            dateJson = {"date": currentDate.strftime(DATE_FORMAT)}
            success = conn.scheduleWorkout(workoutId, dateJson)
            if (success):
                logger.info(f"""Scheduled workout '{workout}' on date {currentDate}""")
            else:
                logger.error(f"""Failed to schedule workout '{workout}' on date {currentDate}""")

def main():
    logger.info(f"""Running Garmin Planner {__version__}""")
    argparser = argparse.ArgumentParser(description="Garmin Planner")
    argparser.add_argument('file_name', type=str, help='Input YAML file name')
    args = argparser.parse_args()
    file_name = args.file_name

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    if not os.path.exists(file_path):
        logger.error(f"The file '{file_path}' does not exist.")
        sys.exit("Exited program due to yaml file not found")

    logger.info(f"Current working directory: {os.getcwd()}")

    # default settings
    settings = {"deleteSameNameWorkout": False}

    # preprocess secrets yaml file and get email and password
    secrets = parseYaml(os.path.join(current_dir, "secrets.yaml"))
    if not secrets:
        logger.error("Failed to parse secrets.yaml")
        sys.exit("Exiting: secrets.yaml not found.")
    if ("email" not in secrets) or ("password" not in secrets):
        logger.error("Missing 'email' or 'password' in YAML input.")
        sys.exit("Exiting: 'email' or 'password' not found.")

    email = secrets['email']
    password = secrets['password']
    garminCon = Client(email,password)

    # parse input yaml file
    data = parseYaml(file_path)

    # settings
    if "settings" in data:
        if "deleteSameNameWorkout" in data['settings']:
            settings['deleteSameNameWorkout'] = data['settings']['deleteSameNameWorkout']

    # replace definitions
    if "definitions" in data:
        definitionsDict = data['definitions']
        data = replace_variables(data, definitionsDict)
    if "workouts" in data:
        workouts = data['workouts']
        importWorkouts(workouts=workouts, 
                       toDeletePrevious=settings['deleteSameNameWorkout'], 
                       conn=garminCon)
    if "schedulePlan" in data:
        schedulePlan = data['schedulePlan']
        startDate = schedulePlan['start_from']
        workouts = schedulePlan['workouts']
        scheduleWorkouts(startDate, workouts, garminCon)

    logger.info("Finished processing yaml file")