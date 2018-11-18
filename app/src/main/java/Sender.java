import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.Socket;

public class Sender implements Runnable {
    int port;
    String message;
    InetAddress ip;
    String messageReceived;


    public Sender(InetAddress ip, int port, String message){ //Constructor
        this.port=port;
        this.ip=ip;
        this.message=message;
    }

    @Override
    public void run() {

        try {
            Socket socket = new Socket(ip, port);

            //initiate input and output streams
            DataOutputStream cmdOut = new DataOutputStream(socket.getOutputStream());

            // while (true) {
            cmdOut.writeBytes(message); //convert them into bytes
            System.out.println("Packet sent:   " + message);


            //Receiving ACK froom the input stream
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            messageReceived = in.readLine();
            System.out.println(messageReceived);

            socket.close();

            //  }//end while(true)
        } catch (Exception e) {
            e.printStackTrace();
        }//end catch

    }//end run

}
