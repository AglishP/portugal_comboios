import requests
import datetime
from bs4 import BeautifulSoup


URL = "https://www.cp.pt/sites/passageiros/pt/consultar-horarios/horarios-resultado"
dateFormater = '%Y-%m-%d'
timeFormater = '%H:%M'



def get_whole_schedule(sdate, stime, departure, arrival):
    print('schedule')

    postData = {'allServices': 'allServices',
            'depart': departure,
            'arrival': arrival,
            # 'Date': '8 Maio, 2023',
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
            resultList.append(td.text)
    return resultList


if __name__ == '__main__':
    now = datetime.datetime.now()
    sdate = now.strftime(dateFormater)
    stime = now.strftime(timeFormater)
    departure = 'Carcavelos'
    arrival = 'Cascais'

    rowSchedule = get_whole_schedule(sdate, stime, departure, arrival)
    
    rowList = rowSchedule_ToList(rowSchedule)
    print(rowList)

