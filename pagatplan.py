import datetime
import glob
import os.path
import random

class RoundInput:
    def __init__(self, dato, allPlayers, availableIndices):
        self.date = dato
        self.allPlayers = allPlayers
        self.available = availableIndices

    def calculatePlayers(self, status):
        pass

    def getAllConfigurations(self, status):
        pass

    def getBestLocalLine(self, status):
        pass

    def getStr(self):
        if possiblePlayers:
            fill = len(possiblePlayers)*'X'
        else:
            pass
                                   

    def getSimpleRound(self):
        if len(self.available) < 4:
            return RoundFilled(self.date, None, None)
        else:
            selectedPlayers = random.sample(self.available, 4)
            selectedManager = random.randrange(len(selectedPlayers))
            
        return RoundFilled(self.date, 
                           [self.allPlayers[x] for x in selectedPlayers],
                           self.allPlayers[selectedPlayers[selectedManager]])
        
class RoundFilled:
    def __init__(self, date, players, arranger):
        self.date = date
        self.players = players
        self.arranger = arranger

    def getString(self, unused):
        dateStr = self.date.__str__()
        if self.players:
            res =  dateStr + ' - ' 
            for x in self.players:
                res = res + x + ', '
            return res[:-2] + '\n'
        return dateStr + '\n'

    def getLine(self, allPlayers, template):
        dateStr = self.date.__str__()
        players = [' ']*len(allPlayers)
        if self.players:
            for x in self.players:
                players[allPlayers.index(x)] = 'X'

            players[allPlayers.index(self.arranger)] = 'XX'
        return template.format(dateStr, *players)


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

    def __init__(self, title, startDate, endDate, skipDates):
        self.startDate = startDate
        self.endDate = endDate
        self.skipDates = skipDates
        self.status = SpilStatus()
        self.players = [x for x in self.status.names]
        self.backupTempName = 'plan.bak'

    def getPlanName(self):
        return ('pagatplan-{}-{}.pln'.format(
            self.startDate.year, self.startDate.month))

    def makePlanHeader(self):
        return self.lineTemplate().format('',*self.status.names)
    
    def lineTemplate(self):
        lineTemplate = '{0:<10}|'
        for x in range(len(self.players)):
            lineTemplate = lineTemplate + '{'+'{}'.format(x+1)+':^8}|'
        lineTemplate = lineTemplate + '\n'
        return lineTemplate

    #this can be updated to indicate where people cannot play
    def makePlanInput(self):
        print('Making temp plan - edit where people cannot play')
        dates = []
        curDate = self.startDate
        incTime = datetime.timedelta(days = 7)
        while curDate <= self.endDate:
            dates.append(curDate)
            curDate = curDate + incTime
            
        res = self.lineTemplate().format(' ', *self.players)
        
        for d in dates:
            if d in self.skipDates: 
                fillChar = ' '
            else:
                fillChar = 'X'

            res = res + self.lineTemplate().format(
                d.__format__('%Y-%m-%d'),*(len(self.players)*fillChar))

        f = open(Plan.tempFileName, 'w')
        print(res)
        f.write(res)
        f.close()

    def run(self):
        if not os.path.exists(Plan.tempFileName):
            self.makePlanInput()
        else:
            self.makeNewPlan()

    def makeNewPlan(self):
        print('making final plan:', self.getPlanName())
        suggested = Plan.getTempPlan(self.players)
        planInput = []
        for rec in suggested:
            datestr = rec[0]
            date = datetime.date(int(datestr[0:4]),
                                 int(datestr[5:7]),
                                 int(datestr[8:]))
            indices = []
            for n,element in enumerate(rec[1:]):
                if element == 'X':
                    indices.append(n)
            planInput.append(RoundInput(date, self.players, indices))

        plan = []
        for x in planInput:
            plan.append(x.getSimpleRound())
        
        res = self.makePlanHeader()
        for p in plan:
            res = res + p.getLine(self.players, self.lineTemplate())
        print(res)

        f = open(self.getPlanName(),'w')
        f.write(res)
        f.close()
        os.remove(Plan.tempFileName)
        self.status.saveNewStatus(self.startDate)

    @staticmethod
    def getTempPlan(players):
        canPlan = []
        f = open(Plan.tempFileName, 'r')
        lines = f.readlines()
        names = lines[0].split('|')[1:]

        try:
            for n,m in zip(players, names):
                n == m
        except:
            raise baseException()

        for l in  lines[1:]:
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
