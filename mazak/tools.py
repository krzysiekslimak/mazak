from enum import Enum, auto


class Tool(Enum):
    SELECT = auto()
    ARROW = auto()
    BUBBLE = auto()
    TEXT = auto()
    FRAME = auto()
    STICKER = auto()
    BLUR = auto()
    CROP = auto()


class ArrowStyle(Enum):
    CLASSIC = auto()
    SLIM = auto()
    BOLD = auto()


class BubbleShape(Enum):
    ROUNDED = auto()
    OVAL = auto()
    CLOUD = auto()


class StickerKind(Enum):
    EXCLAMATION = auto()
    QUESTION = auto()
    CHECK = auto()
    CROSS = auto()
    STAR = auto()
    WARNING = auto()
