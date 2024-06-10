import datetime
import os
import turtle

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "../"))

import freezegun
from solid.auth import Auth
from solid.solid_api import SolidAPI
from datetime import datetime, timedelta

from scripts.solid_pod_updater_ttl import SolidPodUpdaterTTL


class MockRequest:
    def __init__(self):
        self.text = ""

    def json(self):
        return {
            "o3": 1.0,
            "no2": 2.0,
            "pm25": 3.0,
            "pm10": 4.0,
            "humidity": 5.0,
            "temperature": 6.0,
            "latitude": 7.0,
            "longitude": 8.0,
        }


# Checks that environment variables are assigned
def test_attributes_set_correctly(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    # Assert
    assert updater.pod_provider == pod_provider
    assert updater.pod_endpoint == pod_endpoint
    assert updater.aqm_folder == aqm_folder
    assert updater.aqm_name == aqm_name
    assert updater.polling_frequency == polling_frequency
    assert updater.wot_url == wot_url
    assert updater.wot_port == wot_port
    assert updater.retry_time == retry_time


# Checks that the Solid Pod login functionality works
def test_login(mocker):
    # Arrange
    login = mocker.patch.object(Auth, "login")

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    # Assert
    login.assert_called_once_with(pod_provider, pod_username, pod_password)


# Checks that the AQM properties are retrieved
def test_request_header_from_wot_interface(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    request = mocker.patch("requests.get", return_value=MockRequest())

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    header = updater.request_header_from_wot_interface()

    # Assert
    assert header == "o3,no2,pm25,pm10,humidity,temperature,latitude,longitude"

    request.assert_called_once_with(
        f"{wot_url}:{wot_port}/properties",
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=None,
    )


# Checks exception handling if unable to retrieve the AQM properties
def test_error_request_header_from_wot_interface(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    header_unavailable = mocker.patch(
        "time.sleep", return_value=None, side_effect=SystemExit
    )

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 0
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.request_header_from_wot_interface()
    except SystemExit:
        # Assert
        header_unavailable.assert_called()


# Checks that AQM data is retrieved
def test_request_data_from_wot_interface(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    request = mocker.patch("requests.get", return_value=MockRequest())

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    data = updater.request_data_from_wot_interface()

    # Assert
    assert data == "1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0"

    request.assert_called_once_with(
        f"{wot_url}:{wot_port}/properties",
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=None,
    )


# Checks exception handling if unable to retrieve AQM data
def test_error_request_data_from_wot_interface(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    data_unavailable = mocker.patch(
        "time.sleep", return_value=None, side_effect=SystemExit
    )

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 0
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.request_data_from_wot_interface()
    except SystemExit:
        # Assert
        data_unavailable.assert_called_once()


# Checks that data is correctly retrieved and stored in an existing folder in Solid Pod
def test_request_loop(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch("time.sleep", side_effect=InterruptedError)
    exists = mocker.patch.object(SolidAPI, "item_exists", return_value=True)
    create_folder = mocker.patch.object(SolidAPI, "create_folder", return_value=True)
    put = mocker.patch.object(SolidAPI, "put_file", return_value=True)
    request = mocker.patch("requests.get", return_value=MockRequest())

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.start()
    except InterruptedError:
        pass

    # Assert
    request.assert_called()
    exists.assert_called()
    create_folder.assert_not_called()
    put.assert_called()


# Checks that a folder is created in the Solid Pod and data is correctly retrieved and stored there
def test_request_loop_no_files_yet_exist(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch("time.sleep", side_effect=InterruptedError)
    exists = mocker.patch.object(SolidAPI, "item_exists", return_value=False)
    create_folder = mocker.patch.object(SolidAPI, "create_folder", return_value=True)
    put = mocker.patch.object(SolidAPI, "put_file", return_value=True)
    request = mocker.patch("requests.get", return_value=MockRequest())

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8889
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.start()
    except InterruptedError:
        pass

    # Assert
    request.assert_called()
    exists.assert_called()
    create_folder.assert_called()
    put.assert_called()


# Checks exception handling if unable to check if Solid Pod folder exists
def test_error_folder_exists(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    folder_unavailable = mocker.patch(
        "time.sleep", return_value=None, side_effect=SystemExit
    )

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "http://127.0.0.1"
    wot_port = 8080
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.start()
    except SystemExit:
        # Assert
        folder_unavailable.assert_called_once()


# Checks the Turtle formatting works correctly
@freezegun.freeze_time("2022-03-21 11:19:47.949456")
def test_generate_turtle_rdf():
    # Arrange
    headers = [
        "o3",
        "no2",
        "pm25",
        "pm10",
        "humidity",
        "temperature",
        "latitude",
        "longitude",
    ]
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]

    # Act
    turtle_output = SolidPodUpdaterTTL.generate_turtle_rdf(
        datetime.now(), headers, data
    )

    expected_output = [
        b"@prefix ns1: <http://www.w3.org/ns/ssn/>",
        b"prefix xsd: <http://www.w3.org/2001/XMLSchema#>",
        b'ns1:resultTime "2022-03-21T11:19:47.949456"^^xsd:dateTime',
        b'ns1:Sensor "no2"',
        b"ns1:hasSimpleResult 2e+00",
        b'ns1:Sensor "pm10"',
        b"ns1:hasSimpleResult 4e+00",
        b'ns1:Sensor "temperature"',
        b"ns1:hasSimpleResult 6e+00",
        b'ns1:Sensor "o3"',
        b"ns1:hasSimpleResult 1e+00",
        b'ns1:Sensor "latitude"',
        b"ns1:hasSimpleResult 7e+00",
        b'ns1:Sensor "longitude"',
        b"ns1:hasSimpleResult 8e+00",
        b'ns1:Sensor "humidity"',
        b"ns1:hasSimpleResult 5e+00",
        b'ns1:Sensor "pm25"',
        b"ns1:hasSimpleResult 3e+00",
    ]

    # Assert
    for elem in expected_output:
        assert elem in turtle_output


# Checks that the file hashing is executed every interval
@freezegun.freeze_time("2022-03-21 11:19:47.949456")
def test_hash_execution(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch("time.sleep", side_effect=InterruptedError)
    mocker.patch.object(SolidAPI, "item_exists", return_value=True)
    mocker.patch.object(SolidAPI, "create_folder", return_value=True)
    mocker.patch.object(SolidAPI, "put_file", return_value=True)
    mocker.patch.object(SolidAPI, "get", return_value=MockRequest())
    mocker.patch("requests.get", return_value=MockRequest())
    hash = mocker.patch.object(SolidPodUpdaterTTL, "hash_file")

    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"
    polling_frequency = 60
    wot_url = "127.0.0.1"
    wot_port = 8080
    retry_time = 30

    # Act
    updater = SolidPodUpdaterTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
        polling_frequency=polling_frequency,
        wot_url=wot_url,
        wot_port=wot_port,
        retry_time=retry_time,
    )

    try:
        updater.start()
    except InterruptedError:
        pass

    # Assert
    with freezegun.freeze_time("2022-03-21 11:19:47.949456") as frozen_date_time:
        hash.assert_called_once()
        frozen_date_time.move_to(datetime.now() + timedelta(seconds=polling_frequency))
        hash.assert_called_once()
