#include <Keypad.h>   //use the Keypad libraries
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

//Definitions for Stepper Motor
#define IN1  2
#define IN2  3
#define IN3  4
#define IN4  5

//Global Variables
int cstep = 0;
String append = "";
String incoming = "";

// addr, en,rw,rs,d4,d5,d6,d7,bl,blpol
LiquidCrystal_I2C lcd(0x20, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE); //SDA -> A4 //SCL -> A5

//Set up Keypad
const byte ROWS = 4; //four rows
const byte COLS = 4; //four columns
//define the cymbols on the buttons of the keypads
char hexaKeys[ROWS][COLS] = {
  { '1','2','3',' '},
  { '4','5','6',' '},
  { '7','8','9',' '},
  { 'A','0','B',' '}
};
byte rowPins[ROWS] = {6, 7, 8, 9}; //y1 y2 y3 y4 //connect to the row pinouts of the keypad
byte colPins[COLS] = {10, 11, 12, 13}; //x1 x2 x3 x4 //connect to the column pinouts of the keypad

//initialize an instance of class NewKeypad
Keypad myKeypad = Keypad( makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS); 

void setup()
{
  Serial.begin(9600); //sets data rate
  
  pinMode(IN1, OUTPUT); 
  pinMode(IN2, OUTPUT); 
  pinMode(IN3, OUTPUT); 
  pinMode(IN4, OUTPUT); 
  
  lcd.begin(16,2);               // initialize the lcd
  welcome();                    //Display welcome message on lcd
}

void loop() {
  char keyPressed = myKeypad.getKey();//get the key value
  preform (keyPressed);
  if (Serial.available() > 0) {
    incoming = Serial.readString();
    if (incoming.substring(0,2) == "AG") {
      AccessGranted(incoming.substring(2));
    }
    else if (incoming.substring(0,2) == "AD") {
      AccessDenied();
    }
    welcome();
    incoming = "";
  }
}

void AccessGranted(String incoming) {
    lcd.clear();
    lcd.print(incoming);
    lcd.setCursor(0,1);
    lcd.print("Door Opening");
    rotateCounterClockwise();
    lcd.clear();
    lcd.print("Access Granted");
    lcd.setCursor(0,1);
    lcd.print("Door Closing");
    Serial.println("ACK&Urgay");
    rotateClockwise();
}

void AccessDenied() {
      lcd.clear();
      lcd.print("Access Denied");
      lcd.setCursor(0,1);
      lcd.print("Martins GAY");
      delay(2000);
}

void welcome(){
  lcd.clear();
  lcd.print("Welcome to YSB"); 
  lcd.setCursor(0,1);
  lcd.print("B to buzz owner"); 
}

void preform (char keyPressed) {
  if (keyPressed == 'B') {
    lcd.clear();
    lcd.print("Buzzer Pressed");
    Serial.println("Buzzer");
    append = "";
  }
  else if (keyPressed == '0' || keyPressed == '1' || keyPressed == '2' || keyPressed == '3' || keyPressed == '4' || keyPressed == '5' || keyPressed == '6' || keyPressed == '7' || keyPressed == '8' || keyPressed == '9') {
    append += keyPressed;
    if (append.length() == 4) {
      lcd.clear();
      lcd.print(append);
      Serial.println("DATA&" + append);
      append = "";
    }
  }
  else if (keyPressed == 'A') {
    lcd.clear();
    lcd.print("Lock this bitch");
    rotateClockwise();
    welcome();
    append = "";
  }
}

void rotateCounterClockwise () { //function to rotate stepper motor 360 degrees counterclockwise
    for(int x=0;x<4096;x++) {
      algorithm(true);
      delayMicroseconds(1000);
    }
}

void rotateClockwise () { //function to rotate stepper motor 360 degrees clockwise
    for(int x=0;x<4096;x++) {
      algorithm(false);
      delayMicroseconds(1000);
    }
}

void algorithm(bool dir) //algorithm to rotate stepper motor
{
  switch(cstep)
  {
   case 0:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, HIGH);
   break; 
   case 1:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, HIGH);
     digitalWrite(IN4, HIGH);
   break; 
   case 2:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, HIGH);
     digitalWrite(IN4, LOW);
   break; 
   case 3:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, HIGH);
     digitalWrite(IN3, HIGH);
     digitalWrite(IN4, LOW);
   break; 
   case 4:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, HIGH);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, LOW);
   break; 
   case 5:
     digitalWrite(IN1, HIGH); 
     digitalWrite(IN2, HIGH);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, LOW);
   break; 
     case 6:
     digitalWrite(IN1, HIGH); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, LOW);
   break; 
   case 7:
     digitalWrite(IN1, HIGH); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, HIGH);
   break; 
   default:
     digitalWrite(IN1, LOW); 
     digitalWrite(IN2, LOW);
     digitalWrite(IN3, LOW);
     digitalWrite(IN4, LOW);
   break; 
  }
  SetDirection(dir);
}


void SetDirection(bool dir){ //function to rotate stepper motor clockwise or counter clockwise
  if(dir==true){ 
    cstep++;
   }
  if(dir==false){ 
    cstep--; 
   }
  if(cstep>7){
    cstep=0;
   }
  if(cstep<0){
    cstep=7; 
   }
}
