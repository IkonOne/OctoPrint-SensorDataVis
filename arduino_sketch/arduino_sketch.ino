/**
 * Required Libraries:
 *  - ArduinoJSON
 *  - DHT Sensor Library
 *  - Adafruit Unified Sensor library
 */

#include <ArduinoJson.h>
#include <DHT.h>
// #include <Encoder.h>

const float VCC = 5.0;
const float QOV = 0.5 * VCC;

// TODO @Harsha : Why not 1024?
const float ADC_RESOLUTION = 1023.0;


/**
 * Precise linear interpolation in interval [lo,hi] by t.
 * 
 * @param lo  lower value of the interval
 * @param hi  upper value of the interval
 * @param t   t in [0,1]
 * @return    Precise linearly interpolated value in the interval [lo,hi]
 * 
 * This method of calculation ensures that lo is returned when t==0 and
 * hi is returned when t==1.  The more commmon implementation is susceptible
 * to roundoff error resulting in incorrect values at the extrema.
 * 
 * https://en.wikipedia.org/wiki/Linear_interpolation
 */
inline float lerpf(float lo, float hi, float t) {
  return (1 - t) * lo + t * hi;
}

/**
 * Maps value from the interval [fromLo,fromHi] to [toLo,toHi]
 * 
 * Same as : https://www.arduino.cc/reference/en/language/functions/math/map/
 * But for floating point numbers.
 * 
 * @param value   value in [fromLo,fromHi]
 * @param fromLo  lower value of the source interval
 * @param fromHi  upper value of the source interval
 * @param toLo    lower value of the target interval
 * @param toHi    upper value of the target interval
 * @return  value mapped from the source interval to the target interval
 */
inline float mapf(float value, float fromLo, float fromHi, float toLo, float toHi) {
    float t = (value - fromLo) / (fromHi - fromLo);
    return lerpf(toLo, toHi, t);
}

class Sensor {
  public:
    Sensor() = delete;
    ~Sensor() = default;
    Sensor(const Sensor&) = delete;

    Sensor(const String& lims_field)
      : _lims_field(lims_field) {}
    
    /**
     * NOTE: You do not generally want to use virtual functions on a microcontroller.
     * They have performance overhead due to VTable lookups.  But we don't care in this
     * instance because we don't care about 'real time'.
     */
    virtual bool read() = 0;
    virtual void publish(JsonObject& obj) const = 0;

    // optional...
    virtual void begin() {}

    const String lims_field() const { return this->_lims_field; }

  private:
    const String _lims_field;
};

class AnalogSensor : public Sensor {
  public:
  AnalogSensor(const String& lims_field, uint8_t pin)
    : Sensor(lims_field), _value(-1), _pin(_pin) {}
  
  bool read() override {
    this->value(analogRead(this->pin()));
    return true;
  }

  void publish(JsonObject& obj) const override {
    obj["lims_field"] = this->lims_field();
    obj["value"] = this->value();
  }

  const uint8_t pin() const { return this->_pin; }

  const int value() const { return this->_value; }
  void value(int value) { this->_value = value; }

  private:
    uint8_t _pin;
    int _value;
};

// Current sensor
class ACS712ELCTRSensor : public Sensor {
  public:
  static const float sensitivity_05B = 0.185;
  static const float sensitivity_20A = 0.100;
  static const float sensitivity_30A = 0.066;

  public:
  ACS712ELCTRSensor(const String& lims_field, uint8_t pin, float sensitivity)
    : Sensor(lims_field), _pin(pin), _sensitivity(sensitivity), _value(0) { }

  bool read() override {
    // port to: https://www.engineersgarage.com/acs712-current-sensor-with-arduino/


    float voltage_raw = (VCC/ADC_RESOLUTION)*analogRead(_pin);

    // We think that 0.
    float voltage = voltage_raw - QOV + 0.012;
    this->value(voltage / this->sensitivity());
    return true;
  }

  void publish(JsonObject& obj) const override {
    obj["lims_field"] = this->lims_field();
    obj["value"] = this->value();
  }

