# OCLC Developer Network Webinar, 16 October 2018

## Using Wikibase as a platform for library linked data management and discovery

## Demonstration notes

These notes describe the steps for installing Wikibase and Pywikibot and an Amazon Elastic Compute Cloud (EC2) virtual machine, running an image of the Amazon Linux system, and batch loading some sample data.  

### Create an AWS EC2 instance

* Use this image: Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type - ami-0b59bfac6be064b78.  
* Configure it as a “t2.large” instance (to get sufficient memory for Wikibase and the Query engine), with the default 8GB of storage (which should be plenty until working with larger datasets)
* In the instance’s security group, enable SSH port 22, and Custom http ports 8181 and 8282 (the Wikibase and SPARQL Query UIs), for access from the address ranges you want to support

Connect to your EC2 instance via SSH with a private key, and logon with username ec2-user.

The following steps should work with any Linux or Mac machine, and may work in a virtual Linux machine under Windows:

### Install Docker

* Update installed packages
* `sudo yum update -y`
* Install the most recent Docker Community Edition package.
* `sudo yum install -y docker`
* Start the Docker service.
* `sudo service docker start`
* Add the ec2-user to the docker group so you can execute Docker commands without using sudo.
* `sudo usermod -a -G docker ec2-user`
* Log out and log back in again to pick up the new docker group permissions. 
* Verify that the ec2-user can run Docker commands without sudo.
  docker info
  
### Install docker-compose

* `sudo curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
* `sudo chmod +x /usr/local/bin/docker-compose`
  
### Install git

* `sudo yum install git`
     
### Clone the Wikibase docker image repository

* `git clone https://github.com/wmde/wikibase-docker.git`

Change to the path for the Wikibase docker image repo, and start up with wikibase-docker images using docker-compose:
     
* `cd wikibase-docker`
* `docker-compose up`
     
If all goes well, the Wikibase UI should be available for your EC2 site’s IP address and public DNS on port 8181, and the SPARQL UI should be running on port 8282.  An updater script should be checking for Wikibase data changes every 10 seconds, synchronizing data in the SPARQL servers Blazegraph triplestore.  Go to your IP address (or localhost if running on a notebook) with those two ports and see if Wikibase is up and running.

The Wikibase site is automatically configured with a username (Admin) and password (adminpass).  Login to the Wikibase UI with those credentials.

We want to create a "bot password" associated with the Admin account, for Pywikibot scripts to use.  To do that, find the "Special pages" link on the left-hand side of the Wikibase screen, select that, and scroll down to its "Users and Rights" section, and select the link to "Bot passwords". Enter the bot name "bot", and click "Create".  Check the boxes for "High-volume editing", "Edit existing pages", and "Create, edit, and move pages", then click Create.

You should see a new bot password, something like "bot@rer5mtkvfvhui36ata36ac7nrmfaclrn".  Make a note of that, as you'll need it later when we configure Pywikibot.

### Install Pywikibot

Pywikibot is a Python library that provides support for creating and editing entity data in Wikibase.  Documentation is here: https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation

If a supported version of Python (2.7.4+, or 3.4+, check your version with python --version) isn't available yet on your machine, download and install it: https://www.python.org/downloads/

Pywikibot depends on the Python "requests" package.  If you are running Python 2.7.9+ or 3.4+, it should already be available.  If not, you can install it with pip install requests.

Create a directory for where you want to install Pywikibot, change to that directory, and clone the Pywikibot core repository there:
git clone --recursive https://gerrit.wikimedia.org/r/pywikibot/core.git

Change to the "core" directory that should result from cloning the repo.

### Configuring Pywikibot

Pywikibot is designed to work with any one of a number of "families" of wikis.  Out of the box, it's configured to work with Wikipedia, Wikidata, and assorted other wikis.  We're launching our own brand new wiki, which it doesn't yet know about. So we'll want to create a family configuration.  Run this script:

`python generate_family_file.py`
  
and supply a URL for your wikibase host (since we're running Pywikibot on the same machine as our host, http://localhost:8181/w/ should work) and supply a brief family name (like "devnetdemo").

Generate a user-config.py file for your new wiki family by entering the command

`python pwb.py generate_user_files`
  
You should see your new family name in the prompted list of families.  Select it, select the default language ('en'), enter "Admin" as your username (Wikibase is pre-configured with that username and a default password), and respond with "No" for the other prompts to add other users or bot passwords.

There are a couple of other changes to make to the user-config.py file.  Open it up with a text editor, and look for the line that reads  
`password_file = None`

and change it to 

`password_file = "password"`
  
Later we'll be adding our Wikibase bot password to a file with that name.  

Also look for the line that reads 

`put_throttle = 10`

and change it to 

`put_throttle = 0`

The "put_throttle" is the number of seconds Pywikibot will wait between commands sent to its target wiki.  So as not to swap other shared systems like Wikidata, it is set by default to 10 seconds.  But for our instance we can send commands without pausing, so we set it to 0 seconds.

Finally, in the core directory create a file named "password", and enter your Wikibase Admin account's bot password there (the bot password created and (hopefully!) noted in an earlier step), using this text pattern (supplying your own password in place of the one shown here):

`("Admin", "bot@2li3nfhikmtu9c0pev15om7c9lik3vqc")`

### Getting sample data to load

The demonstration includes a Python script that reads in pre-assembled sample data for Wikibase items and properties from tab-delimited text files, and uses Pywikibot to create the entities in our Wikibase instance.  These files can be retrieved from this OCLC Developer Network project, in its sample directory.  To these files, you can clone this repo, with git clone https://github.com/OCLC-Developer-Network/devconnect_2018_wikibase.git

Copy the files in the sample to the core/scripts/userscripts/ directory for your Pywikibot installation.

Then try loading the sample data into your Wikibase, from the command line in the core directory, with the command:

`python pwb.py /scripts/userscripts/load.py`
  
(If you named your wikibase's pywikibot family something other than "devnetdemo", you'll have to hunt down that line in the load.py file and update it.  Sorry about that!)

### Related Resources:

[Wikibase for Research Infrastructure — Part 1](https://medium.com/@thisismattmiller/wikibase-for-research-infrastructure-part-1-d3f640dfad34), by Matt Miller
[Customizing Wikibase config in the docker-compose example](https://addshore.com/2018/06/customizing-wikibase-config-in-the-docker-compose-example/), by Addshore













