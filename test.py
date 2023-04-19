import random
import time
import uuid

import allure
import pytest
import requests

import const as c
import mainfunc as mf


# Получение результатов (GET/events) по панорамным скришотам
@pytest.mark.panoramic
@allure.title('Получение результатов (GET/events) по панорамным скришотам')
def test_get_panoramic_events():
    panoramic_image_type = 1
    response = mf.get_events(c.IMAGE_TYPE, panoramic_image_type)
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][_][c.IMAGE_TYPE] == panoramic_image_type
        assert response.json()[c.RESULTS][_][c.DEVICE] is None


# Проверка отсутствия результатов обработки архивов из других источников
@pytest.mark.panoramic
@allure.title('Проверка отсутствия результатов обработки архивов из других источников')
def test_check_for_results_from_another_sources():
    timestamp_list = []
    values = [0, 1, 2]
    for _ in range(len(values)):
        response = mf.get_events(c.IMAGE_TYPE, _)
        timestamp_list.append(response.json()[c.RESULTS][0][c.TIMESTAMP])

    iteration_uuid_1 = mf.get_list_iterations(c.SOURCE_ID).json()[c.DATA][c.ITERATIONS][0][c.UUID]
    time.sleep(5)

    mf.upload_archive()

    iteration_uuid_2 = mf.get_list_iterations(c.SOURCE_ID).json()[c.DATA][c.ITERATIONS][0][c.UUID]
    time.sleep(5)

    assert iteration_uuid_1 != iteration_uuid_2

    for i in range(len(values)):
        repeated_response = mf.get_events(c.IMAGE_TYPE, i)
        assert repeated_response.json()[c.RESULTS][0][c.TIMESTAMP] == timestamp_list[i]


# Актуализация списка расписаний ЕЦХД
@pytest.mark.zkh
@allure.title('Актуализация списка расписаний ЕЦХД')
def test_get_list_of_actual_schedules_ECHD():
    url = f"{c.host}/schedules/refresh"
    headers = c.AUTH_HEADERS
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert response.json()[c.MSG] == 'OK'


# Создание задачи на обработку – проверка функционала ЖКХ
@allure.title('Создание задачи на обработку – проверка функционала ЖКХ')
@pytest.mark.zkh
def test_create_task():
    response = mf.create_task(labels=c.RANDOM_LABELS(),
                              detectors=c.RANDOM_DETECTORS, schedule_id=c.SCHEDULE_ID)
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    mf.delete_task_from_db(response.json()[c.TASK_ID])


# Создание задачи с указанием некорректных параметров «labels»/«detectors»
@pytest.mark.zkh
@pytest.mark.parametrize('labels', [random.random(), None, ['101']])
@pytest.mark.parametrize('detectors', [random.random(), None, ['10']])
@allure.title('Создание задачи с указанием некорректных параметров «labels»/«detectors»')
def test_create_task_with_incorrect_label_or_detector(labels, detectors):
    if labels != None and detectors != None:
        response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
        assert response.status_code == 400


# Создание задачи дублированной задачи (с идентичными «labels»/«detectors»)
@pytest.mark.zkh
@allure.title('Создание задачи дублированной задачи (с идентичными «labels»/«detectors»)')
def test_create_task_with_existed_params():
    detectors = c.RANDOM_DETECTORS
    labels = c.RANDOM_LABELS()

    response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]

    create = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    assert create.status_code == 400
    assert create.json()[c.MSG] == "task with such parameters already exist"

    mf.delete_task_from_db(task_id)


# Создание задачи с несуществующим расписанием («schedule»)
@pytest.mark.zkh
@allure.title('Создание задачи с несуществующим расписанием («schedule»)')
def test_create_task_with_non_existed_schedule():
    response = mf.create_task(c.RANDOM_LABELS(),
                              [random.randint(5, 20)], str(uuid.uuid4()))
    assert response.status_code == 409
    assert response.json()[c.MSG] == "external system error"


# Создание задачи с некорректным расписанием («schedule»)
@pytest.mark.zkh
@allure.title('Создание задачи с некорректным расписанием («schedule»)')
def test_create_task_with_incorrect_format_schedule():
    response = mf.create_task(c.RANDOM_LABELS(),
                              c.RANDOM_DETECTORS, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == 'validate'


# Создание задачи при отсутствии одного из обязательных параметров – без указания «schedule»)
@pytest.mark.zkh
@allure.title('Создание задачи при отсутствии одного из обязательных параметров – без указания «schedule»)')
def test_create_task_without_schedule():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, None)
    assert response.status_code == 400
    assert response.json()[c.MSG] == 'validate'


