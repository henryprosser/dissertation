from pathlib import Path

ENV_DEFAULT = f"""PRIVATE_KEY = 0xYOUR_PRIVATE_KEY
WEB3_INFURA_PROJECT_ID = YOUR_INFURA_API_KEY
ETHERSCAN_TOKEN = YOUR_ETHERSCAN_API_KEY
CONTRACT_ADDRESS = YOUR_CONTRACT_ADDRESS
SOLID_POD_PROVIDER=https://solidcommunity.net/
SOLID_POD_URL=https://[USERNAME].solidcommunity.net/
CSV_AQM_FOLDER_NAME=csv-aqm-data
TTL_AQM_FOLDER_NAME=ttl-aqm-data
AQM_NAME=aqm1
USER_NAME=username
PASSWORD=password
POLLING_TIME=900
SOLID_RETRY_TIME=30
TZ=Europe/London
WOT_URL=http://127.0.0.1
WOT_PORT=8080
AQM_LATITUDE=51.37981428316116
AQM_LONGITUDE=-2.328047487717645
AQM_DESCRIPTION=A WoT AQM.
AQM_POLLING_TIME=900000
AQM_CSV_HASH_TIME=23:59:59
"""

# Creates env file
def create_env(env_file):
    env_file.write_text(ENV_DEFAULT)
    env_file.chmod(0o600)
    print(f"Created {env_file}")


# Checks whether an env file already exists
def create_env_if_not_already_created(env_file):
    env_file = Path(env_file)
    if env_file.exists():
        print(f"{env_file} already exists!")
    else:
        create_env(env_file)


if __name__ == "__main__":
    create_env_if_not_already_created(".env")
