#include <ArduinoBLE.h>

BLEService        PDM("BA44C78E-12AD-4CC6-8EE2-4FFC42F0757D");
BLEIntCharacteristic Pulse_BLE("D3C40F85-0ADA-4072-A155-FC78CE198193", BLERead | BLENotify);
BLEIntCharacteristic SpO2_BLE("5297A449-5B81-4629-8A74-6FBD8F7A2D26", BLERead | BLENotify);
BLEIntCharacteristic GSR_BLE("2b0f58d7-efe5-4549-9dda-28078a068de0", BLERead | BLENotify);
BLEIntCharacteristic TEMP_BLE("3cfb2433-d190-4ab9-832a-ce539126d508", BLERead | BLENotify);

int wait = 10;
unsigned long time_now = 0;

int pulse = 10;
uint16_t spo2 = 10;
int temp = 10;
int gsr = 10;

void collect_data(void){
  char data[4];

  Serial1.readBytes(data,4);

  pulse = (int)data[0];
  spo2 = (int)data[1];
  //Serial.println(data[1],HEX);
  temp = (int)data[2];
  gsr = (int)data[3];
}

void setup() {
  Serial.begin(9600);
  Serial1.begin(115200);

  if (!BLE.begin())
  {
    Serial.println("starting BLE module failed!");
  }

  BLE.setLocalName("PDM");
  BLE.setAdvertisedService(PDM);
  PDM.addCharacteristic(Pulse_BLE);
  PDM.addCharacteristic(SpO2_BLE);
  PDM.addCharacteristic(GSR_BLE);
  PDM.addCharacteristic(TEMP_BLE);
  BLE.addService(PDM);
  BLE.advertise();
  Serial.println("broadcasting");
}

void loop() {

  BLEDevice central = BLE.central();
  Serial.println("Waiting for connection");

  if(central){
    Serial.println("Connected!");
  }

  while(central.connected()){
    if(Serial1.available()){
    collect_data();
  }

  Pulse_BLE.writeValue(pulse);
  SpO2_BLE.writeValue(spo2);
  GSR_BLE.writeValue(gsr);
  TEMP_BLE.writeValue(temp);

  time_now = millis();
  while(millis() < time_now + wait){}
  }

}
