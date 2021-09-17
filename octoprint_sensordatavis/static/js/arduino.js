$(function() {
    function SensorDataVisViewModel(parameters) {
        var self = this;

        self.loginState = parameters[0];
        self.settings = parameters[0];

        self.limsIP = ko.observable();
        self.limsPort = ko.observable();

        self.currentPort = ko.observable();
        self.availablePorts = ko.observableArray();

        self.currentBaud = ko.observable();

        self.onPortSelected = function(event) {
            console.log(event);
        }

        self.getAvailablePorts = function() {
            $.ajax({
                url: OctoPrint.getBlueprintUrl('sensordatavis') + 'arduino/ports',
                type: 'GET',
                dataType: 'json',
                success: function(response) {
                    self.availablePorts.removeAll();
                    const ports = response.ports;
                    for (let i = 0; i < ports.length; ++i)
                        self.availablePorts.push(ports[i]);
                },
                error: function(error) {
                    console.warn(error);
                }
            });
        }

        self.onSettingsShown = function() {
            self.getAvailablePorts();
            self.currentPort(self.settings.settings.plugins.sensordatavis.arduino_port());
            self.currentBaud(self.settings.settings.plugins.sensordatavis.arduino_baud());
            self.limsIP(self.settings.settings.plugins.sensordatavis.lims_ip());
            self.limsPort(self.settings.settings.plugins.sensordatavis.lims_port());
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: SensorDataVisViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_sensordatavis"]
    });
});