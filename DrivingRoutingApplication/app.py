import json
import csv
import sys
from collections import defaultdict


class Driver:

    def __init__(self, name=None, zone=None, shift=None):
        self.name = name
        self.zone = zone
        self.shift = shift
        self.shiftMap = {}
        self.driverShifts = defaultdict(list)

    def fetchDriverDetails(self, filename):
        reader = csv.reader(open(filename))
        next(reader)  # to skip the header row
        for row in reader:
            shift = row[1].strip()
            name = row[0].strip()
            self.shiftMap[name] = shift
            self.driverShifts[shift].append(Driver(name=name, zone=None, shift=shift))
        return self.driverShifts,self.shiftMap


class Pickup:

    def __init__(self, address=None, pickupwindow=None, pickupzone=None):
        self.address = address
        self.pickupwindow = pickupwindow
        self.pickupzone = pickupzone
        self.shiftZoneMap = defaultdict(list)
        self.zoneMap = {}
        self.pickUpData = None

    def fetchPickupData(self,filename):
        with open(filename) as json_file:
            self.pickUpData = json.load(json_file)
        return self.pickUpData

    def fetchWindowAndZone(self):
        for idx, item in enumerate(self.pickUpData):
            self.address = item.get('address')
            self.pickupzone = item.get('zone')
            self.pickupwindow = item.get('pickupWindow')
            self.shiftZoneMap[self.pickupwindow].append(self.pickupzone)
        return self.shiftZoneMap

    def fetchZoneCount(self):
        for shift,zones in self.shiftZoneMap.items():
            zoneCountMap = defaultdict(int)
            for zone in zones:
                zoneCountMap[zone] = zoneCountMap.get(zone, 0)+1
            self.zoneMap[shift] = zoneCountMap
        return self.zoneMap

    def parsePickupData(self, filename):
        pickUpData = self.fetchPickupData(filename=filename)
        shiftZoneMap = self.fetchWindowAndZone()
        zoneMap = self.fetchZoneCount()
        return pickUpData,shiftZoneMap,zoneMap


class Routes:

    def __init__(self, driverShifts, pickupData, zoneMap):
        self.routeMap = {}
        self.assignMap = defaultdict(list)
        self.driverShifts = driverShifts
        self.pickupData = pickupData
        self.zoneMap = zoneMap

    def createRouteMap(self):
        for shift, drivers in self.driverShifts.items():
            self.routeMap[shift] = {'drivers': self.driverShifts[shift], 'zones': self.zoneMap[shift]}
        return self.routeMap

    def updateRouteMap(self,shift,zone):
        zoneCountMap = self.zoneMap[shift]
        zoneCountMap[zone] = zoneCountMap.get(zone, 0) - 1
        self.zoneMap[shift] = zoneCountMap

        for shift,drivers in self.driverShifts.items():
            self.routeMap[shift] = {'drivers': self.driverShifts[shift], 'zones': self.zoneMap[shift]}
        # print(self.routeMap)
        return self.routeMap

    def assignRoutes(self):

        for pickupidx, item in enumerate(self.pickupData):
            flag = 0
            shift = item['pickupWindow']
            pickupzone = item['zone']
            shiftDetails = self.routeMap[shift]
            drivers = shiftDetails['drivers']
            zonestoCover = shiftDetails['zones']

            for person in drivers:

                if (self.assignMap[person.name] is None) or (person.zone is None) or \
                        (person.zone == pickupzone)\
                        and (zonestoCover[pickupzone] != 0):
                    self.assignMap[person.name].append(pickupidx)
                    person.zone = pickupzone
                    self.updateRouteMap(shift, pickupzone)
                    flag = 1
                    break

            if flag==0: #pickup not assigned to anyone

                minpickups = sys.maxsize
                for pickuplist in self.assignMap.values():
                    minpickups = min(len(pickuplist), minpickups)

                for driver in self.assignMap.keys():
                    if len(self.assignMap[driver]) == minpickups:
                        self.assignMap[driver].append(pickupidx)
                        break

        return self.assignMap

class RoutingApplication:

    def runRoutingApp(self):

        drivershiftsFile = sys.argv[1]
        pickupsFile = sys.argv[2]

        driver = Driver()
        driverShifts, shiftMap = driver.fetchDriverDetails(filename=drivershiftsFile)

        pickup = Pickup()
        pickupData,shiftZoneMap,zoneMap = pickup.parsePickupData(filename=pickupsFile)

        route = Routes(driverShifts, pickupData, zoneMap)
        routeMap = route.createRouteMap()
        assignMap = route.assignRoutes()

        self.toJSONOutput(assignMap, pickupData, shiftMap)

    def toJSONOutput(self,assignMap, pickupData, shiftMap):
        assignedRoutes = []
        outputfilename = sys.argv[3]
        for name, pickupList in assignMap.items():
            pickups = [pickupData[idx] for idx in pickupList]
            itemMap = {'driverName': name, 'shift': shiftMap[name], 'pickups': pickups}
            assignedRoutes.append(itemMap)

        with open(outputfilename, 'w') as f:
            json.dump(assignedRoutes, f, indent=4)

        print('The assigned routes can be found in {}'.format(outputfilename))


if __name__ == '__main__':

    print('Driver Routing Application')
    print('--------------------------')
    app = RoutingApplication()
    app.runRoutingApp()