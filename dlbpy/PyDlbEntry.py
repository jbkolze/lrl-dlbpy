from tkinter import *
import time
from datetime import datetime
import calendar
import ratings
import os
from os.path import exists
import re
from tkinter import messagebox as mb
import urllib.request
import math
from PIL import Image, ImageGrab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, DayLocator
import seaborn as sns
import pandas as pd

pd.plotting.register_matplotlib_converters()

def build_plot(parent, data, title):
    sns.set()
    sns.set_context("paper")
    sns.set_style("whitegrid")
    f, ax = plt.subplots(1, 1, figsize=(2.5, 2.5), dpi=100, constrained_layout=True)
    times = [datetime.strptime(x, '%Y-%m-%d %H:%M') for x in list(data.keys())]
    values = list(data.values())
    sns.lineplot(times, values, ax=ax)
    sns.despine(f, ax)
    plt.xticks(rotation=90)
    plt.title(title)
    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%b %d'))
    canvas = FigureCanvasTkAgg(f, master=parent)
    return canvas

def Interpolate(Data,datestamp):
    try:
        return Data[datestamp]
    except:
        x = time.mktime(time.strptime(datestamp,'%Y-%m-%d %H:%M'))
        dates = list(Data.keys())
        dates.sort()
        i = 0
        while dates[i]< datestamp:
            i+=1
        x1,x2 =time.mktime(time.strptime(dates[i-1],'%Y-%m-%d %H:%M')),time.mktime(time.strptime(dates[i],'%Y-%m-%d %H:%M'))
        y1,y2 = Data[dates[i-1]],Data[dates[i]]
        if abs (x-x1) < 30*60 and abs (x-x2) < 30*60:
            return round(y1 + (x-x1)*((y2-y1)/(x2-x1)),2)
        else:
            return ''
def Graph(Data,w,h,win):
    #Not Currently in use
    Xs = []
    Ys = []
    keys = list(Data.keys())
    keys.sort()
    ticks = []
    for key in keys:
        timestamp = time.mktime(time.strptime(key,'%Y-%m-%d %H:%M'))
        Xs.append(timestamp)
        Ys.append(float(Data[key]))
        if key[-5:] == '06:00':
            ticks.append(timestamp)
    r = 0
    canvas = Canvas(win, width=w, height=h, bg= 'white')
    scale_x = w/(max(Xs)-min(Xs))
    scale_y = h/(max(Ys)-min(Ys))
    canvas.create_text(1,h-(min(Ys)-min(Ys))*scale_y,text=str(min(Ys)),anchor=SW)
    canvas.create_line(0,h-(min(Ys)-min(Ys))*scale_y,w,h-(min(Ys)-min(Ys))*scale_y,fill='black',width=1)
    canvas.create_text(1,h-(max(Ys)-min(Ys))*scale_y,text=str(max(Ys)),anchor=NW)
    canvas.create_line(0,h-(max(Ys)-min(Ys))*scale_y,w,h-(max(Ys)-min(Ys))*scale_y,fill='black',width=1)
    for i in range(1,len(Xs)):
        wx = (Xs[i-1]-min(Xs))*scale_x
        tx = (Xs[i]-min(Xs))*scale_x
        wy = h-(Ys[i-1]-min(Ys))*scale_y
        ty = h-(Ys[i]-min(Ys))*scale_y
        canvas.create_line(wx,wy,tx,ty,fill="red",width=2)
    for i in range(len(ticks)):
        canvas.create_line((ticks[i]-min(Xs))*scale_x,0,(ticks[i]-min(Xs))*scale_x,h,width=1,fill='grey')
    return canvas

def GetBasin(lake):
    """Checks the basin_lakes dictionary for the lake code

        Returns:
            str: A string containing the basin code or an empty string if the lake code
            is not valid
    """
    basin_lakes = {'GRB':['GRR','NRR','BRR','RRR'],'MAB':['WFR','CBR','CCK','WHL'],
               'MWB':['CHL','CMR','MNR','PRR'],'SRB':['TVL'],'UKL':['CFK','BHR','CRR'],
               'UWB':['HTR','SRR','MSR'],'WWB':['BVR']}
    for key in basin_lakes.keys():
        if lake in basin_lakes[key]:
            return key
    return ''
def pad(t,l,s):
    """Pads string t with character s until length is not less than l

        Returns:
            str: A string containing the contents of t with s appended to the front a number of times
            to make the total length equal to l
    """
    while len(t) < l:
        t = s+t
    return t
def datatypes(rdbfile):
    datatypes = []
    for line in rdbfile.split('\n'):
        if line[13:15] == 'TS':
            StartOfDD = 1
        try:
            if line[0] == '#'  and StartOfDD:
                matchobj = re.match('#\D*(\d+)\D*(\d\d\d\d\d)\w*([^\[\]]*)(\[\\S+.*?\])?',line)
                if matchobj:
                    if matchobj.group(4):
                        datatypes.append([matchobj.group(1),matchobj.group(2),matchobj.group(4)])
                    else:
                        datatypes.append([matchobj.group(1),matchobj.group(2),'Bar'])
        except:
            pass
    return datatypes
