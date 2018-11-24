#include <Keypad.h>   //Keypad libraries
#include <Wire.h> //Wire Pin Libararies
#include <LiquidCrystal_I2C.h> //LCD libraries

//Definitions for Stepper Motor
#define IN1  2
#define IN2  3
#define IN3  4
#define IN4  5

// address,enable,read/write,reset,data 4,data 5,data 6,data 7,backlight,backlight pol
LiquidCrystal_I2C lcd(0x20, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE); //Hardware set up = SDA -> A4 / SCL -> A5

//Global Variables
int revolutionSteps = 4096;   //Amount of steps required to complete a full 360 degree rotation
int motorSteps = 0;           //going through 7 different cases to send voltages to certain pins on the motor
String pinCode = "";          //the pin that is entered on the keypad
String packetReceieved = "";  //the string packet that is receieved from the RPi

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

byte rowPins[ROWS] = {6, 7, 8, 9}; //Hardware set up = y1 y2 y3 y4 //connect to the row pinouts of the keypad
byte colPins[COLS] = {10, 11, 12, 13}; //Hardware set up = x1 x2 x3 x4 //connect to the column pinouts of the keypad

//initialize an instance of class Keypad which is from the Keypad library 
Keypad myKeypad = Keypad( makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS); 

void setup()
{
  Serial.begin(9600); //sets data rate

  //Set Motor driver pins as output pins (sent voltages to pin)
  pinMode(IN1, OUTPUT); 
  pinMode(IN2, OUTPUT); 
  pinMode(IN3, OUTPUT); 
  pinMode(IN4, OUTPUT); 
  
  lcd.begin(16,2);                            //Initialize the lcd
  welcome();                                  //Display welcome message on lcd
}

void loop() {
  char keyPressed = myKeypad.getKey();             //Get the key value
  perform (keyPressed);                            //Calling function to see what button is pressed
  if (Serial.available() > 0) {                    //Checking to see if anything is being sent to the Arduino from the RPi
    packetReceieved = Serial.readString();         //Save incoming message into string
    if (packetReceieved.substring(0,2) == "AG") {  //Check if message incoming is an Access Granted (AG) message (AG + data)
      AccessGranted(packetReceieved.substring(2)); //Call function to deal with access being granted (input paramter = data) //data = username or nothing (if buzzer was pressed)
    }
    else if (packetReceieved == "AD") {       //Check if message incoming is an Access Denied (AD) message
      AccessDenied();                         //Call function to deal with access being granted
    }
    else if (packetReceieved == "UD") {       //Unlock Door
      lcd.clear();                            //Clear LCD screen
      lcd.print("Door Opening");              //Print String on LCD
      rotateCounterClockwise();               //Unlock Door (retract bolt)
      lcd.clear();                                
      lcd.print("Door Opened");               
      delay(1000);                            //Wait for 1 second
    }
    else if (packetReceieved == "LD") {      //Lock Door
      lcd.clear();                           
      lcd.print("Door Closing");
      rotateClockwise();                    //Lock Door (re-enforce bolt)
      lcd.clear();
      lcd.print("Door Closed");
      delay(1000);
    }
    else {
      Serial.println("Error&Wrong Packet Sent");  //Send error message back to RPi if wrong packet sent
    }
    welcome();                  //Display Welcome message again after incoming messages are dealt with
    packetReceieved = "";       //Clear previous message receieved
  }
}

//
void welcome(){
  lcd.clear();
  lcd.print("Welcome to YSB"); 
  lcd.setCursor(0,1); //Set cursor to print on second line of LCD
  lcd.print("B to buzz owner"); 
}

//function to deal with access being granted
void AccessGranted(String packetReceieved) {  
    lcd.clear();                              
    lcd.print("Access Granted");              
    lcd.setCursor(0,1);                       
    lcd.print("Door Unlocking");              
    rotateCounterClockwise();
    lcd.clear();
    if (packetReceieved == "") { //If buzzer was pressed then data would be empty 
      lcd.print("Access Granted");
    }
    else {                      //If pin entered then data would be guests name
      lcd.print(packetReceieved);
    }
    lcd.setCursor(0,1);
    lcd.print("Door Locking");
    Serial.println("ACK&Done"); //Send acknowledgement packet once door was unlocked then locked
    rotateClockwise();
}

//Method to deal with if owner does not want guest to enter 
void AccessDenied() {
  lcd.clear();
  lcd.print("Access Denied");
  lcd.setCursor(0,1);
  lcd.print("Go Away");
  delay(2000);
}

//
void perform (char keyPressed) {
  //If the buzzer was pressed
  if (keyPressed == 'B') {
    lcd.clear();
    lcd.print("Buzzer Pressed");
    Serial.println("DATA&BUZZ"); //Send the Data packet which instructs the RPi that buzzer was pressed
    pinCode = ""; //clear previous pin entered
  }
  //If a number on the keypad was pressed
  else if (keyPressed == '0' || keyPressed == '1' || keyPressed == '2' || keyPressed == '3' || keyPressed == '4' || keyPressed == '5' || keyPressed == '6' || keyPressed == '7' || keyPressed == '8' || keyPressed == '9') {
    pinCode += keyPressed; //append key pressed to the pin code
    lcd.clear();
    lcd.print(pinCode); //print each key pressed
    if (pinCode.length() == 4) { //Once 4 digits are entered 
      Serial.println("DATA&" + pinCode); //send the pin to the RPi
      pinCode = "";
    }
  }
  //If the lock door button was pressed on the keypad
  else if (keyPressed == 'A') {
    lcd.clear();
    lcd.print("Locking Door");
    rotateClockwise(); //Lock Door
    lcd.clear();
    lcd.print("Door Locked");
    delay(2000);
    welcome();
    pinCode = "";
  }
}

//function to rotate stepper motor 360 degrees counterclockwise
void rotateCounterClockwise () { 
    for(int x=0;x<revolutionSteps;x++) {
      algorithm(true); //call function to rotate motor
      delayMicroseconds(1000); //rotation speed
    }
}

//function to rotate stepper motor 360 degrees clockwise
void rotateClockwise () { 
    for(int x=0;x<revolutionSteps;x++) {
      algorithm(false);
      delayMicroseconds(1000);
    }
}

//algorithm to rotate stepper motor
void algorithm(bool dir) 
{
  //Overview: send voltages to certain pins to rotate motor
  switch(motorSteps)
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
  SetDirection(dir); //Call method to reset motorSteps if all cases finished and to increment according to rotation direction
}

//function to rotate stepper motor clockwise or counter clockwise and increment motorSteps
void SetDirection(bool dir){ 
  if(motorSteps>7){
    motorSteps=0;
   }
  if(motorSteps<0){
    motorSteps=7; 
   }
  if(dir==true){ 
    motorSteps++;
   }
  if(dir==false){ 
    motorSteps--; 
   }
}
