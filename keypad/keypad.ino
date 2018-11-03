
#include <Keypad.h>   //use the Keypad libraries

const byte ROWS = 4; //four rows
const byte COLS = 4; //four columns
//define the cymbols on the buttons of the keypads
char hexaKeys[ROWS][COLS] = 
{
  { 
    '1','2','3',' '      }
  ,
  { 
    '4','5','6',' '      }
  ,
  { 
    '7','8','9',' '      }
  ,
  { 
    'A','0','B',' '      }
};
byte rowPins[ROWS] = {4, 5, 6, 7}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {8, 9, 10, 11}; //connect to the column pinouts of the keypad

//initialize an instance of class NewKeypad
Keypad myKeypad = Keypad( makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS); 

String append = "";

void setup()
{
  Serial.begin(9600); //sets data rate
}

void loop()
{
  char keyPressed = myKeypad.getKey();//get the key value
  if (keyPressed == 'B') {
    Serial.println("Buzzer is pressed");
  }
  else if (keyPressed == '0' || keyPressed == '1' || keyPressed == '2' || keyPressed == '3' || keyPressed == '4' || keyPressed == '5' || keyPressed == '6' || keyPressed == '7' || keyPressed == '8' || keyPressed == '9') {
    append += keyPressed;
    if (append.length() == 4) {
      Serial.println(append);
      append = "";
    }
  }
  else if (keyPressed == 'A') {
    Serial.println("Country Sucks ");//Add new finger print scanner user");
  }
}
