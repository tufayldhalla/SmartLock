package com.example.birat.yousafeboly;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.Button;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;

public class Door1Activity extends AppCompatActivity{
    //App variables
    Button lockButton;
    Button unlockButton;
    ImageView doorPicture;

    //Sender variables
    String appName = "YSBolt";
    String myIP = "192.168.0.21";
    int portNum = 2018;
    InetAddress IPADDRESS;
    final int DOORNUMBER = 1;
    final String LOCKCOMMAND = "CMD\0LOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";
    final String UNLOCKCOMMAND = "CMD\0UNLOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";

    //Receiver variables
    DataOutputStream dataOutputStream = null;
    DataInputStream dataInputStream = null;
    Socket socket;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_door1);
        setTitle("Door 1");

        lockButton = (Button)findViewById(R.id.lockbutton);
        unlockButton = (Button)findViewById(R.id.unlockbutton);
        doorPicture = (ImageView)findViewById(R.id.doorpicture);

        //Create an IPAddress
        try{
            IPADDRESS = InetAddress.getByName(myIP);
        }catch(UnknownHostException e){
            e.printStackTrace();
        }

        //TODO: Current bitmap too large. Scale picture down and display on the phone(Code Below)
//        //Receiving a picture on the phone
//        try {
//             socket = new Socket(IPADDRESS, portNum);
//
//             dataInputStream = new DataInputStream(socket.getInputStream());
//
//             String base64Code = dataInputStream.readUTF();
//
//             Log.d("String", ":" + base64Code);
//
//             byte[] decodedString = null;
//             try{
//                 decodedString = Base64.decode(base64Code, Base64.DEFAULT);
//             }catch (Exception e){
//                 e.printStackTrace();
//                 Log.d("ERROR HERE", "" + e);
//             }
//             Log.d("St--",":" +decodedString.length);
//
//            Bitmap bitmap = BitmapFactory.decodeByteArray(decodedString, 0, decodedString.length);
//            doorPicture.setImageBitmap(bitmap);
//
//        }catch(UnknownHostException e) {
//            e.printStackTrace();
//        }catch (Exception e ){
//            e.printStackTrace();
//        }finally {
//            if(socket != null){
//                try{
//                    socket.close();
//                }catch(IOException e){
//                    e.printStackTrace();
//                }
//            }//end if - Socket
//
//            if(dataInputStream != null){
//                try{
//                    dataInputStream.close();
//                }catch(IOException e){
//                    e.printStackTrace();
//                }
//            }//end if - dataInputStream
//
//        }//end finally



        lockButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                //Connection bits - send the lock command packet to the RPi
                Thread lockSender = new Thread(new Sender(IPADDRESS, portNum, LOCKCOMMAND));
                lockSender.start();


                //Notification after door has been locked.
                NotificationManager notif = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                Notification notify = new Notification.Builder(getApplicationContext()).setContentTitle("Door Locked!").setContentText("Door 1 is now locked.").setContentTitle(appName)
                        .setSmallIcon(R.drawable.jokelogo).build();

                notify.flags |= Notification.FLAG_AUTO_CANCEL;
                notif.notify(0, notify);

            }
        });

        unlockButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                //Connection bits - send the unlock command packet to the RPi;
                Thread unlockSender = new Thread(new Sender(IPADDRESS, portNum, UNLOCKCOMMAND));
                unlockSender.start();


                //Notification after door has been unlocked.
                NotificationManager notifUN = (NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
                Notification notifyUN = new Notification.Builder(getApplicationContext()).setContentTitle("Door 1 Unlocked!").setContentText("Door 1 is now locked.").setContentTitle(appName)
                        .setSmallIcon(R.drawable.jokelogo).build();

                notifyUN.flags |= Notification.FLAG_AUTO_CANCEL;
                notifUN.notify(0, notifyUN);
            }
        });

    }//end onCreate

    //------------------------Networking with RPi(Server)-------------------------------------------
    private class Sender implements Runnable{
        int port;
        String message;
        InetAddress ip;
        String messageReceived;


        /**
         * This is a constructor Sender class.
         *
         * @param ip
         * @param port
         * @param message
         */
        public Sender(InetAddress ip, int port, String message){
            this.port=port;
            this.ip=ip;
            this.message=message;
        }

        @Override
        public void run() {

            try {

                try{
                    Socket socket = new Socket(ip, port);
                }catch (SocketException e){
                    e.printStackTrace();
                }


                //initiate output stream
                DataOutputStream cmdOut = new DataOutputStream(socket.getOutputStream());

                while (true) {
                    cmdOut.writeBytes(message); //Convert the command to bytes.
                    System.out.println("Packet sent:   " + message);

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

}//end the Door1Activity class