  const uint8_t pin() const { return this->_pin; }

  const float sensitivity() const { return this->_sensitivity; }
  void sensitivity(float sensitivity) { this->_sensitivity = sensitivity; }
  
  const float value() const { return this->_value; }
  void value(float value) { this->_value = value; }

  private:
  uint8_t _pin;
  float _sensitivity;
  float _value;
};

class MainsCurrentSensor : public Sensor {
  public:
  static const int mVperAmp = 66;

  public:
  MainsCurrentSensor(const String& lims_field, uint8_t pin)
  : Sensor(lims_field), _pin(pin), _value(0) { }

  bool read() override {
   
  float MCresult;
  int readValue;             //value read from the sensor
  int maxValue = 0;          // store max value here
  int minValue = 1024;          // store min value here
  
   uint32_t start_time = millis();
   while((millis()-start_time) < 16) //sample for 1 Sec
   {
       readValue = analogRead(this->pin());
       // see if you have a new maxValue
       if (readValue > maxValue) 
       {
           /*record the maximum sensor value*/
           maxValue = readValue;
       }
       if (readValue < minValue) 
       {
           /*record the minimum sensor value*/
           minValue = readValue;
       }
   }
   
   // Subtract min from max
   MCresult = ((maxValue - minValue) * 5.0)/1024.0;
   float VRMS = (MCresult/2.0) *0.707;  //root 2 is 0.707
   float AmpsRMS = (VRMS * 1000)/mVperAmp;
    this->value(AmpsRMS);
    return true;
  }

  void publish(JsonObject& obj) const override {
    obj["lims_field"] = this->lims_field();
    obj["value"] = this->value();
  }

  const uint8_t pin() const { return this->_pin; }
  
  const float value() const { return this->_value; }
  void value(float value) { this->_value = value; }

  private:
  uint8_t _pin;
  float _value;
};


class FilamentDiameterSensor : public Sensor {
  public:
  static const int LUT_SIZE = 4;
  static const float LUT[LUT_SIZE][2];
  
  public:
  FilamentDiameterSensor(const String& lims_field, uint8_t pin)
    : Sensor(lims_field), _pin(pin), _value(0) {}
  
  bool read() override {
    int analog_raw = analogRead(this->pin());
    float analog_value = 0;
    for (int i = 1; i < LUT_SIZE; ++i) {
      if (LUT[i][0] > analog_raw) {
        analog_value = mapf(
          analog_raw,
          LUT[i-1][0], LUT[i][0], // from ADC
          LUT[i-1][1], LUT[i][1]  // to current
        );
        break;
      }
    }

    this->value(analog_value);
    return true;
  }

  void publish(JsonObject& obj) const override {
    obj["lims_field"] = this->lims_field();
    obj["value"] = this->value();
  }

  const uint8_t pin() const { return this->_pin; }

  const float value() const { return this->_value; }
  void value(float value) { this->_value = value; }
  
  private:
  uint8_t _pin;
  float _value;
};

// Lookup table for currents within ranges
// {analogRead value, current}
const float FilamentDiameterSensor::LUT[FilamentDiameterSensor::LUT_SIZE][2] = {
  {13, 0},
  {70, 1.53},
  {195, 1.74},
  {284, 2.00}
};

// class EncoderSensor : public Sensor {
//   public:
//     EncoderSensor(const String &lims_field, uint8_t pin_a, uint8_t pin_b)
//       : Sensor(lims_field), _encoder(pin_a, pin_b), _value(-1) {}
    
//     bool read() override {
//       _value = _encoder.read();
//       return true;
//     }

//     void publish(JsonObject& obj) const override {
//       obj["lims_field"] = this->lims_field();
//       obj["value"] = this->value();
//     }

//     int value() const { return this->_value; }
     
//   private:
//     Encoder _encoder;
//     int _value;
// };

class DHTSensor : public Sensor {
  public:
    DHTSensor(const String& lims_field, uint8_t pin, uint8_t type = DHT22, bool as_farenheit = true)
      : Sensor(lims_field), _dht(pin, type), _as_farenheit(as_farenheit), _temperature(-1.0f), _humidity(-1.0f) {}
    
