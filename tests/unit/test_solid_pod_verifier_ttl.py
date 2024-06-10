import argparse
import os
from solid.auth import Auth
from solid.solid_api import SolidAPI, FolderData
from typing import List
from scripts.solid_pod_verifier_ttl import SolidPodVerifierTTL
import pytest
import sys
from brownie import HashStorage, convert
from scripts.contract_scripts import (
    get_account,
    generate_hash,
)
import os
import urllib

# Solid Pod Folder Mocking
class ItemMock:
    def __init__(self, name):
        self.name = name


class EmptyFolderDataMock:
    def __init__(self):
        self.files: List[ItemMock] = []


class FolderDataMock:
    def __init__(self):
        self.files: List[ItemMock] = [test_file_1, test_file_2]


# Test files
test_file_1 = ItemMock("2022-03-21 11:19:47.ttl")
test_file_2 = ItemMock("2022-03-22 11:19:47.ttl")


# Contract Mocking
def mock_contract():
    account = get_account()
    hash_storage = HashStorage.deploy({"from": account})

    ttl_files = [test_file_1, test_file_2]

    all_results = []

    for file_no, file in enumerate(ttl_files):
        test_file_name = urllib.parse.quote(
            file.name, encoding="utf-8", errors="replace"
        )

        open(test_file_name, "w").write(f"Test File {file_no}")

        test_file_hash = generate_hash(test_file_name)

        if file_no == 1:
            hash_storage.store_hash(test_file_hash, {"from": account})

        test_file_valid_hash = hash_storage.verify_hash(test_file_hash)

        test_file_result = [file.name, test_file_valid_hash]

        os.remove(test_file_name)

        all_results.append(test_file_result)

    return all_results


# Verifier Mocking
def mock_verifier(mocker):
    pod_provider = "http://example.com/"
    pod_username = "username"
    pod_password = "password"
    pod_endpoint = "http://pod.example.com/"
    aqm_folder = "aqm_folder"
    aqm_name = "aqm_name"

    # Act
    verifier = SolidPodVerifierTTL(
        pod_provider=pod_provider,
        pod_username=pod_username,
        pod_password=pod_password,
        pod_endpoint=pod_endpoint,
        aqm_folder=aqm_folder,
        aqm_name=aqm_name,
    )

    return verifier


# Checks error handling for "single" verification type with missing date and time
def test_single_date_and_time_none(mocker, capsys):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    verifier = mock_verifier(mocker)

    with pytest.raises(SystemExit) as e:
        # Act
        verifier.start(
            verification_type="single", date_to_verify=None, time_to_verify=None
        )

        out, _ = capsys.readouterr()

        # Assert
        assert (
            out
            == "Error - Please enter a date (YYYY-MM-DD) and time (HH:MM:SS) to verify a single file."
        )
        assert e.type == SystemExit
        assert e.value.code == 1


# Checks error handling for "single" verification type with missing date
def test_single_date_none(mocker, capsys):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    verifier = mock_verifier(mocker)

    with pytest.raises(SystemExit) as e:
        # Act
        verifier.start(
            verification_type="single", date_to_verify=None, time_to_verify="11:19:47"
        )

        out, _ = capsys.readouterr()

        # Assert
        assert (
            out == "Error - Please enter a date (YYYY-MM-DD) to verify a single file."
        )
        assert e.type == SystemExit
        assert e.value.code == 1


# Checks error handling for "single" verification type with missing time
def test_single_time_none(mocker, capsys):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    verifier = mock_verifier(mocker)

    with pytest.raises(SystemExit) as e:
        # Act
        verifier.start(
            verification_type="single", date_to_verify="2022-03-21", time_to_verify=None
        )

        out, _ = capsys.readouterr()

        # Assert
        assert out == "Error - Please enter a time (HH:MM:SS) to verify a single file."
        assert e.type == SystemExit
        assert e.value.code == 1


# Checks error handling for "single" verification type with incorrect date format
def test_single_incorrect_date_format(mocker, capsys):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    verifier = mock_verifier(mocker)

    with pytest.raises(SystemExit) as e:
        # Act
        verifier.start(
            verification_type="single",
            date_to_verify="21/03/2022",
            time_to_verify="11:19:47",
        )

        out, _ = capsys.readouterr()

        # Assert
        assert out == "Error - Date is not in the format YYYY-MM-DD"
        assert e.type == SystemExit
        assert e.value.code == 1


# Checks error handling for "single" verification type with incorrect time format
def test_single_incorrect_time_format(mocker, capsys):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    verifier = mock_verifier(mocker)

    with pytest.raises(SystemExit) as e:
        # Act
        verifier.start(
            verification_type="single",
            date_to_verify="2022-03-21",
            time_to_verify="11:19",
        )

        out, _ = capsys.readouterr()

        # Assert
        assert out == "Error - Time is not in the format HH:MM:SS"
        assert e.type == SystemExit
        assert e.value.code == 1


# Checks output for "single" verification type with no matching TTL files present in Solid Pod folder
def test_single_input_no_files_exist(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=EmptyFolderDataMock())
    verifier = mock_verifier(mocker)

    # Act
    table_result = verifier.start(
        verification_type="single",
        date_to_verify="2022-03-21",
        time_to_verify="11:19:47",
    )
    date_to_verify = "2022-03-21"
    time_to_verify = "11:19:47"

    # Assert
    assert table_result == f"No TTL files exist for: {date_to_verify} {time_to_verify}"


# Checks output for "all" verification type with no TTL files present in Solid Pod folder
def test_all_input_no_files_exist(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=EmptyFolderDataMock())
    verifier = mock_verifier(mocker)

    # Act
    table_result = verifier.start(
        verification_type="all",
        date_to_verify=None,
        time_to_verify=None,
    )

    # Assert
    assert table_result == "No TTL files exist in this AQM folder"


# Checks output for "single" verification type with matching TTL files present in Solid Pod folder
def test_single_input_files_exist(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    mocker.patch.object(SolidPodVerifierTTL, "verify_file")

    verifier = mock_verifier(mocker)

    # Act
    table_result = verifier.start(
        verification_type="single",
        date_to_verify="2022-03-21",
        time_to_verify="11:19:47",
    )

    all_results = mock_contract()

    # Assert
    assert all_results[0] == ["2022-03-21 11:19:47.ttl", False]


# Checks output for "all" verification type with TTL files present in Solid Pod folder
def test_all_input_files_exist(mocker):
    # Arrange
    mocker.patch.object(Auth, "login")
    mocker.patch.object(SolidAPI, "read_folder", return_value=FolderDataMock())
    mocker.patch.object(SolidPodVerifierTTL, "verify_file")

    verifier = mock_verifier(mocker)

    # Act
    table_result = verifier.start(
        verification_type="all",
        date_to_verify=None,
        time_to_verify=None,
    )

    all_results = mock_contract()

    # Assert
    assert all_results[0] == ["2022-03-21 11:19:47.ttl", False]
    assert all_results[1] == ["2022-03-22 11:19:47.ttl", True]
