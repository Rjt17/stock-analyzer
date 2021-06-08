from django.shortcuts import render
from nsetools import Nse
from datetime import date
from nsepy import get_history
import calendar

# Create your views here.
def dashboard(request):

    default_code = "cipla"
    #code
    if request.GET.get('stock') == None:
        code = default_code
    else:
        code = request.GET.get('stock')
    
    raw_data_history_by_month = history_by_month(code, 1)
    data_history_by_month = sequencer(raw_data_history_by_month)
    graph_data_values = raw_data_history_by_month.to_dict('list')
    graph_data_dates_raw = data_history_by_month['dates']
    graph_data_dates = []
    for x in graph_data_dates_raw:
        graph_data_dates.append(x.strftime("%d/%m/%Y"))
    #context
    context = {
    'labels' : graph_data_dates,
    'data' : graph_data_values['Open'],
    'headers' : data_history_by_month['keys'],
    'values' : data_history_by_month['values'],
    'stock_code' : code
    }
    return render(request, "dashboard.html", context)

def about(request):
    return render(request, 'about.html')


# Backend functions
def check_stock_code(stock_code):
    nse = Nse()
    return(nse.is_valid_code(stock_code))

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(day=d,month=m, year=y)

def history_by_month(stock_code, delta):
    end = date.today()
    d1 = end.strftime("%d/%m/%Y")
    day, month, year = map(int, d1.split('/'))
    start = monthdelta(date.today(), -delta)
    d2 = start.strftime("%d/%m/%Y")
    day2, month2, year2 = map(int, d2.split('/'))
    data = get_history(symbol=stock_code, start=date(year2, month2, day2), end=date(year,month,day))
    data = data.loc[::-1]
    return data

def sequencer(data):
    split_data = data.to_dict('split')
    record_data = data.to_dict('records')
    keys = split_data["columns"]
    keys.remove('Turnover')
    keys.remove('VWAP')
    keys.remove('Deliverable Volume')
    keys.remove('%Deliverble')
    keys.insert(0, 'Date')
    dates = split_data['index']
    final_dict = record_data
    values = []
    i = 0
    for x in final_dict:
        dict = x
        del x['VWAP']
        del x['Turnover']
        del x['%Deliverble']
        del x['Deliverable Volume']
        temp = list(dict.values())
        temp.insert(0, dates[i])
        values.append(temp)
        i+=1
    final_dict = {'keys': keys, 'dates': dates, 'values' : values}
    return final_dict