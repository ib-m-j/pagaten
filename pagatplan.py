import datetime
import glob
import os.path
import random

class SpilStatus:
    def __init__(self):
        self.header = ['name', 'target', 'spillet', 'afholdt', 'sidensidst']
        planFiles = glob.glob('*.pln')
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
            
        
    def pr(self):
        for n in self.names:
            print('{:<8} {}\n'.format(n, self.status[n]))
        print()



class Plan:
    def __init__(self, title, startDate, endDate, skipDates):
        self.startDate = startDate
        self.endDate = endDate
        self.skipDates = skipDates
        self.players = ['Guddie', 'Einar', 'Bente', 'Philippe', 'Ib']


    def init(self):
        dates = []
        curDate = self.startDate
        incTime = datetime.timedelta(days = 7)
        print(curDate, self.endDate, curDate <=self.endDate)
        while curDate <= self.endDate:
            dates.append(curDate)
            curDate = curDate + incTime

        line = '{0:<8}|{1:^8}|{2:^8}|{3:^8}|{4:^8}|{5:^8}\n'

        f = open('plan.tmp', 'w')
        res = line.format(' ', *self.players)
        for d in dates:
            if d in self.skipDates: 
                fill = 5*' '
            else:
                fill = 5*'X'
            res = res + line.format(d.__format__('%d/%m'),*fill)

        print(res)
        f.write(res)
        f.close()


    def newPlan(self):
        suggested = Plan.getTempPlan()
        new = []
        for rec in suggested:
            selected = [' ' for x in range(5)]
            indices = []
            for n,element in enumerate(rec):
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
                selected[manager] = 'XX'
            new.append(selected)
        return new
                

    @staticmethod
    def getTempPlan():
        canPlan = []
        f = open('plan.tmp', 'r')
        for l in  f.readlines()[1:]:
            elements = l.split('|')
            canPlan.append([x.strip() for x in elements[1:]])
        f.close()
        return canPlan



if __name__ == '__main__':
    print("starting")
    plan = Plan('PagatPlan Forår 2015',datetime.date(2015, 1, 8), datetime.date(2015, 6, 25),
         [datetime.date(2015,4,2), datetime.date(2015,5,14)])
    plan.init()

    status = SpilStatus()
    status.pr()
    status.addPlanLine(['X','X','X','XX',''])
    status.pr()
    for l in plan.newPlan():
        print(l)
        status.addPlanLine(l)
        status.pr()
