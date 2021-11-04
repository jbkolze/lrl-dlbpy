from tkinter import *
import time
import datetime
import calendar
import ratings
from os.path import exists
import re
def GetBasin(lake):
    basin_lakes = {'GRB':['GRR','NRR','BRR','RRR'],'MAB':['WFR','CBR','CCK','WHL'],
               'MWB':['CHL','CMR','MNR','PRR'],'SRB':['TVL'],'UKL':['CFK','BHR','CRR'],
               'UWB':['HTR','SRR','MSR'],'WWB':['BVR']}
    for key in basin_lakes.keys():
        if lake in basin_lakes[key]:
            return key
    return ''
def pad(t,l,s):
    while len(t) < l:
        t = s+t
    return t
class gui:
    def __init__(self):
        self.Lakes = {'Barren':'BRR','Buckhorn':'BHR','Brookville':'BVR',
                      'Caesar Creek':'CCK','Cagles Mill':'CMR','Carr Creek':'CFK','Cave Run':'CRR','C J Brown':'CBR','C M Harden':'CHL',
                      'Green':'GRR','Monroe':'MNR','Nolin':'NRR','Rough':'RRR','Patoka':'PRR',
                      'Taylorsville':'TVL','WestFork':'WFR','W H Harsha':'WHL'}
        self.root = Tk()
        self.root.title('DLB Input Program')
        MainFrame = Frame()
        canvas = Canvas(self.root, height=500, width= 500, bg="white")
        canvas.pack()
        self.tkvar = StringVar(self.root)
        self.tkvar.set('Choose Lake')
        lakesort= list(self.Lakes.keys())
        print (type(lakesort))
        lakesort.sort()
        popupMenu1 = OptionMenu(canvas, self.tkvar, *lakesort)
        popupMenu1.pack()
        self.tkvar.trace('w', self.change_dropdown)
        self.root.mainloop()
    def change_dropdown(self,*args):
        print("Chosen lake " + self.tkvar.get())
        print("Lake Code: " + self.Lakes[self.tkvar.get()])
        self.Load_DLB_Interface(self.Lakes[self.tkvar.get()],'20OCT2021')
         
    def Load_DLB_Interface(self,lkname,date):
        #Need to get upper evelvations for top of Dam
        #Lower should be winter pool -5
        self.Elev_Limits = {'BHR':[750,840],'BRR':[520,590],'BVR':[713,775],'CBR':[991,1023],'CCK':[800,883],'CFK':[1000,1055],'CHL':[638,695],'CMR':[626,704],
                             'CRR':[713,765],'GRR':[635,713],'MNR':[515,556],'NRR':[480,560],'PRR':[506,555],'RRR':[465,524],'TVL':[515,592],'WFR':[670,700],'WHL':[685,795]}
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
        newWindow = Toplevel(self.root)
        self.recheck = False
        self.lkname = lkname
        self.flow = ratings.GateRatingSet(self.lkname)
        self.infobox = Label(newWindow,font=("Arial", 25))
        self.infobox.grid(row=7,column=12,rowspan=2)
        Label(newWindow,text = lkname,font=("Arial", 25)).grid(row = 0, column = 12, rowspan=2)
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
            self.DateF.append(Entry(newWindow))
            self.TimeF.append(Entry(newWindow))
            self.TimeF[i].bind('<FocusOut>',self.Validate_time)
            self.ElevF.append(Entry(newWindow))
            self.ElevF[i].bind('<FocusOut>',self.Validate)
            self.TailWaterF.append(Entry(newWindow))
            self.TailWaterF[i].bind('<FocusOut>',self.Validate)
            for j in range(len( self.Gate_configuration[lkname])):
                self.gates[j].append(Entry(newWindow))
                self.gates[j][i].grid(row=i+1,column=j+4)
                self.gates[j][i].bind('<FocusOut>',self.Validate)
            self.DateF[i].grid(row=i+1,column=0)
            self.TimeF[i].grid(row=i+1,column=1)
            self.ElevF[i].grid(row=i+1,column=2)
            self.TailWaterF[i].grid(row=i+1,column=3)
            self.FlowL.append(Label(newWindow))
            self.FlowL[i].grid(row=i+1,column=j+5)
        Label(newWindow,text="OutFlow").grid(row=0,column=j+5)
