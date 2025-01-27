#include <GyverStepper.h>
GStepper<STEPPER4WIRE> stepperAzimuth(2048, 2, 3, 4, 5);
GStepper<STEPPER4WIRE> stepperRange(2048, 8, 9, 10, 11);

float rangeDegree = 90.;
float azimuthDegree = 90.;
String readString = "";

void setup()
{
  stepperRange.setMaxSpeed(500);    // скорость движения к цели
  stepperRange.setCurrentDeg(0.);    // установить текущую позицию мотора на 0 градусов

  stepperAzimuth.setMaxSpeed(800);    // скорость движения к цели
  stepperAzimuth.setCurrentDeg(0.);    // установить текущую позицию мотора на 0 градусов

  // Начинаем работу с Serial портом на скорости 9600 бит/с
  Serial.begin(9600);
}

void setPosDegRange(int degree)
{
  stepperRange.setTargetDeg(degree);    // отправляем на 90 градусов
}

void setPosDegAzimuth(int degree)
{
  stepperAzimuth.setTargetDeg(degree);   // отправляем на 90 градусов
}

void runRotationTest()
{
  bool bRangeTick = stepperRange.tick();
  bool bAzimuthTick = stepperAzimuth.tick();
  
  if (!bRangeTick)
  {
    float curRangeDeg = stepperRange.getCurrentDeg();
    if (abs(curRangeDeg) < 1e-6)
      setPosDegRange(rangeDegree);
    else
      setPosDegRange(0.);
  }

  if (!bAzimuthTick)
  {
    float curAzimuthDeg = stepperAzimuth.getCurrentDeg();
    if (abs(curAzimuthDeg) < 1e-6)
      setPosDegAzimuth(azimuthDegree);
    else
      setPosDegAzimuth(0.);
  }
}

void pythonChecker()
{
  bool bRangeTick = stepperRange.tick();
  bool bAzimuthTick = stepperAzimuth.tick();

  int counter = 0;
  int incByte = 0;
  while (Serial.available() >= 1)
  {
    incByte = Serial.read();
    
    if (incByte == 27)
      break;
    else if (incByte == -1)
    {
      counter++;
      continue;
    }

    readString += char(incByte);
    delay(2);
    counter++;
  }
  if (readString.length() > 0 && incByte == 27)
  {
    int indexAz = readString.indexOf("A");
    int indexRange = readString.indexOf("U");

    if (indexAz == -1 || indexRange == -1)
      return;
    float az = readString.substring(indexAz + 1, indexRange).toFloat();
    float range = readString.substring(indexRange + 1).toFloat();
    
    if (!bRangeTick)
    {
      float curRangeDeg = stepperRange.getCurrentDeg();
      setPosDegRange(range);
    }

    if (!bAzimuthTick)
    {
      float curAzimuthDeg = stepperAzimuth.getCurrentDeg();
      setPosDegAzimuth(az);
    }

    readString="";
  }
}

void loop()
{
  runRotationTest();
  // pythonChecker();
}