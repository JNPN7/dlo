import re


def clean_cron(cron: str) -> str:
    replacements = {
        " ": "_",
        "*": "all",
        "?": "any",
        "/": "by",
        ",": "and",
        "#": "hash",
    }

    # Replace special characters one-by-one
    cleaned = re.sub(
        r"[ */?,#]",
        lambda m: replacements[m.group()],
        cron,
    )

    # Remove anything still unsafe
    cleaned = re.sub(r"[^\w\-]", "", cleaned)

    # Collapse multiple underscores
    cleaned = re.sub(r"_+", "_", cleaned)

    return cleaned.strip("_")


def cron_to_human_time(cron: str) -> str:
    """
    Converts a Quartz cron expression into a human-readable string.
    Supports: minutes, hours, days, weeks, months, daily fixed times.
    """
    parts = cron.strip().split()
    if len(parts) < 6:
        return "invalid cron"

    sec, minute, hour, day, month, dow = parts[:6]

    def get_interval(field):
        if "/" in field:
            return field.split("/")[1]
        return None

    def is_all(field):
        return field == "*" or field == "?" or field == "1/1" or field == "*/1"

    # Minutes interval
    min_interval = get_interval(minute)
    if min_interval and is_all(hour) and is_all(day) and is_all(dow):
        if min_interval == "1":
            return "every minute"
        return f"every {min_interval} minutes"

    # Hours interval
    hour_interval = get_interval(hour)
    if hour_interval and minute == "0" and is_all(day) and is_all(dow):
        if hour_interval == "1":
            return "every hour"
        return f"every {hour_interval} hours"

    # Days interval
    day_interval = get_interval(day)
    if day_interval and minute == "0" and hour == "0" and is_all(dow):
        if day_interval == "1":
            return "every day"
        return f"every {day_interval} days"

    # Daily at fixed time
    is_time_fixed = ("/" not in minute) and ("/" not in hour) and (minute != "*") and (hour != "*")
    is_daily = is_all(day) and is_all(dow) and is_all(month)

    if is_time_fixed and is_daily:
        return f"every day at {int(hour):02d}:{int(minute):02d}"

    # Weekly on day_of_week
    is_weekly = (not is_all(dow)) and is_all(day)
    if is_weekly and is_time_fixed:
        try:
            # Helper to parse single dow token
            def parse_dow(d_str):
                d_str = d_str.upper()
                replacements = {
                    "SUN": 1,
                    "MON": 2,
                    "TUE": 3,
                    "WED": 4,
                    "THU": 5,
                    "FRI": 6,
                    "SAT": 7,
                }
                if d_str in replacements:
                    return replacements[d_str]
                return int(d_str)

            dow_list = []
            for part in dow.split(","):
                if "-" in part:
                    start, end = map(parse_dow, part.split("-"))
                    dow_list.extend(range(start, end + 1))
                else:
                    dow_list.append(parse_dow(part))

            # Unique and sort
            dow_list = list(set(dow_list))
            # Sort by calendar order (Mon=0 .. Sun=6)
            dow_list.sort(key=lambda d: (d - 2) % 7)

            # Convert to names: Quartz 1=SUN...7=SAT -> Calendar 0=MON...6=SUN
            # (d - 2) % 7 maps 1->6 (Sun), 2->0 (Mon)
            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            days_str = ", ".join([day_names[(d - 2) % 7] for d in dow_list])
            return f"every {days_str} at {int(hour):02d}:{int(minute):02d}"
        except Exception:
            return "custom schedule"

    # Monthly on a specific day
    if day != "?" and day != "*" and month == "*" and is_all(dow):
        return f"every month on day {day} at {int(hour):02d}:{int(minute):02d}"

    return "custom schedule"
