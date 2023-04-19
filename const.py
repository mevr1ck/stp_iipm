import os
import random

host = os.environ.get('HOST')
MINIO = os.environ.get('MINIO')

LOGIN = os.environ.get('LOGIN')
PASSWORD = os.environ.get('PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_PASS = os.environ.get('DB_PASS')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

SCHEDULE_ID = os.environ.get('SCHEDULE_ID')
SOURCE_ID = os.environ.get('SOURCE_ID')

ARCHIVE_LINK = os.environ.get('ARCHIVE_LINK')
ARCHIVE_NAME = os.environ.get('ARCHIVE_NAME')

AUTH_HEADERS = {
    'Authorization': f'Basic {os.environ.get("BASIC_AUTH")}'
}

AUTH_APPLICATION_HEADERS = {
    'Authorization': f'Basic {os.environ.get("BASIC_AUTH")}',
    'Content-Type': 'application/json'
}
APPLICATION_HEADERS = {
    'Content-Type': 'application/json'
}

urlevents = f"{host}/events/"
urldevices = f"{host}/devices/"
urlcameras = f"{host}/devices/cameras/"
urlvehicle = f"{host}/devices/vehicleTypes/"

IMAGE_TYPE = "image_type"
TIMESTAMP = "timestamp"
DEVICE = "device"
RESULTS = "results"
CAMERA = "camera"
ID = "id"
LABEL = "label"
ISSUES = "issues"
PANORAMIC = "panoramic"
DATA = "data"
login = "login"
user = "user"
users = "users"
ITERATIONS = "iterations"
UUID = "uuid"
MSG = "msg"
TASK_ID = "taskId"
TASKS = 'tasks'
LABELS = 'labels'
DETECTORS = 'detectors'
SCHEDULES = 'schedules'
PAGE = 'page'
VALIDATE = 'validate'
SHOW_BY = 'showBy'
BIND = 'bind'
FROM_DT = 'from_dt'
TO_DT = 'to_dt'

LIST_LABELS = [50, 51, 60, 61, 70, 71, 80, 81, 90, 91, 100, 101, 110, 111, 121, 120, 130, 131, 140, 141, 150, 151,
               160, 161, 170, 181, 180, 190, 191, 200, 201, 211, 210, 221, 220, 231, 230, 240, 241, 250, 251,
               260, 261]
RANDOM_DETECTORS = [random.randint(5, 26)]

ZKH_LABELS = [70, 71, 80, 81, 90, 91, 100, 101, 110, 111, 120, 121, 130, 131, 140, 141, 150, 151,
              160, 161, 170, 171, 180, 181]
ZKH_DETECTORS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

ZKH_PLUS_LABELS = [190, 191, 200, 201, 210, 211, 220, 221, 230, 231, 240, 241, 250, 251, 260, 261]
ZKH_PLUS_DETECTORS = [19, 20, 21, 22, 23, 24, 25, 26]

ZKH_SHOPS_LABELS = [50, 51, 60, 61]
ZKH_SHOPS_DETECTORS = [5, 6]

ZKH_NEW_LABELS = [290, 291, 300, 301, 310, 311]
ZKH_NEW_DETECTORS = [29, 30, 31]


def RANDOM_LABELS():
    a = 1
    b = 1
    c = 1

    while a == b or b == c or a == c:
        a = random.randint(0, len(LIST_LABELS) - 1)
        b = random.randint(0, len(LIST_LABELS) - 1)
        c = random.randint(0, len(LIST_LABELS) - 1)
    print(LIST_LABELS[a], LIST_LABELS[b], LIST_LABELS[c])
    return [LIST_LABELS[a], LIST_LABELS[b], LIST_LABELS[c]]
