import asyncio
import threading
import queue
from dataclasses import dataclass
from typing import Optional

import pygame
from bleak import BleakClient, BleakScanner


SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"
DEVICE_NAME: Optional[str] = "Note20"

@dataclass
class ControllerPacket:
    buttons: int
    x: int
    y: int

input_queue: "queue.Queue[ControllerPacket]" = queue.Queue()

ble_connected = False


async def find_device():
    print("Scanning for", DEVICE_NAME)
    devices = await BleakScanner.discover(timeout=5.0)

    for d in devices:
        if d.name and DEVICE_NAME.lower() in d.name.lower():
            print("Found:", d.name, d.address)
            return d.address

    print("No device matching name found")
    return None
    

def notification_handler(sender: int, data: bytearray) -> None:

    print("Notification from", sender)
    print("  raw:", data)
    print("  as list:", list(data))
    
    if len(data) < 3:
        print("Notification too short", data)
        return
    
    buttons = data[0]
    x_raw = data[1]
    y_raw = data[2]

    x = x_raw - 128
    y = y_raw - 128

    pkt = ControllerPacket(buttons=buttons, x=x, y=y)
    input_queue.put(pkt)


async def ble_main():
    """
    Main BLE coroutine:
      - scan for device
      - connect
      - subscribe to notifications
      - keep the connection alive
    """
    global ble_connected

    addr = await find_device()
    if addr is None:
        print("BLE: device not found, aborting")
        return
    
    print("BLE: connecting to", addr)
    async with BleakClient(addr) as client:
        print("BLE: connected")
        ble_connected = True

        print("BLE: starting notification on", CHAR_UUID)
        await client.start_notify(CHAR_UUID, notification_handler)

        try:
            while True:
                if not client.is_connected:
                    print("BLE: disconnected")
                await asyncio.sleep(0.1)
        finally:
            ble_connected = False
            try:
                await client.stop_notify(CHAR_UUID)
            except Exception:
                pass
            print("BLE: exiting ble_main")


def start_ble_thread():
    """
    Run the BLE asyncio loop in a background thread so pygame can own the main thread.
    """
    loop = asyncio.new_event_loop()

    def runner():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ble_main())
        loop.close()

    t = threading.Thread(target=runner, daemon=True)
    t.start()


def run_pygame():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    button_img = pygame.image.load("sprites\\L_Red.png").convert_alpha()
    button_img = pygame.transform.scale_by(button_img, 0.5)

    buttons_state = 0
    x_axis = 0
    y_axis = 0

    dt = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(pygame.Color(239, 233, 227))

        try:
            while True:
                pkt = input_queue.get_nowait()
                buttons_state = pkt.buttons
                x_axis = pkt.x
                y_axis = pkt.y
        except queue.Empty:
            pass

        pos.x = max(0, min(800, pos.x + x_axis * dt))
        pos.y = max(0, min(600, pos.y + y_axis * dt))

        screen.blit(button_img, pos)

        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            running = False

        dt = clock.tick(60) / 1000

pygame.quit()


if __name__ == "__main__":
    start_ble_thread()
    run_pygame()