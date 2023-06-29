from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
)

furball = Actor(
    char="f",
    color=(63, 127, 63),
    name="Furball",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
fairy = Actor(
    char="F",
    color=(0, 127, 0),
    name="Fairy",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)