class gui:
    """Build the base menu to allow the selection of the lake for the DLB
    Lakes are presented in a dropdown menu sorted alphabeticly.  A "Load Entry Sheet" Button
    will launch the DLB Entry Form"""
    def __init__(self):
        self.Lakes = {'Barren':'BRR','Buckhorn':'BHR','Brookville':'BVR',
                      'Caesar Creek':'CCK','Cagles Mill':'CMR','Carr Creek':'CFK','Cave Run':'CRR','C J Brown':'CBR','C M Harden':'CHL',
                      'Green':'GRR','Monroe':'MNR','Nolin':'NRR','Rough':'RRR','Patoka':'PRR',
                      'Taylorsville':'TVL','WestFork':'WFR','W H Harsha':'WHL'}
        self.root = Tk()
        self.root.title('DLB Input Program')
        self.LaunchCanvas = Canvas(self.root, height=500, width= 500, bg="white")
        self.LaunchCanvas.pack()
        self.tkvar = StringVar(self.root)
        self.tkvar.set('Choose Lake')
        lakesort= list(self.Lakes.keys())
        lakesort.sort()
        popupMenu1 = OptionMenu(self.LaunchCanvas, self.tkvar, *lakesort)
        popupMenu1.config(width=60)
        popupMenu1.config(height=5)
        popupMenu1.grid(row=0,column = 0, rowspan=4, columnspan=4)
        self.load_status = Label(self.LaunchCanvas,font=("Arial", 24))
        self.load_status.grid(row=5,column=0,columnspan=4)
        Launch = Button(self.LaunchCanvas,text="Load Entry Sheet",command = self.LoadDLB)
        Launch.config(width=45)
        Launch.config(height=5)
        Launch.config(bg='light blue')
        Launch.grid(row=9, column =0, rowspan=4, columnspan=4)
        self.root.state('zoomed')
        self.root.mainloop()
    def getData(self):
        self.Data = {}
        code = {'ELEV':'62614','Stage':'00065','Tailwater':'00010=on&cb_00065'}
        Tailwater = {'BHR':'','BRR':'03313000','BVR':'03276000','CBR':'03268100','CCK':'03242350','CFK':'03277450',
                     'CHL':'03340900','CMR':'03359000','CRR':'03249500','GRR':'03306000','MNR':'03372500','NRR':'03311000',
                     'PRR':'03374500','RRR':'03318010','TVL':'03295597','WFR':'','WHL':'03247041'}
        self.River_Stations =     {'BHR':['Hyden','Wooten','Tallega','Lock 14'],
                              'BRR':['Alvaton','Bowling Green','Lock 4 (Woodbury)'],
                              'BVR':['Alpine','Brookville'],
                              'CBR':['Eagle City','Springfield (Mad R)'],
                              'CCK':['Milford','Spring Valley'],
                              'CFK':['Hazard'],
                              'CHL':['Fincastle','Ferndale','Coxville'],
                              'CMR':['Reelsville','Bowling Green','Spencer'],
                              'CRR':['Salyersville','Farmers','Moorehead (TR. C)'],
                              'GRR':['Greenburg','Columbia'],
                              'MNR':['Shoals','Petersburg'],
                              'NRR':['Munfordville','Brownsville'],
                              'PRR':['Jasper'],
                              'RRR':['Dundee'],
                              'TVL':['Brashears Creek'],
                              'WFR':['Reading','Carthage'],
                              'WHL':['Perintown']}
        usgs ={'BHR':'03280800','BRR':'03312900','BVR':'03275990','CBR':'03268090','CCK':'03242340','CFK':'03277450','CHL':'03340870','CMR':'03358900',
               'CRR':'03249498','GRR':'03305990','MNR':'03372400','NRR':'03310900','RRR':'03318005','PRR':'03374498','TVL':'03295597','WFR':'03256500','WHL':'03247040',
               'Hyden':'03280612','Wooten':'03280700','Tallega':'03281000','Lock 14':'03282000',
               'Alvaton':'03314000','Bowling Green KY':'03314500','Lock 4 (Woodbury)':'03315500',
               'Alpine':'03275000','Brookville':'03276000',
               'Eagle City':'03267900','Springfield (Mad R)':'03269500',
               'Milford':'03245500','Spring Valley':'03242050',
               'Hazard':'03277500',
               'Fincastle':'03340800','Ferndale':'03340900','Coxville':'03341300',
               'Reelsville':'03357500','Bowling Green IN':'03360000','Spencer':'03357000',
               'Salyersville':'03248300','Farmers':'03249505','Moorehead (TR. C)':'03250000',
               'Greenburg':'03306500','Columbia':'03307000',
               'Shoals':'03282060','Petersburg':'03373980',
               'Munfordville':'03308500','Brownsville':'03311505',
               'Jasper':'03375500',
               'Dundee':'03319000',
               'Brashears Creek':'03295890',
               'Reading':'03255500','Carthage':'03259000',
               'Perintown':'03247500'}
        locs = []
        for i in range(len(self.River_Stations[self.lkname])):
            locs.append(self.River_Stations[self.lkname][i])
        parameters = ['Stage']* len(locs)
        locs.append(self.lkname)
        locs.append('Tailwater')
        parameters.append('ELEV')
        parameters.append('Tailwater')
        for i in range(len(locs)):
            try:
                self.load_status.configure(text="Getting " + locs[i] + " Data from USGS")
                self.root.update_idletasks()
                url = ""
                if locs[i] == 'Bowling Green':
                    if self.lkname == 'BRR':
                        station = locs[i] + ' KY'
                    elif self.lkname == 'CMR':
                        station = locs[i] + ' IN'
                else:
                    station = locs[i]
                if parameters[i] == 'Tailwater':
                    self.Data['Tailwater'] = {}
                    self.Data['WaterTemp'] = {}
                    if Tailwater[self.lkname] != '':
                        url = 'https://waterdata.usgs.gov/nwis/uv?cb_'+code['Tailwater']+'=on&format=rdb&site_no='+Tailwater[self.lkname]+'&period=7'
                else:
                    self.Data[locs[i]] = {}
                    url = 'https://waterdata.usgs.gov/nwis/uv?cb_'+code[parameters[i]]+'=on&format=rdb&site_no='+usgs[station]+'&period=7'
                if len(url) > 0:
                    req = urllib.request.Request(url)
                    response = urllib.request.urlopen(req)
                    html = response.read()
                    html = html.decode('utf8')
                    types = datatypes(html)
                    if self.lkname == 'TVL':
                        for t in types:
                            if t[2] == '[Tailwater]' and t[1] == '00065':
                                    tail_off = 2*types.index(t)
                            if t[2] == 'Bar' and t[1] == '00010':
                                temp_off = 2*types.index(t)
                    else:
                        if types[0][1] == '00065':
                            tail_off,temp_off = 0,2
                        else:
                            tail_off,temp_off = 2,0
                    
                    for line in html.split('\n'):
                        if parameters[i] == 'Tailwater':
                            if line.split('\t')[0] == 'USGS':
                                try:
                                    self.Data[locs[i]][line.split('\t')[2]] = float(line.split('\t')[4+tail_off])
                                except:
                                    pass
                                try:
                                    self.Data['WaterTemp'][line.split('\t')[2]] = float(line.split('\t')[4+temp_off])
                                except:
                                    pass
                        else:
                            if line.split('\t')[0] == 'USGS':
                                try:
                                    self.Data[locs[i]][line.split('\t')[2]] = float(line.split('\t')[4])
                                except:
                                    pass
            except:
                pass
                        
    def LoadDLB(self):
        self.lkname = self.Lakes[self.tkvar.get()]
        self.getData()
        self.LaunchCanvas.destroy()
        self.Load_DLB_Interface()
         
    def Load_DLB_Interface(self):
        lkname = self.lkname
        """Gui interface is built dynamiclly using dictionary lookups to setup gate configurations, data validation criteria, and river stations using the lake code as the lookup"""
        self.Elev_Limits = {'BHR':[752,877],'BRR':[523,618],'BVR':[735,775],'CBR':[1004,1040],'CCK':[841,904],'CFK':[1012,1083],'CHL':[635,712],'CMR':[631,730],
                             'CRR':[719,788],'GRR':[663,734],'MNR':[533,574],'NRR':[487,581],'PRR':[527,564],'RRR':[465,554],'TVL':[540,623],'WFR':[670,735.5],'WHL':[724,819]}
        #Upper Elevation is top of Dam
        #Lower Elevation is winter pool -5

        self.Gate_configuration = {'BHR':[('Main Gate','MG1',3),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1)],
                              'BRR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',2),('Bypass 2 Level','L2',2)],
                              'BVR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',6),('Bypass 2 Level','L2',6)],
                              'CBR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',2),('Bypass 2 Level','L2',2)],
                              'CCK':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',4),('Bypass 2 Level','L2',4)],
                              'CFK':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',3),('Bypass 2 Level','L2',3)],
                              'CHL':[('Main Gate','MG1',3),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1)],
                              'CMR':[('Main Gate','MG1',1),('Bypass 1 Opening','BP1',1)],
                              'CRR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',3),('Bypass 2 Level','L2',3)],
                              'GRR':[('Main Gate','MG1',3),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',9),('Bypass 2 Level','L2',9)],
                              'MNR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',7),('Bypass 2 Level','L2',7)],
                              'NRR':[('Main Gate','MG1',3),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',3),('Bypass 2 Level','L2',3)],
                              'PRR':[('Main Gate','MG1',0,2),('Bypass 1 Opening','BP1',0,1),('Bypass 2 Opening','BP2',0,1),('Bypass 1 Level','L1',1,3),('Bypass 2 Level','L2',4,6)],
                              'RRR':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1)],
                              'TVL':[('Service Gate 1','MG1',0.6),('Bypass 1 Opening','BP1',1),('Bypass 1 Level','L1',9),('Service Gate 2','MG2',0.6),('Bypass 2 Opening','BP2',1),('Bypass 2 Level','L2',9)],
                              'WFR':[('Main Gate','MG1',3),('Bypass 1 Opening','BP1',1)],
                              'WHL':[('Main Gate','MG1',2),('Bypass 1 Opening','BP1',1),('Bypass 2 Opening','BP2',1),('Bypass 1 Level','L1',5),('Bypass 2 Level','L2',5)]}


        self.Validating = False
        newWindow = Frame(self.root)
        newWindow.pack()
        self.infobox = Label(newWindow,font=("Arial", 10))
        self.infobox.grid(row=4,column=12,rowspan=2,columnspan=3)
        self.recheck = False
        self.flow = ratings.GateRatingSet(self.lkname)
        Label(newWindow,text = lkname,font=("Arial", 25)).grid(row = 0, column = 12, rowspan=2)
        #Gate and Elevations Section.  Entries are stored as arrays of Entry Objects.
        #Gate arrays are stored in an array and use the lookup to determine which gate a given array entry is from.
        Label(newWindow,text ="Date").grid(row = 0, column = 0)
        Label(newWindow,text ="Time").grid(row = 0, column = 1)
        Label(newWindow,text ="Elevation").grid(row = 0, column = 2)
        Label(newWindow,text ="Tailwater").grid(row = 0, column = 3)
        r,c = 0,4
        for i in range(len( self.Gate_configuration[lkname])):
            Label(newWindow,text= self.Gate_configuration[lkname][i][0]).grid(row=r,column=c)
            c+=1
        self.DateF = []
        self.TimeF = []
        self.ElevF = []
        self.TailWaterF = []
        self.Entry_dates = []
        for i in range(30):
            year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-i*60*60*24)
            self.Entry_dates.append(str(month)+'/'+str(day)+'/'+str(year))
        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime()
        self.TkDate = StringVar(newWindow)
        self.TkDate.set(str(month)+'/'+str(day)+'/'+str(year))
        self.Date = self.TkDate.get()
        DateDropDown = OptionMenu(newWindow, self.TkDate, *self.Entry_dates)
        DateDropDown.grid(row = 2, column = 12,rowspan=2)
        self.TkDate.trace('w', self.Load)
        self.gates = []
        self.FlowL = []
        for j in range(len( self.Gate_configuration[lkname])):
            self.gates.append([])
        for i in range(20):
            self.DateF.append(Label(newWindow))
            self.TimeF.append(Entry(newWindow))
            self.TimeF[i].bind('<FocusOut>',self.Validate_time)
            self.ElevF.append(Entry(newWindow))
            self.ElevF[i].bind('<FocusOut>',self.Validate)
            self.TailWaterF.append(Entry(newWindow))
            self.TailWaterF[i].bind('<FocusOut>',self.Validate)
            for j in range(len( self.Gate_configuration[lkname])):
                self.gates[j].append(Entry(newWindow))
                self.gates[j][i].bind('<FocusOut>',self.Validate)
            self.FlowL.append(Label(newWindow))
        self.gate_rows = list(zip(
                self.TimeF,
                self.ElevF,
                self.TailWaterF,
                *self.gates,
            ))
        Label(newWindow,text="Outflow (cfs)").grid(row=0,column=j+5)
        self.numrows = 0
        Button(newWindow,text="Add Gate Change",command = self.AddGateRow).grid(row=6,column=12)
        for i in range(4):
            self.AddGateRow()
