package com.example.birat.yousafeboly;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.view.ViewTreeObserver;
import android.widget.ImageView;
import android.widget.Button;
import android.widget.RelativeLayout;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;

public class Door1Activity extends AppCompatActivity{
    //App variables
    Button lockButton, unlockButton, pictureButton;
    ImageView doorPicture;

    //Sender variables
    String appName = "YSBolt";
    String myIP = "192.168.0.21";
    String phoneIP = "192.168.0.240";//The phone running the application will be assigned static IP.
    int portNum = 8018;
    int phonePort = 2001;
    InetAddress IPADDRESS;
    InetAddress PHONEIPADDRESS;
    final int DOORNUMBER = 1;
    final String LOCKCOMMAND = "CMD\0LOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";
    final String UNLOCKCOMMAND = "CMD\0UNLOCK DOOR&" + Integer.toString(DOORNUMBER) + "\0M";

    //Receiver variables
    Socket socket,receivingSocket;
    ServerSocket ss;
    DataInputStream dataInputStream;
    int length;
    byte [] data;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_door1);
        setTitle("Door 1");

        lockButton = (Button)findViewById(R.id.lockbutton);
        unlockButton = (Button)findViewById(R.id.unlockbutton);
        doorPicture = (ImageView)findViewById(R.id.doorpicture);

        //Create an IPAddress - phone's IP(static): PHONEIPADDRESS, serverIP: IPADDRESS
        try{
            IPADDRESS = InetAddress.getByName(myIP);
            PHONEIPADDRESS = InetAddress.getByName(phoneIP);
        }catch(UnknownHostException e){
            e.printStackTrace();
        }

        Thread pictureThread = new Thread(new Receiver());
        pictureThread.start();

        /**
         * Invoked when asked to lock the door.
         */
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
        });//end lock door

        /**
         * Invoked when asked to open door.
         */
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
        });//end unlock door
    }//end onCreate

    //------------------------Networking with RPi(Server)-------------------------------------------
    public class Sender implements Runnable{
        int port;
        String message;
        InetAddress ip;
        String messageReceived;

        /**
         * Constructor Sender class.
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

        /**
         * Setter method to set message.
         *
         * @param m
         */
        public void setMessage(String m){
            message = m;
        }

        @Override
        public void run() {

            try {

                try{
                    socket = new Socket(ip, port);
                }catch (SocketException e){
                    e.printStackTrace();
                }

                //Initiate output stream
                DataOutputStream cmdOut = new DataOutputStream(socket.getOutputStream());

                while (true) {
                    cmdOut.writeBytes(message); //Convert the command to bytes and send them out through the stream.

                    //Receiving ACK from the input stream
                    BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    messageReceived = in.readLine();

                    socket.close();
                }//end while(true)
            } catch (Exception e) {
                e.printStackTrace();
            }//end catch

        }//end run

    }//end the nested class Sender

    //------------------Nested Receiver class to receive Picture-------------------
    public class Receiver implements Runnable{
        int pictureByteSize = 535055;

        @Override
        public void run(){
            try{
                ss = new ServerSocket(phonePort, pictureByteSize, PHONEIPADDRESS);
                while (true){
                    receivingSocket = ss.accept();
                    final InputStream in = receivingSocket.getInputStream();
                    dataInputStream = new DataInputStream(in);

                    length = dataInputStream.readInt();
                    data = new byte[pictureByteSize];

                    dataInputStream.read(data);

                    //Thread to contiually read bytes of picture.
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            final RelativeLayout view = (RelativeLayout)findViewById(R.id.doorview);

                              view.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
                                  @SuppressWarnings("deprecation")
                                  @Override
                                  public void onGlobalLayout() {
                                      view.getViewTreeObserver().removeOnGlobalLayoutListener(this);
                                      //Create a bitmap out of the received bytes.
                                      Bitmap bitmap = Bitmap.createBitmap(view.getWidth(), view.getHeight(), Bitmap.Config.ARGB_8888);
                                      Canvas c = new Canvas(bitmap);

                                      //the bitmap is placed on the canvas'c' and placed on the activity.
                                      view.layout(view.getLeft(), view.getTop(), view.getRight(), view.getBottom());
                                      view.draw(c);
                                      doorPicture.setImageBitmap(bitmap);
                                  }
                              });

                            try {
                                //Close both the streams after all the data has been read.
                                dataInputStream.close();
                                in.close();
                            }catch (Exception e){
                                e.printStackTrace();
                            }
                        }
                    });
                }
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }//end of nested receiver class

}//end the Door1Activity class