#Weather
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
        Label(newWindow,text="Snow On").grid(row=22,column=3)
        Label(newWindow,text="Ground").grid(row=23,column=3)
        self.snow = Entry(newWindow)
        self.snow.grid(row=24,column=3)
        Label(newWindow,text="Snow Water").grid(row=22,column=4)
        Label(newWindow,text="Content").grid(row=23,column=4)
        self.swe = Entry(newWindow)
        self.swe.grid(row=24,column=4)
        Label(newWindow,text="Present Weather").grid(row=23,column=5,columnspan=2)
        self.tkvar2 = StringVar(newWindow)
        self.tkvar2.set('Select Weather')
        weather_conditions = ['Clear','Fair','Hazy','Fog','Partly Cloudy','Cloudy','Drizzle','Light Rain','Rain','Showers','Thunderstorms','Sleet','Freezing Rain','Light Snow','Snow','Blowing Snow','Dust Storm']
        self.weather = OptionMenu(newWindow, self.tkvar2, *weather_conditions)
        self.weather.grid(row=24,column=5,columnspan=2)
        Label(newWindow,text="Temperature").grid(row=21,column=7,columnspan=4)
        Label(newWindow,text="Current").grid(row=22,column=7)
        Label(newWindow,text="Min").grid(row=23,column=8)
        Label(newWindow,text="Max").grid(row=23,column=9)
        Label(newWindow,text="Tailwater").grid(row=23,column=10)
        Label(newWindow,text="Temp Degrees C").grid(row=23,column=10)
        self.curTemp,self.minTemp,self.maxTemp,self.tailTemp = Entry(newWindow),Entry(newWindow),Entry(newWindow),Entry(newWindow)
        self.curTemp.grid(row=24,column=7)
        self.minTemp.grid(row=24,column=8)
        self.maxTemp.grid(row=24,column=9)
        self.tailTemp.grid(row=24,column=10)
#Aniticipated
        Label(newWindow,text="Anticipated next 06:00 Outlet Settings").grid(row=25,column=0,columnspan=3)
        r,c = 26,0
        for i in range(len( self.Gate_configuration[lkname])):
            Label(newWindow,text= self.Gate_configuration[lkname][i][0]).grid(row=r,column=c)
            c+=1
        self.a_gates = []
        for j in range(len( self.Gate_configuration[lkname])):
            self.a_gates.append(Entry(newWindow))
            self.a_gates[j].grid(row=27,column=j)
#River Stations
        self.r_station = []
        for i in range(len( self.River_Stations[lkname])):
            Label(newWindow,text= self.River_Stations[lkname][i]).grid(row=28+i,column=0,columnspan=2)
            self.r_station.append(Entry(newWindow))
            self.r_station[i].grid(row=28+i,column=2)
#Remarks
        Label(newWindow,text='Remarks:').grid(row=34,column=0)
        self.remarks = Entry(newWindow,width=77)
        self.remarks.grid(row=34,column=1,columnspan=5)
