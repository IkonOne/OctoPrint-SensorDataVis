#include <SD.h>
#include <SPI.h>
#define outputA 6
#define outputB 7
 
int counter = 0;
int aState;
int aLastState;
File dataLog;
const int chipSelect = 4;
String fileName = "";
String command = "";

void printMenu() {
  // put your setup code here, to run once:
  delay(1000);
  Serial.println("Data Acquisition Menu");
  Serial.println("1) start recording");
  Serial.println("2) print data");
  Serial.println("Enter selection");  
}

void setup() {
  Serial.print("Setting up: ");
  pinMode (outputA,INPUT);
  pinMode (outputB,INPUT);
   
  Serial.begin (115200);
  // Reads the initial state of the outputA
  aLastState = digitalRead(outputA);

  //set up the SD card
  Serial.println("Enter file name: ");
  fileName = Serial.readString();
  Serial.setTimeout(6000);
  if (fileName.equals(""))
    fileName = "test.csv";   
  Serial.println("Initializing SD card...");
  pinMode(chipSelect, OUTPUT); //chip select pin must be set to output mode
  delay(100);
  if(!(SD.begin(chipSelect))){//Initialize SD card
    Serial.println("Could not initialize SD card."); //if return false, initialization failed
  }
  if(SD.exists(fileName)){ //if a file exists, delete it
    Serial.println("File exists; deleting...");
    if(SD.remove(fileName)){
      Serial.println("Successfully removed file.");
    }else{
      Serial.println("Could not remove fie.");
    }
  }
  dataLog = SD.open(fileName, FILE_WRITE);
  Serial.println("File created: " + (String)dataLog.name());
  dataLog.println("Counter,Diameter1,Diameter2");
  printMenu();
}

void loop() {
  if(Serial.available()){
    command = Serial.readString();
  }
  if(command.equals("1\n")){
    aState = digitalRead(outputA); // Reads the "current" state of the outputA
    // If the previous and the current state of the outputA are different, that means a Pulse has occured
    if (aState != aLastState){
      // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
      if (digitalRead(outputB) != aState) {
        counter ++;
      } else {
        counter --;
      }
      Serial.print("Position: ");
      Serial.println(counter);
      //now write to the file
      //dataLog.println("current position: " + (String)counter);
      dataLog.println((String)counter + ",1,2");
    }
    aLastState = aState; // Updates the previous state of the outputA with the current state
  }else if(command.equals("2\n")){
  //Serial.println("You entered: " + Serial.readString());
    dataLog.close();
    Serial.println("done recording. File content:");
    dataLog = SD.open(fileName);
    while(dataLog.available()){
      Serial.println(dataLog.readStringUntil('\n'));
    }
    dataLog.close();
    dataLog = SD.open(fileName, FILE_WRITE);
    command = "";
    printMenu();
  }else if(!command.equals("")){
    Serial.println("Invalid Command");
    printMenu();
  }
}
