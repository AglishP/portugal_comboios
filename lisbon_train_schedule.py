import requests
import datetime
import argparse
from bs4 import BeautifulSoup


URL = "https://www.cp.pt/sites/passageiros/pt/consultar-horarios/horarios-resultado"
dateFormater = '%Y-%m-%d'
timeFormater = '%H:%M'
timeResponseFormater = '%Hh%M'
DEPARTURE_STATION = 'Santo Amaro'
ARRIVE_STATION = 'Lisboa - Cais do Sodre'
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
    direction = [{'arriveTo': cityStation, 'trains': getNext2Trains(currentStation, cityStation)}]
    if oceanStation != None:
        direction.append({'arriveTo': oceanStation, 'trains': getNext2Trains(currentStation, oceanStation)})

    result = {'currentStation': currentStation,'direction': direction}
    
    print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get next 2 trains from yours station to Cais do Sodre and Cascais')
    parser.add_argument('-d', '--departure', help='Your home stations from wich we search schedule', required=False)
    parser.add_argument('-a', '--arrive', help='Your arrival station', required=False)
    parser.add_argument('-tw', '--twoway', help='Use default station for second directions', required=False, action='store_true', default=False)
    parser.add_argument('-o', '--ocean', help='Your ocean station', required=False)
    args = parser.parse_args()
    if args.departure != None:
        departureStation = args.departure
    else:
        departureStation = DEPARTURE_STATION
    if args.arrive != None:
        cityStation = args.arrive
    else:
        cityStation = ARRIVE_STATION
    oceanStation = None
    if args.ocean != None:
        oceanStation = args.ocean
    else:
        if args.twoway != None and args.twoway == True:
            oceanStation = OCEAN_STATION
    main(departureStation, cityStation, oceanStation)

