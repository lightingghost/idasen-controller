#!/usr/bin/python3

import bleak
import struct
import logging
import time

class IdasenDesk:
    MAX_HEIGHT = 6500
    MIN_HEIGHT = 0
    MIN_MOVEMENT = 0
    POSITION_SERVICE_UUID = "99FA0020-338A-1024-8A49-009C0215F78A"

    def __init__(self, address):
        self._address = address
        self._client = bleak.BleakClient(address)

    async def is_connected(self):
        return await self._client.is_connected()

    async def _connect(self):
        logging.info('Connecting to the desk..')
        await self._client.connect()
        if await self.is_connected():
            logging.info('Desk connected!')
            return True
        else:
            logging.info('Unable to connect to the desk.')
            return False
        
    async def _connect_and_validate(self):
        if not await self._connect():
            return False
        return await self._validate()

    async def _disconnect(self):
        await self._client.disconnect()
        logging.info('Desk disconnected!')

    async def _validate(self):
        services = await self._client.get_services()
        for svc in services:
            if str(svc.UUID()) == self.POSITION_SERVICE_UUID:
                logging.info('Valid Idasen desk.')
                return True
        logging.info('Invalid Idasen desk')
        return False

    async def _move_up(self):
        await self._client.write_gatt_char(15, bytes.fromhex("4700"))

    async def _move_down(self):
        await self._client.write_gatt_char(15, bytes.fromhex("4600"))

    async def get_position(self):
        pos = await self._client.read_gatt_char(25)
        return struct.unpack('<H', pos[0:2])[0]

    async def move_to(self, target_pos):
        prev_pos = -6500
        cur_pos = await self.get_position()
        logging.debug(f"Current position: {cur_pos}")
        if target_pos < cur_pos:
            while target_pos < cur_pos and abs(cur_pos - prev_pos) > self.MIN_MOVEMENT:
                await self._move_down()
                prev_pos = cur_pos
                time.sleep(0.3)
                cur_pos = await self.get_position()
                logging.debug(f"Current position: {cur_pos}")
        elif target_pos > cur_pos:
            while target_pos > cur_pos and abs(cur_pos - prev_pos) > self.MIN_MOVEMENT:
                await self._move_up()
                prev_pos = cur_pos
                time.sleep(0.3)
                cur_pos = await self.get_position()
                logging.debug(f"Current position: {cur_pos}")
