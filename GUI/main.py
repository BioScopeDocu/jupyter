# import packages
import json
import os.path
from os.path import exists
from pathlib import Path  # core python module
import PySimpleGUI as sg  # pip install pysimplegui
import configparser

# import costume packages
from scripts.API_requests import API_server
from GUI.API_requests import API_server
from GUI.converter import Export
from GUI.contentbuilder import ContentBuilder

# init classes
content_builder = ContentBuilder()
converter = Export()

# variables
sg.theme("DarkGreen")
configname = "config.ini"
action_list = content_builder.action_names
file_types = converter.file_types
layertypes = ("Biomassa (p2)")

def collapse(layout, key, visible):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this section visible / invisible
    :param visible: visible determines if section is rendered visible or invisible on initialization
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0, 0)))

# windows
def main_window(server):
    # ------ Menu Definition ------ #
    menu_def = [["Instellingen", ["Token", "Over", "Exit"]]]
    # ------ GUI Definition ------ #
    content_builder.get_fields(server)
    field_names = content_builder.field_names
    layout = [
            [sg.MenubarCustom(menu_def, pad=(0, 0))],
            [sg.Frame("Selecteer gegevens",  [
                     [sg.T("Data type:", s=15, justification="r"),
                      sg.Combo(action_list, default_value=action_list[0], enable_events=True, key="-ACTION-", size=50)],
                     [collapse([[sg.T("Perceel:", s=15, justification="r", key="-FIELDtext-"),
                                 sg.Combo(field_names, default_value="Alle percelen", key="-FIELD-", size=50)]],
                               "-FIELDS-", False)],
                 ], pad=(10, 5))],
            [sg.Frame("Selecteer output", [
                     [sg.T("Output Folder:", s=15, justification="r"), sg.I("/", key="-OUT-"),
                      sg.FolderBrowse()],
                     [sg.T("Bestandsnaam:", s=15, justification="r"),
                      sg.I("Example", s=20, key="-FILENAME-"),
                      sg.Combo(file_types, default_value=file_types[0], key="-FILETYPE-", size=(20, 2))]
                 ], pad=(10,5))],
            [sg.Exit(s=16, button_color="tomato", pad=(10,5)), sg.Button("Toon gegevens", s=16), sg.Button("Sla gegevens op", s=16)]]
    return sg.Window('FieldScout API downloader',
                     layout,
                     location=(400, 200), margins=(0,0),

                     finalize=True,
                     resizable=True,
                     icon="cropped-favicon.ico")

def display_window(size, heading):
    layout = [[sg.Combo(("Table", "Text"), key="-DISPLAYTYPE-", enable_events=True, default_value="Table")],
              [collapse([{sg.Table(
                  values=[],
                  headings=heading,
                  key="-TABLE-",
                  size=(19, 14),
                  alternating_row_color='darkgreen',
                  auto_size_columns=True,
                  justification="left",
                  row_height=18,
                  vertical_scroll_only=False)}],
                  "-TABLE_DISPLAY-",
                  True)
              ],
              [collapse([{sg.Multiline(
                  "",
                  size=(100, 20),
                  k='-RAWRESULT-')}],
                  "-TEXT_DISPLAY-",
                  False)
              ],
              [sg.Button('Exit', s=16, button_color="tomato")]]
    return sg.Window('De gegevens', layout, resizable=True, finalize=True, size=size)

def error_window(settings):
    # ------ GUI Definition ------ #
    layout = [[sg.T("Geen gebruiker gevonden")],
              [sg.B("Pas token aan", s=20), sg.Exit(s=16, button_color="tomato")]]

    window = sg.Window("User token", layout, modal=True, use_custom_titlebar=True)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == "Pas token aan":
            token_window(settings)
            break
    window.close()

