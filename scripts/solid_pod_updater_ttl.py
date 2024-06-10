from brownie import config, Contract
import os
import time
from datetime import datetime
from scripts.contract_scripts import get_account, generate_hash
import dotenv
import requests
import urllib
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import SOSA
from solid.auth import Auth
from solid.solid_api import SolidAPI


class SolidPodUpdaterTTL:
    def __init__(
        self,
        pod_provider,
        pod_username,
        pod_password,
        pod_endpoint,
        aqm_folder,
        aqm_name,
        polling_frequency,
        wot_url,
        wot_port,
        retry_time,
    ):
        self.pod_provider = pod_provider
        self.pod_endpoint = pod_endpoint
        self.aqm_folder = aqm_folder
        self.aqm_name = aqm_name
        self.polling_frequency = polling_frequency
        self.wot_url = wot_url
        self.wot_port = wot_port
        self.retry_time = retry_time

        auth = Auth()
        self.api = SolidAPI(auth)
        auth.login(pod_provider, pod_username, pod_password)

    # Retrieves AQM properties
    def request_header_from_wot_interface(self):

        headers = {"Content-Type": "application/json; charset=utf-8"}

        while True:
            try:
                req = requests.get(
                    f"{self.wot_url}:{self.wot_port}/properties",
                    headers=headers,
                    timeout=None,
                )
                break
            except Exception:
                print(
                    f"Unable to get header from WoT interface. Will retry in {self.retry_time}s."
                )
                time.sleep(self.retry_time)

        results = req.json()

        # Get a header based on the keys of the response. E.g., the
        # header may look something like o3, no2, ...
        weather_station_header = [result for result in results]

        header_as_string = ""
        for item in weather_station_header:
            header_as_string += f"{item},"

        # Strip the trailing comma
        header_as_string = header_as_string[:-1]

        return header_as_string

    # Retrieves AQM data
    def request_data_from_wot_interface(self):
        headers = {"Content-Type": "application/json; charset=utf-8"}

        while True:
            try:
                req = requests.get(
                    f"{self.wot_url}:{self.wot_port}/properties",
                    headers=headers,
                    timeout=None,
                )
                break
            except Exception:
                print(
                    f"Unable to get data from WoT interface. Will retry in {self.retry_time}s."
                )
                time.sleep(self.retry_time)

        results = req.json()

        # Get the values of the AQM properties. E.g., the data may look something like
        # 7.21602550234155, 0.3994960553201695, ...
        weather_station_data = [results[result] for result in results]

        data_as_string = ""
        for datum in weather_station_data:
            data_as_string += f"{datum},"

        # Strip the trailing comma
        data_as_string = data_as_string[:-1]

        return data_as_string

    # Generates and stores file hashes
    def hash_file(self, file):
        print("File hashing started...")
        account = get_account()
        file_hash = generate_hash(file)
        hash_storage = Contract(config["contract"]["address"])
        hash_storage.store_hash(file_hash, {"from": account})
        print("File hashing complete")

    # Executes the Solid Pod updater
    def start(self):
        # https://www.geeksforgeeks.org/http-headers-content-type/
        FILE_CONTENT_TYPE = "text/rdf"

        header = self.request_header_from_wot_interface().split(",")

        base_url = self.pod_endpoint
        aqms_folder_url = base_url + self.aqm_folder
        aqm_folder_url = aqms_folder_url + self.aqm_name

        print(f"Base Pod URL is '{base_url}'.")
        print(f"AQM data folder in Pod is '{aqms_folder_url}'.")
        print(f"Folder for this AQM in the Pod is '{aqm_folder_url}'.")

        while True:
            try:
                if not self.api.item_exists(aqms_folder_url):
                    self.api.create_folder(aqms_folder_url)
                    print(f"Created AQM parent folder at '{aqms_folder_url}'.")
                break
            except Exception:
                print(
                    f"Unable to check if AQM parent folder exists. Will retry in {self.retry_time}s."
                )
                time.sleep(self.retry_time)

        while True:
            try:
                if not self.api.item_exists(aqm_folder_url):
                    self.api.create_folder(aqm_folder_url)
                    print(f"Created AQM folder at '{aqm_folder_url}'.")
                break
            except Exception:
                print(
                    f"Unable to check if AQM folder exists. Will retry in {self.retry_time}s."
                )
                time.sleep(self.retry_time)

        while True:
            # Creates a new TTL file for the current date and time
            current_datetime = datetime.now()
            FILE_NAME = f"{current_datetime}.ttl"
            file_url = aqm_folder_url + FILE_NAME

            # Retrieve new data from AQM
            new_aqm_data = self.request_data_from_wot_interface().split(",")

            # Format the data into Turtle format
            turtle_data = self.generate_turtle_rdf(
                current_datetime, header, new_aqm_data
            )

            while True:
                try:
                    self.api.put_file(file_url, turtle_data, FILE_CONTENT_TYPE)
                    print(f"Added entry at '{file_url}'.")
                    self.api.get(file_url)
                    # Encode file name
                    local_file = urllib.parse.quote(FILE_NAME)
                    open(local_file, "wb").write(turtle_data)
                    self.hash_file(local_file)
                    # Delete the file locally
                    os.remove(local_file)
                    break
                except Exception:
                    print(
                        f"Unable to add data to Pod. Will retry in {self.retry_time}s."
                    )
                    time.sleep(self.retry_time)

            time.sleep(self.polling_frequency)

    @staticmethod
    def generate_turtle_rdf(datetime, list_of_headers, list_of_data):
        g = Graph()
        aqm = URIRef("")
        nodes = [BNode() for _ in list_of_headers]
        g.add((aqm, SOSA.resultTime, Literal(datetime)))

        for node, sensor_name, sensor_data in zip(nodes, list_of_headers, list_of_data):
            g.add((node, SOSA.Sensor, Literal(sensor_name)))
            g.add((node, SOSA.hasSimpleResult, Literal(sensor_data)))

        return g.serialize(format="turtle")