# Создание задачи при отсутствии одного из обязательных параметров в запросе – пустой параметр «labels»
@pytest.mark.zkh
@allure.title('Создание задачи при отсутствии одного из обязательных параметров в запросе – пустой параметр «labels»')
def test_create_task_without_label():
    response = mf.create_task(labels=None,
                              detectors=c.RANDOM_DETECTORS, schedule_id=c.SCHEDULE_ID)
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    mf.delete_task_from_db(response.json()[c.TASK_ID])


# Создание задачи при отсутствии обязательных параметров в запросе – пустые параметры «labels» и «detectors»
@pytest.mark.zkh
@allure.title(
    'Создание задачи при отсутствии обязательных параметров в запросе – пустые параметры «labels» и «detectors»')
def test_create_task_without_labels_and_detectors():
    response = mf.create_task(labels=None, detectors=None, schedule_id=c.SCHEDULE_ID)
    assert response.status_code == 400
    assert response.json()[c.MSG] == 'validate'


# Получение списка созданных заданий - проверка наличия задачи в списке созданных заданий
@pytest.mark.zkh
@allure.title('Получение списка созданных заданий - проверка наличия задачи в списке созданных заданий')
def test_create_and_get_task_from_tasks_list_show_cancelled_true():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200

    task_list = []

    search = mf.get_tasks(showCancelled='true')
    for _ in range(len(search.json()[c.TASKS])):
        task_list.append(search.json()[c.TASKS][_][c.ID])
    if task_id in task_list:
        assert 1 == 1
    else:
        assert 1 == 2

    mf.delete_task_from_db(task_id)


# Получение списка задач без параметра «showCancelled»
@pytest.mark.zkh
@allure.title('Получение списка задач без параметра «showCancelled»')
def test_create_and_get_task_from_tasks_list_wothout_show_cancelled():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200

    task_list = []

    search = mf.get_tasks()
    for _ in range(len(search.json()[c.TASKS])):
        task_list.append(search.json()[c.TASKS][_][c.ID])
    if task_id in task_list:
        assert 1 == 1
    else:
        assert 1 == 2

    mf.delete_task_from_db(task_id)


# Получение списка всех задач
@pytest.mark.zkh
@allure.title('Получение списка всех задач')
def test_get_tasks():
    response = mf.get_tasks()
    assert response.status_code == 200
    assert type(response.json()[c.TASKS]) == list


# Получение статуса задания
@pytest.mark.zkh
@allure.title('Получение статуса задания')
def test_get_task_status():
    labels = c.RANDOM_LABELS()
    response = mf.create_task(labels, c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]

    result = mf.get_task_status(task_id)
    mf.delete_task_from_db(task_id)

    assert result.status_code == 200
    assert result.json()[c.LABELS][0] in labels
    assert result.json()[c.SCHEDULES] == [c.SCHEDULE_ID]


# Получение статуса задачи по несуществующему taskId
@pytest.mark.zkh
@allure.title('Получение статуса задачи по несуществующему taskId')
def test_get_non_existed_task_status():
    response = mf.get_task_status(str(uuid.uuid4()))
    assert response.status_code == 404
    assert response.json()[c.MSG] == 'taskUuid not found'


# Получение статуса задачи с некорректным taskId(не соотвествует формату uuid)
@pytest.mark.zkh
@allure.title('Получение статуса задачи с некорректным taskId(не соотвествует формату uuid)')
def test_get_wrong_format_task_status():
    response = mf.get_task_status(str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == 'validate'


# Получение результатов анализа по задаче
@pytest.mark.zkh
@allure.title('Получение результатов анализа по задаче')
def test_get_results():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]

    result = mf.get_task_result(task_id)
    assert result.status_code == 200
    assert type(result.json()[c.RESULTS]) == list

    mf.delete_task_from_db(task_id)