# Submit
        submit = Button(newWindow,text="Submit",command = self.Submit)
        submit.grid(row=34,column=8)
        self.Load()
    def Submit(self):
        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime()
        Modtime = str(year)+pad(str(month),2,'0')+pad(str(day),2,'0')+pad(str(hour),2,'0')+pad(str(Min),2,'0')+pad(str(sec),2,'0')
        basin = GetBasin(self.lkname)
        f = open('c:/temp/'+self.lkname+'pydlb.txt','w')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date +' '+ ' 00000 :' + Modtime + '\n')
        f.write('#Lake Levels and Gate Setting\n')
        for i in range(15):
            if self.DateF[i].get():
                if self.TimeF[i].get():
                    if self.ElevF[i].get():
                        gatesComplete = True
                        for j in range(len(self.Gate_configuration[self.lkname])):
                            if self.gates[j][i].get():
                                pass
                            else:
                                gatesComplete = False
                        if gatesComplete:
                            f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() +' ELEV :' + self.ElevF[i].get() +'\n')
                            if self.TailWaterF[i].get():
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() +' TAILWATER :' + self.TailWaterF[i].get() +'\n')
                            for j in range(len(self.Gate_configuration[self.lkname])):
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() + ' ' +  self.Gate_configuration[self.lkname][j][1] + ' :' + self.gates[j][i].get() + '\n')
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
    def Validate_time(self,event):
        tm = re.compile("([01]?[0-9]|2[0-3])[0-5][0-9]")
        if tm.match(event.widget.get()) or event.widget.get() == '':
            self.DateF[self.TimeF.index(event.widget)].delete(0,"end")
            if int(event.widget.get()) > 600:
                year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-(self.Entry_dates.index(self.Date)+1)*60*60*24)
                yesterday = str(month)+'/'+str(day)+'/'+str(year)
                self.DateF[self.TimeF.index(event.widget)].insert(0,yesterday)
            else:
                self.DateF[self.TimeF.index(event.widget)].insert(0,self.Date)
            self.infobox.configure(text="")
        else:
            self.infobox.configure(text="Time is not in hhmm format")
            self.recheck = True
            event.widget.focus_set()
    def Validate(self,event):
        try:
            flow_calc = False
            index = -1
            gn = 0
            if not (event.widget.get() == '') and not self.recheck:
                self.infobox.configure(text="")
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
                        if self.Gate_configuration[self.lkname][i][1][0] == 'L':
                            try:
                                int(event.widget.get())
                            except:
                                self.infobox.configure(text="Must be an integer")
                                self.recheck = True
                                event.widget.focus_set()
                                return
                if event.widget in [self.curTemp,self.minTemp,self.maxTemp]:
                    min_val, max_val = -50,130
                if event.widget in [self.precip,self.snow,self.swe]:
                    min_val, max_val = 0,50
                val = float(event.widget.get())
                if val < min_val:
                    self.infobox.configure(text="Value is too low")
                    self.recheck = True
                    event.widget.focus_set()
                    return
                if val > max_val:
                    self.infobox.configure(text="Value is to high")
                    self.recheck = True
                    event.widget.focus_set()
                    return
            else:
                self.recheck = False
            if index > -1:
                try:
                    gates = {}
                    for i in range(len(self.Gate_configuration[self.lkname])):
                        if self.Gate_configuration[self.lkname][i][1] in ['L1','L2']:
                            gates[self.Gate_configuration[self.lkname][i][1]] = int(self.gates[i][index].get())
                        else:
                            gates[self.Gate_configuration[self.lkname][i][1]] = float(self.gates[i][index].get())
                    for key in ['MG1','MG2','BP1','BP2','L1','L2']:
                        if key not in gates.keys():
                            gates[key] = None
                    self.FlowL[index].configure(text=str(self.flow.get_total_flow(float(self.ElevF[index].get()),gates['MG1'],gates['MG2'],gates['BP1'],gates['BP2'],gates['L1'],gates['L2'])))
                except:
                    self.FlowL[index].configure(text='')
        except:
            self.infobox.configure(text="Must be a number.")
            event.widget.focus_set()
    def Load(self,*args):
        self.Date = self.TkDate.get()
        filename = 'c:/temp/'+self.lkname+'pydlb'+self.Date.replace('/','-')+'.txt'
        if exists(filename):
            self.Clear()
            f = open(filename,'r')
            Times = []
            Gates = []
            lines = f.readlines()
            f.close()
            maxRow,a,r=0,0,0
            for line in lines:
                if line[0] != '#':
                    meta,data = line.split(':')
                    meta = meta.split(' ')
                    if meta[4] == 'MODTIME':
                        pass
                    elif meta[4] == 'ELEV':
                        if meta[3] in Times:
                            row = Times.index(meta[3])
                        else:
                            row = maxRow
                            self.DateF[row].insert(0,meta[2])
                            self.TimeF[row].insert(0,meta[3])
                            Times.append(meta[3])
                            maxRow += 1
                        self.ElevF[row].insert(0, data[:-1])
                    elif meta[4] == 'TAILWATER':
                        self.TailWaterF[row].insert(0, data[:-1])
                    elif meta[4] in ['MG1','BP1','L1','MG2','BP2','L2']:
                        if meta[4] in Gates:
                            self.gates[Gates.index(meta[4])][row].insert(0,data[:-1])
                            self.gates[Gates.index(meta[4])][row].event_generate('<FocusOut>')
                        else:
                            Gates.append(meta[4])
                            self.gates[Gates.index(meta[4])][row].insert(0,data[:-1])
                            self.gates[Gates.index(meta[4])][row].event_generate('<FocusOut>')
                    elif meta[4].find('_ANTICIPATED_')>0:
                        self.a_gates[a].insert(0,data[:-1])
                        a+=1
                    elif meta[4] == 'CHANGE':
                        self.change.insert(0,data[:-1])
                    elif meta[4] == 'AMTRAIN':
                        self.precip.insert(0,data[:-1])
                    elif meta[4] == 'SNOW':
                        self.snow.insert(0,data[:-1])
                    elif meta[4] == 'SNOWATER':
                        self.swe.insert(0,data[:-1])
                    elif meta[4] == 'PRESWEATHR':
                        self.tkvar2.set(data[:-1])
                    elif meta[4] == 'AIR':
                        self.curTemp.insert(0,data[:-1])
                    elif meta[4] == 'MAX24':
                        self.maxTemp.insert(0,data[:-1])
                    elif meta[4] == 'MIN24':
                        self.minTemp.insert(0,data[:-1])
                    elif meta[4] == 'WATERTEMP':
                        self.tailTemp.insert(0,data[:-1])
                    elif meta[4] == 'REMARKS':
                        self.remarks.insert(0,data[:-1])
                    else:
                        self.r_station[r].insert(0,data[:-1])
                        r+=1
        else:
            self.Clear()
            year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-(self.Entry_dates.index(self.Date)+1)*60*60*24)
            yesterday = str(month)+'/'+str(day)+'/'+str(year)
            dates = [yesterday]*3 +[self.Date]+['']*16
            times = ['1200','1800','2400','0600'] + ['']*16
            for i in range(20):
                self.DateF[i].insert(0,dates[i])
                self.TimeF[i].insert(0,times[i])
                                            
    def Clear(self):
        for i in range(20):
            self.DateF[i].delete(0,"end")
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

