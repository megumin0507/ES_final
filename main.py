from typing import Optional
import logging

from src.ble import BLE
from src.game import Game


SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"
DEVICE_NAME: Optional[str] = "Note20"

RESOLUTION = (1280, 720)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    ble = BLE(SERVICE_UUID, CHAR_UUID, DEVICE_NAME)
    ble.start_ble_thread()
    game = Game(ble, RESOLUTION)
    game.run()


if __name__ == "__main__":
    main()