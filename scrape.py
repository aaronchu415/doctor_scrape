from bs4 import BeautifulSoup
import json
import requests
import csv


def cleanData(raw_json):
    #strip out anything before mapboxlocations =
    raw_json = raw_json[raw_json.index("mapboxlocations =") + len("mapboxlocations ="):]
    #strip out any spacing before and after
    raw_json = raw_json.strip()
    #remove the semi colon at the end
    raw_json = raw_json[:-1]
    #return dictionary of the data
    return json.loads(raw_json)


def extractData(BASE_URL):

    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    #we only care about the first script, that is were the data is
    list_of_scripts = soup.findAll("script")
    doctor_data_raw = list_of_scripts[1].text

    #clean data and turn into object
    doctor_data_obj = cleanData(doctor_data_raw)

    output = []

    for data in doctor_data_obj['features']:
        doctor_obj = {}
        doctor_obj['firstName'] = data['properties']['firstName']
        doctor_obj['lastName'] = data['properties']['lastName']
        doctor_obj['phone'] = data['properties']['phone']
        doctor_obj['address'] = data['properties']['address']
        doctor_obj['city'] = data['properties']['city']
        doctor_obj['state'] = data['properties']['state']
        doctor_obj['profileLink'] = f"https://doctor.webmd.com/doctor/{data['properties']['profilelink']}"

        output.append(doctor_obj)

    return output


FINAL_DATA = []
TOTAL_PAGES = 91

for i in range(1, TOTAL_PAGES):
    PAGE_NUM = i
    BASE_URL = f"https://doctor.webmd.com/results?city=San%20Francisco&state=CA&loc=San%20Francisco%2C%20CA&sd=29264&distance=250&pagenumber={PAGE_NUM}"
    print(BASE_URL)
    print(f'----------------{int(i/TOTAL_PAGES * 100)}% DONE------------------')
    FINAL_DATA.extend(extractData(BASE_URL))

print(FINAL_DATA)

keys = FINAL_DATA[0].keys()
with open('doctors.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(FINAL_DATA)
