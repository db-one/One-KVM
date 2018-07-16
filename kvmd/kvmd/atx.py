import asyncio

from typing import Dict

from .logging import get_logger

from . import aioregion
from . import gpio


# =====
class AtxIsBusy(aioregion.RegionIsBusyError):
    pass


class Atx:
    def __init__(
        self,
        power_led: int,
        hdd_led: int,

        power_switch: int,
        reset_switch: int,
        click_delay: float,
        long_click_delay: float,
    ) -> None:

        self.__power_led = gpio.set_input(power_led)
        self.__hdd_led = gpio.set_input(hdd_led)

        self.__power_switch = gpio.set_output(power_switch)
        self.__reset_switch = gpio.set_output(reset_switch)
        self.__click_delay = click_delay
        self.__long_click_delay = long_click_delay

        self.__region = aioregion.AioExclusiveRegion(AtxIsBusy)

    def get_state(self) -> Dict:
        return {
            "busy": self.__region.is_busy(),
            "leds": {
                "power": (not gpio.read(self.__power_led)),
                "hdd": (not gpio.read(self.__hdd_led)),
            },
        }

    async def click_power(self) -> None:
        await self.__click(self.__power_switch, self.__click_delay)
        get_logger().info("Clicked power")

    async def click_power_long(self) -> None:
        await self.__click(self.__power_switch, self.__long_click_delay)
        get_logger().info("Clicked power (long press)")

    async def click_reset(self) -> None:
        await self.__click(self.__reset_switch, self.__click_delay)
        get_logger().info("Clicked reset")

    async def __click(self, pin: int, delay: float) -> None:
        with self.__region:
            for flag in (True, False):
                gpio.write(pin, flag)
                await asyncio.sleep(delay)
