<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1 align="center">Air Quality Monitoring Network</h3>

</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#setup">Setup</a>
      <ul>
        <li><a href="#python-and-brownie">Python and Brownie</a></li>
        <li><a href="#code">Code</a></li>
        <li><a href="#docker">Docker</a></li>
        <li><a href="#metamask">MetaMask</a></li>
      </ul>
    </li>
    <li>
      <a href="#configuration-file">Configuration File</a>
      <ul>
        <li><a href="#metamask">MetaMask</a></li>
        <li><a href="#infura">Infura</a></li>
        <li><a href="#etherscan">Etherscan</a></li>
        <li><a href="#solid">Solid</a></li>
        <li><a href="#smart-contract">Smart Contract</a></li>
      </ul>
    </li>
    <li><a href="#getting-started">Getting Started</a></li>
    <ul>
        <li><a href="#web-of-things">Web of Things</a></li>
    </ul>
    <li><a href="#usage">Usage</a></li>
    <ul>
        <li><a href="#solid-pod-updater">Solid Pod Updater</a></li>
        <li><a href="#solid-pod-file-verifier">Solid Pod File Verifier</a></li>
    </ul>
    <li><a href="#testing">Testing</a></li>
    <ul>
        <li><a href="#unit-tests">Unit Tests</a></li>
        <li><a href="#performance-tests">Performance Tests</a></li>
    </ul>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This project is a fully decentralised Web of Things Air Quality Monitoring Network. It employes the Ethereum blockchain in combination with decentralised data stores in the form of Solid Pods. The result delivers full user control over data, whilst upholding data integrity through blockchain-based verification.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Ethereum][ethereum]][ethereum-url]
