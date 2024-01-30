
#include <AccelStepper.h>
#include <MultiStepper.h>
#include <elapsedMillis.h>
#include <SPI.h>

//Sensor's memory register addresses:
const int DEVICE_CONFIG = 0x00; //0x0 is used for writes, should really handle this in the read command
const int SENSOR_CONFIG = 0x01;   
const int SYSTEM_CONFIG = 0x02; // this is where we can switch to the 12bit XY sampling mode                                      
const int TEST_CONFIG = 0x0F;
const int X_CH_RESULT = 0x89; //0x8 is used for reads, should really handle this in the write command
const int Y_CH_RESULT = 0x8A;
const int Z_CH_RESULT = 0x8B;
const int TEMP_RESULT = 0x8C;
const int range = 50;
uint32_t SPI_Clock_Speed = 1000000;

const int PICO_PIN = 4;
const int POCI_PIN = 3;
const int CS_PIN = 1;
const int SCK_PIN = 2;

// Steppers
AccelStepper stepper1(AccelStepper::DRIVER, 28, 29); // X
AccelStepper stepper2(AccelStepper::DRIVER, 26, 27); // Y
AccelStepper stepper3(AccelStepper::DRIVER, 14, 15); // Z

// Up to 10 steppers can be handled as a group by MultiStepper
MultiStepper steppers;

// elapsedMillis printTime; // can be used for optional real time data updates

// for steps/mm (accurate to around 0.1mm):
const float x_steps_per_mm = 200.885;
const float y_steps_per_mm = 200.7752;
const float z_steps_per_mm = 1614.961;

// for steps testing:
// const float x_steps_per_mm = 1; 
// const float y_steps_per_mm = 1;
// const float z_steps_per_mm = 1;

long target[3];

//READ COMMAND, returns an unsigned 16 bit int
unsigned int readRegister(byte thisRegister, byte thisValueA, byte thisValueB, byte thisCommand) {
  byte inByte = 0x0;           // incoming byte from the SPI
  int16_t result = 0;   // result to return
  unsigned char bytesToRead = 2;
  byte dataToSend = thisRegister; // Previously concatinated the address and commmand, but we won't do this

  digitalWrite(CS_PIN, LOW);   // take the chip select low to select the device:
  SPI.transfer(dataToSend); // sending address
  result = SPI.transfer(thisValueA);
  result = result << 8;   // shift the first byte, then get the second byte:
  inByte = SPI.transfer(thisValueB);
  SPI.transfer(thisCommand);
  //Serial.println(thisValueB);
  result = result | inByte;   // combine the byte you just got with the previous one:
  //Serial.println(result);
  digitalWrite(CS_PIN, HIGH);   // take the chip select high to de-select:
  return (result);
}

//WRITE COMMAND, returns nothing
void writeRegister(byte thisRegister, byte thisValueA, byte thisValueB, byte thisCommand) { //we've rolled command and CRC into one byte
  // take the chip select low to select the device:
  digitalWrite(CS_PIN, LOW);
  // when we set an SPI.transfer to a variable it will fill up with what's coming in on MISO
  byte writeResult = SPI.transfer(thisRegister); // we concatinated above, now we are sending the complete address
  writeResult = SPI.transfer(thisValueA);  // thisValue is really 16 bits, but we've chopped it to send in chunks of 8 here
  writeResult = SPI.transfer(thisValueB);
  writeResult = SPI.transfer(thisCommand);
  digitalWrite(CS_PIN, HIGH);   // take the chip select high to de-select:
}

void TMAG5170_init(){
  //Configure sensor with syntax (address,dataA, dataB,command+CRC)
  writeRegister(TEST_CONFIG, 0x00, 0x04, 0x07); // from TI support - write a 0x0F000407 which disables CRC in the test config addres //https://e2e.ti.com/support/sensors/f/1023/t/937812
  delay(50);
  writeRegister(SENSOR_CONFIG, 0x19, 0xEA, 0x00);  //0x1 = SENSOR_CONFIG: Configure X,Y, and Z RANGE to be +/-100mT, as well as activating them (they default to off)
  delay(50);
  //writeRegister(SYSTEM_CONFIG, 0x00, 0x00, 0x00);  //0x2 = SYSTEM_CONFIG: This is where we can get the special 2 channels in one 32bit comm setting, to activate XZ you want 0b00000000, 0b10000000, and for ZY 0b00000000, 0b11000000
  //delay(50);
  writeRegister(DEVICE_CONFIG, 0b00110001, 0x20, 0x00); // 0x0 = DEVICE_CONFIG: Set to 8x averaging + no temp coefficient + set to active measure mode + disable temp stuff
  delay(100); // give the sensor time to set up:
}

