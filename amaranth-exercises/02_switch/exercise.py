from typing import List, Tuple

from amaranth import Signal, Module, Elaboratable
from amaranth.asserts import Assert

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util import main


class NextDay(Elaboratable):
    def __init__(self):
        self.in_year = Signal(range(1, 10000))
        self.in_month = Signal(4)
        self.in_day = Signal(5)

        self.out_year = Signal(range(1, 10001))
        self.out_month = Signal.like(self.in_month)
        self.out_day = Signal.like(self.in_day)
        self.out_invalid = Signal(1)

    def elaborate(self, _) -> Module:
        m = Module()

        # Invalid inputs
        with m.If((self.in_year == 0) &
                  (self.in_month == 0) &
                  (self.in_day == 0)):
            m.d.comb += self.out_year.eq(0)
            m.d.comb += self.out_month.eq(0)
            m.d.comb += self.out_day.eq(0)
            m.d.comb += self.out_invalid.eq(1)

        is_leap = Signal()
        rollover = Signal.like(self.in_day)

        # Leap year
        m.d.comb += is_leap.eq(0)
        with m.If(((self.in_year % 4) == 0) & ((self.in_year % 100) != 0)):
            m.d.comb += is_leap.eq(1)
        with m.If(((self.in_year % 400) == 0)):
            m.d.comb += is_leap.eq(1)

        # Rollover - max days in month
        with m.Switch(self.in_month):
            with m.Case(2):
                m.d.comb += rollover.eq(28 + is_leap)

            with m.Case(4, 6, 9, 11):
                m.d.comb += rollover.eq(30)

            with m.Default():  # (1, 3, 5, 7, 8, 10, 12)
                m.d.comb += rollover.eq(31)

        # Calculate next day
        m.d.comb += self.out_year.eq(self.in_year)
        m.d.comb += self.out_month.eq(self.in_month)
        m.d.comb += self.out_day.eq(self.in_day + 1)

        with m.If(self.in_day == rollover):
            m.d.comb += self.out_day.eq(1)
            m.d.comb += self.out_month.eq(self.in_month + 1)

            with m.If(self.in_month == 12):
                m.d.comb += self.out_month.eq(1)
                m.d.comb += self.out_year.eq(self.in_year + 1)

        return m

    @classmethod
    def formal(cls) -> Tuple[Module, List[Signal]]:
        m = Module()
        m.submodules.dut = dut = cls()

        with m.If((dut.in_year == 2000) &
                  (dut.in_month == 1) &
                  (dut.in_day == 1)):
            m.d.comb += Assert((dut.out_year == 2000) &
                               (dut.out_month == 1) &
                               (dut.out_day == 2) &
                               (dut.out_invalid == 0)
                               )

        # Leap year
        with m.If((dut.in_year == 2000) &
                  (dut.in_month == 2) &
                  (dut.in_day == 28)):
            m.d.comb += Assert((dut.out_year == 2000) &
                               (dut.out_month == 2) &
                               (dut.out_day == 29) &
                               (dut.out_invalid == 0)
                               )

        # Not a leap year
        with m.If((dut.in_year == 1900) &
                  (dut.in_month == 2) &
                  (dut.in_day == 28)):
            m.d.comb += Assert((dut.out_year == 1900) &
                               (dut.out_month == 3) &
                               (dut.out_day == 1) &
                               (dut.out_invalid == 0)
                               )

        with m.If((dut.in_year == 0) &
                  (dut.in_month == 0) &
                  (dut.in_day == 0)):
            m.d.comb += Assert(dut.out_invalid == 1)

        return m, [
            dut.in_year,
            dut.in_month,
            dut.in_day
        ]


if __name__ == "__main__":
    main(NextDay)
