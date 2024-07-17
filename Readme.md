# Python Shipping Schedules Fetcher

This project is a Python script that interacts with the website [iCargo Schedules](https://icargo.schedules.qwyk.io/) to retrieve shipping schedules between two ports and display them in a table in the console.

## Requirements

- Python 3.x
- Google Chrome
- Google Chrome Driver
- Xvfb
- Python libraries:
  - `requests`
  - `selenium`
  - `prettytable`
  - `logging`

## Installation

1. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

The script can be run from the command line with the `origin_locode` and `destination_locode` parameters.

```sh
python fetch_schedules.py <origin_locode> <destination_locode>
```

To use the webdriver-manager option, add the --use-webdriver-manager flag:
```sh
python fetch_schedules.py <origin_locode> <destination_locode> --use-webdriver-manager
```

### Example
```sh
python fetch_schedules.py NLRTM SGSIN
python fetch_schedules.py NLRTM SGSIN --use-webdriver-manager
```


### Docker way
```sh
docker build -t shipping-schedules-fetcher .
docker run --rm shipping-schedules-fetcher <origin_locode> <destination_locode>
```