# Получение результатов анализа по задаче с некорректным taskId (не соответствует формату uuid)
@pytest.mark.zkh
@allure.title('Получение результатов анализа по задаче с некорректным taskId (не соответствует формату uuid)')
def test_get_wrong_format_task_results():
    response = mf.get_task_result(str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == 'validate'


# Получение результатов анализа по задаче по несуществующему taskId
@pytest.mark.zkh
@allure.title('Получение результатов анализа по задаче по несуществующему taskId')
def test_get_non_existed_task_results():
    response = mf.get_task_result(str(uuid.uuid4()))
    assert response.status_code == 404
    assert response.json()[c.MSG] == 'taskUuid not found'


# Приостановить задачу
@pytest.mark.zkh
@allure.title('Приостановить задачу')
def test_stop_task():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]

    pause = mf.pause_task(task_id)

    assert pause.status_code == 200
    assert pause.json()[c.MSG] == 'OK'

    mf.delete_task_from_db(task_id)


# Приостановить задачу, которая уже на паузе
@pytest.mark.zkh
@allure.title('Приостановить задачу, которая уже на паузе')
def test_pause_already_paused_task():
    response = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]

    mf.pause_task(task_id)
    repeated_pause = mf.pause_task(task_id)

    assert repeated_pause.status_code == 400
    assert repeated_pause.json()[c.MSG] == 'task not running'

    mf.delete_task_from_db(task_id)


# Изменение статуса задачи «cancelled» на «paused»
@pytest.mark.zkh
@allure.title('Изменение статуса задачи «cancelled» на «paused»')
def test_pause_cancelled_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    stop = mf.stop_task(task_id)
    assert stop.status_code == 200

    pause = mf.pause_task(task_id)
    assert pause.status_code == 400
    assert pause.json()[c.MSG] == 'incorrect request'

    mf.delete_task_from_db(task_id)


# Возобновление задачи - изменение статуса задачи «paused» на «inProgress»
@pytest.mark.zkh
@allure.title('Возобновление задачи - изменение статуса задачи «paused» на «inProgress»')
def test_resume_paused_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    mf.pause_task(task_id)

    resume = mf.resume_task(task_id)
    assert resume.status_code == 200
    assert resume.json()[c.MSG] == 'OK'


# Изменение статуса задачи «inProgress» на «inProgress»
@pytest.mark.zkh
@allure.title('Изменение статуса задачи «inProgress» на «inProgress»')
def test_resume_resumed_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    response = mf.resume_task(task_id)

    assert response.status_code == 400
    assert response.json()[c.MSG] == 'task not paused'

    mf.delete_task_from_db(task_id)


# Изменение статуса задачи «cancelled» на «inProgress»
@pytest.mark.zkh
@allure.title('Изменение статуса задачи «cancelled» на «inProgress»')
def test_resume_cancelled_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    stop = mf.stop_task(task_id)
    assert stop.status_code == 200
    assert stop.json()[c.MSG] == 'OK'

    resume = mf.resume_task(task_id)
    assert resume.status_code == 400
    assert resume.json()[c.MSG] == 'task not paused'

    mf.delete_task_from_db(task_id)


# Отмена задачи - изменение статуса задачи «inProgress» на «cancelled»
@pytest.mark.zkh
@allure.title('Отмена задачи - изменение статуса задачи «inProgress» на «cancelled»')
def test_cancel_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    cancel = mf.stop_task(task_id)

    assert cancel.status_code == 200
    assert cancel.json()[c.MSG] == 'OK'

    mf.delete_task_from_db(task_id)


# Изменение статуса задачи «paused» на «cancelled»
@pytest.mark.zkh
@allure.title('Изменение статуса задачи «paused» на «cancelled»')
def test_cancel_paused_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    pause = mf.pause_task(task_id)

    assert pause.status_code == 200

    cancel = mf.stop_task(task_id)

    assert cancel.status_code == 200
    assert cancel.json()[c.MSG] == 'OK'

    mf.delete_task_from_db(task_id)


# Изменение статуса задачи «cancelled» на «cancelled»
@pytest.mark.zkh
@allure.title('Изменение статуса задачи «cancelled» на «cancelled»')
def test_cancel_cancelled_task():
    task_id = mf.create_task(c.RANDOM_LABELS(), c.RANDOM_DETECTORS, c.SCHEDULE_ID).json()[c.TASK_ID]
    mf.stop_task(task_id)
    cancel = mf.stop_task(task_id)

    assert cancel.status_code == 400
    assert cancel.json()[c.MSG] == 'task cannot be cancelled'

    mf.delete_task_from_db(task_id)


