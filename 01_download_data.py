"""Download input data: NOAA OISST v2.1 daily SST and NOAA/NSIDC CDR
sea-ice concentration (G02202 v4, yearly aggregates)."""

import datetime
import requests

SST_URL = ("https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/"
           "v2.1/access/avhrr/{ym}/oisst-avhrr-v02r01.{ymd}.nc")
SIC_URL = ("https://noaadata.apps.nsidc.org/NOAA/G02202_V4/north/aggregate/"
           "seaice_conc_daily_nh_{year}_v04r00.nc")


def fetch(url, filename):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def download_sst(start="1982-01-01", end="2025-12-31", out_dir="data/SST"):
    day = datetime.date.fromisoformat(start)
    stop = datetime.date.fromisoformat(end)
    while day <= stop:
        ymd = day.strftime("%Y%m%d")
        fetch(SST_URL.format(ym=ymd[:6], ymd=ymd),
              f"{out_dir}/oisst-avhrr-v02r01.{ymd}.nc")
        day += datetime.timedelta(days=1)


def download_sic(year_start=1982, year_end=2025, out_dir="data/SIC"):
    for year in range(year_start, year_end + 1):
        fetch(SIC_URL.format(year=year), f"{out_dir}/sic{year}.nc")


if __name__ == "__main__":
    download_sst()
    download_sic()
