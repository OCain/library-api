from abc import ABC, abstractmethod
import os


class FeeRule(ABC):
    @abstractmethod
    def get_fee(self, days_late: int) -> float:
        pass

    def calculate_fee(self, days_late: int, penalty_rate: float, interest_rate: float) -> float:
        return penalty_rate + (interest_rate * days_late)


class InitialFeeRule(FeeRule):
    MIN_DAYS_LATE = os.getenv('MIN_DAYS_LATE', 1)
    MAX_DAYS_LATE = 3
    PENALTY_RATE = 0.03
    INTEREST_RATE = 0.002

    def __init__(self) -> None:
        self.next_rule = FeeRule2()

    def get_fee(self, days_late: int) -> float:
        if self.MIN_DAYS_LATE <= days_late <= self.MAX_DAYS_LATE:
            return super().calculate_fee(days_late, self.PENALTY_RATE, self.INTEREST_RATE)
        return self.next_rule.get_fee(days_late)

class FeeRule2(FeeRule):
    PREVIOUS_MAX_DAYS_LATE = InitialFeeRule.MAX_DAYS_LATE
    MAX_DAYS_LATE = 5
    PENALTY_RATE = 0.05
    INTEREST_RATE = 0.004

    def __init__(self) -> None:
        self.next_rule = LastFeeRule()

    def get_fee(self, days_late: int) -> float:
        if self.PREVIOUS_MAX_DAYS_LATE < days_late <= self.MAX_DAYS_LATE:
            return super().calculate_fee(days_late, self.PENALTY_RATE, self.INTEREST_RATE)
        return self.next_rule.get_fee(days_late)


class LastFeeRule(FeeRule):
    PREVIOUS_MAX_DAYS_LATE = FeeRule2.MAX_DAYS_LATE
    PENALTY_RATE = 0.07
    INTEREST_RATE = 0.006
    
    def get_fee(self, days_late: int) -> float:
        if days_late > self.PREVIOUS_MAX_DAYS_LATE:
            return super().calculate_fee(days_late, self.PENALTY_RATE, self.INTEREST_RATE)
        return 0