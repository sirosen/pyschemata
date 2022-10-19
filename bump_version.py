import datetime
import subprocess

from packaging.version import Version


def bump_pre(v: Version) -> str:
    assert v.pre
    assert v.pre[0] == "a"
    pre_num = v.pre[1] + 1
    return f"{v.major}.{v.minor}.{v.micro}{v.pre[0]}{pre_num}"


def get_version() -> Version:
    raw = subprocess.check_output(["hatch", "version"], text=True)
    return Version(raw)


def get_new_version():
    old = get_version()
    old_year, old_month, old_day = old.major, old.minor, old.micro

    today_v_str = datetime.date.today().strftime("%y.%m.%db0")
    today_v = Version(today_v_str)
    if (today_v.major, today_v.minor, today_v.micro) == (old_year, old_month, old_day):
        return bump_pre(old)

    return today_v_str


def main():
    print("updating...")
    subprocess.run(["hatch", "version", get_new_version()])
    print("done")


if __name__ == "__main__":
    main()