# Отправка экспертной оценки по скриншоту
@pytest.mark.zkh
@allure.title('Отправка экспертной оценки по скриншоту')
def test_send_expert_answer():
    screenshot_id = mf.get_screenshot_id_from_db()
    response = mf.send_expert_answer(screenshot_id)
    assert response.status_code == 200
    assert response.json()[c.MSG] == 'OK'


# Создание задачи на обработку, в поле "detectors" указывается значение массива [7,8,9,10,11,12,13,14,15,16,17,18]
# Получение статуса задания
# Получение результатов анализа по задаче, в поле "labels" получаем значение массива [71,81,91,101,111,121,131,141,151,161,171,181]
@pytest.mark.zkh
@allure.title('создание задачи, ЖКХ')
@allure.description(
    'Создание задачи на обработку, в поле "detectors" указывается значение массива [7,8,9,10,11,12,13,14,15,16,17,18]'
    'Получение статуса задания'
    'Получение результатов анализа по задаче, в поле "labels" получаем значение массива [71,81,91,101,111,121,131,141,151,161,171,181]')
def test_create_zkh_task():
    labels = c.ZKH_LABELS
    detectors = c.ZKH_DETECTORS
    response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    status = mf.get_task_status(task_id)
    assert status.status_code == 200
    assert status.json()[c.LABELS] == labels
    assert status.json()[c.DETECTORS] == detectors

    result = mf.get_task_result(task_id)
    assert result.status_code == 200
    assert type(result.json()[c.RESULTS]) == list

    mf.delete_task_from_db(task_id)


# Создание задачи на обработку, в поле "detectors" указывается значение массива [19,20,21,22,23,24,25,26]
# Получение статуса задания
# Получение результатов анализа по задаче, в поле "labels" получаем значение массива [191,201,211,221,231,241,251,261]
@pytest.mark.zkh
@allure.title('создание задачи, ЖКХ+')
@allure.description(
    'Создание задачи на обработку, в поле "detectors" указывается значение массива [19,20,21,22,23,24,25,26]'
    'Получение статуса задания'
    'Получение результатов анализа по задаче, в поле "labels" получаем значение массива [191,201,211,221,231,241,251,261]')
def test_create_zkh_plus_task():
    labels = c.ZKH_PLUS_LABELS
    detectors = c.ZKH_PLUS_DETECTORS
    response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    status = mf.get_task_status(task_id)
    assert status.status_code == 200
    assert status.json()[c.LABELS] == labels
    assert status.json()[c.DETECTORS] == detectors

    result = mf.get_task_result(task_id)
    assert result.status_code == 200
    assert type(result.json()[c.RESULTS]) == list

    mf.delete_task_from_db(task_id)


# Создание задачи на обработку, в поле "detectors" указывается значение массива [5,6]
# Получение статуса задания
# Получение результатов анализа по задаче, в поле "labels" получаем значение массива [51,61]
@pytest.mark.zkh
@allure.title('создание задачи, ИНС МАГАЗИНЫ')
@allure.description('Создание задачи на обработку, в поле "detectors" указывается значение массива [5,6]'
                    'Получение статуса задания'
                    'Получение результатов анализа по задаче, в поле "labels" получаем значение массива [51,61]')
def test_create_zkh_shops_task():
    labels = c.ZKH_SHOPS_LABELS
    detectors = c.ZKH_SHOPS_DETECTORS
    response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    status = mf.get_task_status(task_id)
    assert status.status_code == 200
    assert status.json()[c.LABELS] == labels
    assert status.json()[c.DETECTORS] == detectors

    result = mf.get_task_result(task_id)
    assert result.status_code == 200
    assert type(result.json()[c.RESULTS]) == list

    mf.delete_task_from_db(task_id)


# Создание задачи на обработку, в поле "detectors" указывается значение массива [27,28,29,30,31]
# Получение статуса задания
# Получение результатов анализа по задаче, в поле "labels" получаем значение массива [271,281,291,301,311]
@pytest.mark.zkh
@allure.title('создание задачи, ЖКХ++')
@allure.description('Создание задачи на обработку, в поле "detectors" указывается значение массива [27,28,29,30,31]'
                    'Получение статуса задания'
                    'Получение результатов анализа по задаче, в поле "labels" получаем значение массива [271,281,291,301,311]')
