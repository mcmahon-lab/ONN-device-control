package com.example.imagestreamlocal;

import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import com.example.library.AndroidOpenAccessoryBridge;
import com.example.library.BufferHolder;
import android.view.WindowManager;

import java.util.Arrays;

public class MainActivity extends Activity implements AndroidOpenAccessoryBridge.Listener {

    ConstraintLayout constraintLayout;
    private AndroidOpenAccessoryBridge mAoab;
    private TextView mTextView;
    private ImageView i;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // prevent screen from dimming
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        mAoab = new AndroidOpenAccessoryBridge(this, this);

        //setting up gui for app
        View decorView = getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        constraintLayout = new ConstraintLayout(this);  //generic android gui call

        i = new ImageView(this);
        i.setImageResource(R.drawable.black);
        i.setAdjustViewBounds(true); //allow image to use full screen
        i.setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));  //generic android gui call
        i.setScaleType(ImageView.ScaleType.FIT_CENTER);  //use FIT_CENTER for no stretching

        //add image, with specified parameters, to the app's display
        constraintLayout.addView(i);
        setContentView(constraintLayout);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mAoab = null;
    }

    // AndroidOpenAccessoryBridge.Listener

    @Override
    public void onAoabRead(final BufferHolder bufferHolder) {
        try {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    // Open and display image file with the name received over USB.
                    String fileName = bufferHolder.toString();
                    int resID = getResources().getIdentifier(fileName, "drawable",
                            getPackageName());
                    i.setImageResource(resID);
                }
            });
        } catch (NumberFormatException exception) {
            return;
        }
        /*
         *  Add code for sending response back to laptop here
         */
    }

    @Override
    public void onAoabShutdown() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Commented out on purpose. Including shuts down app after use.
                // There may be alternative functionality to add later.
                //finish();
            }
        });
    }

}
