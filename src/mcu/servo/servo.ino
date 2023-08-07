#include <PIV_v1.h>
#define ARDUINOPIN1 7
#define ARDUINOPIN2 8
#define arraysize 124
#define USB_SETTINGS_SIZE 6
void gas();
void Achange();
void Bchange();
void interruptFunction1();
void interruptFunction2();
volatile boolean A,B;
float count=0,lastcount=0;
byte state, prvstate;
int  pin2=2, pin3=3,motorpin1=5,motorpin2=6,lastime=0,pwm_value1=0,pwm_value2=0,arrNum=1, pos_sampletime=1000;
volatile int QEM[16]={0,-1,0,1,1,0,-1,0,0,1,0,-1,-1,0,1,0},event=0,timeclock=0,timeval,error=0,target=0;
volatile int sizecheck[255];
volatile double  dstate, pstate, dterm, pterm,istate,iterm;
int Output2=0,Output1=0; 
double Kp, Ki, Kd;
double Input=0,Output,Setpoint=0;
unsigned int timenow=0,lastiime=0;
volatile int connected_2_py=0,timelast=0;
PIV myPIV(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);
volatile unsigned int timestart=0,timestamp=0,timestampp=0;
boolean readstate=false,bufferstate=true;

int i=0;

struct data1 { 
   volatile unsigned int encoder1[arraysize];
};

struct data2 { 
   volatile unsigned int encoder2[arraysize];
};

struct data3 { 
   volatile int kp;
   volatile int ki;
   volatile int kd;
   volatile int mult;
   volatile int num_2plot;
   volatile int pos_sampletime;
   volatile int pos_step_Input;
   //volatile int PIV_sampleTime;
};

struct data1 buffer1;
struct data2 buffer2;
struct data3 buffer3;

IntervalTimer myTimer;

void setup() {
  Serial.begin(115200);
  do{                                    // blocking if not connected
    if(Serial.available()){
      connected_2_py = try_connect();
    }
  }while(connected_2_py==0);
  while(Serial.available()<28){         //wait for settings
    ;
  }
  get_USB_settings();
  pinMode(pin2,INPUT_PULLUP);
  pinMode(pin3,INPUT_PULLUP); 
  attachInterrupt(pin2,Achange,FALLING);
  attachInterrupt(pin3,Bchange,FALLING);
  myTimer.begin(fillbuffer, pos_sampletime);
  myPIV.SetTunings(Kp,Ki,Kd);
  myPIV.SetMode(AUTOMATIC);
  myPIV.SetSampleTime(500);
  myPIV.SetOutputLimits(-150,150);
  analogWriteFrequency(5, 234375);
}

void loop() { 
    gas();
    if (readstate && arrNum<buffer3.num_2plot){
      if(bufferstate){
          Serial.write((const uint8_t*)&buffer2,sizeof(buffer2));
          arrNum++;
       }else{
          Serial.write((const uint8_t*)&buffer1,sizeof(buffer1));
          arrNum++;
       }
       readstate=false;
       if (arrNum==buffer3.num_2plot){
          myTimer.end();
          int tlast=millis();
          do{
             gas();
          }while(Serial.available()==0);
          analogWrite(motorpin1,0);
          analogWrite(motorpin2,0);
          setup();
       }
    }    
 }

int try_connect(){
   if (Serial.read()== 'p') return 1;
   else return 0;
}


void gas(){
       Output2=Output;
       myPIV.Compute();
        if(Output2<0){
          Output1=0-Output2;
          Output2=0;
        }else{
                Output1=0;
        }
       analogWrite(motorpin1,Output2);
       analogWrite(motorpin2,Output1);
}


void get_USB_settings(){
   count=0;
   Input=0;
   i=0;
   readstate=false;
   bufferstate=true;
   arrNum=0;
   byte todo = Serial.read();
      switch (todo){
        case 0:{
          uint8_t temp_buffer[28];
          Serial.readBytes((char *)&temp_buffer, sizeof(temp_buffer));
          memmove(&buffer3,temp_buffer,sizeof(buffer3));
          Kp = (buffer3.kp*1.0)/buffer3.mult;
          Ki = (buffer3.ki*1.0)/buffer3.mult;
          Kd = (buffer3.kd*1.0)/buffer3.mult;
          pos_sampletime = buffer3.pos_sampletime;
          Setpoint = buffer3.pos_step_Input*1.0;
          break;
        }
        case 1:{
          count=0;
          myPIV.SetTunings(0.0,0.0,0.0);
          break;
        }
    }
} 

void fillbuffer(){
   if(bufferstate){
     buffer1.encoder1[i] = count;
   }else{
     buffer2.encoder2[i] = count;
   }
   i++;
   if (i==arraysize){             //just reset to zero so the buffer locate again at the start point (first object e.g a[0])
      bufferstate=!bufferstate;
      i=0;
      readstate=true;             //one of the buffers has pushed all the way so fill it with new values
   }
}

void Achange(){
  if (digitalRead(3))    count++;             // if(digitalRead(encodPinB1)==HIGH)   count ++;
  else                   count--;             // if (digitalRead(encodPinB1)==LOW)   count --;
  Input=count;
}

void Bchange()
{  
  if (digitalRead(2))    count--;             // if(digitalRead(encodPinB1)==HIGH)   count ++;
  else                   count++;             // if (digitalRead(encodPinB1)==LOW)   count --;
  Input=count;
}
