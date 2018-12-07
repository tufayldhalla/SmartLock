package com.example.birat.yousafeboly;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;

//Class designed to handle any activities relating to door2, the dummy door.
// Hence, many functions that can be found implemented in Door 1 are not implemented here.
public class Door2Activity extends AppCompatActivity {

    Button lockButton;
    Button unlockButton;

    String appName = "YSBolt";
    final int DOORNUMBER = 2;
    final String lockCommand = "CMD\0LOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";
    final String unlockCommand = "CMD\0UNLOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";
    InetAddress IPADDRESS;
    int portNum = 8018;
    String myIP = "192.168.0.21"; //IP addrees of the server RPi


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_door2);
        setTitle("Door 2");

        lockButton = (Button)findViewById(R.id.lockbutton);
        unlockButton = (Button)findViewById(R.id.unlockbutton);

        //Create an IPAddress
        try{
            IPADDRESS = InetAddress.getByName(myIP);
        }catch(UnknownHostException e){
            e.printStackTrace();
        }

        /**
         * This method is invoked every time lock button is pressed.
         */
        lockButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                //Connection bits - send the lock command packet to the RPi
                Thread lockSender = new Thread(new Door2Activity.Sender(IPADDRESS, portNum, lockCommand));
                lockSender.start();

                //Notification after door has been locked.
                NotificationManager notif = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                Notification notify = new Notification.Builder(getApplicationContext()).setContentTitle("Door Locked!").setContentText("Door 2 is now locked.").setContentTitle(appName)
                        .setSmallIcon(R.drawable.jokelogo).build();

                notify.flags |= Notification.FLAG_AUTO_CANCEL;
                notif.notify(0, notify);

            }
        });

        /**
         * Every time unlock button is pressed.
         */
        unlockButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                //Connection bits - send the unlock command packet to the RPi;
                Thread unlockSender = new Thread(new Door2Activity.Sender(IPADDRESS, portNum, unlockCommand));//This bit can be abstracted by creating just one Sender class.
                unlockSender.start();


                //Notification after door has been unlocked.
                NotificationManager notif = (NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
                Notification notify = new Notification.Builder(getApplicationContext()).setContentTitle("Door Unlocked!").setContentText("Door 1 is now locked.").setContentTitle(appName)
                        .setSmallIcon(R.drawable.jokelogo).build();

                notify.flags |= Notification.FLAG_AUTO_CANCEL;
                notif.notify(0, notify);
            }
        });
    }//end of onCreate


    //------------------------Networking with Raspberry Pi(Server).------------------------------------------
    //A better implementation is just to create a sender class to use for both door 1 and 2.
    private class Sender implements Runnable{
        int port;
        String message;
        InetAddress ip;
        String messageReceived;

        /**
         * Constructor for the class.
         *
         * @param ip
         * @param port
         * @param message
         */
        public Sender(InetAddress ip, int port, String message){ //Constructor
            this.port=port;
            this.ip=ip;
            this.message=message;
        }

        @Override
        public void run() {

            try {
                Socket socket = new Socket(ip, port); //New socket

                //initiate output stream
                DataOutputStream cmdOut = new DataOutputStream(socket.getOutputStream());

                while (true) {
                    cmdOut.writeBytes(message); //convert them into bytes
                    System.out.println("Packet sent:    " + message);


                    //Receiving ACK from the input stream
                    BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    messageReceived = in.readLine();
                    System.out.println("Ack packet received:   " + messageReceived);

                    socket.close();
                }//end while(true)

            } catch (Exception e) {
                e.printStackTrace();
            }//end catch

        }//end run

    }//end the nested class Sender

}//end of Door2Activity.java