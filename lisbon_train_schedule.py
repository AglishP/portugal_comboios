import requests
import datetime
import argparse
from bs4 import BeautifulSoup


URL = "https://www.cp.pt/sites/passageiros/pt/consultar-horarios/horarios-resultado"
dateFormater = '%Y-%m-%d'
timeFormater = '%H:%M'
timeResponseFormater = '%Hh%M'
CITY_STATION = 'Lisboa - Cais do Sodre'
OCEAN_STATION = 'Cascais'



def get_whole_schedule(sdate, stime, departure, arrival):
    postData = {'allServices': 'allServices',
            'depart': departure,
            'arrival': arrival,
            'departDate': sdate,
            'timeType': 1,
            'time': stime,
            'returnTimeType': 1
        }
    
    requestResult = requests.post(URL, data = postData)
    parsed = BeautifulSoup(requestResult.content, 'html.parser')
    
    return parsed.find('table', {'class': 'table table-search-results'})
    
def rowSchedule_ToList(rowSchedule):
    resultList = []
    foundTr = rowSchedule.findAll('tr')
    
    for tr in foundTr:
        foundTd = tr.findAll('td', {'class': 'hidden-xs visible-sm visible-md visible-lg visible-print'})
        if foundTd == None:
            continue
        for td in foundTd:
            if 'id' in td.attrs and 'goDeparTime' in td.attrs['id']:
                resultList.append(td.text)
    return resultList

def findClosestAndNest(rowList):
    now = datetime.datetime.now().strftime(timeFormater)
    currentTime = datetime.datetime.strptime(now, timeFormater)
    sortedList = sorted(rowList)
    closestTo = None
    i = 0
    closestIndex = None
    nextTime = None
    while i < len(sortedList):
        time = sortedList[i]
        time = datetime.datetime.strptime(time, timeResponseFormater)
        if time > currentTime:
            if closestTo == None:
                closestTo = time
                closestIndex = i
            elif time < closestTo:
                closestTo = time
                closestIndex = i
        i+=1
    if closestIndex != None and closestIndex < len(sortedList) - 1:
        nextTime = sortedList[closestIndex + 1]
    result = {'closestTo': closestTo.strftime(timeResponseFormater), 'nextTime': nextTime}
    return result

def getNext2Trains(departure, arrival):
    now = datetime.datetime.now()
    sdate = now.strftime(dateFormater)
    stime = now.strftime(timeFormater)
    rowSchedule = get_whole_schedule(sdate, stime, departure, arrival)
    if rowSchedule == None or len(rowSchedule) == 0:
        print('No schedule found')
        exit()
    rowList = rowSchedule_ToList(rowSchedule)

    if rowList == None or len(rowList) == 0:
        print('No schedule found')
        exit()
    return findClosestAndNest(rowList)

def main(currentStation, cityStation, oceanStation):
    toCity = getNext2Trains(currentStation, cityStation)
    toOcean = getNext2Trains(cityStation, oceanStation)

    result = {'currentStation': currentStation,'toCity': toCity, 'toOcean': toOcean}
    
    print(result)

if __name__ == '__main__':
    currentStation = 'Santo Amaro'
    parser = argparse.ArgumentParser(description='Get next 2 trains from yours station to Cais do Sodre and Cascais')
    parser.add_argument('-s', '--station', help='Your home stations from wich we search schedule', required=False)
    parser.add_argument('-c', '--city', help='Your city station', required=False)
    parser.add_argument('-o', '--ocean', help='Your ocean station', required=False)
    args = parser.parse_args()
    if args.station != None:
        currentStation = args.station
    if args.city != None:
        cityStation = args.city
    else:
        cityStation = CITY_STATION
    if args.ocean != None:
        oceanStation = args.ocean
    else:
        oceanStation = OCEAN_STATION
    main(currentStation, cityStation, oceanStation)

