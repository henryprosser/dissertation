from brownie import config, Contract
import os
from scripts.contract_scripts import get_account, generate_hash
from prettytable import PrettyTable
import dotenv
from solid.auth import Auth
from solid.solid_api import SolidAPI
import sys
import urllib
import argparse
from datetime import datetime

aqm_verification_table = PrettyTable()
aqm_verification_table.field_names = ["File Name", "Valid Hash"]


class SolidPodVerifierTTL:
    def __init__(
        self,
        pod_provider,
        pod_username,
        pod_password,
        pod_endpoint,
        aqm_folder,
        aqm_name,
    ):

        self.pod_provider = pod_provider
        self.pod_endpoint = pod_endpoint
        self.aqm_folder = aqm_folder
        self.aqm_name = aqm_name

        auth = Auth()
        self.api = SolidAPI(auth)
        auth.login(pod_provider, pod_username, pod_password)

    def verify_file(self, aqm_folder_url, file):
        file_url = aqm_folder_url + file
        response = self.api.get(file_url)
        open(file, "wb").write(response.content)
        hash = generate_hash(file)
        hash_storage = Contract(config["contract"]["address"])
        is_valid_hash = hash_storage.verify_hash(hash)
        # Decode URL
        formatted_file_name = urllib.parse.unquote(
            file, encoding="utf-8", errors="replace"
        )
        aqm_verification_table.add_row([formatted_file_name, is_valid_hash])
        # Delete file locally
        os.remove(file)

    # Run the verifier
    def start(self, verification_type, date_to_verify, time_to_verify):
        base_url = self.pod_endpoint
        aqms_folder_url = base_url + self.aqm_folder
        aqm_folder_url = aqms_folder_url + self.aqm_name

        print(f"Base Pod URL is '{base_url}'.")
        print(f"AQM data folder in Pod is '{aqms_folder_url}'.")
        print(f"Folder for this AQM in the Pod is '{aqm_folder_url}'.")

        aqm_folder = self.api.read_folder(aqm_folder_url)
        # print(aqm_folder.files)
        all_files = list(map(lambda x: x.name, aqm_folder.files))
        all_files.sort()
        print(f"Files in the folder: {all_files}")

        table_empty = True
        table_result = None

        # If files exist in the Solid Pod
        if len(all_files) > 0:
            for file in all_files:
                # Decode file name
                formatted_file = urllib.parse.unquote(
                    file, encoding="utf-8", errors="replace"
                )

                if verification_type == "single":

                    if date_to_verify is None and time_to_verify is None:
                        print(
                            "Error - Please enter a date (YYYY-MM-DD) and time (HH:MM:SS) to verify a single file."
                        )
                        sys.exit(1)

                    if date_to_verify is None:
                        print(
                            "Error - Please enter a date (YYYY-MM-DD) to verify a single file."
                        )
                        sys.exit(1)

                    if time_to_verify is None:
                        print(
                            "Error - Please enter a time (HH:MM:SS) to verify a single file."
                        )
                        sys.exit(1)

                    if date_to_verify is not None:
                        try:
                            datetime.strptime(date_to_verify, "%Y-%m-%d")
                        except ValueError:
                            print("Error - Date is not in the format YYYY-MM-DD")
                            sys.exit(1)

                    if time_to_verify is not None:
                        try:
                            datetime.strptime(time_to_verify, "%H:%M:%S")
                        except ValueError:
                            print("Error - Time is not in the format HH:MM:SS")
                            sys.exit(1)

                    # Encode time
                    formatted_time_to_verify = urllib.parse.quote(time_to_verify)

                    if date_to_verify in file and formatted_time_to_verify in file:
                        self.verify_file(aqm_folder_url, file)
                        table_empty = False

                elif verification_type == "all":
                    self.verify_file(aqm_folder_url, file)
                    table_empty = False

        print(aqm_verification_table)

        if table_empty == True:
            if verification_type == "single":
                table_result = (
                    f"No TTL files exist for: {date_to_verify} {time_to_verify}"
                )
                print(table_result)
            elif verification_type == "all":
                table_result = "No TTL files exist in this AQM folder"
                print(table_result)

        return table_result


def verify(verification_type, date_to_verify=None, time_to_verify=None):
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

    verifier = SolidPodVerifierTTL(
        pod_provider=SOLID_POD_PROVIDER,
        pod_username=USER_NAME,
        pod_password=PASSWORD,
        pod_endpoint=POD_ENDPOINT,
        aqm_folder=AQM_FOLDER_NAME,
        aqm_name=AQM_NAME,
    )

    # Run the verifier
    verifier.start(verification_type, date_to_verify, time_to_verify)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--verificationtype", type=str, required=True, help="verificationtype"
    )
    parser.add_argument("--date", type=str, required=False, help="date")
    parser.add_argument("--time", type=str, required=False, help="time")
    args = parser.parse_args()

    # verify(args.verificationtype, args.date, args.time)
