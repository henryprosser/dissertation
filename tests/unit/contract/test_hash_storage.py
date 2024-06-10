from brownie import HashStorage, convert
from scripts.contract_scripts import (
    get_account,
    generate_hash,
)
import hashlib
import os

# Checks that the smart contract is deployed correctly to an address
def test_deploy():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    # Assert
    assert hash_storage.address


# Checks that CSV file hashes are stored correctly
def test_csv_hash():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    file_name = "test.csv"
    open(file_name, "w")
    file_hash = generate_hash(file_name)
    hash_storage.store_hash(file_hash, {"from": account})
    actual_value = hash_storage.retrieve_hash()
    expected_value = convert.datatypes.HexString(file_hash, "bytes32")
    os.remove(file_name)
    # Assert
    assert actual_value == expected_value


# Checks that TTL file hashes are stored correctly
def test_ttl_hash():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    file_name = "test.ttl"
    open(file_name, "w")
    file_hash = generate_hash(file_name)
    hash_storage.store_hash(file_hash, {"from": account})
    actual_value = hash_storage.retrieve_hash()
    expected_value = convert.datatypes.HexString(file_hash, "bytes32")
    os.remove(file_name)
    # Assert
    assert actual_value == expected_value


# Checks the initial number of hashes is 0
def test_default_hash_number():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    actual_value = hash_storage.check_hash_number()
    expected_value = 0
    # Assert
    assert actual_value == expected_value


# Checks when a file is hashed, the number of stored hashes increases by 1
def test_file_hash_number():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    hash = hashlib.sha256().hexdigest()
    hash_storage.store_hash(hash, {"from": account})
    actual_value = hash_storage.check_hash_number()
    expected_value = 1
    # Assert
    assert actual_value == expected_value


# Checks that a stored file hash is verified as True
def test_hash_verification_true():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    hash = hashlib.sha256().hexdigest()
    hash_storage.store_hash(hash, {"from": account})
    actual_value = hash_storage.verify_hash(hash)
    expected_value = True
    # Assert
    assert actual_value == expected_value


# Checks that a file hash that is not stored is verified as False
def test_hash_verification_false():
    # Arrange
    account = get_account()
    # Act
    hash_storage = HashStorage.deploy({"from": account})
    hash = hashlib.sha256().hexdigest()
    actual_value = hash_storage.verify_hash(hash)
    expected_value = False
    # Assert
    assert actual_value == expected_value
