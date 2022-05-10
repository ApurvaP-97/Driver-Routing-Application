## Instructions to run the code: 
1. Navigate to the DriverRoutingApplication folder.
2. The input files containing the driver shift information(driverShifts.csv) and pickup information(pickups.json) should be present under this folder.
3. To run the application, type the following command <br>
     <br>
     <b><i>python app.py driverShifts.csv pickups.json output.json</i></b>
     
   Note: Output.json is the name of the output file with the pickups mapped to drivers.
4. By default, the output is directed to output.json file(toConsole=False). To get console output, set toConsole=True in the main function.<br> 
     <br>
     <b><i>app.runRoutingApp(toConsole=True)</i></b>
6. Run test_routes.py to verify the outputs. OutputRequired.json should be modified as per the expected output.

## Assumptions/Tradeoffs: 
1. If multiple drivers are working in the same shift, the pickup for that particular shift is assigned to one of them. That zone gets associated with the driver. 
2. If there is a pickup during shift X and no driver is belonging to that shift, the pickup is being ignored.
3. If there are no pickups during a driver's shift, that driver is never assigned any pickup.

## Future steps or edge cases: 
### Improvements in terms of code logic: 
The following steps can be taken to overcome the tradeoffs of the current logic. However, I did not implement these because I did not want to override the basic assumption that the driver is only assigned pickups that have the same pickup window and all of the driver's pickups are within the same window. 
1. To handle assumption 1, instead of assigning the pickup to the first driver, I could implement load balancing while assigning the first pickup.
2. To handle assumption 2, instead of ignoring the pickup and not assigning it to any driver, we can keep track of the drivers closest to this pickup. This can be done in two ways: 
    (a) Code will include a logic to identify the relative ordering of the shifts: [morning, afternoon, evening, night]. If afternoon pickup is not assigned to anyone, it can be assigned to a driver who has completed his morning pickup or a driver with evening pickup(whichever is closer, if we try to incorporate the time(hh: mm) factor)
    (b) We can also use the address of the pickup being ignored and map it to the driver who is closest to this pickup in terms of distance.
    
### Improvements in terms of code:
1. More test coverage can be done.
2. Separate configuration files for local and production environments can be added to handle any path/variable changes.
