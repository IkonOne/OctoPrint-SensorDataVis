# OctoPrint-SensorDataVis

This plugin is a man in the middle to facilitate data transfer from an Arduino to a Solution Family LIMS box.

## Setup

There are two pieces of software that must be installed and configured for this plugin to work.
They are this octoprint plugin and the Arduino sketch.

### Octoprint Plugin Installation

The Octoprint plugin is not published to the plugin repository.
It is therefore necessary to install the plugin manually from either one of the branches of this repository, or one of the tagged releases.
The instructions here will describe the process to install the plugin from a tagged release.

Prerequisites:

* IP/Web address of the octopi on which you will be installing this plugin
* IP address of the LIMS box
* Port used for the LIMS box
* Name of the LIMS endpoint for the printer the octopi is connected to

The steps we will follow are:

1. Navigate to the Octoprint Plugin Manager
2. Manually install this plugin
3. Configure the plugin with the LIMS connection information

Let's get started...

#### Step 1: Navigate to the Octoprint Plugin Manager

1. In a web browser, **navigate to the ip/web address of the octopi and log in**.
2. Navigate to the *Octoprint Settings* panel by **clicking on the wrench icon at the top right of the Octoprint website**.  A modal dialog should pop up with the title *Octoprint Settings*.
3. On the left side of the *Octoprint Settings* dialog there is a list of sub-dialogs.  **Find and click on the *Plugin Manager* link.**  You should now see a list of *Installed Plugins* on the right side of the modal.

#### Step 2: Manually Install the Plugin

In this step, I will describe how to install the latest official release of the plugin.
You should generally not be installing any other version unless you have a specific reason to do so.

1. **Navigate to this plugins latest release by opening [this link](https://github.com/IkonOne/OctoPrint-SensorDataVis/releases/latest) in a new browser or tab.**
2. At the bottom of the page in the *Assets* section, there will be two links to the *Source*.  **Right click the *Source (.zip)* link and copy the address**.
3. With the link to the latest releases source code copied, **return to the Octoprint website where you have the *Plugin Manager* open**.  If that tab has been closed, simply repeat the first step of these instructions.
4. There are three buttons at the top of the *Plugin Manager*, **click on the button with the + symbol titled *'+ Get More'***.  This will open another smaller modal dialog titled *Install new Plugins...*
5. At the bottom of the *Install new Plugins...* dialog, there is a textbox where you can enter a URL to install a plugin.  **Paste the *Source (.zip)* link you copied earlier into the textbox**.
6. **Click the *Install* button next to the textbox.**  Yet another modal dialog will pop up with text showing the installation progress.  **NOTE:** If this is the first time you are installing the plugin, it may take a long time to install as it compiles the *numpy* library.
7. **Restart Octoprint after the installation is complete.**

#### Step 3: Configure the Installed Plugin with the LIMS Connection Information

1. Once Octoprint has restarted and you are logged back in, **navigate to the *Octoprint Settings* dialog by clicking the gear in the top right of the Octoprint webpage.**
2. In the left panel of the *Octoprint Settings* dialog, **scroll down until you see *Octoprint Sensor Data Vis***.
3. **Click on the *Octoprint Sensor Data Vis* link to open its settings dialog**.
4. **Fill in the *LIMS Box* section of the settings.**
  a. *Enpoint* takes the LIMS endpoint that identifies the printer.
  b. *IP Address* takes the IP address of the lIMS box.
  c. *Port* is the port of the LIMS box.
5. **Click the *Save* button.**

Octoprint plugin installation is complete.
