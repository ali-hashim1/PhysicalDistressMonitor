#include <SoftwareSerial.h>
int wait = 100;
unsigned long time_now = 0;

SoftwareSerial BLE(0,1);

void send_data(int pulse, int spo2, int temp, int gsr){
  char mssg[4];
  mssg[0] = pulse;
  mssg[1] = spo2/10;
  mssg[2] = temp;
  mssg[3] = gsr;
  BLE.write(mssg,4);
}

void get_board_serial(unsigned char *str)
{
    unsigned char mssg[5] = {0xA1, 0x01, 0x70, 0x70, 0xAF};
    char recv_buff[64];
    Serial1.write(mssg, 5);
    delay(200);
    Serial1.readBytes(recv_buff,64);
    for (int i = 0; i < 4; i++)
        str[i] = recv_buff[i + 3];
}

void unlock_board(unsigned char *mfg)
{
    unsigned char mssg[16];
    unsigned char serial[4];
    char recv_buff[64];
    int CSUM = 0;

    get_board_serial(serial);

    mssg[0] = 0xA1; // SOM
    mssg[1] = 0x0B; // LEN = 11
    mssg[2] = 0x71; // d1=0x71 Unlock Board
    // d2..d5 = Board_Serial_Number XOR Manufacturer_ID
    for (int i = 0; i < 4; i++)
        mssg[i + 3] = serial[i] ^ mfg[i];
    mssg[7] = 0x00;  // d6
    mssg[8] = 0x00;  // d7
    mssg[9] = 0x00;  // d8
    mssg[10] = 0x03; // d9
    mssg[11] = 0x00; // d10
    mssg[12] = 0x00; // d11
    for (int j = 2; j <= 12; j++)
        CSUM += mssg[j];
    mssg[13] = CSUM & 0xFF; // CSUM
    mssg[14] = 0xAF;        // EOM

    Serial1.write(mssg, 15);//change
    delay(200);//change
    Serial1.readBytes(recv_buff,64);//change

   if (!((recv_buff[1] == 0x01) && (recv_buff[2] == 0x01)))
    {
        delay(500);
        Serial.print("failed unlock, trying again");
        Serial.println(recv_buff[1],HEX);
        unlock_board(mfg);
    }
}

uint16_t request_pulse(void)
{
    char recv_buff[64];
    unsigned char mssg[6] = {0xA1, 0x02, 0x10, 0x02, 0x12, 0xAF}; // SOM LEN d1 d2 CSUM EOM: d1 = request parameter, d2 = pulse rate

    Serial1.write(mssg, 6);
    time_now = millis();
    while(millis() < time_now + wait){}
    //delay(100);
    Serial1.readBytes(recv_buff,64);
    return ((int)recv_buff[5]);
}

uint16_t request_SpO2(void)
{
    char recv_buff2[64];
    unsigned char mssg[6] = {0xA1, 0x02, 0x10, 0x01, 0x11, 0xAF}; // SOM LEN d1 d2 CSUM EOM: d1 = request parameter, d2 = SpO2
    Serial1.write(mssg, 6);
    time_now = millis();
    while(millis() < time_now + wait){}
    //delay(100);
    Serial1.readBytes(recv_buff2, 64);
    return ((int)(recv_buff2[4] << 8 | recv_buff2[5]));
}

void setup() {
  unsigned char Mfg_ID[4] = {0x19, 0xF9, 0x56, 0x14};
  BLE.begin(115200);
  Serial.begin(9600);
  Serial1.begin(9600);

  delay(4000);
  unlock_board(Mfg_ID);
}

uint16_t pulse = 10;
uint16_t spo2 = 10;
float temp = 10;
const int GSR_pin=A5;
const int tempSensorPin = A4;
int sensorValue=0;
int tempsensorValue = 0;
int gsr = 10;

void loop() {
      pulse = request_pulse();
      spo2 = request_SpO2();
      tempsensorValue = analogRead(tempSensorPin);
      float voltage = tempsensorValue * (5.0 / 1024.0);
      float temperatureC = (voltage - 0.5) * 100.0;
      temp = (temperatureC*(9/5)) + 32;
  
      long sum=0;
      for(int i=0;i<10;i++){
        sensorValue=analogRead(GSR_pin);
        sum += sensorValue;
        }
      gsr = sum/20;

      send_data(pulse,spo2,temp,gsr);

      Serial.print("Pulse = ");
      Serial.print(pulse);

      Serial.print(", SpO2 = ");
      Serial.print(spo2);

      Serial.print(", GSR = ");
      Serial.print(gsr);

      Serial.print(", Temp = ");
      Serial.println(temp);

}
