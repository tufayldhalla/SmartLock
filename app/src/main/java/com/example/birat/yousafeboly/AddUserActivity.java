package com.example.birat.yousafeboly;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Button;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;

public class AddUserActivity extends AppCompatActivity {

    String name, PINS;
    EditText userName, PIN;
    Socket socket;
    int portNum = 8018;
    InetAddress IPADDRESS;
    String myIP = "192.168.0.21";
    Button SET;
    String ADDUSER, FINALPACKET;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_user);

        userName = (EditText)findViewById(R.id.user);
        PIN = (EditText)findViewById(R.id.pin);
        SET = (Button)findViewById(R.id.setButton);

        name = userName.getText().toString();
        PINS = PIN.getText().toString();

        //Create an IPAddress
        try{
            IPADDRESS = InetAddress.getByName(myIP);
        }catch(UnknownHostException e){
            e.printStackTrace();
        }


        SET.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //ADDUSER = "CMD\0ADD USER&"+ name + " " + PINS+ "\0M";
                ADDUSER = "CMD\0ADD USER&Tufayl 1234\0M";
                FINALPACKET = ADDUSER.toString();

                System.out.println("DEBUG:"+ADDUSER);
                System.out.println("DEBUG:"+name);
                System.out.println("DEBUG:"+PINS);

                //Connection bits - send the lock command packet to the RPi
                Thread userSender = new Thread(new Sender(IPADDRESS, portNum, FINALPACKET));
                userSender.start();

                //Notification after door has been locked.
                NotificationManager notif = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                Notification notify = new Notification.Builder(getApplicationContext()).setContentTitle("New User").setContentText("New User added").setContentTitle("YSBOLT")
                        .setSmallIcon(R.drawable.jokelogo).build();

                notify.flags |= Notification.FLAG_AUTO_CANCEL;
                notif.notify(0, notify);

            }
        });

    }

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
                    socket = new Socket(ip, port);
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

                    //  socket.close();

                }//end while(true)
            } catch (Exception e) {
                e.printStackTrace();
            }//end catch

        }//end run

    }//end the nested class Sender



}//End UserActivityClass
