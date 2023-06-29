from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action:
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action..

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()

class ChangeMovementModeAction(Action):
    def perform(self) -> None:
        if self.entity.movement_mode == 0:
            self.entity.movement_mode = 1
            self.entity.color = (255, 255, 0)
        elif self.entity.movement_mode == 1:
            self.entity.movement_mode = 0
            self.entity.color = (255, 255, 255)
        self.entity.horizontal_movement = 0
        self.entity.vertical_movement = 0

class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return  # No entity to attack.

        self.entity.real_action = 1

        print(f"You kick the {target.name}, much to its annoyance!")

class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
                return  # Destination is out of bounds.
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                return  # Destination is blocked by a tile.
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
                return  # Destination is blocked by an entity.

        self.entity.real_action = 1
        self.entity.move(self.dx, self.dy)

class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.entity.movement_mode == 0:
            self.entity.ready_move = 1
        elif self.entity.movement_mode == 1:
            if self.dx != 0:
                self.entity.horizontal_movement = self.dx
            if self.dy != 0:
                self.entity.vertical_movement = self.dy
            if self.entity.horizontal_movement != 0 and self.entity.vertical_movement != 0:
                self.entity.ready_move = 1
                self.dx = self.entity.horizontal_movement
                self.dy = self.entity.vertical_movement
                self.entity.horizontal_movement = 0
                self.entity.vertical_movement = 0
        if self.entity.ready_move == 1:
            self.entity.ready_move = 0

            if self.blocking_entity:
                return MeleeAction(self.entity, self.dx, self.dy).perform()

            else:
                return MovementAction(self.entity, self.dx, self.dy).perform()