def test_create_zkh_new_task():
    labels = c.ZKH_NEW_LABELS
    detectors = c.ZKH_NEW_DETECTORS
    response = mf.create_task(labels, detectors, c.SCHEDULE_ID)
    task_id = response.json()[c.TASK_ID]
    assert response.status_code == 200
    assert type(response.json()[c.TASK_ID]) == str

    status = mf.get_task_status(task_id)
    assert status.status_code == 200
    assert status.json()[c.LABELS] == labels
    assert status.json()[c.DETECTORS] == detectors

    result = mf.get_task_result(task_id)
    assert result.status_code == 200
    assert type(result.json()[c.RESULTS]) == list

    mf.delete_task_from_db(task_id)


@pytest.mark.gin
@allure.title('Получение списка событий')
def test_get_events():
    response = mf.get_events()
    assert response.status_code == 200
    assert type(response.json()[c.RESULTS]) == list


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "page = 0" (счёт страниц начинается с 0 (0=1))')
def test_get_events_page_0():
    response = mf.get_events(c.PAGE, 0)
    assert response.status_code == 200
    assert type(response.json()[c.RESULTS]) == list


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "page = 1" (счёт страниц начинается с 0 (1=2))')
def test_get_events_page_1():
    response = mf.get_events(c.PAGE, 1)
    assert response.status_code == 200
    assert type(response.json()[c.RESULTS]) == list


