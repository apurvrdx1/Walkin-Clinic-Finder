from bs4 import BeautifulSoup
import requests
import re, sys, datetime
from decouple import config
import googlemaps
from tqdm import tqdm


# gmaps api key through .env file
API_KEY = config("GOOGLE_MAPS_API_KEY")


def main():
    clinic_list = scrape_data()
    # print(clinic_list)
    update_hours(clinic_list)
    # print(clinic_list[0])
    update_distance(clinic_list)
    update_isOpen(clinic_list)
    sorted_clinic_list = sort_clinic_list(clinic_list)
    open_now_list = open_clinics_list(sorted_clinic_list)
    # print_results(sorted_clinic_list)
    print_results(open_now_list)
    # # print(sorted_clinic_list)


def isOpenUntil(clinic_hours):
    # clinic_hours = clinic['hours']
    now = datetime.datetime.now()
    day = now.strftime("%a")
    todays_hours = None
    # print(clinic_hours)
    for item in clinic_hours:
        if item["day"] == day:
            todays_hours = item
    hoursTime = str(todays_hours["end_hour"]) + ":" + str(todays_hours["end_minutes"])
    d = datetime.datetime.strptime(hoursTime, "%H:%M")
    c = d.strftime("%I:%M %p")
    timeText = "   This clinic is open until " + str(c)
    print(timeText)


# assign and then print the closest clinic details
def print_results(sorted_clinic_list):
    i = 0
    try:
        print()
        print()
        print("Closest clinics to you >> ")
        print()
        for i in [0, 1, 2]:
            print(f"{i+1}  Clinic name: {sorted_clinic_list[i]['name']}")
            print(f"   Address: {sorted_clinic_list[i]['address']}")
            print(f"   Phone number: {sorted_clinic_list[i]['phone']}")
            print("   ______________________")
            print()
            print(f"   Distance from you: {sorted_clinic_list[i]['distance']}")
            print(f"   Time req. to drive there: {sorted_clinic_list[i]['drive_time']}")
            print(
                f"   Time req. to get there by transit: {sorted_clinic_list[i]['transit_time']}"
            )
            isOpenUntil(sorted_clinic_list[i]["hours"])
            print(f"   Additional info: {sorted_clinic_list[i]['url']}")
            print()
            print("________________________________________________________________")
            print()
            print()
            i += 1
    except:
        sys.exit("Could not find nearest clinics. Error code: PRT")


def scrape_data():
    # scrape data from source website
    source = requests.get(
        "https://www.torontocentralhealthline.ca/listServices.aspx?id=10072"
    ).text
    soup = BeautifulSoup(source, "lxml")

    form = soup.form
    rows = soup.find_all("tr")

    clinic_list = []
    for row in rows:
        try:
            clinic = {
                "name": None,
                "url": None,
                "address": None,
                "phone": None,
                "distance": 0,
                "drive_time": None,
                "transit_time": None,
                "hours": None,
                "isOpen": None,
            }
            clinic["name"] = row.a.text
            clinic_url_stub = row.a["href"]
            clinic_url = None
            if clinic_url_stub:
                clinic_url = (
                    "https://www.torontocentralhealthline.ca/" + clinic_url_stub
                )
            else:
                raise ValueError("Clinic URL stub does not exist")
            clinic_contact_polluted = row.find_all(
                "span", class_="regtext", id=re.compile("ContentPlaceHolder")
            )
            # print(clinic_contact_polluted)
            clinic["url"] = clinic_url
            if len(clinic_contact_polluted) != 0:
                clinic["address"] = (clinic_contact_polluted[0].text).replace(
                    "\xa0\xa0", " "
                )
                clinic["phone"] = clinic_contact_polluted[1].text
            if clinic["name"] != "www.cpso.on.ca" and clinic["address"] != None:
                clinic_list.append(clinic)

        except AttributeError:
            pass

    # print(clinic_list)
    print("Downtown Toronto walkin clinics found: ", len(clinic_list))
    return clinic_list


# request user address to get location
def user_location():
    user_address = input("Please enter your address: ")
    return user_address


# update distance key for all clinics found
def update_distance(clinic_list):
    user_address = user_location()

    for item in tqdm(clinic_list, desc="Calculating distance"):
        dest_address = item["address"]
        # print(dest_address, user_address)

        # Requires API key
        gmaps = googlemaps.Client(key=API_KEY)

        # Requires cities name
        google_maps_reponse_drive = gmaps.distance_matrix(user_address, dest_address)[
            "rows"
        ][0]["elements"][0]
        google_maps_reponse_transit = gmaps.distance_matrix(
            user_address, dest_address, mode="transit"
        )["rows"][0]["elements"][0]

        # assigning distance, drive_time and transit_time to clinic_list dicts
        item["distance"] = google_maps_reponse_drive["distance"]["text"]
        item["drive_time"] = google_maps_reponse_drive["duration"]["text"]
        item["transit_time"] = google_maps_reponse_transit["duration"]["text"]
        # Printing the result
        # print(item)


