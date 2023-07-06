"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod
from tcod import libtcodpy

import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers
from input_handlers import MOVE_KEYS, CONFIRM_KEYS


# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )
    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    dagger = copy.deepcopy(entity_factories.dagger)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)

    dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    highlight_index = 0

    menu_length = 3

    highlight_string = " "

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "Rogue in Pseudo-Paradise",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        if self.highlight_index == 0:
            console.print(
                console.width // 2,
                console.height // 2,
                " New  ",
                fg=color.menu_text,
                bg=(0, 0, 255),
                alignment=libtcodpy.CENTER,
            )
        else:
            console.print(
                console.width // 2,
                console.height // 2,
                " New  ",
                fg=color.menu_text,
                alignment=libtcodpy.CENTER,
            )
        if self.highlight_index == 1:
            console.print(
                console.width // 2,
                console.height // 2 + 2,
                " Load ",
                fg=color.menu_text,
                bg=(0, 0, 255),
                alignment=libtcodpy.CENTER,
            )
        else:
            console.print(
                console.width // 2,
                console.height // 2 +2,
                " Load ",
                fg=color.menu_text,
                alignment=libtcodpy.CENTER,
            )
        if self.highlight_index == 2:
            console.print(
                console.width // 2,
                console.height // 2 + 4,
                " Quit ",
                fg=color.menu_text,
                bg=(0, 0, 255),
                alignment=libtcodpy.CENTER,
            )
        else:
            console.print(
                console.width // 2,
                console.height // 2 + 4,
                " Quit ",
                fg=color.menu_text,
                alignment=libtcodpy.CENTER,
            )
        console.print(
            console.width // 2,
            console.height - 2,
            "By EmiHyper7",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        key = event.sym

        if key in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif key in (tcod.event.KeySym.c, tcod.event.KeySym.l):
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif key == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler(new_game())
        elif key in MOVE_KEYS:
            x, y = MOVE_KEYS[key]
            if y < 0:
                self.highlight_index -= 1
            elif y > 0:
                self.highlight_index += 1
            if self.highlight_index < 0:
                self.highlight_index = self.menu_length - 1
            elif self.highlight_index > (self.menu_length - 1):
                self.highlight_index = 0
        elif key in CONFIRM_KEYS:
            if self.highlight_index == 0:
                return input_handlers.MainGameEventHandler(new_game())
            elif self.highlight_index == 1:
                try:
                    return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
                except FileNotFoundError:
                    return input_handlers.PopupMessage(self, "No saved game to load.")
                except Exception as exc:
                    traceback.print_exc()  # Print to stderr.
                    return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
            elif self.highlight_index == 2:
                raise SystemExit()

        return None
