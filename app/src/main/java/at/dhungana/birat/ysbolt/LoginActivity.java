package at.dhungana.birat.ysbolt;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.graphics.Color;

import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.w3c.dom.Text;

public class LoginActivity extends AppCompatActivity {

    Button loginButton, cancelButton;
    EditText userName, passWord;
    TextView tx1;
    int counter =3;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        loginButton = (Button)findViewById(R.id.button);
        cancelButton = (Button) findViewById(R.id.button2);
        userName = (EditText) findViewById(R.id.editText);
        passWord = (EditText) findViewById(R.id.editText2);
        tx1 = (TextView)findViewById(R.id.textView3);
        tx1.setVisibility(View.GONE);

        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(userName.getText().toString().equals("b") &&
                        passWord.getText().toString().equals("a")){
                    Toast.makeText(getApplicationContext(),"Redirecting..",Toast.LENGTH_SHORT).show();
                    Intent loadMainScreen = new Intent(LoginActivity.this, MainActivity.class);
                    startActivity(loadMainScreen);
                }else{
                    Toast.makeText(getApplicationContext(),"Wrong Credentials",Toast.LENGTH_SHORT).show();

                    tx1.setVisibility(View.VISIBLE);
                    tx1.setBackgroundColor(Color.RED);
                    counter--;
                    tx1.setText(Integer.toString(counter));

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
