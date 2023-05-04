import pytest
import requests
import psycopg2
from psycopg2 import Error
import const as c


def get_token_for_auth(login, password):
    url = f"{c.host}/api/v1/login"

    payload = {
        "login": login,
        "password": password
    }
    headers = c.APPLICATION_HEADERS

    response = requests.post(url, headers=headers, json=payload)
    token = response.json()[c.DATA]
    return token


def get_events(filter=None, value=None, filter2=None, value2=None,
               filter3=None, value3=None, filter4=None, value4=None):
    url = c.urlevents
    headers = c.AUTH_HEADERS
    new_params = {filter: str(value), filter2: str(value2), filter3: str(value3), filter4: str(value4)}

    response = requests.get(url, headers=headers, params=new_params)
    print(url, new_params)
    return response


def upload_archive():
    url = f"{c.host}/api/v1/sources/{c.SOURCE_ID}"

    payload = {
        "schedule_id": c.SCHEDULE_ID,
        "url": c.ARCHIVE_LINK,
        "completion": 100
    }
    headers = {
        'Authorization': f'Bearer {get_token_for_auth(c.LOGIN, c.PASSWORD)}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    return response


def get_list_iterations(source_id):
    url = f"{c.host}/api/v1/iterations?limit=1&sourceUuid={source_id}"
    headers = {
        'Authorization': f'Bearer {get_token_for_auth(c.LOGIN, c.PASSWORD)}'
    }
    response = requests.get(url, headers=headers)
    print(response.text)
    return response


def create_task(labels=None, detectors=None, schedule_id=None):
    url = f"{c.host}/tasks/create"
    payload = {
        "labels": labels,
        "detectors": detectors,
        "schedule": schedule_id
    }

    headers = c.AUTH_APPLICATION_HEADERS
    response = requests.post(url, headers=headers, json=payload)
    print(payload)
    print(response.text)
    return response


def delete_task_from_db(taskId):
    try:
        connection = psycopg2.connect(user=c.DB_USER, password=c.DB_PASS, host=c.DB_HOST, port=c.DB_PORT,
                                      database=c.DB_NAME)
        cursor = connection.cursor()
        sql_delete_query = """DELETE FROM task WHERE uuid = %s"""
        cursor.execute(sql_delete_query, (taskId,))
        connection.commit()
        count = cursor.rowcount
        print(count, "Запись успешно удалена")
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    else:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def get_screenshot_id_from_db():
    screenshot_id = ''
    try:
        connection = psycopg2.connect(user=c.DB_USER, password=c.DB_PASS, host=c.DB_HOST, port=c.DB_PORT,
                                      database=c.DB_NAME)
        cursor = connection.cursor()
        sql_select_query = """SELECT info#>> '{headpoint,screenshotId}' FROM image
        WHERE bucket = 'headpoint'
        LIMIT 1; """
        cursor.execute(sql_select_query)
        screenshot_id = cursor.fetchone()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    else:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
    print(screenshot_id)
    return screenshot_id[0]


def get_tasks(showCancelled=None):
    url = f"{c.host}/tasks/index"
    headers = c.AUTH_HEADERS
    params = {'showCancelled': showCancelled}
    response = requests.get(url, headers=headers, params=params)
    return response


def get_task_status(task_id):
    url = f"{c.host}/tasks/{task_id}/status"
    headers = c.AUTH_HEADERS
    response = requests.get(url, headers=headers)
    return response


def get_task_result(task_id):
    url = f"{c.host}/results/{task_id}"
    headers = c.AUTH_HEADERS
    response = requests.get(url, headers=headers)
    return response


def pause_task(task_id):
    url = f"{c.host}/tasks/{task_id}/pause"

    headers = c.AUTH_HEADERS

    response = requests.patch(url, headers=headers)
    return response


def resume_task(task_id):
    url = f"{c.host}/tasks/{task_id}/resume"

    headers = c.AUTH_HEADERS

    response = requests.patch(url, headers=headers)
    return response


def stop_task(task_id):
    url = f"{c.host}/tasks/{task_id}/cancel"

    headers = c.AUTH_HEADERS

    response = requests.patch(url, headers=headers)
    return response


def send_expert_answer(screenshot_id):
    url = f"{c.host}/event/{screenshot_id}/feedback"

    payload = {
        "status": "issue confirmed",
        "text": "free text message about screenshot",
        "label": 101,
        "boxes": [
            {
                "x": 123,
                "y": 123,
                "w": 123,
                "h": 123
            },
            {
                "x": 123,
                "y": 123,
                "w": 123,
                "h": 123
            }
        ]
    }
    headers = c.AUTH_APPLICATION_HEADERS

    response = requests.post(url, headers=headers, json=payload)
    return response


def get_gin_labels():
    url = f"{c.host}/events/labels/"
    headers = c.AUTH_HEADERS
    response = requests.get(url, headers=headers)
    return response


def get_cameras(filter_1=None, value_1=None, filter_2=None, value_2=None):
    url = f"{c.host}/devices/cameras/"
    headers = c.AUTH_HEADERS
    params = {filter_1: value_1, filter_2: value_2}
    response = requests.get(url, headers=headers, params=params)
    return response


def get_devices(filter_1=None, value_1=None, filter_2=None, value_2=None):
    url = f"{c.host}/devices/"
    headers = c.AUTH_HEADERS
    params = {filter_1: value_1, filter_2: value_2}
    response = requests.get(url, headers=headers, params=params)
    print(response.text)
    return response

