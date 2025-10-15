"""
Rate limiting implementation for preventing abuse
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API endpoints"""

    def __init__(self):
        self.rate_limits: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

        # Configuration
        self.default_requests_per_minute = 60
        self.max_failed_logins = 5
        self.lockout_duration = 300  # 5 minutes
        self.failed_login_attempts: Dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(
        self, identifier: str, window_seconds: int = 60, max_requests: int = None
    ) -> bool:
        """
        Check if request is allowed based on rate limit

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            window_seconds: Time window in seconds
            max_requests: Maximum requests allowed in window

        Returns:
            True if request is allowed, False otherwise
        """
        if max_requests is None:
            max_requests = self.default_requests_per_minute

        current_time = time.time()

        with self.lock:
            # Get request history for this identifier
            requests = self.rate_limits[identifier]

            # Remove old requests outside the window
            while requests and current_time - requests[0] > window_seconds:
                requests.popleft()

            # Check if we're under the limit
            if len(requests) < max_requests:
                requests.append(current_time)
                return True

            return False

    def is_ip_allowed(self, ip_address: str, user_agent: str = "") -> bool:
        """
        Check if IP address is allowed (with user agent consideration)

        Args:
            ip_address: Client IP address
            user_agent: User agent string

        Returns:
            True if IP is allowed, False otherwise
        """
        # Create identifier combining IP and user agent
        identifier = f"{ip_address}:{hash(user_agent) % 1000}"

        # Check for failed login attempts
        if self._is_ip_locked_out(ip_address):
            logger.warning(
                f"IP {ip_address} is locked out due to failed login attempts"
            )
            return False

        return self.is_allowed(identifier)

    def record_failed_login(self, ip_address: str) -> bool:
        """
        Record a failed login attempt

        Args:
            ip_address: Client IP address

        Returns:
            True if IP should be locked out
        """
        current_time = time.time()

        with self.lock:
            failed_attempts = self.failed_login_attempts[ip_address]

            # Remove old failed attempts outside lockout window
            while (
                failed_attempts
                and current_time - failed_attempts[0] > self.lockout_duration
            ):
                failed_attempts.popleft()

            # Add current failed attempt
            failed_attempts.append(current_time)

            # Check if we should lock out this IP
            if len(failed_attempts) >= self.max_failed_logins:
                logger.warning(
                    f"IP {ip_address} locked out due to {len(failed_attempts)} failed login attempts"
                )
                return True

            return False

    def record_successful_login(self, ip_address: str):
        """
        Record a successful login (clears failed attempts)

        Args:
            ip_address: Client IP address
        """
        with self.lock:
            if ip_address in self.failed_login_attempts:
                self.failed_login_attempts[ip_address].clear()
                logger.info(f"Cleared failed login attempts for IP {ip_address}")

    def _is_ip_locked_out(self, ip_address: str) -> bool:
        """
        Check if IP is currently locked out

        Args:
            ip_address: Client IP address

        Returns:
            True if IP is locked out
        """
        current_time = time.time()

        with self.lock:
            failed_attempts = self.failed_login_attempts[ip_address]

            # Remove old failed attempts
            while (
                failed_attempts
                and current_time - failed_attempts[0] > self.lockout_duration
            ):
                failed_attempts.popleft()

            return len(failed_attempts) >= self.max_failed_logins

    def get_remaining_attempts(self, ip_address: str) -> int:
        """
        Get remaining login attempts for IP

        Args:
            ip_address: Client IP address

        Returns:
            Number of remaining attempts
        """
        current_time = time.time()

        with self.lock:
            failed_attempts = self.failed_login_attempts[ip_address]

            # Remove old failed attempts
            while (
                failed_attempts
                and current_time - failed_attempts[0] > self.lockout_duration
            ):
                failed_attempts.popleft()

            return max(0, self.max_failed_logins - len(failed_attempts))

    def get_lockout_time_remaining(self, ip_address: str) -> int:
        """
        Get remaining lockout time for IP

        Args:
            ip_address: Client IP address

        Returns:
            Remaining lockout time in seconds, 0 if not locked out
        """
        current_time = time.time()

        with self.lock:
            failed_attempts = self.failed_login_attempts[ip_address]

            if len(failed_attempts) < self.max_failed_logins:
                return 0

            # Find the oldest failed attempt
            oldest_attempt = min(failed_attempts)
            time_elapsed = current_time - oldest_attempt
            time_remaining = self.lockout_duration - time_elapsed

            return max(0, int(time_remaining))

    def cleanup_old_records(self, max_age_seconds: int = 3600):
        """
        Clean up old rate limit records

        Args:
            max_age_seconds: Maximum age of records to keep
        """
        current_time = time.time()

        with self.lock:
            # Clean up rate limits
            for identifier in list(self.rate_limits.keys()):
                requests = self.rate_limits[identifier]
                while requests and current_time - requests[0] > max_age_seconds:
                    requests.popleft()

                # Remove empty records
                if not requests:
                    del self.rate_limits[identifier]

            # Clean up failed login attempts
            for ip_address in list(self.failed_login_attempts.keys()):
                failed_attempts = self.failed_login_attempts[ip_address]
                while (
                    failed_attempts
                    and current_time - failed_attempts[0] > max_age_seconds
                ):
                    failed_attempts.popleft()

                # Remove empty records
                if not failed_attempts:
                    del self.failed_login_attempts[ip_address]

    def get_stats(self) -> Dict[str, any]:
        """
        Get rate limiter statistics

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                "active_rate_limits": len(self.rate_limits),
                "locked_out_ips": len(
                    [
                        ip
                        for ip in self.failed_login_attempts
                        if self._is_ip_locked_out(ip)
                    ]
                ),
                "total_failed_attempts": sum(
                    len(attempts) for attempts in self.failed_login_attempts.values()
                ),
            }


# Global rate limiter instance
rate_limiter = RateLimiter()
