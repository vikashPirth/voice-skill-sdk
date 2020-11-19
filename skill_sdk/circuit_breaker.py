""" Circuit breaker for skills requesting external services """

from .config import config
from circuitbreaker import CircuitBreaker
from requests.exceptions import RequestException


class SkillCircuitBreaker(CircuitBreaker):
    """ Circuit breaker's defaults from skill config """

    FAILURE_THRESHOLD = config.getint('circuit_breakers', 'threshold', fallback=5)
    RECOVERY_TIMEOUT = config.getint('circuit_breakers', 'timeout', fallback=30)
    EXPECTED_EXCEPTION = RequestException


# Default circuit breaker will be used if no custom breaker supplied
DEFAULT_CIRCUIT_BREAKER = SkillCircuitBreaker()
