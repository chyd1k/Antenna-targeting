#include <GyverStepper.h>
#include <Servo.h>

GStepper<STEPPER2WIRE> stepperAzimuth(3200, 2, 3);  // step, dir

Servo mainServo;
int angServCurr = 0;        // текущий угол привода
int angServDest = 0;        // целевой угол привода

float azimuthDegree = 180.;   // для функции runRotationTest - задаёт угол поворота по азимуту

String readString = "";

void servoMove(int *angCurr, int angDest, int spDelay);

void setup()
{
  mainServo.attach(9);                        // attaches the servo on pin 9 to the servo object
  servoMove(&angServCurr, angServDest, 50);

  stepperAzimuth.setMaxSpeed(800);            // скорость движения к цели
  stepperAzimuth.setCurrentDeg(0.);           // установить текущую позицию мотора на 0 градусов

  // Начинаем работу с Serial портом на скорости 9600 бит/с
  Serial.begin(9600);
}

void setPosDegAzimuth(int degree)
{
  stepperAzimuth.setTargetDeg(degree);
}

void servoMove(int *angCurr, int angDest, int spDelay)
{
  static long prevTime = 0;
  long nowTime = millis();
  //запускаем фоновое движение сервопривода в заданное положение с учетом заданной обратной скорости
  if (nowTime - prevTime > spDelay)
  {
    if (*angCurr > angDest)
      (*angCurr)--; //меняем текущий угол возвышения

    if (*angCurr < angDest)
      (*angCurr)++;//меняем текущий угол возвышения

    int serAng = *angCurr;
    serAng = constrain(serAng, 0, 90); //обрезаем значения в допустимый диапазон
    serAng = map(serAng, 0, 90, 10, 85); //обрезаем значения в допустимый диапазон
    mainServo.write(90 - serAng);
    prevTime = nowTime;
  }
}

void runRotationTest()
{
  bool bAzimuthTick = stepperAzimuth.tick();
  
  if (!bAzimuthTick)
  {
    float curAzimuthDeg = stepperAzimuth.getCurrentDeg();
    if (abs(curAzimuthDeg) < 1e-6)
      setPosDegAzimuth(azimuthDegree);
    else
      setPosDegAzimuth(0);
  }
}

void pythonChecker()
{
  bool bAzimuthTick = stepperAzimuth.tick();
  servoMove(&angServCurr, angServDest, 35); //плавно перемещаем сервопривод с шагом 4 мс
  
  int counter = 0;
  int incByte = 0;
  while (Serial.available() >= 1)
  {
    incByte = Serial.read();
    // Serial.println(char(incByte));
    
    if (incByte == 27)
    {
      // Serial.println("VALUE FOUND, BREAK");
      break;
    }
    else if (incByte == -1)
    {
      // Serial.println("Escape ignored, continue");
      counter++;
      continue;
    }

    readString += char(incByte);
    delay(2);
    counter++;
  }
  if (readString.length() > 0 && incByte == 27)
  {
    Serial.println("STRING->" + readString);
    int indexAz = readString.indexOf("A");
    int indexRange = readString.indexOf("U");

    if (indexAz == -1 || indexRange == -1)
      return;
    float az = readString.substring(indexAz + 1, indexRange).toFloat();
    float range = readString.substring(indexRange + 1).toFloat();
    angServDest = range; // угол для выставки наклона к горизонту 0...90 градусов

    // Serial.println(readString.substring(indexAz + 1, indexRange));
    // Serial.println(readString.substring(indexRange + 1));

    if (!bAzimuthTick)
    {
      float curAzimuthDeg = stepperAzimuth.getCurrentDeg();
      // Serial.println(curAzimuthDeg);
      // Serial.println(az);
      setPosDegAzimuth(az);
    }
    readString="";
  }
}

void loop()
{
  // runRotationTest();
  pythonChecker();
  // servoMove(&angServCurr, angServDest, 50); //плавно перемещаем сервопривод
}
