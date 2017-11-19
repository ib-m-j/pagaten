 # -*- coding: utf-8 -*-


import datetime
import glob
import os.path
import random
import create
import sys

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
                                   

    def getSimpleRound(self, status):
        if len(self.available) < 4:
            return RoundFilled(self.date, None, None)
        else:
            selected = []
            priority = []
            for x in self.available:
                name = status.names[x]
                if status.status[name]['target'] == 1:
                    selected.append(x)
                else:
                    priority.append(
                        (status.status[name]['target'] - 
                         status.currentPlayed(name),
                         -status.status[name]['spillet'], x))

            priority.sort(reverse = True)
            sel = 0
            for x in range(4 - len(selected)):
                selected.append(priority[sel][2])
                sel = sel + 1

            manager = []
            currentNames = [status.names[x] for x in selected]
            if 'Einar' in currentNames and 'Guddie' in currentNames:
                adjust = 0.5
            else:
                adjust = -1

            for x in selected:
                name = status.names[x]
                guidingValue = status.status[name]['sidensidst']
                if name == 'Einar' or name == 'Guddie':
                    guidingValue = guidingValue + adjust
                manager.append((guidingValue, x))
            manager.sort(reverse = True)

            selectedManager = manager[0][1]
            #print(priority, selected, selectedManager)
            return RoundFilled(
                self.date, currentNames,
                status.names[selectedManager])

#            
#
#
#
#
#            selectedPlayers = random.sample(self.available, 4)
#
#
#
#
#
#            selectedManager = random.randrange(len(selectedPlayers))
#            
#        return RoundFilled(self.date, 
#                           [self.allPlayers[x] for x in selectedPlayers],
#                           self.allPlayers[selectedPlayers[selectedManager]])
#

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

    def getHtml(self, allPlayers):
        dateStr = self.date.__format__('%d/%m')
        players = [' ']*len(allPlayers)
        if self.players:
            for x in self.players:
                players[allPlayers.index(x)] = 'X'

            players[allPlayers.index(self.arranger)] = 'XX'
        res = '<td class="center">{}</td>'.format(dateStr)
        for x in players:
            if x == 'X':
                res = res + '<td class="center">{}</td>'.format('X')
            elif x == 'XX':
                res = res + '<td class="center_select">{}</td>'.format('X')
            else:
                res = res + '<td></td>'
        return res

class SpilStatus:
    def __init__(self):
        self.header = [
            'name', 'e-mail', 'target', 'spillet', 'afholdt', 'sidensidst']
        self.headerFormats = ['{}', '{}', '{:.2f}','{:.0f}','{:.0f}','{:.0f}']
        
    @staticmethod
    def fromRepository():
        self = SpilStatus()
        planFiles = glob.glob('*.stat')
        lastValue = 0
        lastPlan = None
        for f in planFiles:
            newV = os.stat(f).st_atime
            if newV > lastValue:
#            if newV > lastValue and \
#            datetime.date.fromtimestamp(newV) != datetime.date.today():
                lastValue = newV
                lastPlan = f
        print("Using statusfile: {}\nTimestamped {}\n".format(
            lastPlan, datetime.date.fromtimestamp(lastValue)))
        fil = open(lastPlan, 'r')
        self.status = {}
        self.names = []
        for f in fil.readlines():
            elements = f.split(';')
            name = elements[0]
            self.names.append(name)
            record = [float(x) for x in elements[2:]]
            self.status[name] = {}
            self.status[name]['e-mail'] = elements[1]
            for (h, v) in zip(self.header[2:], record):
                self.status[name][h] = v
        fil.close()
        for n in self.names:
            self.status[n]['playednow'] = 0
            self.status[n]['possiblerounds'] = 0

        return self

    @staticmethod
    def fromRoundUpdate(st, round):
        self = SpilStatus()
        self.names = st.names
        self.status = {}
        
        for name in self.names:
            self.status[name] = {}
            self.status[name]['target'] = st.status[name]['target']
            self.status[name]['e-mail'] = st.status[name]['e-mail']
            self.status[name]['spillet'] = st.status[name]['spillet']
            self.status[name]['sidensidst'] = st.status[name]['sidensidst']
            self.status[name]['afholdt'] = st.status[name]['afholdt']
            self.status[name]['playednow'] = st.status[name]['playednow']
            self.status[name]['possiblerounds'] = st.status[name][
                'possiblerounds'] + 1

        for name in round.players:
            self.status[name]['spillet'] += 1
            self.status[name]['sidensidst'] += 1
            self.status[name]['playednow'] += 1

        self.status[round.arranger]['afholdt'] += 1
        self.status[round.arranger]['sidensidst'] = 0
        return self
                                
    def currentPlayed(self, name):
        relevant = self.status[name]
        if relevant['possiblerounds'] == 0:
            return 0
        else:
            return relevant['playednow']/relevant['possiblerounds']

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
        statName = 'pagaten-{}-{}.stat'.format(startDate.year, startDate.month)
        f = open(statName,'w')
        res =''
        for x in self.names:
            res = res + x
            for format,v in zip(self.headerFormats[1:], self.header[1:]):
                res = res + ';' + format.format(self.status[x][v])
            res = res + '\n'
        f.write(res)
        f.close()
        print(res)
        print('Wrote new status {}\n'.format(statName))
        
                 

    def pr(self):
        for n in self.names:
            print('{:<8} {}\n'.format(n, self.status[n]))
        print()