- [![Python][python]][python-url]
- [![Solidity][solidity]][solidity-url]
- [![Docker][docker]][docker-url]
- [![Raspberry Pi][raspberry pi]][raspberry pi-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- SETUP -->

# Setup

## Python and Brownie

1. Download [Python3](https://www.python.org/downloads/).
2. Install pipx: `python3 -m pip install --user pipx` and `python3 -m pipx ensurepath`.
3. Restart terminal by closing and reopening.
4. Install brownie: `pipx install eth-brownie`
5. To check installation is complete, type `brownie`.

## Code

1. Download or clone the project code.
2. Inject modules necessary for the project into the brownie virtual environment by running:

`pipx inject eth-brownie filehash windows-curses schedule requests webthing solid-file freezegun prettytable argparse pytest mock pytest-mock`

3. Install Python dependencies using:
   `pip3 install -r requirements.txt`

## Docker

1. Navigate to [Docker](https://docs.docker.com/get-docker/) and download the relevant version for your operating system.

## MetaMask

### Creating wallet

1. Go to [MetaMask](https://metamask.io/) and download extension to your browser (only supported by Chrome, Firefox and Brave).
2. Click “Get Started” > “Create a Wallet”.
3. Follow the setup instructions and ensure you store your Secret Backup Phrase.

### Obtaining Test Ether

1. Click on MetaMask extension and click the button "Ethereum Mainnet" to view a dropdown of networks.
2. Click "Show/hide test networks" and toggle "Show test networks" to ON to display the testnets.
3. Click the dropdown again and select "Goerli Test Network"
4. Visit this [faucet](https://goerlifaucet.com/).
5. Click on MetaMask extension and under "Account 1" copy the address (this is the public key).
6. Paste this address in the faucet to obtain free Ether for the Goerli Test network.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION FILE -->

# Configuration File

The configuration file contains all settings related to the project. Run `python3 scripts\create_env.py` to create the .env file. The environment variables are detailed below:

- `PRIVATE_KEY`: Private key for your MetaMask account.
- `WEB3_INFURA_PROJECT_ID`: API key for your Infura Project.
- `ETHERSCAN_TOKEN`: API key for your Etherscan account.
- `CONTRACT_ADDRESS`: Address of your deployed smart contract.
- `SOLID_POD_PROVIDER`: Provider of your Solid Pod.
- `SOLID_POD_URL`: The URL of your Solid Pod.
- `CSV_AQM_FOLDER_NAME`: The name of the folder in which CSV files containing AQM data will be stored in your Solid Pod.
- `TTL_AQM_FOLDER_NAME`: The name of the folder in which TTL files containing AQM data will be stored in your Solid Pod.
- `AQM_NAME`: The name of the AQM.
- `USER_NAME`: Your Solid Pod username.
- `PASSWORD`: Your Solid Pod password.
- `POLLING_TIME`: The frequency in which data will be polled from the AQM and stored in the Solid Pod (seconds).
- `SOLID_RETRY_TIME`: Time delay to retry adding data to the Solid Pod in case of error.
- `TZ`: The time zone of the AQM location.
- `WOT_URL`: URL for the WoT Gateway.
- `WOT_PORT`: Port for the WoT Gateway. This should be the same port as the WoT AQM device.
- `AQM_LATITUDE`: Latitude of the AQM.
- `AQM_LONGITUDE`: Longitude of your AQM.
- `AQM_DESCRIPTION`: Description of the AQM.
- `AQM_POLLING_TIME`: The frequency in which new readings will be polled from the AQM (milliseconds).
- `AQM_CSV_HASH_TIME`: The time at which the CSV file is hashed. Set to immediately before midnight by default to ensure all daily data has been collected.

The subsequent sections will detail how to replace some of these variables with specific values.

## MetaMask

### Obtaining Private Key

1. Click on MetaMask extension then click on the three dots in the upper right corner.
2. Select “Account details” > “Export Private Key”
3. Type in your password then “Confirm” to view your private key.
4. Insert this value into the `PRIVATE_KEY` environment variable.

## Infura

### Obtaining API key to connect to Ethereum network

1. Navigate to [Infura](https://infura.io/) and create an account.
2. Go to your dashboard and click “Create New Key” at the top right.
3. Select “Web3 API (Formerly Ethereum)” as the network and then enter a name and click “Create”.
4. Copy the API key displayed at the top.
5. Insert this value into the `WEB3_INFURA_PROJECT_ID` environment variable.

## Etherscan

### Obtaining API key to verify smart contract

1. Navigate the [Etherscan](https://etherscan.io/) then click “Sign In” at the top right.
2. Sign up for an account then login.
3. Hover over your account name at the top right then click “API keys”
4. Click “Add” under “My API keys”, enter a name then click “Create New API Key”
5. Your API Key should then be displayed.
6. Insert this value into the `ETHERSCAN_TOKEN` environment variable.

## Solid

### Obtaining a Solid Pod

1. Go to [Solid Community](https://solidcommunity.net/).
2. Click the button "Register to get a Pod" in the top right.
3. Fill in the required details.
4. Replace the `USER_NAME`, `PASSWORD` and `SOLID_POD_URL` with your Solid Pod username, password and URL respectively.

## Smart Contract

### Obtaining a Contract Address

1. Deploy the contract to the Goerli testnet: `brownie run scripts\deploy_contract --network goerli`
2. The contract should subsequently be deployed and verified (provided your MetaMask account has sufficient test Ether and the Etherscan API is set up correctly)
3. Copy the contract address printed to the terminal - "HashStorage deployed at: YOUR_CONTRACT_ADDRESS".
4. Insert this value into the `CONTRACT_ADDRESS` environment variable.

#### **_All other environment variables can be tweaked as required_**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

# Getting Started

## Web of Things

### WebThings Gateway setup and connection

1. Open Docker.
2. Navigate to [WebThings Gateway](https://hub.docker.com/r/webthingsio/gateway) and run the following command in the terminal, replacing the file path with a local directory to store Docker data:

`docker run -d -p 8080:8080 -p 4443:4443 -e TZ=Europe/London -v /path/to/shared/data:/home/node/.webthings --log-opt max-size=1m --log-opt max-file=10 --name webthings-gateway webthingsio/gateway:latest`

3. In Docker, run the “webthings-gateway” container and type http://localhost:8080 in your browser to connect to the gateway.
4. You should be greeted with a welcome screen. Follow the instructions to create a user account.

### Adding a virtual AQM to the Gateway

1. Once connected to the Gateway, click the three lines at the top left, then “Settings” > “Add-ons”. Click the plus icon at the bottom right then search for “Web Thing” and click “Add”.
2. Run the virtual AQM: `python3 scripts\virtual_aqm.py`
3. Find your network IPv4 address
4. On the Gateway, click the plus icon at the bottom left then click “Add by URL…” and enter the following “Your_IPv4_address:8080”. The virtual AQM should then be discovered.
5. Enter a name for the AQM and click “Save”. Your AQM should now be displayed on the Gateway.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

# Usage

## Solid Pod Updater

The Solid Pod Updater performs the primary tasks of the system; it fetches new data from the AQM to be stored in either CSV or TTL files, and stores these files in the Solid Pod. Additionally, it generates and stores hashes of these files, which are sent and stored in the smart contract.

### CSV

The CSV version stores AQM data readings in daily CSV files at the user-set interval. It can be run with the following command:

`brownie run scripts\solid_pod_updater_csv --network goerli`

### RDF

The RDF version stores AQM data readings in individual TTL files at the user-set interval. It can be run with the following command:

`brownie run scripts\solid_pod_updater_ttl --network goerli`

## Solid Pod File Verifier

The Solid Pod Verifier retrieves the user-requested Solid Pod files, generates the hashes and compares them with the hashes stored on the smart contract. The verifier subsequently returns the result of this comparison as a boolean value. It is run using custom command-line arguments.

Each file type (CSV and TTL) has a respective verifier.
Each of these verifiers can either be used to verify single files of that file type, or to verify all files of that file type present in the AQM Solid Pod folder.

### CSV

#### Single

To verify a single CSV Solid Pod file, the "single" verification type must be used. In addition to this, a date must be supplied (YYYY-MM-DD) to identify the CSV file to be verified. The command has the following structure:

`brownie run scripts\solid_pod_verifier_csv verify single DATE_TO_VERIFY --network goerli`

For example, to verify a CSV file on the 8th July 2022:

`brownie run scripts\solid_pod_verifier_csv verify single 2022-07-08 --network goerli`

#### All

To verify all CSV Solid Pod files, the "all" verification type must be used. Unlike the single verification, **no date argument** is required.

`brownie run scripts\solid_pod_verifier_csv verify all --network goerli`

### RDF

#### Single

To verify a single TTL Solid Pod file, the "single" verification type must be used. In addition to this, a date must be supplied (YYYY-MM-DD), along with a time (HH-MM-SS) to identify the TTL file to be verified. The command has the following structure:

`brownie run scripts\solid_pod_verifier_ttl verify single DATE_TO_VERIFY TIME_TO_VERIFY --network goerli`

For example, to verify a TTL file on the 14th June 2022 at 12:43:54 :

`brownie run scripts\solid_pod_verifier_ttl verify single 2022-06-14 12:43:54 --network goerli`

#### All

To verify all TTL Solid Pod files, the "all" verification type must be used. Unlike the single verification, **no date or time argument** is required.

`brownie run scripts\solid_pod_verifier_ttl verify all --network goerli`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- TESTING -->

# Testing

## Unit Tests

All units tests can be run using: `brownie test tests\unit --network goerli`

It is worth highlighting that unit tests should ideally be run on local blockchains for better performance, however the setup of this is beyond the scope of the README.

## Performance Tests

### CSV

The CSV performance test can be run using:

`brownie test tests\performance\test_performance_csv.py -s --network goerli`

### TTL

The TTL performance test can be run using:

`brownie test tests\performance\test_performance_ttl.py -s --network goerli`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[product-screenshot]: images/screenshot.png
[ethereum]: https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=Ethereum&logoColor=white
[ethereum-url]: https://ethereum.org/en/
[python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org/
[solidity]: https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white
[solidity-url]: https://soliditylang.org/
[docker]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[docker-url]: https://www.docker.com/
[raspberry pi]: https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi
[raspberry pi-url]: https://www.raspberrypi.com/
