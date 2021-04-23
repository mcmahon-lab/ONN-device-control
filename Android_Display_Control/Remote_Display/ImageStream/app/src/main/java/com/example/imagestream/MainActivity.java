package com.example.imagestream;

import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;

import android.graphics.Bitmap;
import android.media.Image;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.ImageView;
import com.example.background.USBComms;
import com.example.background.ImageBuffer;

public class MainActivity extends AppCompatActivity implements USBComms.Listener{

    ConstraintLayout constraintLayout;
    private USBComms comms;
    private Bitmap image;
    private int [] pixels;
    private int numPixels = ImageBuffer.imageWidth*ImageBuffer.imageHeight;
    private ImageView i;
    private View decorView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // prevent screen from dimming
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        comms = new USBComms(this, this);
        pixels = new int[numPixels];
        image = Bitmap.createBitmap(ImageBuffer.imageWidth, ImageBuffer.imageHeight,
                Bitmap.Config.ARGB_8888);

        //setting up gui for app
        hideSystemUI();


        constraintLayout = new ConstraintLayout(this);  //generic android gui call

        i = new ImageView(this);
        //setting up an image to be displayed in the app screen
        i.setImageResource(R.drawable.black);
        //display_image is located in app/res/drawable

        i.setAdjustViewBounds(true); //allow image to use full screen
        i.setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));  //generic android gui call
        i.setScaleType(ImageView.ScaleType.FIT_CENTER);  //use FIT_CENTER for no stretching

        //add image, with specified parameters, to the app's display
        constraintLayout.addView(i);
        setContentView(constraintLayout);
    }

    @Override
    public void onAoabRead(final ImageBuffer buffer) {
        try {
            for(int i = 0; i < numPixels; i++){
                pixels[i] = (0xff) << 24 | (buffer.bytes.get(3*i) & 0xff) << 16 |
                        (buffer.bytes.get(3*i + 1) & 0xff) << 8 | (buffer.bytes.get(3*i + 2) & 0xff);
            }
            image.setPixels(pixels, 0, ImageBuffer.imageWidth, 0, 0,
                    ImageBuffer.imageWidth, ImageBuffer.imageHeight);

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    i.setImageBitmap(image);
                }
            });
        } catch (NumberFormatException exception) {
            return;
        }
        //if (comms != null) {
        //    comms.write(buffer);
        //}
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        comms = null;
    }

    @Override
    protected void onResume() {
        hideSystemUI();
        super.onResume();
    }

    public void onAoabShutdown() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                //finish();
            }
        });
    }

    private void hideSystemUI() {
        decorView = getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY;
        decorView.setSystemUiVisibility(uiOptions);
    }
}
