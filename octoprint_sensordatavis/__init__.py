# coding=utf-8
from __future__ import absolute_import
from flask import json, jsonify, request
import octoprint_sensordatavis.arduino as arduino
import octoprint_sensordatavis.lims as lims

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin

class SensordatavisPlugin(
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.BlueprintPlugin,
    octoprint.plugin.EventHandlerPlugin
):
    ##-- AssetPlugin mixin

    # def get_assets(self):
    #     return dict(
    #         js=['js/arduino.js']
    #     )

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            lims_ip='192.168.0.190',
            lims_port=8080,
            arduino_port='/dev/ttyACM0',
            arduino_baud=115200,
            # put your plugin's default settings here
        )
    
    ##-- TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]
    
    # def get_template_vars(self):
    #     vars = dict(
    #         arduino_ports=arduino.get_ports(),
    #     )
    #     self._logger.debug(vars)
    #     return vars

    ##-- BlueprintPlugin mixin
    # This is where the rest api is defined

    @octoprint.plugin.BlueprintPlugin.route("/arduino/ports", methods=["GET"])
    def arduino_ports(self):
        ports = arduino.get_ports()
        response = dict(ports=ports)
        return jsonify(response)
    
    @octoprint.plugin.BlueprintPlugin.route("/arduino/baud", methods=["GET"])
    def arduino_baud(self):
        response = dict(baud=115200)
        return jsonify(response)
    
    ##-- EventHandlerPlugin mixin

    def on_event(self, event, payload):
        # printer states: https://docs.octoprint.org/en/master/modules/printer.html#octoprint.printer.PrinterInterface.get_state_id
        if event == 'PrinterStateChanged':
            self._logger.debug('Printer State : {1}'.format(event, payload))
            state_id = payload['state_id']
            if state_id == 'STARTING':
                lims_ip = self._settings.get(["lims_ip"])
                lims_port = self._settings.get(["lims_port"])
                lims.start_streaming(lims_ip, lims_port, self._logger)

                port = self._settings.get(["arduino_port"])
                baud = self._settings.get(["arduino_baud"])
                sensors = self._settings.get(["arduino_sensors"])
                arduino.start_streaming(port, baud, lims.msgQueue, sensors, self._logger)
            if state_id in ['OPERATIONAL', 'CANCELLLING']:
                arduino.stop_streaming()
                lims.stop_streaming()

        return super().on_event(event, payload)
    
    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "sensordatavis": {
                "displayName": "Sensordatavis Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "IkonOne",
                "repo": "OctoPrint-SensorDataVis",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/IkonOne/OctoPrint-SensorDataVis/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "CSU Sensor Data Vis"
# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SensordatavisPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
