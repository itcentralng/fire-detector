#include <DHT.h>
#include <MQ2.h>

int mq2Pin = A0;
int dhtPin = A1;

DHT dht(dhtPin, DHT11);
MQ2 mq2(mq2Pin);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  dht.begin();
  mq2.begin();
}

void loop() {
  // put y our main code here, to run repeatedly:

  Serial.print("LPG: ");
  Serial.print(mq2.readLPG());
  Serial.print("  ");
  
  Serial.print("CO: ");
  Serial.print(mq2.readCO());
  Serial.print("  ");
  
  Serial.print("Smoke: ");
  Serial.print(mq2.readSmoke());
  Serial.print("  ");

  Serial.print("Temperature: ");
  Serial.print(dht.readTemperature());
  Serial.print("  ");
  
  Serial.print("Humidity: ");
  Serial.println(dht.readHumidity());
  
}
