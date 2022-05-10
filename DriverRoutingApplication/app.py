import json
import csv
import sys
from collections import defaultdict


class Driver:
    """ This class is used to hold Driver object information parsed from the driverShifts.csv file.
     Creates driverShifts({shift:[list of drivers]}) and shiftMap({driver name: shift})"""

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
    """ This class is used to hold Pickup object information parsed from the pickups.json file.
        Utility functions to fetch pickupwindow, pickupzone.
        Creates shiftZoneMap({shift:[zone]}) and zoneCountMap({zone:count}) """

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
    """ This class contains utility functions to
        (1) createRouteMap : Creates routeMap {shift: [list of drivers],zonecountMap}
        (2) updateRouteMap : Updates the zonecounts once the pickup is assigned to a driver
        (3) assignRoutes   : Assigns pickup to the drivers having the same shift as the pickup.
                             Logic to ensure that all of driver's pickups are in same zone. """

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
    """ This is the driver class contains utility functions to run the application"""

    def runRoutingApp(self,toConsole=False):

        #Command-line argument for driverShifts.csv file
        drivershiftsFile = sys.argv[1]
        #Command-line argument for pickups.json file
        pickupsFile = sys.argv[2]

        driver = Driver()
        driverShifts, shiftMap = driver.fetchDriverDetails(filename=drivershiftsFile)

        pickup = Pickup()
        pickupData,shiftZoneMap,zoneMap = pickup.parsePickupData(filename=pickupsFile)

        route = Routes(driverShifts, pickupData, zoneMap)
        routeMap = route.createRouteMap()
        assignMap = route.assignRoutes()

        self.toJSONOutput(assignMap, pickupData, shiftMap,toConsole)

    #To convert the assigned routes into required JSON format
    def toJSONOutput(self,assignMap, pickupData, shiftMap,toConsole):
        assignedRoutes = []
        #Command-line argument for output file name. Ex: output.json
        outputfilename = sys.argv[3]
        for name, pickupList in assignMap.items():
            pickups = [pickupData[idx] for idx in pickupList]
            itemMap = {'driverName': name, 'shift': shiftMap[name], 'pickups': pickups}
            assignedRoutes.append(itemMap)

        if toConsole:
            print('Assigned Routes:{}'.format(assignedRoutes))
        else:
            with open(outputfilename, 'w') as f:
                json.dump(assignedRoutes, f, indent=4)

            print('The assigned routes can be found in {}'.format(outputfilename))


if __name__ == '__main__':

    print('Driver Routing Application')
    print('--------------------------')
    app = RoutingApplication()
    app.runRoutingApp(toConsole=False)