def token_window(settings):
    # ------ GUI Definition ------ #
    layout = [[sg.Multiline(settings['TOKEN']['code'], s=(50, 20), key="-TOKEN-")],
              [sg.B("Save token", s=20), sg.Exit(s=16, button_color="tomato")]]
    window = sg.Window("User token", layout, modal=True, use_custom_titlebar=True)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == "Save token":
            # Write to ini file
            settings['TOKEN']['code'] = values["-TOKEN-"]

            # Display success message & close window
            sg.popup_no_titlebar("Gebruikers token opgeslagen!")
            break
    window.close()
    check_user()

def controller(server):
    window1, window2 = main_window(server), None
    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            if window == window2:  # if closing win 2, mark as closed
                window2 = None
            elif window == window1:  # if closing win 1, exit program
                break
        if event == '-ACTION-':
            window['-FIELDS-'].update(visible=True)
            if values['-ACTION-'] != action_list[1] and values['-ACTION-'] != action_list[2]:
                window['-FIELDS-'].update(visible=False)
        if event == '-DISPLAYTYPE-':
            window2['-TABLE_DISPLAY-'].update(visible=True)
            window2['-TEXT_DISPLAY-'].update(visible=False)
            if values['-DISPLAYTYPE-'] == "Text":
                window2['-TABLE_DISPLAY-'].update(visible=False)
                window2['-TEXT_DISPLAY-'].update(visible=True)

        if event == "Toon gegevens" and not window2:
            # parameters
            action_name = values['-ACTION-']
            field_name = values["-FIELD-"]
            field_index = content_builder.field_names.index(field_name)
            field_id = content_builder.field_ids[field_index]

            # content
            content = content_builder.get_content(server, action_name, field_id)

            # display
            content_df = content_builder.get_content_df(content, action_name)  # get table content
            size = (600, 400)
            if action_name == "Percelen":
                size = (800, 400)
            window2 = display_window(size, content_df.keys().tolist())  # open show window

            # update contentv
            cleaned = json.dumps(content[0:2], indent=4)
            window2['-RAWRESULT-'].update(cleaned)
            table = window2['-TABLE-']
            table.update(content_df.values.tolist())
        if event == "Sla gegevens op":
            # parameters
            path = values['-OUT-']
            file_name = values['-FILENAME-']
            file_type = values['-FILETYPE-']
            action_name = values['-ACTION-']
            field_name = values["-FIELD-"]
            field_index = content_builder.field_names.index(field_name)
            field_id = content_builder.field_ids[field_index]

            # content
            content = content_builder.get_content(server, action_name, field_id)
            if file_type == ".csv":
                content = content_builder.get_content_df(content, action_name)

            # export
            settings['OUTPUT']['path'] = path
            converter.output = os.path.join(path, file_name + file_type)
            result = converter.export_as(file_type, content)
            if result == True:
                sg.popup_no_titlebar("Het bestand is succesvol opgeslagen! :)")
            else:
                sg.popup_error(result)
        if event == "Token":
            token_window(settings)
        if event == "Over":
            window.disappear()
            sg.popup("Over", "Version 1.0", "Download gegevens van de API", grab_anywhere=True)
            window.reappear()
    window.close()

def check_user():
    """
          Check if user token exist.
          """
    token = settings['TOKEN']['code']
    server = API_server(token)
    user = server.get_request("user")
    if user:
        controller(server)
    else:
        error_window(settings)

def create_config_file():
    """
          Create configuration file if it doesn't exist yet
          """
    config = configparser.ConfigParser()
    config.read(configname)
    try:
        config.add_section("TOKEN")
        config.add_section("OUTPUT")
    except configparser.DuplicateSectionError:
        pass
    config.set("TOKEN", "code", "Vul hier je persoonlijke token in...")
    config.set("OUTPUT", "path", "")
    with open(configname, "w") as config_file:
        config.write(config_file)

# init app and settings
def run_app(token):
    server = API_server(token)
    controller(server)

if __name__ == "__main__":
    if not exists(configname):
        create_config_file()
    SETTINGS_PATH = Path.cwd()
    settings = sg.UserSettings(
        path=SETTINGS_PATH, filename=configname, use_config_file=True, convert_bools_and_none=True,
    )
    # check if user exists
    check_user()
