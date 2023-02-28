# Opportunities
## Monitor new volunteer opportunities at Timecounts.com 

The Timecounts™ website provides a way to organize volunteers.

However, there is no current feature for volunteers to get notifications when new opportunities are added, at least for some organizations.

Enter Opportunities! It can tell when new opportunities appear. If new opportunities are available (compared to the last time it was run), it will print out lines like

```
Some New Event on Sat., Feb. 18, (02/18/2023) , https://timecounts.org/my-hub-name/events/12345
Another New Event on Sat., Feb. 25, (02/25/2023) , https://timecounts.org/my-hub-name/events/54321
```

## How to run the program `opportunities.py` to see if there are new opportunties

The program requires python version 3+, which on a mac you can install with `brew install python3` (assuming `homebrew` already installed). For a more automated approach, use `direnv`, for which a dotfile is included.

Requirements for pip modules are listed in `setup.py`. The command to install/update all modules is:

`python setup.py install`

The command to run Opportunities is:

`python opportunities.py`

The program will prompt you for your username, password, and organization.  

Your organization name (org name) is lowercase, and instead of any spaces, may be hyphenated. Find your org name in the URL of your "hub" at Timecounts.com. For example, in the hub URL `https://timecounts.org/my-nice-hub/me`, the org name is 'my-nice-hub'.

The first time you run the program, there will be no output since there is no comparison history yet. The next time you run it, it will have a comparison, and will show new opportunities if there are any.

## Properties file

Although Opportunities can prompt you for your login to timecounts.com, you may wish to create a properties file so that you can rerun it more easily. The format for the properties file is like this:

```properties
[Opportunities]
username=myemail@someserver.com
password=mysecretpassword
org=my-org-name
```

To use a properties file, invoke Opportunity and supply the path to your properties file as the first argument, like so: 

`./opportunities.py <my properties file>`

## How to run the notifier program `notify.py`

An additional program, `notify.py`, is provided to run the `opportunities.py` program and send an email, by way of a Google™ Form entry. In other words, if there is a new opportunity, the `notify.py` program will send an entry to a Google Form that you specify. That form, in turn, can send you an email.

You can [learn about Google Forms](https://support.google.com/docs/answer/6281888?hl=en&co=GENIE.Platform%3DDesktop) and create one with a 'Long Answer' type of survey question (multiple lines are possible in the answers). Also enable it to email you when new entries arrive. If you then determine the URL for this survey, and the [name of that 'Long Answer' parameter](https://yaz.in/p/submitting-a-google-form-using-the-command-line/), you can add them to a properties file like this:

```properties
[Cron]
param=entry.12345
url=https://docs.google.com/blahblah/formResponse?usp=pp_url&submit=Submit
```

Invoking the notifier is then as:

`./notify.py opportunities.properties`

You may want to make a `cron` job to run this periodically.

## Disclaimer

Timecounts™ is a registered trademark of Timecounts Inc.
This Opportunity software is NOT affiliated with Timecounts Inc.
Google is a trademark of Google, Inc.