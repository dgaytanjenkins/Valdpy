import zoneinfo

class Settings:
    DEFAULT_TIMEZONE = "America/Los_Angeles"
    ALLOWED_TIMEZONES = zoneinfo.available_timezones()