void setup() {
  Serial.begin(9600);
  while (!Serial); //hold setup while serial starts up

  // SPI pins setup
  SPI.setRX(PICO_PIN);
  SPI.setTX(POCI_PIN);
  SPI.setSCK(SCK_PIN);

  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, 1);

  // start the SPI library:
  // SPI.begin();
  SPI.begin(false); // passing true will cause the RP2040 to handle the CS pin in hardware (wasn't working?)
  SPI.beginTransaction(SPISettings(SPI_Clock_Speed, MSBFIRST, SPI_MODE0));
  TMAG5170_init();
  // SPI.setDataMode(0);
  // SPI.setBitOrder(MSBFIRST);

  // Configure each stepper
  stepper1.setMaxSpeed(8000);
  stepper2.setMaxSpeed(16000);
  stepper3.setMaxSpeed(16000);

  stepper1.setCurrentPosition(0);
  stepper2.setCurrentPosition(0);
  stepper3.setCurrentPosition(0);

  // Then give them to MultiStepper to manage
  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
  steppers.addStepper(stepper3);
}

void loop() {
    if(Serial.available()>0){
    // String message = Serial.readString();

    int command = Serial.parseFloat();
    // 1 - Zero stepper positions
    // 2 - Move command
    // 3 - Request data

    if (command == 3){
      // printTime = 0;
      Serial.print("Position: ");
      Serial.print(stepper1.currentPosition()/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper2.currentPosition()/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper3.currentPosition()/z_steps_per_mm);
      Serial.print(" | ");
      Serial.print("Target: ");
      Serial.print(target[0]/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[1]/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[2]/z_steps_per_mm);
      Serial.print('\n');

      // SENSOR READOUT: Read X and Z, do math, then print
      int16_t xChannel = readRegister(X_CH_RESULT,0x00, 0x00, 0x00);
      signed short xValue = xChannel + 80; //100/(32768);
      // Serial.print("m");
      Serial.print(xValue);
      Serial.print(", ");
      int16_t yChannel = readRegister(Y_CH_RESULT,0x00, 0x00, 0x00);
      signed short yValue = yChannel + 80; //100/(32768);
      Serial.print(yValue);
      Serial.print(", ");
      int16_t zChannel = readRegister(Z_CH_RESULT,0x00, 0x00, 0x00);
      signed short zValue = zChannel + 50; //*100/(32768);
      Serial.println(zValue);
    }

    else if (command == 2){
      float p1 = Serial.parseFloat();
      float p2 = Serial.parseFloat();
      float p3 = Serial.parseFloat();

      target[0] = round(p1*x_steps_per_mm);
      target[1] = round(p2*y_steps_per_mm);
      target[2] = round(p3*z_steps_per_mm);    

      steppers.moveTo(target);

      steppers.runSpeedToPosition(); // Blocks until all are in position
      // steppers.run(); // does 1 step every loop iteration

      // printTime = 0;
      Serial.print("Position: ");
      Serial.print(stepper1.currentPosition()/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper2.currentPosition()/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper3.currentPosition()/z_steps_per_mm);
      Serial.print(" | ");
      Serial.print("Target: ");
      Serial.print(target[0]/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[1]/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[2]/z_steps_per_mm);
      Serial.print('\n');

      // SENSOR READOUT: Read X and Z, do math, then print
      int16_t xChannel = readRegister(X_CH_RESULT,0x00, 0x00, 0x00);
      signed short xValue = xChannel + 80; //100/(32768);
      // Serial.print("m");
      Serial.print(xValue);
      Serial.print(", ");
      int16_t yChannel = readRegister(Y_CH_RESULT,0x00, 0x00, 0x00);
      signed short yValue = yChannel + 80; //100/(32768);
      Serial.print(yValue);
      Serial.print(", ");
      int16_t zChannel = readRegister(Z_CH_RESULT,0x00, 0x00, 0x00);
      signed short zValue = zChannel + 50; //*100/(32768);
      Serial.println(zValue);
    }
    
    else if (command == 1){
      stepper1.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      stepper3.setCurrentPosition(0);
      target[0] = 0;
      target[1] = 0;
      target[2] = 0;
      // Serial.print("zero command received");
    
      // printTime = 0;
      Serial.print("Position: ");
      Serial.print(stepper1.currentPosition()/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper2.currentPosition()/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(stepper3.currentPosition()/z_steps_per_mm);
      Serial.print(" | ");
      Serial.print("Target: ");
      Serial.print(target[0]/x_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[1]/y_steps_per_mm);
      Serial.print(",  ");
      Serial.print(target[2]/z_steps_per_mm);
      Serial.print('\n');

      // SENSOR READOUT: Read X and Z, do math, then print
      int16_t xChannel = readRegister(X_CH_RESULT,0x00, 0x00, 0x00);
      signed short xValue = xChannel + 80; //100/(32768);
      // Serial.print("m");
      Serial.print(xValue);
      Serial.print(", ");
      int16_t yChannel = readRegister(Y_CH_RESULT,0x00, 0x00, 0x00);
      signed short yValue = yChannel + 80; //100/(32768);
      Serial.print(yValue);
      Serial.print(", ");
      int16_t zChannel = readRegister(Z_CH_RESULT,0x00, 0x00, 0x00);
      signed short zValue = zChannel + 50; //*100/(32768);
      Serial.println(zValue);
   }
  }
}



