from aiogram.utils.helper import Helper, HelperMode, ListItem


class foodState(Helper):
    mode = HelperMode.snake_case

    MENU = ListItem()
    HELP = ListItem()
    SETTINGS = ListItem()
    GENERATE = ListItem()
    SETTINGS_ADD = ListItem()
    SETTINGS_DEL = ListItem()
    SETTINGS_SHOW = ListItem()

