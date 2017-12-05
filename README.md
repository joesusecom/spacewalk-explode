# spacewalk-explode
A set of scripts to populate a Spacewalk/SUSE Manager server with organizations, groups, and systems

This is the result of a SUSE Hackweek (https://hackweek.suse.com/) project.

# Goals
* Create a Python script that uses the Spacewalk XML-RPC API to populate a Spacewalk/SUSE Manager server with
  + organizations (countries of the world)
  + system groups for
    - stages (like Development, Production)
    - hardware types
    - roles (e.g. web server)
    - OS (SLES 11 SP4, SLES 12 SP3, etc.)
    - locations (cities)
* Create a Python script that re-configures a Salt Minion to "impersonate" a certain system, registers it, and re-cycles the minion for the next system

# Why is this useful?
With **spacewalk-explode** you can
* easily create a pre-populated demo system for a pilot, customer presentation, developing new UI features, or just taking screenshots
* to some extent test the limits of Spacewalk/SUSE Manager, especially its UI and XML-RPC API

# Limitations
While the creation of organizations and groups through the XML-RPC API is reasonably fast, on-boarding new systems with the current implementation is slow. If you want to have several thousands of minions, you may need to run one or more instances of the script for a few days.
  
# Requirements
The script is tested against Python 3.6.3. The only additional dependency should be PyYAML (python3-PyYAML on a SUSE system).

# How does it work?

First, you need to edit the script **setup.py** to match your environment:

* MANAGER_URL = 'http://url.to.your.server/rpc/api'
* MANAGER_LOGIN = 'login'
* MANAGER_PASSWORD = 'password'
* MAX_COUNTRIES = 10
* MAX_CITIES = 10
* GROUPS_FILE = 'your_groups_definitions.yml'
* DUMMY_EMAIL = 'name@domain'

To use a secure connection, you need to change the script slightly, especially if your server has a self-signed certificate, because the latest XML-RPC libraries on Python 3 are very picky when it comes to SSL/TLS security.

The **MAX_COUNTRIES** setting will define how many organizations are created. The current **countries.json** file has over 200 countries.

The **MAX_CITIES** setting will define how many groups are created for locations within the organizations. Note that there currently is no limits check, so for high numbers of cities you may run out of cities available for the country. Just try it out. :-)

Your **GROUPS_FILE** is a simple YAML file that's used to generate those groups that aren't locations. You need to provide the same categories as in the example file **groups_scenario_retail.yml** or adapt the script accordingly.

The **DUMMY_EMAIL** is used for the organization admins. I didn't think creating fake e-mail addresses would be a good idea as those are actually used by Spacewalk to send notifications to the admins.

Now that you've customized the script and provided a valid groups file, try it out with a low number of countries and cities.

If everything works, increase the numbers as desired.

You can always run the **teardown.py** script to remove the auto-generated organizations again. But unless you completely reset your database, every run will increase the internal numbering of the organizations and group ids because Spacewalk doesn't re-cycle unused ids.

# What exactly does the script create?
Just look at the source code of the **setup.py** script. :-)

# Hacks
* Both the first and last name of organizations admins are picked from a list of popular first names. This works reasonably well and has no influence on the usefulness of the scripts.

# Possible improvements
* Currently, both the organization and group (location) creation take the first items in the list. While this makes the created groups deterministic, it would make sense to add an alternative mode where countries and cities are chosen randomly for more diversity.
* There's very little error checking. For example, you may run out of cities if your MAX_CITIES value is too high.

# What are your data sources? Are they all free to use?
I've used the following data from public sources:
* first names: https://data.sa.gov.au/data/dataset/popular-baby-names
* cities: https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json
* countries: https://gist.github.com/keeguon/2310008
Some data was corrected compared to the original files. To my knowledge, those sources are free to use. In general, mere collections of facts are only weakly copyrighted in most jurisdictions.

