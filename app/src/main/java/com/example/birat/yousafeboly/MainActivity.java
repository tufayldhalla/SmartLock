package com.example.birat.yousafeboly;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;



public class MainActivity extends AppCompatActivity {

    Button door1;
    Button door2;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        setTitle("Main Page");

        door1 = (Button) findViewById(R.id.door1button);
        door2 = (Button) findViewById(R.id.door2button);

        door1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intentloaddoor1 = new Intent(MainActivity.this, Door1Activity.class);
                intentloaddoor1.putExtra("message", "This is here because you clicked button for door 1.");
                startActivity(intentloaddoor1);
            }
        });

        door2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intentloaddoor2 = new Intent(MainActivity.this, Door2Activity.class);
                intentloaddoor2.putExtra("message", "This is here because you clicked button for door 2.");
                startActivity(intentloaddoor2);
            }
        });
    }
}