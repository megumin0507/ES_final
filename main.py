import logging

from src.ble import BLE
from src.game import Game


SERVICE_UUID = "00000000-0001-11e1-ffff-ffffffffffbb"
CHAR_UUID = "00000000-0001-11e1-ffff-ffffffffffdd"

RESOLUTION = (1280, 720)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    ble = BLE(SERVICE_UUID, CHAR_UUID)
    ble.start_ble_thread()
    game = Game(ble, RESOLUTION)
    game.run()


if __name__ == "__main__":
    main()