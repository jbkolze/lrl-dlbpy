from Tkinter import *
import time
import datetime
from Calendar import Calendar
import calendar
def GetBasin(lake):
    basin_lakes = {'GRB':['GRR','NRR','BRR','RRR'],'MAB':['WFR','CBR','CCK','WHL'],
               'MWB':['CHL','CMR','MNR','PRR'],'SRB':['TVL'],'UKL':['CFK','BHR','CRR'],
               'UWB':['HTR','SRR','MSR'],'WWB':['BVR']}
    for key in basin_lakes.keys():
        if lake in basin_lakes[key]:
            return key
    return ''

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
        self.Date = Calendar(self.root,firstweekday=calendar.SUNDAY)
        self.Date.pack(side=TOP)
        self.tkvar = StringVar(self.root)
        self.tkvar.set('Choose Lake')
        lakesort= self.Lakes.keys()
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
        self.Gate_configuration = {'BHR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2')],
                              'BRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'BVR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'CBR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'CCK':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'CFK':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'CHL':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2')],
                              'CMR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1')],
                              'CRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'GRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'MNR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'NRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'PRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')],
                              'RRR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2')],
                              'TVL':[('Service Gate 1','MG1'),('Bypass 1 Opening','BP1'),('Bypass 1 Level','L1'),('Service Gate 2','MG2'),('Bypass 2 Opening','BP2'),('Bypass 2 Level','L2')],
                              'WFR':[('Main Gate','MG1'),('Bypass 1 Opening','BP1')],
                              'WHL':[('Main Gate','MG1'),('Bypass 1 Opening','BP1'),('Bypass 2 Opening','BP2'),('Bypass 1 Level','L1'),('Bypass 2 Level','L2')]}
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
        self.lkname = lkname
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
        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime()
        self.Date = str(month)+'/'+str(day)+'/'+str(year)
        year,month,day,hour,Min,sec,wd,yd,dst = time.gmtime(time.time()-24*60*60)
        yesterday = str(month)+'/'+str(day)+'/'+str(year)
        dates = [yesterday]*3 +[self.Date]+['']*11
        print dates
        times = ['1200','1800','2400','0600'] + ['']*11
        print times
        self.gates = []
        for i in range(15):
            self.DateF.append(Entry(newWindow))
            self.TimeF.append(Entry(newWindow))
            self.ElevF.append(Entry(newWindow))
            self.TailWaterF.append(Entry(newWindow))
            for j in range(len( self.Gate_configuration[lkname])):
                self.gates.append([])
                self.gates[i].append(Entry(newWindow))
            self.DateF[i].grid(row=i+1,column=0)
            self.TimeF[i].grid(row=i+1,column=1)
            self.ElevF[i].grid(row=i+1,column=2)
            self.TailWaterF[i].grid(row=i+1,column=3)
            for j in range(len( self.Gate_configuration[lkname])):
                  self.gates[i][j].grid(row=i+1,column=j+4)
        for i in range(15):
            self.DateF[i].insert(END, dates[i])
            self.TimeF[i].insert(END, times[i])
