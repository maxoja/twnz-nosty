from typing import List, Tuple

from pywinctl._pywinctl_win import Win32Window

from twnz.const import GAME_TITLE_POSTFIX, GAME_TITLE_PREFIX
from twnz.win.const import LEVEL, TEMP_PNG, NAME
from twnz.win.sread import temp_img_to_text, capture_and_crop_window
from twnz.win.bridge import show_win_with_small_delay_if_not_already


def get_game_windows_with_name_level_port(game_wins: List[Win32Window]) -> List[Tuple[Win32Window, str, str, int]]:
    for i, w in enumerate(game_wins):
        show_win_with_small_delay_if_not_already(w)
        crop_player_level_img(w, i)
        crop_player_name_img(w, i)

    result = []
    for i, w in enumerate(game_wins):
        port_title = w.title
        port_title = port_title.replace(GAME_TITLE_PREFIX, "")
        port_title = port_title.replace(GAME_TITLE_POSTFIX, "")
        player_name = temp_img_to_text(NAME, i)
        player_lvl_str = temp_img_to_text(LEVEL, i)
        result.append((w, player_name, player_lvl_str, int(port_title)))
    for t in result:
        print(t)
    return result


def crop_player_level_img(window, i:int):
    fname = f'{LEVEL}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=80, ltop=30, lwidth=30, lheight=20).save(fname)

def crop_player_name_img(window, i:int):
    fname = f'{NAME}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=110, ltop=30, lwidth=137, lheight=20).save(fname)

