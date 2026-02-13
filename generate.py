import cantools as ct
import sys
import os


def is_not_camelcase(name: str) -> bool:
    """Check if a string is NOT in camelCase format. CamelCase should start with uppercase and have no underscores."""
    if name[0].islower():
        return True
    if '_' in name:
        return True
    return False


def is_not_snakecase(name: str) -> bool:
    """Check if a string is NOT in snake_case format. Snake_case should be all lowercase with underscores separating words."""
    if name != name.lower():
        return True
    # Check for consecutive underscores or starting/ending with underscore
    if '__' in name or name.startswith('_') or name.endswith('_'):
        return True
    return False


def check_formatting(db) -> None:
    """Check the formatting of message and signal names in the database. Print warnings if they do not follow the expected conventions."""

    bad_message_names = list()
    bad_signal_names = list()

    for messageType in db.messages:
        messageName = messageType.name
        if is_not_camelcase(messageName):
            bad_message_names.append(messageName)

        for signal in messageType.signals:
            signalName = signal.name
            if is_not_snakecase(signalName):
                bad_signal_names.append(signalName)

    if len(bad_message_names) > 0:
        print("WARNING: message names should be in CamelCase to ensure this script generates code correctly and ensure consistency in the codebase.")
        for name in bad_message_names:
            print(f"  - {name}")

    if len(bad_signal_names) > 0:
        print("WARNING: signal names should be in snake_case to ensure this script generates code correctly and ensure consistency in the codebase.")
        for name in bad_signal_names:
            print(f"  - {name}")


def camelcase_to_snakecase(camelcase: str) -> str:
    """Convert CamelCase to snake_case"""
    
    result = list()
    
    for i, char in enumerate(camelcase):
        if char.isupper() and i > 0:
            # Add underscore before uppercase letter, but not if:
            # 1. Previous character was also uppercase and next character is lowercase (handles acronyms)
            # 2. We're at the beginning
            prev_char = camelcase[i-1]
            prev_is_upper = prev_char.isupper()
            prev_is_digit = prev_char.isdigit()
            next_is_lower = i < len(camelcase) - 1 and camelcase[i+1].islower()
            
            # Add underscore if previous is a digit, or if not in the middle of an acronym
            if prev_is_digit or (not (prev_is_upper and not next_is_lower)):
                result.append('_')
        
        result.append(char.lower())
        
    return ''.join(result)


def make_struct_text(db_name: str, message_name_camelcase: str, signals: list[str], faults: list[str]) -> str:
    message_name_snakecase = camelcase_to_snakecase(message_name_camelcase)
    signals_formatted_string = ", ".join([f"{signal} %u" for signal in signals])
    signals_variable_string = ", ".join([camelcase_to_snakecase(signal) for signal in signals])
    faults_string = " || ".join(faults) + ";" if len(faults) > 0 else "0; // this message has no fault signals"

    return f"""
typedef struct {message_name_camelcase} : CanMessage, {db_name}_{message_name_snakecase}_t {{
    void serialize(SerializedCanMessage *message) {{
        {db_name}_{message_name_snakecase}_pack(message->data, this,
            {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH);
        message->len = {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH;
        message->id = {db_name.upper()}_{message_name_snakecase.upper()}_FRAME_ID;
    }}

    void deserialize(SerializedCanMessage *message) {{
        {db_name}_{message_name_snakecase}_unpack(this, message->data,
            {db_name.upper()}_{message_name_snakecase.upper()}_LENGTH);
    }}

    static uint16_t get_message_ID() {{ return {db_name.upper()}_{message_name_snakecase.upper()}_FRAME_ID; }}

    void log_msg(LogLevel level) const {{
        log(level, __FILE__, __LINE__,
            "{message_name_camelcase}: {signals_formatted_string}"{',' if len(signals) > 0 else ''}
            {signals_variable_string});
    }}

    bool has_active_fault() {{
        return {faults_string}
    }}
}} {message_name_camelcase};
"""


def make_header_file_text(db_name: str, messages) -> str:
    text = f"""
#ifndef {db_name}_CAN_Structs
#define {db_name}_CAN_Structs

#include "can.h"
#include "{db_name}.h"
#include "log.h"
"""
    
    for message in messages:
        messageName = message.name
        signals = [signal.name for signal in message.signals if not signal.is_float]
        faults = [signal.name for signal in message.signals if signal.comment and "fault" in signal.comment.lower()]

        structText = make_struct_text(db_name, messageName, signals, faults)
        text += structText + "\n"

    text += "#endif"
    return text


def main() -> None:
    if len(sys.argv) != 2:
        print("ERROR: Must provide a .dbc file as an argument")
        return
    path = sys.argv[1]
    if not path.endswith(".dbc"):
        print("ERROR: Must be a .dbc file")
        return
    
    db = ct.db.load_file(path)
    db_name = os.path.splitext(os.path.basename(path))[0]

    check_formatting(db)

    db_name_snake = camelcase_to_snakecase(db_name)
    headerText = make_header_file_text(db_name_snake, db.messages)

    with open(f"{db_name}CanStructs.h", "w") as file:
        file.write(headerText)

    print("Done")


if __name__ == "__main__":
    main()