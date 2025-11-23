import asyncio
import queue
from dataclasses import dataclass
import threading
import logging

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)

@dataclass
class ControllerPacket:
    buttons: int
    x: int
    y: int


class BLE:
    def __init__(self, service_uuid, char_uuid, device_name):
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        self.device_name = device_name
        
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
        - scan for device
        - connect
        - subscribe to notifications
        - keep the connection alive
        """
        addr = await self.find_device()
        if addr is None:
            logger.info(f"BLE: device not found, aborting")
            return
        
        logger.info(f"BLE: connecting to {addr}")
        async with BleakClient(addr) as client:
            logger.info(f"BLE: connected")
            self.ble_connected = True

            logger.info(f"BLE: starting notification on {self.char_uuid}")
            await client.start_notify(self.char_uuid, self.notification_handler)

            try:
                while True:
                    if not client.is_connected:
                        logger.info(f"BLE: disconnected")
                    await asyncio.sleep(0.1)
            finally:
                self.ble_connected = False
                try:
                    await client.stop_notify(self.char_uuid)
                except Exception:
                    pass
                logger.info(f"BLE: exiting ble_main")

    # --------- internal helpers --------------------

    async def find_device(self):
        logger.info(f"Scanning for {self.device_name}")
        devices = await BleakScanner.discover(timeout=5.0)

        for d in devices:
            if d.name and self.device_name.lower() in d.name.lower():
                logger.info(f"Found: {d.name}, {d.address}")
                return d.address

        logger.info(f"No device matching name found")
        return None
    
    def notification_handler(self, sender: int, data: bytearray) -> None:

        logger.info(f"Notification from {sender}")
        logger.info(f"  raw: {data}")
        logger.info(f"  as list: {list(data)}")
        
        if len(data) < 3:
            logger.info(f"Notification too short {data}")
            return
        
        buttons = data[0]
        x_raw = data[1]
        y_raw = data[2]

        x = x_raw - 128
        y = y_raw - 128

        pkt = ControllerPacket(buttons=buttons, x=x, y=y)
        self.input_queue.put(pkt)

    