#Weather is standard for all lakes
        Label(newWindow,text="Pool").grid(row=21,column=0)
        Label(newWindow,text="24 Hour").grid(row=22,column=0)
        Label(newWindow,text="Change").grid(row=23,column=0)
        self.change = Entry(newWindow,width=7)
        self.change.grid(row=24,column=0)
        Label(newWindow,text="Precipitation").grid(row=21,column=2,columnspan=3)
        Label(newWindow,text="Amount").grid(row=22,column=2)
        Label(newWindow,text="Last 24hrs").grid(row=23,column=2)
        self.precip = Entry(newWindow)
        self.precip.grid(row=24,column=2)
        self.precip.bind('<FocusOut>',self.Validate)
        Label(newWindow,text="Snow On").grid(row=22,column=3)
        Label(newWindow,text="Ground").grid(row=23,column=3)
        self.snow = Entry(newWindow)
        self.snow.grid(row=24,column=3)
        self.snow.bind('<FocusOut>',self.Validate)
        Label(newWindow,text="Snow Water").grid(row=22,column=4)
        Label(newWindow,text="Content").grid(row=23,column=4)
        self.swe = Entry(newWindow)
        self.swe.grid(row=24,column=4)
        self.swe.bind('<FocusOut>',self.Validate)
        Label(newWindow,text="Present Weather").grid(row=23,column=5,columnspan=2)
        self.tkvar2 = StringVar(newWindow)
        self.tkvar2.set('Select Weather')
        weather_conditions = ['Clear','Fair','Hazy','Fog','Partly Cloudy','Cloudy','Drizzle','Light Rain','Rain','Showers','Thunderstorms','Sleet','Freezing Rain','Light Snow','Snow','Blowing Snow','Dust Storm']
        self.weather = OptionMenu(newWindow, self.tkvar2, *weather_conditions)
        self.weather.grid(row=24,column=5,columnspan=2)
        Label(newWindow,text="Temperature").grid(row=21,column=7,columnspan=4)
        Label(newWindow,text="Current").grid(row=23,column=7)
        Label(newWindow,text="Min").grid(row=23,column=9)
        Label(newWindow,text="Max").grid(row=23,column=8)
        Label(newWindow,text="Tailwater").grid(row=22,column=10)
        Label(newWindow,text="Temp Degrees C").grid(row=23,column=10)
        self.curTemp,self.maxTemp,self.minTemp,self.tailTemp = Entry(newWindow),Entry(newWindow),Entry(newWindow),Entry(newWindow)
        self.curTemp.grid(row=24,column=7)
        self.curTemp.bind('<FocusOut>',self.Validate)
        self.maxTemp.grid(row=24,column=8)
        self.minTemp.grid(row=24,column=9)
        self.minTemp.bind('<FocusOut>',self.Validate)
        self.maxTemp.bind('<FocusOut>',self.Validate)
        self.tailTemp.grid(row=24,column=10)
        self.tailTemp.bind('<FocusOut>',self.Validate)