# create a sorted list from clinic_list using the 'distance' key
def sort_clinic_list(clinic_list):
    sorted_clinics = sorted(clinic_list, key=lambda d: d["distance"])
    return sorted_clinics


def open_clinics_list(sorted_clinic_list):
    open_clinics = []
    for clinic in sorted_clinic_list:
        if clinic["isOpen"] == True:
            open_clinics.append(clinic)
        # else:
        # print(clinic['name'], clinic['hours'])
    # print(open_clinics)
    return open_clinics


def hour_convert(time, day_phase):
    if len(time) in (4, 5):
        hours, minutes = time.split(":")
    elif len(time) not in (4, 5):
        hours = time
        minutes = "00"

    if int(minutes) > 59 or int(hours) > 12:
        raise ValueError

    if day_phase.upper() == "PM" and hours != "12":
        hours = int(hours) + 12
    elif (day_phase.upper() == "AM" and hours == "12") or (
        day_phase.lower() == "midnight" and hours == "12"
    ):
        hours = "00"

    if int(hours) >= 10 or hours == "00" or day_phase == "noon":
        hcout = str(hours) + "-" + minutes
    else:
        hcout = "0" + str(hours) + "-" + minutes
    return hcout


def convert(s):
    regex_var = re.search(
        r"(\d?\d:?\d?\d?)\s?(AM|PM|am|pm|noon|midnight)-?(\d?\d:?\d?\d?)\s?(AM|PM|am|pm|noon|midnight)(.+)?",
        s,
    )
    if regex_var:
        start_time, start_phase, end_time, end_phase = (
            regex_var.group(1),
            regex_var.group(2),
            regex_var.group(3),
            regex_var.group(4),
        )
    elif regex_var == None:
        raise ValueError
    else:
        raise ValueError

    converted_start = hour_convert(start_time, start_phase)
    converted_end = hour_convert(end_time, end_phase)

    converted_time = converted_start + "-" + converted_end
    return converted_time


def update_hours(clinic_list):
    for clinic in tqdm(clinic_list, desc="Updating clinic hours"):
        clinic["hours"] = scrape_time(clinic["url"])


def scrape_time(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")

    form = soup.form
    tables = soup.find_all("table", id="expandedhours")

    for table in tables:
        try:
            clinic_hours_polluted = table.text.split("\n")
            clinic_hours_polluted.pop(0)
            clinic_hours_polluted.pop(0)
            clinic_hours_polluted.pop(-1)

            clinic_hours_polluted1 = []
            for item in clinic_hours_polluted:
                if item.endswith("Open"):
                    item1 = item.split("Open")
                    item = item1[0]
                clinic_hours_polluted1.append(item)

            # print(clinic_hours_trimmed)

            clinic_hours_trimmed = []
            clinic_hours = []
            new_list = [x for x in clinic_hours_polluted1 if x != ""]
            for item in new_list:
                item1 = item.replace("\xa0", "")
                item = item1.replace("-", "")
                clinic_hours_trimmed.append(item)
            for item in clinic_hours_trimmed:
                item1 = item[:3] + "-" + convert(item[3:])
                # print(item1)
                clinic_hours_item = {
                    "day": None,
                    "start_hour": None,
                    "start_minutes": None,
                    "end_hour": None,
                    "end_minutes": None,
                }
                (
                    clinic_hours_item["day"],
                    clinic_hours_item["start_hour"],
                    clinic_hours_item["start_minutes"],
                    clinic_hours_item["end_hour"],
                    clinic_hours_item["end_minutes"],
                ) = item1.split("-")
                clinic_hours.append(clinic_hours_item)
            return clinic_hours

        except AttributeError:
            pass


def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        # Over midnight:
        return nowTime >= startTime or nowTime <= endTime


def update_isOpen(clinic_list):
    for clinic in clinic_list:
        if clinic["hours"] != None:
            clinic["isOpen"] = isOpen(clinic["hours"])


# normal example:
def isOpen(clinic_hours):
    # clinic_hours = clinic['hours']
    now = datetime.datetime.now()
    day = now.strftime("%a")
    todays_hours = None
    # print(clinic_hours)
    for item in clinic_hours:
        if item["day"] == day:
            todays_hours = item

    now_time = datetime.datetime.now().time()
    if todays_hours:
        start_time = datetime.time(
            int(todays_hours["start_hour"]), int(todays_hours["start_minutes"])
        )
        end_time = datetime.time(
            int(todays_hours["end_hour"]), int(todays_hours["end_minutes"])
        )
        # print(start_time, end_time, now_time)
        is_open_value = isNowInTimePeriod(start_time, end_time, now_time)
        return is_open_value
    else:
        return False


if __name__ == "__main__":
    main()
