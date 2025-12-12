import logging
import argparse

from ble import BLE
from src1.game import Game as Game1
from src2.game import Game as Game2


SERVICE_UUID = "00000000-0001-11e1-ffff-ffffffffffbb"
CHAR_UUID = "00000000-0001-11e1-ffff-ffffffffffdd"

RESOLUTION = (1280, 720)


def main(mode: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting game in {mode} mode")


    ble = BLE(SERVICE_UUID, CHAR_UUID)
    ble.start_ble_thread()
    if mode == "1p":
        game = Game1(ble, RESOLUTION)
        game.run()
    else:
        game = Game2(ble, RESOLUTION)
        game.run()


if __name__ == "__main__":
    # 2. 建立 ArgumentParser 物件
    parser = argparse.ArgumentParser(description="執行遊戲的主程式")

    # 3. 加入 --mode 參數
    # type=str: 指定參數型態為字串
    # default="normal": 如果沒輸入參數，預設為 "normal"
    # help: 說明這個參數的用途
    parser.add_argument("--mode", type=str, default="1p", help="1p or 2p mode")

    # 4. 解析參數
    args = parser.parse_args()

    # 5. 將解析到的 mode 傳入 main 函式
    main(mode=args.mode)