#Aniticipated uses the same gate lookup as the Elevation and Gate section to populate both the lables and entry objects
        Label(newWindow,text="Anticipated next 06:00 Outlet Settings").grid(row=25,column=0,columnspan=3)
        r,c = 26,0
        for i in range(len( self.Gate_configuration[lkname])):
            Label(newWindow,text= self.Gate_configuration[lkname][i][0]).grid(row=r,column=c)
            c+=1
        Label(newWindow,text='Anticipated Flow').grid(row=r,column=c)
        self.a_gates = []
        for j in range(len( self.Gate_configuration[lkname])):
            self.a_gates.append(Entry(newWindow))
            self.a_gates[j].grid(row=27,column=j)
            self.a_gates[j].bind('<FocusOut>',self.Validate)
        self.A_FlowL = Label(newWindow)
        self.A_FlowL.grid(row=27,column=j+1)
#River Station labels and entry objects are populated from the River_Stations Dictionary
        self.r_station = []
        elev_plot_frame = LabelFrame(newWindow, text='Lake', borderwidth=2, padx=10, pady=10)
        elev_plot_frame.grid(row=37, column=0, columnspan=2, padx=10)
        g = build_plot(elev_plot_frame, self.Data[lkname], lkname+ ' Elevation')
        g.get_tk_widget().pack(side='left', padx=5)
        g = build_plot(elev_plot_frame, self.Data['Tailwater'], 'Tailwater')
        g.get_tk_widget().pack(side='right', padx=5)
        cp_plot_frame = LabelFrame(newWindow, text='Control Points', borderwidth=2, padx=10, pady=10)
        for i in range(len(self.River_Stations[lkname])):
            station = self.River_Stations[lkname][i]
            Label(newWindow,text= self.River_Stations[lkname][i]).grid(row=28+i,column=0,columnspan=2)
            self.r_station.append(Entry(newWindow))
            self.r_station[i].grid(row=28+i,column=2)
            g = build_plot(cp_plot_frame, self.Data[station], station)
            g.get_tk_widget().pack(side='left', padx=5)
        cp_plot_span = len(self.River_Stations[lkname]) * 2
        cp_plot_frame.grid(row=37, column=2, columnspan=cp_plot_span, padx=5)