    void begin() override {
      _dht.begin();
    }

    bool read() override {
      _temperature = _dht.readTemperature(_as_farenheit);
      _humidity = _dht.readHumidity();

      if (isnan(_temperature)) _temperature = -100.0f;
      if (isnan(_humidity)) _humidity = -100.0f;
      return true;
    }

    void publish(JsonObject &obj) const override {
      auto arr = obj.createNestedArray("values");

      auto temp = arr.createNestedObject();
      temp["lims_field"] = this->lims_field() + ".Temperature";
      temp["value"] = this->temperature();

      auto hum = arr.createNestedObject();
      hum["lims_field"] = this->lims_field() + ".Humidity";
      hum["value"] = this->humidity();
    }
    
    float temperature() const { return this->_temperature; }
    float humidity() const { return this->_humidity; }
    bool as_farenheit() const { return this->_as_farenheit; }

  private:
    DHT _dht;
    bool _as_farenheit;
    float _temperature;
    float _humidity;
};

Sensor** sensors;
int num_sensors;

void setup() {
  Serial.begin(115200);
  while (!Serial) continue;

  num_sensors = 3;
  sensors = new Sensor*[num_sensors];

  sensors[0] = new FilamentDiameterSensor("Facility.PrusaMK3.FilamentDiameter", A5);
  sensors[1] = new DHTSensor("Facility.PrusaMK3.DHTSensor", 2);
  // sensors[1] = new ACS712ELCTRSensor("Facility.PrsuaMK3.MotorCurrent.E0", A1, ACS712ELCTRSensor::sensitivity_30A);
  // sensors[2] = new ACS712ELCTRSensor("Facility.PrusaMK3.MotorCurrent.X0", A2, ACS712ELCTRSensor::sensitivity_30A);
  // sensors[3] = new ACS712ELCTRSensor("Facility.PrusaMK3.MotorCurrent.Y0", A3, ACS712ELCTRSensor::sensitivity_30A);
  // sensors[4] = new ACS712ELCTRSensor("Facility.PrusaMK3.MotorCurrent.Z0", A4, ACS712ELCTRSensor::sensitivity_30A);
  // sensors[2] = new ACS712ELCTRSensor("Facility.PrusaMK3.MotorCurrent.Z1", A5, ACS712ELCTRSensor::sensitivity_30A);
  // sensors[0] = new EncoderSensor("Encoder", 2, 3);
   sensors[2] = new  MainsCurrentSensor("Facility.PrusaMK3.MainsCurrent", A0);
  // sensors[1] = new AnalogSensor("Facility.PrusaMK3.MotorCurrent.E0", A1);
  // sensors[2] = new AnalogSensor("Facility.PrusaMK3.MotorCurrent.X0", A2);
  // sensors[3] = new AnalogSensor("Facility.PrusaMK3.MotorCurrent.Y0", A3);
  // sensors[4] = new AnalogSensor("Facility.PrusaMK3.MotorCurrent.Z0", A4);
  // sensors[5] = new AnalogSensor("Facility.PrusaMK3.MotorCurrent.Z1", A5);

  for (int i = 0; i < num_sensors; ++i)
    sensors[i]->begin();
}

void loop() {
  /*
  A size of 384 is what is recommended for 6 sensors by the ArduinoJson Assistant:
  https://arduinojson.org/v6/assistant/

  I am using a value of 1024 here simply because we will be adding additional sensors
  and our sketch is going to be very light on the processing/memory requirements side.
  */
  // StaticJsonDocument<384> doc;
  StaticJsonDocument<1024> doc;

  delay(100);

  auto json = doc.createNestedArray("sensors");
  for (int i = 0; i < num_sensors; ++i) {
    if (sensors[i]->read()) {
      auto obj = json.createNestedObject();
      sensors[i]->publish(obj);
    }
  }

  serializeJson(doc, Serial);
  Serial.println();
}