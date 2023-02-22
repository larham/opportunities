# Opportunities
## Monitor new volunteer opportunities at Timecounts.com 

The Timecounts™ website provides a way to organize volunteers.

However, there is no current feature for volunteers to get notifications when new opportunities are added, at least for some organizations.

Enter Opportunities! It can tell when new opportunities appear. If new opportunities are available (compared to the last time it was run), it will print out lines like

```
Some New Event on Sat., Feb. 18, (02/18/2023) , https://timecounts.org/my-hub-name/events/12345
Another New Event on Sat., Feb. 25, (02/25/2023) , https://timecounts.org/my-hub-name/events/54321
```

## How to run the program

The program requires python version 3+, which on a mac you can install with `brew install python3` (assuming `homebrew` already installed). For a more automated approach, use `direnv`, for which a dotfile is included.

Requirements for pip modules are listed in `setup.py`. The command to install/update all modules is:

`python setup.py install`

The command to run Opportunities is:

`python timecounts.py`

The program will prompt you for your username, password, and organization.  

Your organization name is lowercase, and instead of any spaces, may be hyphenated. Find your org name in the URL of your "hub" at Timecounts.com

The first time you run the program, there will be no output since there is no comparison history yet. The next time you run it, it will have a comparison, and will show new opportunities if there are any.

## Properties file

Although Opportunity Alerts can prompt you for your login to timecounts.com, you may wish to create a properties 
file so that you can rerun it more easily. The format for the properties file is like this:

```properties
[Opportunities]
username=myemail@someserver.com
password=mysecretpassword
org=my-org-name
```

To use a properties file, invoke Opportunity Alerts and supply the path to your properties file as the first argument, like so: 

`python opportunities.py <my properties file>`

## Disclaimer

Timecounts™ is a registered trademark of Timecounts Inc.
This Opportunity software is NOT affiliated with Timecounts Inc.