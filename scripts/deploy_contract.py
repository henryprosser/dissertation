from brownie import accounts, config, network, HashStorage
from scripts.contract_scripts import get_account

# Retrieve relevant account
account = get_account()

# Deploy contract
def deploy_hash_storage():

    data_hashing = HashStorage.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )

    return data_hashing


def main():
    deploy_hash_storage()