#Remarks
        Label(newWindow,text='Remarks:').grid(row=34,column=0)
        self.remarks = Entry(newWindow,width=77)
        self.remarks.grid(row=34,column=1,columnspan=5)
# Submit Button and information label
        submit = Button(newWindow,text="Submit",command = self.Submit)
        submit.grid(row=34,column=8)
        #Label(newWindow,text=lkname+' Elev').grid(row=7,column=12,columnspan=2)
        self.root.focus_force()
        self.root.update_idletasks()
        self.Load()


        
    def AddGateRow(self):
        if self.numrows < 20:
            self.DateF[self.numrows].grid(row=self.numrows+1,column=0)
            self.TimeF[self.numrows].grid(row=self.numrows+1,column=1)
            self.ElevF[self.numrows].grid(row=self.numrows+1,column=2)
            self.TailWaterF[self.numrows].grid(row=self.numrows+1,column=3)
            for j in range(len( self.Gate_configuration[self.lkname])):
                self.gates[j][self.numrows].grid(row=self.numrows+1,column=j+4)
            self.FlowL[self.numrows].grid(row=self.numrows+1,column=j+5)
            if self.numrows >= 4 and self.Validating:
                self.TimeF[self.numrows].focus_set()
            self.numrows += 1
    def Submit(self):
        """Submit first runs the find_submit_errors function and displays the error if one is found.
        If no errors it itterates through the entry objects to pruduce the output file.
        The output file is then copied and date stamped for archiving
        Finally the send.bat is called to transfer the files to the server."""
        err = self.find_submit_errors()
        try:
            x0,y0,x1,y1 = self.root.winfo_rootx(),self.root.winfo_rooty(),self.root.winfo_rootx()+self.root.winfo_width(),self.root.winfo_rooty()+self.root.winfo_height()
            im = ImageGrab.grab((x0, y0, x1, y1))
            im.save('//COE-LRLDFE01LOU/ORG/ED/Public/DLB/dlbpy/Captured/'+self.lkname+'.jpg')
            self.infobox.configure(text="Submission Started")
            self.root.update_idletasks()     
        except:
            pass
        if err:
            mb.showwarning("Submission Halted Due to Error",err)
            return False
        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime()
        Modtime = str(year)+pad(str(month),2,'0')+pad(str(day),2,'0')+pad(str(hour),2,'0')+pad(str(Min),2,'0')
        basin = GetBasin(self.lkname)
        f = open('o:/ED/PUBLIC/DLB/OUTPUT/'+self.lkname+'pydlb.txt','w')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date +' 0000 MODTIME:' + Modtime + '\n')
        f.write('#Lake Levels and Gate Setting\n')
        for i in range(20):
            if self.DateF[i]['text']:
                if self.TimeF[i].get():
                    if self.ElevF[i].get():
                        gatesComplete = True
                        for j in range(len(self.Gate_configuration[self.lkname])):
                            if self.gates[j][i].get():
                                pass
                            else:
                                gatesComplete = False
                        if gatesComplete:
                            f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i]['text'] + ' ' + self.TimeF[i].get() +' ELEV :' + self.ElevF[i].get() +'\n')
                            if self.TailWaterF[i].get():
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i]['text'] + ' ' + self.TimeF[i].get() +' TAILWATER :' + self.TailWaterF[i].get() +'\n')
                            for j in range(len(self.Gate_configuration[self.lkname])):
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i]['text'] + ' ' + self.TimeF[i].get() + ' ' +  self.Gate_configuration[self.lkname][j][1] + ' :' + self.gates[j][i].get() + '\n')
        f.write('#Anticipateed and Gate Setting\n')
        for i in range(len(self.a_gates)):
            f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 ' + self.Gate_configuration[self.lkname][i][1][:-1] + '_ANTICIPATED_' + self.Gate_configuration[self.lkname][i][1][-1] + ' :' + self.a_gates[i].get() + '\n')
        f.write('#Weather\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 CHANGE :' + self.change.get() +'\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 AMTRAIN :' + self.precip.get() +'\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 SNOW :' + self.snow.get() +'\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 SNOWWATER :' + self.swe.get() + '\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 PRESWEATHR :' + self.tkvar2.get() + '\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 AIR :' + self.curTemp.get() + '\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 MAX :' + self.maxTemp.get() + '\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 MIN :' + self.minTemp.get() + '\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 WATERTEMP :' + self.tailTemp.get() + '\n')
        f.write('#DownStream Stations\n')
        for i in range(len(self.r_station)):
            f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 ' +  self.River_Stations[self.lkname][i] + ' :' + self.r_station[i].get() + '\n')
        f.write('#Remarks\n')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 REMARKS :' + self.remarks.get() + '\n')
        f.flush()
        f.close()
        os.system('copy o:\\ed\\public\\dlb\\output\\' + self.lkname+'pydlb.txt o:\\ed\\public\\dlb\\archive\\' +self.lkname+'pydlb'+self.Date.replace('/','-')+'.txt')
        self.infobox.configure(text="Starting Transfer to WM's Server")
        self.root.update_idletasks()
        os.system('o:\\ed\\public\\dlb\\database\\extract\\send.bat')
        self.infobox.configure(text="")
        self.root.update_idletasks()
        mb.showinfo("DLB Submission",'Submission Complete')
        return True

    def find_submit_errors(self) -> str:
        """Checks for data entry errors before DLB is processed.

        Returns:
            str: A string containing an error message for the first error discovered,
                or a blank string if no errors are found.
        """
        check_functions = [
            self.check_required_fields,
            self.check_additional_gate_entries,
            self.check_temperature_values,
        ]
        for check_function in check_functions:
            check_error = check_function()
            if check_error:
                return check_error
        return ''

    def check_required_fields(self) -> str:
        """Checks for entered values in every required field.

        Returns:
            str: A string containing an error message listing some or all of the
                missing fields, or a blank string if no required fields are missing.
        """
        for row in self.gate_rows[:4]:  # 1200, 1800, 2400, and 0600
            if not all(entry.get() for entry in row):
                return f'Missing value(s) in gate table at {row[1].get()} on {row[0].get()}'
        required_fields = [
            ["24-Hour Pool Change", self.change],
            ["24-Hour Precip", self.precip],
            ["Snow on Ground", self.snow],
            ["Snow Water Equivalent", self.swe],
            ["Current Temperature", self.curTemp],
            ["Min. Temperature", self.minTemp],
            ["Max. Temperature", self.maxTemp],
            ["Tailwater Temperature", self.tailTemp],
        ]
        for i, station in enumerate(self.River_Stations[self.lkname]):
            required_fields.append([f'{station} Stage', self.r_station[i]])
        for i, gate in enumerate(self.Gate_configuration[self.lkname]):
            required_fields.append([f'Ant. {gate[0]}', self.a_gates[i]])
        missing_fields = [x[0] for x in required_fields if x[1].get() == '']
        if self.tkvar2.get() == 'Select Weather':
            missing_fields.append('Present Weather')
        if missing_fields:
            return f'The following required fields are missing: {missing_fields}'
        return ''

    def check_additional_gate_entries(self) -> str:
        """Checks that all additional gate entry rows have complete data.

        Returns:
            str: A string containing an error message indicating the gate entry row
                containing incomplete data, or a blank string if no incomplete gate
                entry rows are found.
        """
        for i, row in enumerate(self.gate_rows[4:]):
            if any([x.get() for x in row]) and not all(x.get() for x in row):
                return f'Incomplete data entered for gate entry row #{i + 5}'
        return ''

    def check_temperature_values(self) -> str:
        """Checks that temperature values are entered correctly.

        Returns:
            str: A string containing an error message or an empty string if no
                errors are found.
        """
        if float(self.maxTemp.get()) < float(self.minTemp.get()):
            return 'Temp: Min greater than max'
        if not float(self.minTemp.get()) <= float(self.curTemp.get()) <= float(self.maxTemp.get()):
            return 'Temp: Current not between min and max'
        return ''

    def Validate_time(self,event):
        """The time is checked using a regular expression.  If the time is not valid an error is displayed.
        If the time is valid the date for that row is set to the appropreate date"""
        if self.Validating:
            tm = re.compile("([01]?[0-9]|2[0-3])[0-5][0-9]")
            if event.widget.get() != "":
                if tm.match(event.widget.get()):
                    if int(event.widget.get()) > 600:
                        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-(self.Entry_dates.index(self.Date)+1)*60*60*24)
                        yesterday = str(month)+'/'+str(day)+'/'+str(year)
                        self.DateF[self.TimeF.index(event.widget)].configure(text=yesterday)
                    else:
                        self.DateF[self.TimeF.index(event.widget)].configure(text=self.Date)
                    for i in range(len(self.TimeF)):
                        if self.TimeF[i] != event.widget and pad(event.widget.get(),4,'0') == pad(self.TimeF[i].get(),4,'0'):
                            mb.showwarning("","Times must be unique")
                            event.widget.focus_set()
                            return
                    if event.widget.get() == '2400':
                        mon,day,year = self.Date.split('/')
                        h,m = '00','00'
                    else:
                        mon,day,year = self.DateF[self.TimeF.index(event.widget)]['text'].split('/')
                        h,m = int(int(event.widget.get())/100), int(event.widget.get())%100
                    self.ElevF[self.TimeF.index(event.widget)].delete(0,"end")
                    self.ElevF[self.TimeF.index(event.widget)].insert(0,Interpolate(self.Data[self.lkname],year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' '+pad(str(h),2,'0')+':'+pad(str(m),2,'0')))
                    self.TailWaterF[self.TimeF.index(event.widget)].delete(0,"end")
                    self.TailWaterF[self.TimeF.index(event.widget)].insert(0,Interpolate(self.Data['Tailwater'],year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' '+pad(str(h),2,'0')+':'+pad(str(m),2,'0')))
                else:
                    mb.showwarning("","Time is not in hhmm format")
                    event.widget.focus_set()
            else:
                return

    def Validate(self,event):
        """Values for entry objects are checked against the criteria for their given bounds.
        First the entry object in question is checked against the arrays of objects to establish what type of entry ojbect it is.
        Then the min and max values are set accordingly
        If the value is outside of the bound an error is displayed.
        Finally if the value cannot be evaluated because it isn't the right datatype an error message indicating the value is not a number"""
        if self.Validating:
            try:
                stop = True
                index = -901
                if not (event.widget.get() == '') and not self.recheck:
                    if event.widget in self.ElevF:
                        min_val, max_val = self.Elev_Limits[self.lkname]
                        index = self.ElevF.index(event.widget)
                    if event.widget in self.TailWaterF:
                        min_val, max_val = 0,float(self.ElevF[self.TailWaterF.index(event.widget)].get())
                    for i in range(len(self.Gate_configuration[self.lkname])):
                        if event.widget in self.gates[i]:
                            if self.lkname == 'PRR':
                                min_val,max_val=float(self.Gate_configuration[self.lkname][i][2]),float(self.Gate_configuration[self.lkname][i][3])
                            else:
                                min_val,max_val = 0,float(self.Gate_configuration[self.lkname][i][2])
                            index = self.gates[i].index(event.widget)
                            if self.Gate_configuration[self.lkname][i][1][0] == 'M' and self.lkname not in ['CMR','CHL']:
                                if float(event.widget.get()) > 0:
                                    for j in range(len(self.Gate_configuration[self.lkname])):
                                        try:
                                            if self.Gate_configuration[self.lkname][j][1][0] == 'B' and float(self.gates[j][index].get()) > 0:
                                                self.recheck = True
                                                mb.showwarning("Odd Gate Setting","It's Unusal to have Main Gate and Bypasses both open")
                                        except:
                                            pass
                            if self.Gate_configuration[self.lkname][i][1][0] == 'B' and self.lkname != 'TVL':
                                if float(event.widget.get()) == 0.0:
                                    for j in range(len(self.Gate_configuration[self.lkname])):
                                        if self.Gate_configuration[self.lkname][j][1][0] == 'L':
                                            if self.Gate_configuration[self.lkname][j][1][-1] == self.Gate_configuration[self.lkname][i][1][-1]:
                                                self.gates[j][index].delete(0,'end')
                                                self.gates[j][index].insert(0,'0')
                                if float(event.widget.get()) > 0:
                                    for j in range(len(self.Gate_configuration[self.lkname])):
                                        if self.Gate_configuration[self.lkname][j][1][0] == 'M' and self.lkname not in ['CMR','CHL']:
                                            if float(self.gates[j][index].get()) > 0:
                                                self.recheck = True
                                                mb.showwarning("Odd Gate Setting","It's Unusal to have Main Gate and Bypasses both open")
                            if self.Gate_configuration[self.lkname][i][1][0] == 'L':
                                try:
                                    int(event.widget.get())
                                except:
                                    self.recheck = True
                                    mb.showwarning("Entry Not Valid","Must be an integer")
                                    event.widget.focus_set()
                                    return
                        if event.widget == self.a_gates[i]:
                            index = -1
                            if self.lkname == 'PRR':
                                min_val,max_val=float(self.Gate_configuration[self.lkname][i][2]),float(self.Gate_configuration[self.lkname][i][3])
                            else:
                                min_val,max_val = 0,float(self.Gate_configuration[self.lkname][i][2])
                            if self.Gate_configuration[self.lkname][i][1][0] == 'B' and self.lkname != 'TVL':
                                if float(event.widget.get()) == 0.0:
                                    for j in range(len(self.Gate_configuration[self.lkname])):
                                        if self.Gate_configuration[self.lkname][j][1][0] == 'L':
                                            if self.Gate_configuration[self.lkname][j][1][-1] == self.Gate_configuration[self.lkname][i][1][-1]:
                                                self.a_gates[j].delete(0,'end')
                                                self.a_gates[j].insert(0,'0')
                            if self.Gate_configuration[self.lkname][i][1][0] == 'L':
                                try:
                                    int(event.widget.get())
                                except:
                                    self.recheck = True
                                    mb.showwarning("Entry Not Valid","Must be an integer")
                                    event.widget.focus_set()
                                    return
                    if event.widget in [self.curTemp,self.minTemp,self.maxTemp]:
                        min_val, max_val = -50,130
                    if event.widget == self.tailTemp:
                        min_val, max_val = 0,50
                    if event.widget in [self.precip,self.snow,self.swe]:
                        min_val, max_val = 0,25
                        stop = False
                    val = float(event.widget.get())
                    if val < min_val:
                        self.recheck = True
                        mb.showwarning(event.widget.get() +" : Entry Not Valid","Value is below normal range.\nPlease Check value.")
                        if stop:
                            event.widget.focus_set()
                        return
                    if val > max_val:
                        self.recheck = True
                        mb.showwarning(event.widget.get() +" : Entry Not Valid","Value is above normal range.\nPlease Check value.")
                        if stop:
                            event.widget.focus_set()
                        return
                else:
                    self.recheck = False
                flow = True
                if index > -1:
                    gates = {}
                    for i in range(len(self.Gate_configuration[self.lkname])):
                        if self.gates[i][index].get() == "":
                            flow = False
                        else:
                            if self.Gate_configuration[self.lkname][i][1] in ['L1','L2']:
                                gates[self.Gate_configuration[self.lkname][i][1]] = int(self.gates[i][index].get())
                            else:
                                gates[self.Gate_configuration[self.lkname][i][1]] = float(self.gates[i][index].get())
                    for key in ['MG1','MG2','BP1','BP2','L1','L2']:
                        if key not in gates.keys():
                            gates[key] = 0
                    if flow:
                        try:
                            self.FlowL[index].configure(text=str(self.flow.get_total_flow(float(self.ElevF[index].get()),gates['MG1'],gates['MG2'],gates['BP1'],gates['BP2'],gates['L1'],gates['L2'])))
                        except:
                            self.FlowL[index].configure(text="Flow Computation Failed")
                flow = True
                if index == -1:
                    gates = {}
                    for i in range(len(self.Gate_configuration[self.lkname])):
                        if self.a_gates[i].get() == "":
                            flow = False
                            self.A_FlowL.configure(text='')
                        else:
                            if self.Gate_configuration[self.lkname][i][1] in ['L1','L2']:
                                gates[self.Gate_configuration[self.lkname][i][1]] = int(self.a_gates[i].get())
                            else:
                                gates[self.Gate_configuration[self.lkname][i][1]] = float(self.a_gates[i].get())
                    for key in ['MG1','MG2','BP1','BP2','L1','L2']:
                        if key not in gates.keys():
                            gates[key] = 0
                    if flow:
                        try:
                            self.A_FlowL.configure(text=str(self.flow.get_total_flow(float(self.ElevF[3].get()),gates['MG1'],gates['MG2'],gates['BP1'],gates['BP2'],gates['L1'],gates['L2'])))
                        except:
                            self.A_FlowL.configure(text="Flow Computation Failed")
            except:
                mb.showwarning("Entry Not Valid","Must be a number.")
                event.widget.focus_set()
    def Load(self,*args):
        """Checks for the presence of a date stamped file matching the lake and date.
        Parses the file and populates the entry objects"""
        self.Validating = False
        self.Date = self.TkDate.get()
        filename = 'o:\\ed\\public\\dlb\\archive\\'+self.lkname+'pydlb'+self.Date.replace('/','-')+'.txt'
        self.Clear()
        if exists(filename):
            f = open(filename,'r')
            Times = []
            Gates = []
            lines = f.readlines()
            f.close()
            maxRow,a,r=0,0,0
            for line in lines:
                if line[0] != '#':  #Only Process data lines not comments
                    meta,data = line.split(':')  #Seperate metadata from data
                    meta = meta.split(' ')  #Break meta data into array
                    if meta[4] == 'MODTIME':
                        pass
                    elif meta[4] == 'ELEV':
                        if meta[3] in Times:
                            row = Times.index(meta[3])
                        else:
                            row = maxRow
                            self.DateF[row].configure(text=meta[2])
                            self.TimeF[row].insert(0,meta[3])
                            Times.append(meta[3])
                            maxRow += 1
                        self.ElevF[row].insert(0, data[:-1])
                    elif meta[4] == 'TAILWATER':
                        self.TailWaterF[row].insert(0, data[:-1])
                    elif meta[4] in ['MG1','BP1','L1','MG2','BP2','L2']:
                        if meta[4] in Gates:
                            self.gates[Gates.index(meta[4])][row].delete(0,"end")
                            self.gates[Gates.index(meta[4])][row].insert(0,data[:-1])
                        else:
                            Gates.append(meta[4])
                            self.gates[Gates.index(meta[4])][row].delete(0,"end")
                            self.gates[Gates.index(meta[4])][row].insert(0,data[:-1])
                    elif meta[4].find('_ANTICIPATED_')>0:
                        self.a_gates[a].insert(0,data[:-1])
                        a+=1
                    elif meta[4] == 'CHANGE':
                        self.change.insert(0,data[:-1])
                    elif meta[4] == 'AMTRAIN':
                        self.precip.insert(0,data[:-1])
                    elif meta[4] == 'SNOW':
                        self.snow.insert(0,data[:-1])
                    elif meta[4] == 'SNOWWATER':
                        self.swe.insert(0,data[:-1])
                    elif meta[4] == 'PRESWEATHR':
                        self.tkvar2.set(data[:-1])
                    elif meta[4] == 'AIR':
                        self.curTemp.insert(0,data[:-1])
                    elif meta[4] == 'MAX':
                        self.maxTemp.insert(0,data[:-1])
                    elif meta[4] == 'MIN':
                        self.minTemp.insert(0,data[:-1])
                    elif meta[4] == 'WATERTEMP':
                        self.tailTemp.insert(0,data[:-1])
                    elif meta[4] == 'REMARKS':
                        self.remarks.insert(0,data[:-1])
                    else:
                        self.r_station[r].insert(0,data[:-1])
                        r+=1
            i = 0
            while self.gates[0][i].get() != '':
                if i > (self.numrows-1):
                    self.AddGateRow()
                i+=1
            self.Validating = True
            for i in range(20):
                self.gates[0][i].event_generate('<FocusOut>')
                self.root.update_idletasks()
            self.a_gates[0].event_generate('<FocusOut>')
        else:
            year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-(self.Entry_dates.index(self.Date)+1)*60*60*24)
            yesterday = str(month)+'/'+str(day)+'/'+str(year)
            dates = [yesterday]*3 +[self.Date]+['']*16
            times = ['1200','1800','2400','0600'] + ['']*16
            for i in range(4):
                self.DateF[i].configure(text=dates[i])
                self.TimeF[i].insert(0,times[i])
                if times[i] == '2400':
                    h,m = '00','00'
                    mon,day,year = self.Date.split('/')
                else:
                    h,m = int(int(times[i])/100), int(times[i])%100
                    mon,day,year = dates[i].split('/')
                try:
                    self.ElevF[i].insert(0,self.Data[self.lkname][year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' '+pad(str(h),2,'0')+':'+pad(str(m),2,'0')])
                except:
                    pass
                try:
                    self.TailWaterF[i].insert(0,self.Data['Tailwater'][year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' '+pad(str(h),2,'0')+':'+pad(str(m),2,'0')])
                except:
                    pass
            mon2,day2,year2 = dates[0].split('/')
            try:
                self.change.insert(0,str(round(self.Data[self.lkname][year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' 06:00'] - self.Data[self.lkname][year2+'-'+pad(mon2,2,'0')+'-'+pad(day2,2,'0') + ' 06:00'],2)))
            except:
                pass
            mon,day,year = self.Date.split('/')
            for i in range(len( self.River_Stations[self.lkname])):
                try:
                    self.r_station[i].insert(0,self.Data[self.River_Stations[self.lkname][i]][year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' 06:00'])
                except:
                    self.r_station[i].insert(0,'0')
            try:
                self.tailTemp.insert(0,self.Data['WaterTemp'][year+'-'+pad(mon,2,'0')+'-'+pad(day,2,'0') + ' 06:00'])
            except:
                pass
            self.ElevF[0].focus_force()
        self.Validating = True
                    
    def Clear(self):
        """Clears all of the values in the entry objects"""
        for i in range(20):
            self.DateF[i].configure(text='')
            self.TimeF[i].delete(0,"end")
            self.ElevF[i].delete(0,"end")
            self.TailWaterF[i].delete(0,"end")
            self.FlowL[i].configure(text="")
        for i in range(len(self.gates)):
            for O in self.gates[i]:
                O.delete(0,"end")
        self.change.delete(0,"end")
        self.precip.delete(0,"end")
        self.snow.delete(0,"end")
        self.swe.delete(0,"end")
        self.tkvar2.set('Select Weather')
        self.curTemp.delete(0,"end")
        self.minTemp.delete(0,"end")
        self.maxTemp.delete(0,"end")
        self.tailTemp.delete(0,"end")
        for i in range(len( self.Gate_configuration[self.lkname])):
            self.a_gates[i].delete(0,"end")
        for i in range(len( self.River_Stations[self.lkname])):
            self.r_station[i].delete(0,"end")
        self.remarks.delete(0,"end")
if __name__ == "__main__":
        g = gui()
