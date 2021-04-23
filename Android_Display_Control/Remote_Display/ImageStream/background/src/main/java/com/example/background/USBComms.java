/*
  Created by Brian Richard (bcr53) on March 1, 2020

  Structure heavily borrowed from Chris Blay's code at:
    https://github.com/chris-blay/android-open-accessory-bridge
 */

package com.example.background;

import android.content.Context;
import android.hardware.usb.UsbAccessory;
import android.hardware.usb.UsbManager;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.os.ParcelFileDescriptor;
import android.util.Log;

import java.io.Closeable;
import java.io.FileDescriptor;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

public class USBComms {
    private static final String TAG = USBComms.class.getSimpleName();
    private static final long CONNECT_COOLDOWN_MS = 100;
    private static final long READ_COOLDOWN_MS = 100;
    private Listener mListener;
    private UsbManager mUsbManager;
    private ImageBuffer mReadBuffer;
    private InternalThread mInternalThread;
    private boolean mIsShutdown;
    private boolean mIsAttached;
    private FileOutputStream mOutputStream;
    private FileInputStream mInputStream;
    private ParcelFileDescriptor mParcelFileDescriptor;

    public USBComms(final Context context, final Listener listener) {
        if (BuildConfig.DEBUG && (context == null || listener == null)) {
            throw new AssertionError("Arguments context and listener must not be null");
        }
        mListener = listener;
        mUsbManager = (UsbManager) context.getSystemService(Context.USB_SERVICE);
        mReadBuffer = new ImageBuffer();
        mInternalThread = new InternalThread();
        mInternalThread.start();
    }

    private class InternalThread extends Thread {

        private static final int STOP_THREAD = 1;
        private static final int MAYBE_READ = 2;

        private Handler mHandler;

        @Override
        public void run() {
            Looper.prepare();
            mHandler = new Handler() {
                @Override
                public void handleMessage(Message msg) {
                    switch (msg.what) {
                        case STOP_THREAD:
                            Looper.myLooper().quit();
                            break;
                        case MAYBE_READ:
                            final boolean readResult;
                            try {
                                readResult = mReadBuffer.read(mInputStream);
                            } catch (IOException exception) {
                                terminate();
                                break;
                            }
                            if (readResult) {
                                if (mReadBuffer.size == 0) {
                                    mHandler.sendEmptyMessage(STOP_THREAD);
                                } else {
                                    mListener.onAoabRead(mReadBuffer);
                                    mReadBuffer.reset();
                                    mHandler.sendEmptyMessage(MAYBE_READ);
                                }
                            } else {
                                mHandler.sendEmptyMessageDelayed(MAYBE_READ, READ_COOLDOWN_MS);
                            }
                            break;
                    }
                }
            };
            detectAccessory();
            Looper.loop();
            detachAccessory();
            //mIsShutdown = true;
            // Commented out to allow multiple communication exchanges.
            mListener.onAoabShutdown();

            // Clean stuff up
            mHandler = null;
            mListener = null;
            mUsbManager = null;
            mReadBuffer = null;
            mInternalThread = null;
        }

        void terminate() {
            mHandler.sendEmptyMessage(STOP_THREAD);
        }

        private void detectAccessory() {
            while (!mIsAttached) {
                if (mIsShutdown) {
                    mHandler.sendEmptyMessage(STOP_THREAD);
                    return;
                }
                try {
                    Thread.sleep(CONNECT_COOLDOWN_MS);
                } catch (InterruptedException exception) {
                    // pass
                }
                final UsbAccessory[] accessoryList = mUsbManager.getAccessoryList();
                if (accessoryList == null || accessoryList.length == 0) {
                    continue;
                }
                if (accessoryList.length > 1) {
                    Log.w(TAG, "Multiple accessories attached!? Using first one...");
                }
                maybeAttachAccessory(accessoryList[0]);
            }
        }

        private void maybeAttachAccessory(final UsbAccessory accessory) {
            final ParcelFileDescriptor parcelFileDescriptor = mUsbManager.openAccessory(accessory);
            if (parcelFileDescriptor != null) {
                final FileDescriptor fileDescriptor = parcelFileDescriptor.getFileDescriptor();
                mIsAttached = true;
                mOutputStream = new FileOutputStream(fileDescriptor);
                mInputStream = new FileInputStream(fileDescriptor);
                mParcelFileDescriptor = parcelFileDescriptor;
                mHandler.sendEmptyMessage(MAYBE_READ);
            }
        }

        private void detachAccessory() {
            if (mIsAttached) {
                mIsAttached = false;
            }
            if (mInputStream != null) {
                closeQuietly(mInputStream);
                mInputStream = null;
            }
            if (mOutputStream != null) {
                closeQuietly(mOutputStream);
                mOutputStream = null;
            }
            if (mParcelFileDescriptor != null) {
                closeQuietly(mParcelFileDescriptor);
                mParcelFileDescriptor = null;
            }
        }

        private void closeQuietly(Closeable closable) {
            try {
                closable.close();
            } catch (IOException exception) {
                // pass
            }
        }

    }

    public synchronized boolean write(final ImageBuffer bufferHolder) {
        if (BuildConfig.DEBUG && (mIsShutdown || mOutputStream == null)) {
            throw new AssertionError("Can't write if shutdown or output stream is null");
        }
        try {
            return bufferHolder.write(mOutputStream);
        } catch (IOException exception) {
            mInternalThread.terminate();
            return false;
        }
    }

    public interface Listener {
        void onAoabRead(ImageBuffer buffer);
        void onAoabShutdown();
    }
}
