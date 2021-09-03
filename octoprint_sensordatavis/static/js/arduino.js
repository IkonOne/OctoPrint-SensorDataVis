(function (global, factory) {
    if (typeof define === "function" && define.amd) {
        define(["OctoPrintClient"], factory);
    } else {
        factory(window.OctoPrintClient);
    }
})(window || this, function(OctoPrintClient) {
    var ArduinoClient = function(base) {
        this.base = OctoPrintClient.getBlueprintUrl("sensordatavis");
    };

    ArduinoClient.prototype.getPorts = function() {
        return this.base.get('arduino/ports');
    };

    // further define API

    OctoPrintClient.registerPluginComponent("myplugin", ArduinoClient);
    return ArduinoClient;
});