class Plan:
    tempFileName = 'plan.tmp'
    backupTempName = 'plan.bak'

    def __init__(self, title, startDate, endDate, skipDates):
        self.startDate = startDate
        self.endDate = endDate
        self.skipDates = skipDates
        self.status = SpilStatus.fromRepository()
        self.players = self.status.names


    def getPlanName(self, extension):
        return 'pagatplan-{}-{}.{}'.format(
            self.startDate.year, self.startDate.month, extension)

    def makePlanHeader(self):
        return self.lineTemplate().format('',*self.status.names)

    def makePlanHeaderHtml(self):
        res = '<tr><td width="10%"></td>'
        for n in self.status.names:
            res = res + '<th class="center" width = "18%">{}</th>'.format(n)
        return res + '</tr>'

    def lineTemplate(self):
        lineTemplate = '{0:<10}|'
        for x in range(len(self.players)):
            lineTemplate = lineTemplate + '{'+'{}'.format(x+1)+':^8}|'
        lineTemplate = lineTemplate + '\n'
        return lineTemplate

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
        print('Wrote tempplan {}\n'.format(Plan.tempFileName))

    def run(self):
        if not os.path.exists(Plan.tempFileName):
            self.makePlanInput()
        else:
            self.makeNewPlan()

    def makePlanAsText(self, plan):
        res = 'Pagatplan {} til {}\n'.format(self.startDate, self.endDate)
        res = res + self.makePlanHeader()
        for p in plan:
            res = res + p.getLine(self.players, self.lineTemplate())
        return res

    def makePlanAsHtml(self, plan):
        res = '''<!DOCTYPE html>
<html>
<head>
<style>
.center {text-align: center} 
.center_select {text-align: center; background-color: #00DD00;} 
table, th, td {
border: 1px solid black; border-collapse: collapse; font-size:0.85em;
} 
th,td {padding: 3px;
-webkit-print-color-adjust:exact;
}
th,h2 {font-size:1.7em}
</style>
</head>
<body>'''
        res = res + '<h2>Pagatplan {} til {}</h2>'.format(
            self.startDate, self.endDate)
        res = res + '<table border=1px width="100%">' + self.makePlanHeaderHtml()
        for p in plan:
            res = res + '<tr>{}</tr>'.format(p.getHtml(self.players))
        return res + '</body>'

    def updateCalendar(self, plan):
        service  = create.initOAuth()
        f = open('created.txt','a')
        f.write("starting batch\n")
        for p in plan:
            if p.players:
                id = create.createEvent(
                    service, p.date, p.players, p.arranger, 
                    [self.status.status[n]['e-mail'] for n in p.players])
                f.write(id + '\n')
        f.close()

    def makeNewPlan(self):
        print('making final plan: {}\n'.format(self.getPlanName('html')))
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
        currentStatus = self.status
        for x in planInput:
            nextRound = x.getSimpleRound(currentStatus)
            plan.append(nextRound)
            if nextRound.players:
                currentStatus = SpilStatus.fromRoundUpdate(
                    currentStatus, nextRound)
            
        res = self.makePlanAsHtml(plan)

        #print(res)


        deployPath = os.path.join('c:\\','Users','Ib','einarftp','pagaten')

        f = open(os.path.join(deployPath, self.getPlanName('html')),'w')
        f.write(res)
        f.close()

        f = open(os.path.join(deployPath, 'pagatplan.html'),'w')
        f.write(res)
        f.close()


        #res = self.makePlanAsText(plan)
        #print(res)
        #f = open(self.getPlanName('pln'),'w')
        #f.write(res)
        #f.close()
        print('Wrote planfiles: {} and {}\n in {}\n'.format(
            'pagatplan.html', self.getPlanName('html'),deployPath))
        

        if os.path.exists(Plan.backupTempName):
            os.remove(Plan.backupTempName)
        os.rename(Plan.tempFileName, Plan.backupTempName)
        #self.status.saveNewStatus(self.startDate)
        currentStatus.saveNewStatus(self.startDate)
        #uncomment below when plan is ready and ok
        #self.updateCalendar(plan)
        #tobeuncommented



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
    plan = Plan(
        'PagatPlan Foråret 2018',
        datetime.date(2017, 1, 5), 
        datetime.date(2017, 6, 29), 
        [datetime.date(2017,2,9),
         datetime.date(2017,4,13),
         datetime.date(2017,5,25)])
    #if plan.tmp does not exist run creates this and exits.
    #this can be edited by registeribng where people cannot play
    #if plan.tmp exists it assumes this is prepared and creates a plan based on this input 
    # redo.bat copies the last plan.bak over as plan input and the detials are then computed based on this
    #the system uses the last *.stat file but not a *.stat file 
    #from the same date currrently not operational see below
    #hack in fromRepository when this is operational:
    #delete irrelevant new status files before running
    #Problems when ignoring status files created on the same day -
    #when the system is updated from the repository there is a risk
    #that the correct last status file is ignored
    #when ready to create calendar uncommen at word tobeuncommented
    plan.run()