@pytest.mark.gin
@allure.title('Получение списка событий некорректным параметром "page"')
def test_get_events_incorrect_page_number():
    response = mf.get_events(c.PAGE, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "page", на котором нет результатов')
def test_get_events_page_without_results():
    response = mf.get_events(c.PAGE, 99999999999999999)
    assert response.status_code == 200
    assert response.json()[c.RESULTS] is None


@pytest.mark.gin
@allure.title('Получение списка событий с некорректным параметром "showBy"')
def test_get_events_incorrect_show_by():
    response = mf.get_events(c.SHOW_BY, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "from_dt"')
def test_get_events_from_dt():
    timestamp = mf.get_events().json()[c.RESULTS][0][c.TIMESTAMP]
    response = mf.get_events(c.FROM_DT, timestamp - 1)
    assert response.status_code == 200
    assert type(response.json()[c.RESULTS]) == list
    assert type(response.json()[c.RESULTS][0][c.ID]) == int
    for _ in range(len(response.json()[c.RESULTS])):
        assert timestamp <= response.json()[c.RESULTS][_][c.TIMESTAMP]


@pytest.mark.gin
@allure.title('Получение списка событий с некорректным параметром «from_dt»')
def test_get_events_with_incorrect_from_dt():
    response = mf.get_events(c.FROM_DT, 99999999999)
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.VALIDATE


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "from_dt" не в формате Unix Timestamp')
def test_get_events_wrong_format_from_dt():
    response = mf.get_events(c.FROM_DT, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "to_dt"')
def test_get_events_to_dt():
    timestamp = mf.get_events().json()[c.RESULTS][0][c.TIMESTAMP]
    response = mf.get_events(c.TO_DT, timestamp + 1)
    assert response.status_code == 200
    assert type(response.json()[c.RESULTS][0][c.ID]) == int
    for _ in range(len(response.json()[c.RESULTS])):
        assert timestamp >= response.json()[c.RESULTS][_][c.TIMESTAMP]


@pytest.mark.gin
@allure.title('Получение списка событий с некорректным параметром «to_dt»')
def test_get_events_with_incorrect_to_dt():
    response = mf.get_events(c.TO_DT, 99999999999)
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.VALIDATE


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "to_dt" не в формате Unix Timestamp')
def test_get_events_wrong_format_to_dt():
    response = mf.get_events(c.TO_DT, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@pytest.mark.parametrize('image_type', [1, 2, 0])
@allure.title('Получение списка событий с параметром "image_type"')
def test_get_events_image_type(image_type):
    response = mf.get_events(c.IMAGE_TYPE, image_type)
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert (response.json()[c.RESULTS][_][c.IMAGE_TYPE]) == image_type


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими параметрами "image_type"')
def test_get_events_with_2_different_image_types():
    odh_image_type = 0
    bpla_image_type = 2
    response = mf.get_events(filter=c.IMAGE_TYPE, value=odh_image_type,
                             filter2=c.IMAGE_TYPE, value2=bpla_image_type)
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert (response.json()[c.RESULTS][_][c.IMAGE_TYPE] == odh_image_type or
                response.json()[c.RESULTS][_][c.IMAGE_TYPE] == bpla_image_type)


@pytest.mark.gin
@allure.title('Получение списка событий с несуществующим параметром "image_type"')
def test_get_events_nonexist_image_type():
    response = mf.get_events(c.IMAGE_TYPE, 10)
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.VALIDATE


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими и несуществующими параметрами "image_type"')
def test_get_events_exist_and_nonexist_image_types():
    response = mf.get_events(filter=c.IMAGE_TYPE, value=random.randint(0, 2),
                             filter2=c.IMAGE_TYPE, value2=str(uuid.uuid4()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с некорректным параметром "image_type"')
def test_get_events_wrong_format_image_type():
    response = mf.get_events(c.IMAGE_TYPE, str(random.random()))
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "device"')
def test_get_events_with_device():
    device = mf.get_events(c.IMAGE_TYPE, 0).json()[c.RESULTS][0][c.DEVICE]
    response = mf.get_events(c.DEVICE, device)
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][_][c.DEVICE] == device


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими параметрами "device"')
def test_get_events_2_devices():
    device_2 = str(uuid.uuid4())
    get_events = mf.get_events(c.IMAGE_TYPE, 0)
    device_1 = get_events.json()[c.RESULTS][0][c.DEVICE]
    # print(device_1)
    for _ in range(len(get_events.json()[c.RESULTS])):
        if device_1 != get_events.json()[c.RESULTS][_][c.DEVICE]:
            device_2 = get_events.json()[c.RESULTS][_][c.DEVICE]
            break

    response = mf.get_events(filter=c.DEVICE, value=device_1 + ',' + device_2)
    assert response.status_code == 200
    for device in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][device][c.DEVICE] == device_1 \
               or response.json()[c.RESULTS][device][c.DEVICE] == device_2


@pytest.mark.gin
@allure.title('Получение списка событий с несуществующим параметром "device"')
def test_get_events_nonexist_device():
    response = mf.get_events(c.DEVICE, str(uuid.uuid4()))
    assert response.status_code == 200
    assert response.json()[c.RESULTS] is None


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими и несуществующими параметрами "device"')
def test_get_events_exist_and_nonexist_devices():
    device = mf.get_events(c.IMAGE_TYPE, 0).json()[c.RESULTS][0][c.DEVICE]
    response = mf.get_events(c.DEVICE, device + ',' + str(uuid.uuid4()))
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][_][c.DEVICE] == device


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "camera"')
def test_get_events_with_camera():
    camera = mf.get_events(c.IMAGE_TYPE, random.randint(0, 1)).json()[c.RESULTS][0][c.CAMERA]
    response = mf.get_events(c.CAMERA, camera)
    assert response.status_code == 200
    for cam in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][cam][c.CAMERA] == camera


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими параметрами "camera"')
def test_get_events_with_2_cameras():
    camera_2 = str(uuid.uuid4())
    get_events = mf.get_events(c.IMAGE_TYPE, random.randint(0, 1))
    camera_1 = get_events.json()[c.RESULTS][0][c.CAMERA]
    # print(camera_1)
    for _ in range(len(get_events.json()[c.RESULTS])):
        if camera_1 != get_events.json()[c.RESULTS][_][c.CAMERA]:
            camera_2 = get_events.json()[c.RESULTS][_][c.CAMERA]
            break

    response = mf.get_events(filter=c.CAMERA, value=camera_1 + ',' + camera_2)
    assert response.status_code == 200
    for cam in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][cam][c.CAMERA] == camera_1 \
               or response.json()[c.RESULTS][cam][c.CAMERA] == camera_2


@pytest.mark.gin
@allure.title('Получение списка событий с несуществующим параметром "camera"')
def test_get_events_with_nonexist_camera():
    response = mf.get_events(c.CAMERA, str(uuid.uuid4()))
    assert response.status_code == 200
    assert response.json()[c.RESULTS] is None


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими и несуществующими параметрами "camera"')
def test_get_events_with_exist_and_nonexist_cameras():
    camera = mf.get_events(c.IMAGE_TYPE, 0).json()[c.RESULTS][0][c.CAMERA]
    response = mf.get_events(c.CAMERA, camera + ',' + str(uuid.uuid4()))
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][_][c.CAMERA] == camera


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "label"')
def test_get_events_with_label():
    label = mf.get_events().json()[c.RESULTS][0][c.ISSUES][0][c.LABEL]
    response = mf.get_events(c.LABEL, label)
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL] == label


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими параметрами "label"')
def test_get_events_with_2_labels():
    label_2 = '00-000'
    get_events = mf.get_events(c.IMAGE_TYPE, random.randint(0, 2))
    label_1 = get_events.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL]
    # print(camera_1)
    for _ in range(len(get_events.json()[c.RESULTS])):
        if label_1 != get_events.json()[c.RESULTS][_][c.ISSUES][0][c.LABEL]:
            label_2 = get_events.json()[c.RESULTS][_][c.ISSUES][0][c.LABEL]
            break

    response = mf.get_events(filter=c.LABEL, value=label_1 + ',' + label_2)
    assert response.status_code == 200
    print(response.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL])
    for label in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][label][c.ISSUES][0][c.LABEL] == label_1 \
               or response.json()[c.RESULTS][label][c.ISSUES][0][c.LABEL] == label_2


