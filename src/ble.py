import asyncio
import queue
from dataclasses import dataclass
import threading
import logging

from bleak import BleakClient

logger = logging.getLogger(__name__)

# STM addresses
TARGET_DEVICE_ADDRS = [
    # "da:ba:77:98:10:11",
    "d4:8c:49:eb:82:f6",
    "d8:94:7e:7b:0b:6a",
]

@dataclass
class ControllerPacket:
    device_index: int
    buttons: int
    time: int


class BLE:
    def __init__(self, service_uuid, char_uuid):
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        
        self.input_queue: "queue.Queue[ControllerPacket]" = queue.Queue()
        self.ble_connected = False

    def retrieve_pkt(self):
        return self.input_queue.get_nowait()
    
    def start_ble_thread(self):
        """
        Run the BLE asyncio loop in a background thread so pygame can own the main thread.
        """
        loop = asyncio.new_event_loop()

        def runner():
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.ble_main())
            loop.close()

        t = threading.Thread(target=runner, daemon=True)
        t.start()

    async def ble_main(self):
        """
        Main BLE coroutine:
        - connect to all addresses in TARGET_DEVICE_ADDRS
        - subscribe to notifications on each
        - keep all connection alive
        """
        if not TARGET_DEVICE_ADDRS:
            logger.error("BLE: no TARGET_DEVICE_ADDRS configured")
            return
        
        logger.info(f"BLE: starting {len(TARGET_DEVICE_ADDRS)} connections")
        
        tasks = [
            self._run_single_client(addr, idx)
            for idx, addr in enumerate(TARGET_DEVICE_ADDRS)
        ]

        await asyncio.gather(*tasks)

    # --------- internal helpers --------------------

    async def _run_single_client(self, address: str, device_index: int):
        """
        Handle a single physical device:
        - connect (with auto-retry)
        - start notifications
        - feed packets into self.input_queue
        """
        while True:
            try:
                logger.info(f"BLE[{device_index}]: connecting to {address}")
                async with BleakClient(address) as client:
                    if not client.is_connected:
                        logger.warning(f"BLE[{device_index}]: connection failed to {address}")
                        await asyncio.sleep(1.0)
                        continue

                    logger.info(f"BLE[{device_index}]: connected to {address}")
                    self.ble_connected = True

                    handler = self._make_notification_handler(device_index)
                    logger.info(f"BLE[{device_index}]: starting notify on {self.char_uuid}")
                    await client.start_notify(self.char_uuid, handler)

                    try:
                        while True:
                            if not client.is_connected:
                                logger.info(f"BLE[{device_index}]: disconnected")
                                break
                            await asyncio.sleep(0.1)
                    finally:
                        try:
                            await client.stop_notify(self.char_uuid)
                        except Exception:
                            pass
                        logger.info(f"BLE[{device_index}]: notify stopped")
                        self.ble_connected = False

            except Exception as e:
                logger.exception(f"BLE[{device_index}]: error while connected to {address}: {e}")

            logger.info(f"BLE[{device_index}]: retrying connection in 1s")
            await asyncio.sleep(1.0)


    def _make_notification_handler(self, device_index: int):
        def handler(sender: int, data: bytearray) -> None:
            logger.info(f"BLE[{device_index}]: Notification from {sender}")
            logger.info(f"  raw: {data}")
            
            time = data[0]
            time += 256 * data[1]
            buttons = data[2]

            logger.info(f"  buttons = {buttons}, time = {time}")
            pkt = ControllerPacket(device_index=device_index, buttons=buttons, time=time)
            self.input_queue.put(pkt)
        return handler
        