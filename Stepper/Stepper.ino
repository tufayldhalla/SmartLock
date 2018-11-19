#define IN1  2
#define IN2  3
#define IN3  4
#define IN4  5
int cstep = 0;

void setup()
{
  Serial.begin(9600);
  pinMode(IN1, OUTPUT); 
  pinMode(IN2, OUTPUT); 
  pinMode(IN3, OUTPUT); 
  pinMode(IN4, OUTPUT); 

  rotateCounterClockwise(); //rotate counter clockwise (retract bolt)
  delay(1000); //wait one second
  rotateClockwise(); //rotate clockwise (re-enforce bolt)
}

void loop() {}

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