@pytest.mark.gin
@allure.title('Получение списка событий с несуществующим параметром "label"')
def test_get_events_non_exist_label():
    response = mf.get_events(c.LABEL, '30-541')
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.VALIDATE


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими и несуществующими параметрами "label"')
def test_get_events_exist_and_non_exist_labels():
    get_events = mf.get_events(c.IMAGE_TYPE, random.randint(0, 2))
    label = get_events.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL]
    response = mf.get_events(c.LABEL, label + ',' + '34-524')
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.VALIDATE


@pytest.mark.gin
@allure.title('Получение списка событий с параметром "id"')
def test_get_events_with_id():
    image_id = mf.get_events().json()[c.RESULTS][0][c.ID]
    response = mf.get_events(c.ID, image_id)
    assert response.status_code == 200
    assert len(response.json()[c.RESULTS]) == 1
    assert response.json()[c.RESULTS][0][c.ID] == image_id


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими параметрами "id"')
def test_get_events_with_2_ids():
    get_events = mf.get_events()
    image_id_1 = get_events.json()[c.RESULTS][0][c.ID]
    image_id_2 = get_events.json()[c.RESULTS][1][c.ID]
    response = mf.get_events(c.ID, str(image_id_1) + ',' + str(image_id_2))
    assert response.status_code == 200
    for _ in range(len(response.json()[c.RESULTS])):
        assert response.json()[c.RESULTS][_][c.ID] == image_id_1 \
               or response.json()[c.RESULTS][_][c.ID] == image_id_2


@pytest.mark.gin
@allure.title('Получение списка событий с несуществующим параметром "id"')
def test_get_events_non_exist_image_id():
    response = mf.get_events(c.ID, random.randint(9999999999999, 11111111111111111))
    assert response.status_code == 200
    assert response.json()[c.RESULTS] is None


@pytest.mark.gin
@allure.title('Получение списка событий с несколькими существующими и несуществующими параметрами "id"')
def test_get_events_exist_and_non_exist_ids():
    image_id = mf.get_events().json()[c.RESULTS][0][c.ID]
    response = mf.get_events(c.ID, str(image_id) + ',' + str(random.randint(9999999999999, 11111111111111111)))
    assert response.status_code == 200
    assert len(response.json()[c.RESULTS]) == 1
    assert response.json()[c.RESULTS][0][c.ID] == image_id


@pytest.mark.gin
@allure.title('Получение списка событий с незаполненным параметром "id"')
def test_get_events_with_empty_id():
    response = mf.get_events(c.ID, None)
    assert response.status_code == 400
    assert response.json()[c.MSG] == c.BIND


@pytest.mark.gin
@allure.title('Получение списка событий с корректными параметрами "page", "showBy", "from_dt", "to_dt", "image_type", "label"')
def test_get_events_all_filters():
    event = mf.get_events()
    image_type = event.json()[c.RESULTS][0][c.IMAGE_TYPE]
    timestamp = event.json()[c.RESULTS][0][c.TIMESTAMP]
    label = event.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL]

    response = mf.get_events(filter=c.IMAGE_TYPE, value=image_type, filter2=c.FROM_DT, value2=timestamp - 1,
                             filter3=c.TO_DT, value3=timestamp + 1, filter4=c.LABEL, value4=label)
    assert response.status_code == 200
    assert response.json()[c.RESULTS][0][c.IMAGE_TYPE] == image_type
    assert response.json()[c.RESULTS][0][c.ISSUES][0][c.LABEL] == label
    assert response.json()[c.RESULTS][0][c.TIMESTAMP] == timestamp