def main():
    path = dotenv.find_dotenv()

    dotenv.load_dotenv(path)

    # Set the timezone according to the TZ environment variable - Unix only
    # time.tzset()

    SOLID_POD_PROVIDER = os.environ.get("SOLID_POD_PROVIDER")

    # WARNING: You must use the .env or other similar method to securely
    # authenticate to your SOLID POD. Do not enter your details in this file, and
    # definitely do not commit to version control your details. See the README
    # before proceeding.
    USER_NAME = os.environ.get("USER_NAME")
    PASSWORD = os.environ.get("PASSWORD")

    POD_ENDPOINT = os.environ.get("SOLID_POD_URL")

    if POD_ENDPOINT[-1] != "/":
        POD_ENDPOINT += "/"

    AQM_FOLDER_NAME = os.environ.get("TTL_AQM_FOLDER_NAME")

    if AQM_FOLDER_NAME[-1] != "/":
        AQM_FOLDER_NAME += "/"

    AQM_NAME = os.environ.get("AQM_NAME")

    if AQM_NAME[-1] != "/":
        AQM_NAME += "/"

    WOT_URL = os.environ.get("WOT_URL")
    WOT_PORT = os.environ.get("WOT_PORT")
    POLLING_TIME = int(os.environ.get("POLLING_TIME"))
    SOLID_RETRY_TIME = int(os.environ.get("SOLID_RETRY_TIME"))

    updater = SolidPodUpdaterTTL(
        pod_provider=SOLID_POD_PROVIDER,
        pod_username=USER_NAME,
        pod_password=PASSWORD,
        pod_endpoint=POD_ENDPOINT,
        aqm_folder=AQM_FOLDER_NAME,
        aqm_name=AQM_NAME,
        polling_frequency=POLLING_TIME,
        wot_url=WOT_URL,
        wot_port=WOT_PORT,
        retry_time=SOLID_RETRY_TIME,
    )

    # Run the updater
    updater.start()
