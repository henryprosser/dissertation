import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "../"))

from webthing import Value

from scripts.virtual_aqm import VirtualAQM, run_server

# Checks that the server starts correctly
def test_run_server(mocker, capfd):
    server_start = mocker.patch("scripts.virtual_aqm.WebThingServer.start")

    run_server(
        aqm_latitude=0.0,
        aqm_longitude=0.0,
        aqm_name="name",
        aqm_description="description",
        aqm_polling_time=60000,
        port=8080,
    )

    server_start.assert_called_once()
    out, err = capfd.readouterr()
    assert out == f"Starting the server.\n"
    assert err == ""


# Checks that latest readings are retrieved correctly
def test_get_latest_reading(mocker):
    mocker.patch("scripts.virtual_aqm.random.random", return_value=1.0)

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    assert aqm_thing.get_latest_reading() == 35.0


# Checks that o3 reading updates correctly
def test_update_o3(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_o3_reading()
    update_value.assert_called_once_with(1.0)


# Checks that no2 reading updates correctly
def test_update_no2(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_no2_reading()
    update_value.assert_called_once_with(1.0)


# Checks that pm2.5 reading updates correctly
def test_update_pm25(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_pm25_reading()
    update_value.assert_called_once_with(1.0)


# Checks that pm10 reading updates correctly
def test_update_pm10(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_pm10_reading()
    update_value.assert_called_once_with(1.0)


# Checks that humidity reading updates correctly
def test_update_humidity(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_humidity_reading()
    update_value.assert_called_once_with(1.0)


# Checks that temperature reading updates correctly
def test_update_temperature(mocker):

    mocker.patch.object(VirtualAQM, "get_latest_reading", return_value=1.0)

    update_value = mocker.patch.object(Value, "notify_of_external_update")

    latitude = 1.0
    longitude = 2.0
    name = "Name"
    description = "Description"
    polling_time = 120000

    aqm_thing = VirtualAQM(
        aqm_latitude=latitude,
        aqm_longitude=longitude,
        aqm_name=name,
        aqm_description=description,
        aqm_polling_time=polling_time,
    )

    aqm_thing.update_temperature_reading()
    update_value.assert_called_once_with(1.0)
