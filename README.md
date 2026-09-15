# CAN Message Definitions

CAN Messages for Rivanna3. Messages from Rivanna2 are under the Rivanna2 branch. 

## Software Installation

1. Clone this repo
2. Install cantools by running `py -m pip install cantools`
    - Note that you may need to use `python` or `python3` instead of `py`
3. Install [Kvaser Database Editor](https://www.kvaser.com/download/)
    - Version 3 recommended  

## Use
1. Use the *Kvaser Database Editor* to modify or create DBC files that define our CAN messages
2. Generate the C CAN structs and the 'wrapper' header file for a DBC:
    - Easiest: run `py generate.py {DBC file path}`, which also runs `cantools generate_c_source` for you
    - To regenerate everything for every DBC file in the repo at once, run `py generate_all.py`
    - Or, to run the original two steps yourself: first `cantools generate_c_source {path}`, then `py generate.py {DBC file path} --skip-c-source`
3. Add a message ID entry to `Common/include/CANStructMessageIDs.h`

