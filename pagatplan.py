import datetime
import glob
import os.path
import random

class SpilStatus:
    def __init__(self):
        self.header = ['name', 'target', 'spillet', 'afholdt', 'sidensidst']
        self.headerFormats = ['{}', '{:.2f}','{:.0f}','{:.0f}','{:.0f}']
        planFiles = glob.glob('*.stat')
        lastValue = 0
        lastPlan = None
        for f in planFiles:
            newV = os.stat(f).st_atime
            if newV > lastValue:
                lastValue = newV
                lastPlan = f
        fil = open(lastPlan, 'r')
        self.status = {}
        self.names = []
        for f in fil.readlines():
            elements = f.split(';')
            name = elements[0]
            self.names.append(name)
            record = [float(x) for x in elements[1:]]
            self.status[name] = {}
            for (h, v) in zip(self.header[1:], record):
                self.status[name][h] = v
        fil.close()

    def addPlanLine(self, Line):
        for (action, name) in zip(Line, self.names):
            if action == 'X':
                self.status[name]['spillet'] +=1
                self.status[name]['sidensidst'] += 1
            if action == 'XX':
                self.status[name]['afholdt'] +=1
                self.status[name]['spillet'] +=1
                self.status[name]['sidensidst'] = 0
            
    def saveNewStatus(self, startDate):
        f = open('pagaten-{}-{}.stat'.format(startDate.year, startDate.month),'w')
        res =''
        for x in self.names:
            res = res + x
            for format,v in zip(self.headerFormats[1:], self.header[1:]):
                res = res + ';' + format.format(self.status[x][v])
            res = res + '\n'
        f.write(res)
        f.close()
        print(res)
                 

    def pr(self):
        for n in self.names:
            print('{:<8} {}\n'.format(n, self.status[n]))
        print()



class Plan:
    tempFileName = 'plan.tmp'
    lineTemplate = '{0:<8}|{1:^8}|{2:^8}|{3:^8}|{4:^8}|{5:^8}|\n'


    def __init__(self, title, startDate, endDate, skipDates):
        self.startDate = startDate
        self.endDate = endDate
        self.skipDates = skipDates
        self.status = SpilStatus()
        self.players = [x for x in self.status.names]
        self.backupTempName = 'plan.bak'

    def getPlanName(self):
        return ('pagatplan-{}-{}.pln'.format(self.startDate.year, self.startDate.month))

    def makePlanHeader(self):
        return Plan.lineTemplate.format('',*self.status.names)

    def run(self):
        if not os.path.exists(Plan.tempFileName):
            print('Making temp plan - edit where people cannot play')
            dates = []
            curDate = self.startDate
            incTime = datetime.timedelta(days = 7)
            while curDate <= self.endDate:
                dates.append(curDate)
                curDate = curDate + incTime


            f = open(Plan.tempFileName, 'w')
            res = Plan.lineTemplate.format(' ', *self.players)
            for d in dates:
                if d in self.skipDates: 
                    fill = 5*' '
                else:
                    fill = 5*'X'
                res = res + Plan.lineTemplate.format(d.__format__('%y-%m-%d'),*fill)

            print(res)
            f.write(res)
            f.close()
        else:
            self.makeNewPlan()
            
    def makeNewPlan(self):
        print('making final plan:', self.getPlanName())
        suggested = Plan.getTempPlan()
        new = []
        for rec in suggested:
            selected = [' ' for x in range(len(self.status.names))]
            indices = []
            for n,element in enumerate(rec[1:]):
                if element == 'X':
                    indices.append(n)
            if len(indices) >= 4:
                if len(indices) > 4:
                    res = random.sample(indices, 4)
                else:
                    res = indices
                for v in res:
                    selected[v] = 'X'
                manager = random.randrange(len(res))
                selected[res[manager]] = 'XX'
            new.append([rec[0]] + selected)

        f = open(self.getPlanName(),'w')
        res = self.makePlanHeader()
        for l in new:
            res = res + Plan.lineTemplate.format(*l)
            self.status.addPlanLine(l[1:])
            #self.status.pr()
        print(res)
        f.write(res)
        f.close()
        os.remove(Plan.tempFileName)
        self.status.saveNewStatus(self.startDate)

    @staticmethod
    def getTempPlan():
        canPlan = []
        f = open(Plan.tempFileName, 'r')
        for l in  f.readlines()[1:]:
            elements = l.split('|')
            canPlan.append([x.strip() for x in elements])
        f.close()
        return canPlan



if __name__ == '__main__':
    plan = Plan('PagatPlan Forår 2015',datetime.date(2015, 1, 8), datetime.date(2015, 6, 25),
         [datetime.date(2015,4,2), datetime.date(2015,5,14)])
    #if plan.tmp does not exist run creates this and exits.
    #this can be edited by registeribng where people cannot play
    #if plan.tmp exists it assumes this is prepared and creates a plan based on this input 
    plan.run()

#comment
