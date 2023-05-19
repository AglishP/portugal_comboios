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
SECOND_DESTINATION = 'Cascais'



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
        departureTime = None
        duration = None
        for td in foundTd:
            if 'id' in td.attrs and 'goDeparTime' in td.attrs['id']:
                departureTime = datetime.datetime.strptime(td.text, timeResponseFormater)
            elif td.text != None and len(td.text) > 0:
                if td.text[1] == 'h' or td.text[2] == 'h':
                    duration = td.text
        if departureTime != None and duration != None:
            resultList.append({'departureTime': departureTime, 'duration': duration})
    return resultList

def findClosestAndNext(rowList):
    now = datetime.datetime.now().strftime(timeFormater)
    currentTime = datetime.datetime.strptime(now, timeFormater)
    closestTo = None
    i = 0
    closestIndex = None
    nextTime = None
    while i < len(rowList):
        time = rowList[i].get('departureTime')
        if time > currentTime:
            if closestTo == None:
                closestTo = rowList[i]
                closestIndex = i
            elif time < closestTo.get('departureTime'):
                closestTo = rowList[i]
                closestIndex = i
        i+=1
    result = None
    if closestIndex != None and closestIndex < len(rowList) - 1:
        nextTime = rowList[closestIndex + 1]
        nextTime = {'departureTime': nextTime.get('departureTime').strftime(timeFormater), 'duration': nextTime.get('duration')}

    if closestTo != None:
        closestTo = {'departureTime': closestTo.get('departureTime').strftime(timeFormater), 'duration': closestTo.get('duration')}   
    print('Closest to: ' + str(closestTo))
    print('Next time: ' + str(nextTime))    
    result = {'closestTo': closestTo, 'nextTime': nextTime}
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
    return findClosestAndNext(rowList)

def main(currentStation, cityStation, secondDestination):
    direction = [{'arriveTo': cityStation, 'trains': getNext2Trains(currentStation, cityStation)}]
    if secondDestination != None:
        direction.append({'arriveTo': secondDestination, 'trains': getNext2Trains(currentStation, secondDestination)})

    result = {'currentStation': currentStation,'direction': direction}
    
    print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get next 2 trains from yours station to Cais do Sodre and Cascais')
    parser.add_argument('-d', '--departure', help='Your home stations from wich we search schedule', required=False)
    parser.add_argument('-a', '--arrive', help='Your arrival station', required=False)
    parser.add_argument('-tw', '--twoway', help='Use default station for second directions', required=False, action='store_true', default=False)
    parser.add_argument('-sd', '--second_destination', help='Your second destination', required=False)
    args = parser.parse_args()
    if args.departure != None:
        departureStation = args.departure
    else:
        departureStation = DEPARTURE_STATION
    if args.arrive != None:
        cityStation = args.arrive
    else:
        cityStation = ARRIVE_STATION
    secondDestination = None
    if args.second_destination != None:
        secondDestination = args.second_destination
    else:
        if args.twoway != None and args.twoway == True:
            secondDestination = SECOND_DESTINATION
    main(departureStation, cityStation, secondDestination)

