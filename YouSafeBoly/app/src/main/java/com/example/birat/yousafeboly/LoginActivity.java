package com.example.birat.yousafeboly;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.graphics.Color;

import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

/**
 * The class is designed for the user to be able to login using email and password.
 */
public class LoginActivity extends AppCompatActivity {

    Button loginButton, cancelButton;
    EditText userName, passWord;
    TextView tx1;
    TextView tx2;
    int counter =3; //to count number of failed logins.

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        loginButton = (Button)findViewById(R.id.button);
        cancelButton = (Button) findViewById(R.id.button2);
        userName = (EditText) findViewById(R.id.editText);
        passWord = (EditText) findViewById(R.id.editText2);
        tx1 = (TextView)findViewById(R.id.textView3);
        tx2= (TextView)findViewById(R.id.textView2);
        tx1.setVisibility(View.GONE);
        tx2.setVisibility(View.GONE);

        /**
         * Invoked when login button pressed.
         */
        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //If the input matches to correct value.
                if(userName.getText().toString().equals("admin@admin.com") &&
                        passWord.getText().toString().equals("admin")){
                    Toast.makeText(getApplicationContext(),"Success!",Toast.LENGTH_SHORT).show();
                    //given the login info is correct, load main screen.
                    Intent loadMainScreen = new Intent(LoginActivity.this, MainActivity.class);
                    startActivity(loadMainScreen);
                }else{
                    Toast.makeText(getApplicationContext(),"Wrong Credentials",Toast.LENGTH_SHORT).show();

                    tx2.setVisibility(View.VISIBLE);
                    tx1.setVisibility(View.VISIBLE);
                    tx1.setBackgroundColor(Color.RED);
                    counter--;
                    tx1.setText(Integer.toString(counter));

                    //if the suer enters wrong credentials 3 times, disable the login button
                    if (counter==0){
                        loginButton.setEnabled(false);
                    }
                }
            }
        });

        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });

    }

}
