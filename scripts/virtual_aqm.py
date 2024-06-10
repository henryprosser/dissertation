import os
import random
from pathlib import Path

import dotenv
import tornado
from webthing import Event, Property, SingleThing, Thing, Value, WebThingServer


class VirtualAQM(Thing):
    def __init__(
        self,
        aqm_latitude,
        aqm_longitude,
        aqm_name,
        aqm_description,
        aqm_polling_time,
        o3_initial=0.0,
        no2_initial=0.0,
        pm25_initial=0.0,
        pm10_initial=0.0,
        humidity_initial=0.0,
        temperature_initial=0.0,
    ):
        Thing.__init__(
            self,
            f"urn:dev:ops:{''.join(aqm_name.split()).lower()}",
            aqm_name,
            ["AQM"],
            aqm_description,
        )

        self.aqm_latitude = aqm_latitude
        self.aqm_longitude = aqm_longitude
        self.aqm_polling_time = aqm_polling_time

        # Further sensors can be added by following the schema at:
        # https://webthings.io/schemas/
        self.context = "https://webthings.io/schemas/"

        self.polling_frequency_minutes = aqm_polling_time // 60000

        # This has to be set at the start, otherwise you will have the problem
        # that no data will be available from the WoT interface until at least
        # AQM_POLLING_TIME duration has passed.
        self.o3_reading = Value(o3_initial)
        self.no2_reading = Value(no2_initial)
        self.pm25_reading = Value(pm25_initial)
        self.pm10_reading = Value(pm10_initial)
        self.humidity_reading = Value(humidity_initial)
        self.temperature_reading = Value(temperature_initial)

        # Adding WHO limits to the properties seems like it could conform to the
        # WOT specification:
        # https://www.w3.org/TR/2020/
        # REC-wot-thing-description-20200409/#property-serialization-json

        # WHO limits obtained from: Anon, WHO global air quality guidelines ::
        # particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur
        # dioxide and carbon monoxide,

        # Further sensors can be added by following the schema at:
        # https://webthings.io/schemas/
        self.add_property(
            Property(
                self,
                "o3",
                self.o3_reading,
                metadata={
                    "@type": "ConcentrationProperty",
                    "title": "O3",
                    "type": "number",
                    "description": "The current O3 reading in ppm.",
                    "unit": "ppm",
                    "minimum": 0,
                    "whoMaximum": 60,
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "no2",
                self.no2_reading,
                metadata={
                    "@type": "ConcentrationProperty",
                    "title": "NO2",
                    "type": "number",
                    "description": "The current NO2 reading in ppm.",
                    "unit": "ppm",
                    "minimum": 0,
                    "whoMaximum": 10,
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "pm25",
                self.pm25_reading,
                metadata={
                    "@type": "ConcentrationProperty",
                    "title": "PM2.5",
                    "type": "number",
                    "description": "The current PM2.5 reading in µg/m³.",
                    "unit": "µg/m³",
                    "minimum": 0,
                    "whoMaximum": 5,
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "pm10",
                self.pm10_reading,
                metadata={
                    "@type": "ConcentrationProperty",
                    "title": "PM10",
                    "type": "number",
                    "description": "The current PM10 reading in µg/m³.",
                    "unit": "µg/m³",
                    "minimum": 0,
                    "whoMaximum": 15,
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "humidity",
                self.humidity_reading,
                metadata={
                    "@type": "HumidityProperty",
                    "title": "Humidity",
                    "type": "number",
                    "description": "The current relative humidity percentage.",
                    "unit": "percent",
                    "minimum": 0,
                    "maximum": 100,
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "temperature",
                self.temperature_reading,
                metadata={
                    "@type": "TemperatureProperty",
                    "title": "Temperature",
                    "type": "number",
                    "description": "The current temperature in degrees celsius.",
                    "unit": "°C",
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "latitude",
                Value(self.aqm_latitude),
                metadata={
                    "@type": "LocationProperty",
                    "title": "Latitude",
                    "type": "number",
                    "description": "The latitude of the AQM.",
                    "unit": "",
                    "readOnly": True,
                },
            )
        )

        self.add_property(
            Property(
                self,
                "longitude",
                Value(self.aqm_longitude),
                metadata={
                    "@type": "LocationProperty",
                    "title": "Longitude",
                    "type": "number",
                    "description": "The longitude of the AQM.",
                    "unit": "",
                    "readOnly": True,
                },
            )
        )

        self.add_available_event(
            "o3LevelExceedsWHOGuidelines",
            {
                "description": "The AQM had detected an unsafe level of O3.",
                "type": "number",
                "unit": "ppm",
            },
        )

        self.add_available_event(
            "no2LevelExceedsWHOGuidelines",
            {
                "description": "The AQM had detected an unsafe level of NO2.",
                "type": "number",
                "unit": "ppm",
            },
        )

        self.add_available_event(
            "pm25LevelExceedsWHOGuidelines",
            {
                "description": "The AQM had detected an unsafe level of PM2.5.",
                "type": "number",
                "unit": "µg/m³",
            },
        )

        self.add_available_event(
            "pm10LevelExceedsWHOGuidelines",
            {
                "description": "The AQM had detected an unsafe level of PM10.",
                "type": "number",
                "unit": "µg/m³",
            },
        )

        self.o3_timer = tornado.ioloop.PeriodicCallback(
            self.update_o3_reading, self.aqm_polling_time
        )
        self.o3_timer.start()

        self.no2_timer = tornado.ioloop.PeriodicCallback(
            self.update_no2_reading, self.aqm_polling_time
        )
        self.no2_timer.start()

        self.pm25_timer = tornado.ioloop.PeriodicCallback(
            self.update_pm25_reading, self.aqm_polling_time
        )
        self.pm25_timer.start()

        self.pm10_timer = tornado.ioloop.PeriodicCallback(
            self.update_pm10_reading, self.aqm_polling_time
        )
        self.pm10_timer.start()

        self.humidity_timer = tornado.ioloop.PeriodicCallback(
            self.update_humidity_reading, self.aqm_polling_time
        )
        self.humidity_timer.start()

        self.temperature_timer = tornado.ioloop.PeriodicCallback(
            self.update_temperature_reading, self.aqm_polling_time
        )
        self.temperature_timer.start()

    # Check the reading compared to a WHO limit and add an event if needed.
    def check_add_pollution_event(self, sensor_name, who_limit, reading):
        if reading > who_limit:
            self.add_event(
                Event(self, f"{sensor_name}LevelExceedsWHOGuidelines", reading)
            )

    def update_o3_reading(self):
        new_reading = self.get_latest_reading()
        self.check_add_pollution_event("o3", 60.0, new_reading)
        self.o3_reading.notify_of_external_update(new_reading)

    def update_no2_reading(self):
        new_reading = self.get_latest_reading()
        self.check_add_pollution_event("no2", 10.0, new_reading)
        self.no2_reading.notify_of_external_update(new_reading)

    def update_pm25_reading(self):
        new_reading = self.get_latest_reading()
        self.check_add_pollution_event("pm25", 5.0, new_reading)
        self.pm25_reading.notify_of_external_update(new_reading)

    def update_pm10_reading(self):
        new_reading = self.get_latest_reading()
        self.check_add_pollution_event("pm10", 15.0, new_reading)
        self.pm10_reading.notify_of_external_update(new_reading)

    def update_humidity_reading(self):
        new_reading = self.get_latest_reading()
        self.humidity_reading.notify_of_external_update(new_reading)

    def update_temperature_reading(self):
        new_reading = self.get_latest_reading()
        self.temperature_reading.notify_of_external_update(new_reading)

    @staticmethod
    def get_latest_reading():
        return abs(70.0 * random.random() * (-0.5 + random.random()))


def run_server(
    aqm_latitude, aqm_longitude, aqm_name, aqm_description, aqm_polling_time, port
):
    aqm_thing = VirtualAQM(
        aqm_latitude=aqm_latitude,
        aqm_longitude=aqm_longitude,
        aqm_name=aqm_name,
        aqm_description=aqm_description,
        aqm_polling_time=aqm_polling_time,
    )

    server = WebThingServer(SingleThing(aqm_thing), port=port)
    try:
        print("Starting the server.")
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    # Find and load the .env file
    path = dotenv.find_dotenv()
    dotenv.load_dotenv(path)

    # You should create the .env according to the README.
    AQM_LATITUDE = float(os.environ.get("AQM_LATITUDE"))
    AQM_LONGITUDE = float(os.environ.get("AQM_LONGITUDE"))
    AQM_NAME = os.environ.get("AQM_NAME")
    AQM_DESCRIPTION = os.environ.get("AQM_DESCRIPTION")
    AQM_POLLING_TIME = int(os.environ.get("AQM_POLLING_TIME"))
    WOT_PORT = int(os.environ.get("WOT_PORT"))

    run_server(
        aqm_latitude=AQM_LATITUDE,
        aqm_longitude=AQM_LONGITUDE,
        aqm_name=AQM_NAME,
        aqm_description=AQM_DESCRIPTION,
        aqm_polling_time=AQM_POLLING_TIME,
        port=WOT_PORT,
    )