#Weather
        Label(newWindow,text="Pool").grid(row=17,column=0)
        Label(newWindow,text="24 Hour").grid(row=18,column=0)
        Label(newWindow,text="Change").grid(row=19,column=0)
        self.change = Entry(newWindow)
        self.change.grid(row=20,column=0)
        Label(newWindow,text="Precipitation").grid(row=17,column=2,columnspan=3)
        Label(newWindow,text="Amount").grid(row=18,column=2)
        Label(newWindow,text="Last 24hrs").grid(row=19,column=2)
        self.precip = Entry(newWindow)
        self.precip.grid(row=20,column=2)
        Label(newWindow,text="Snow On").grid(row=18,column=3)
        Label(newWindow,text="Ground").grid(row=19,column=3)
        self.snow = Entry(newWindow)
        self.snow.grid(row=20,column=3)
        Label(newWindow,text="Snow Water").grid(row=18,column=4)
        Label(newWindow,text="Content").grid(row=19,column=4)
        self.swe = Entry(newWindow)
        self.swe.grid(row=20,column=4)
        Label(newWindow,text="Present Weather").grid(row=17,column=5,columnspan=2)
        self.tkvar2 = StringVar(newWindow)
        self.tkvar2.set('Select Weather')
        weather_conditions = ['Clear','Fair','Hazy','Fog','Partly Cloudy','Cloudy','Drizzle','Light Rain','Rain','Showers','Thunderstorms','Sleet','Freezing Rain','Light Snow','Snow','Blowing Snow','Dust Storm']
        self.weather = OptionMenu(newWindow, self.tkvar2, *weather_conditions)
        self.weather.grid(row=20,column=5,columnspan=2)
        Label(newWindow,text="Temperature").grid(row=17,column=7,columnspan=4)
        Label(newWindow,text="Current").grid(row=19,column=7)
        Label(newWindow,text="Min").grid(row=19,column=8)
        Label(newWindow,text="Max").grid(row=19,column=9)
        Label(newWindow,text="Tailwater").grid(row=19,column=10)
        Label(newWindow,text="Temp Degrees C").grid(row=19,column=10)
        self.curTemp,self.minTemp,self.maxTemp,self.tailTemp = Entry(newWindow),Entry(newWindow),Entry(newWindow),Entry(newWindow)
        self.curTemp.grid(row=20,column=7)
        self.minTemp.grid(row=20,column=8)
        self.maxTemp.grid(row=20,column=9)
        self.tailTemp.grid(row=20,column=10)
#Aniticipated
        Label(newWindow,text="Anticipated next 06:00 Outlet Settings").grid(row=22,column=0,columnspan=3)
        r,c = 23,0
        for i in range(len( self.Gate_configuration[lkname])):
            Label(newWindow,text= self.Gate_configuration[lkname][i][0]).grid(row=r,column=c)
            c+=1
        self.a_gates = []
        for j in range(len( self.Gate_configuration[lkname])):
            self.a_gates.append(Entry(newWindow))
            self.a_gates[j].grid(row=24,column=j)
#River Stations
        self.r_station = []
        for i in range(len( self.River_Stations[lkname])):
            Label(newWindow,text= self.River_Stations[lkname][i]).grid(row=27+i,column=0,columnspan=2)
            self.r_station.append(Entry(newWindow))
            self.r_station[i].grid(row=27+i,column=2)
#Remarks
        Label(newWindow,text='Remarks:').grid(row=34,column=0)
        self.remarks = Entry(newWindow,width=70)
        self.remarks.grid(row=34,column=1,columnspan=5)
# Submit
        submit = Button(newWindow,text="Submit",command = self.Submit)
        submit.grid(row=34,column=8)
    def Submit(self):
        Modtime = time.ctime()
        basin = GetBasin(self.lkname)
        f = open('c:/temp/output.txt','w')
        f.write(basin + ' ' + self.lkname + ' ' + self.Date +' '+ ' 00000 :' + Modtime + '\n')
        f.write('#Lake Levels and Gate Setting\n')
        for i in range(15):
            if self.DateF[i].get():
                if self.TimeF[i].get():
                    if self.ElevF[i].get():
                        gatesComplete = True
                        for j in range(len(self.gates[i])):
                            if self.gates[i][j].get():
                                pass
                            else:
                                gatesComplete = False
                        if gatesComplete:
                            f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() +' ELEV :' + self.ElevF[i].get() +'\n')
                            if self.TailWaterF[i].get():
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() +' TAILWATER :' + self.TailWaterF[i].get() +'\n')
                            for j in range(len(self.gates[i])):
                                f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() + ' ' +  self.Gate_configuration[self.lkname][j][1] + ' :' + self.gates[i][j].get() + '\n')
                                       
                    f.write(basin + ' ' + self.lkname + ' ' + self.DateF[i].get() + ' ' + self.TimeF[i].get() + '\n')
        f.write('#Anticipateed and Gate Setting\n')
        for i in range(len(self.a_gates)):
            f.write(basin + ' ' + self.lkname + ' ' + self.Date + ' 0600 ' + self.Gate_configuration[self.lkname][j][1][:-1] + '_ANTICIPATED_' + self.Gate_configuration[self.lkname][j][1][-1] + ' :' + self.a_gates[i] + '\n')
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
        
if __name__ == "__main__":
        g = gui()

