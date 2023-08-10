import requests
import os
import concurrent.futures

# Reads the URL from the command line argument


def findFileObs(url, year, doy, obs, station):
    if not url.endswith("*?list"):
        url = url.format(year, doy, obs) + "*?list"
    r = requests.get(url)
    for file in r.text.splitlines():
        if file.startswith(station):
            return file.split(" ")[0]


def findFileNav(url, year, doy, nav, navStation):
    if not url.endswith("*?list"):
        url = url.format(year, doy, nav) + "*?list"
    r = requests.get(url)
    for file in r.text.splitlines():
        if file.startswith(navStation):
            return file.split(" ")[0]


def download(url, year, doy):
    # Assigns the local file name to the last part of the URL
    filename = url.split("/")[-1]

    # Makes request of URL, stores response in variable r
    r = requests.get(url)

    if not os.path.exists(f"gddis/{year}/{doy}"):
        os.makedirs(f"gddis/{year}/{doy}")

    # Opens a local file of same name as remote file for writing to
    with open(f"gddis/{year}/{doy}/{filename}", "wb") as fd:
        for chunk in r.iter_content(chunk_size=1000):
            fd.write(chunk)

    # Closes local file
    fd.close()


def download_files(url, startYear, doy, obs, station, nav, navStation):
    fileObs = findFileObs(url, startYear, doy, obs, station)
    dFileObs = url.format(startYear, doy, obs) + fileObs
    print(f"Downloading {dFileObs}...")
    download(dFileObs, startYear, doy)

    fileNav = findFileNav(url, startYear, doy, nav, navStation)
    dFileNav = url.format(startYear, doy, obs) + fileNav
    print(f"Downloading {fileNav}...")
    download(dFileNav, startYear, doy)

    print(f"Downloaded {startYear}/{doy}.")


years = ["2000", "2022"]
print(f"years {years}")
url = "https://cddis.nasa.gov/archive/gnss/data/daily/{}/{}/{}/"

navStation = "brdc"
print(f"navStation {navStation}")
station = "mad"
print(f"station {station}")
for year in years:
    print(f"year {year}")

    suffixYear = year[2:4]

    nav = f"{suffixYear}n"
    print(f"nav {nav}")

    obs = f"{suffixYear}o"
    print(f"obs {obs}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for doy in range(1, 366):
            futures.append(
                executor.submit(
                    download_files,
                    url,
                    year,
                    str(doy).zfill(3),
                    obs,
                    station,
                    nav,
                    navStation,
                )
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")
