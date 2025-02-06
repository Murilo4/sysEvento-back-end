from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class DailyRateThrottle(UserRateThrottle):
    scope = 'daily'


class HourlyRateThrottle(UserRateThrottle):
    scope = 'hourly'


class MinuteRateThrottle(UserRateThrottle):
    scope = 'minute'


class MinuteRateThrottleAnon(AnonRateThrottle):
    scope = 'anon'
