/*
  Created by Brian Richard (bcr53) on March 1, 2020

  Structure heavily borrowed from Chris Blay's code at:
    https://github.com/chris-blay/android-open-accessory-bridge
 */

package com.example.background;
import android.system.ErrnoException;
import android.system.OsConstants;
import android.util.Log;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;


public class ImageBuffer {
    private static final String TAG = ImageBuffer.class.getSimpleName();
    private final byte[] mSizeBytes;
    public ByteBuffer bytes;
    public int size;

    public static int imageHeight = 1920;
    public static int imageWidth = 1080;

    public ImageBuffer() {
        mSizeBytes = new byte[3];
        bytes = ByteBuffer.allocate(0xffffff);
    }

    public void reset() {
        bytes.clear();
        size = 0;
    }

    boolean read(final FileInputStream inputStream) throws IOException {
        if (size <= 0) {
            final int bytesRead;
            try {
                bytesRead = inputStream.read(mSizeBytes);
            } catch (IOException exception) {
                if (ioExceptionIsNoSuchDevice(exception)) {
                    throw exception;
                }
                Log.d(TAG, "IOException while reading size bytes", exception);
                return false;
            }
            if (bytesRead != mSizeBytes.length) {
                Log.d(TAG, "Incorrect number of bytes read while reading size bytes:"
                        + " actual=" + bytesRead + " expected=" + mSizeBytes.length);
                return false;
            }
            size = readSizeBytes();
            bytes = ByteBuffer.allocate(size);
        }
        final int bytesRead;
        try {
            int foo = 1;
            int count = 0;
            while(foo > 0){
                foo = inputStream.read(bytes.array(), count, size-count);
                count += foo;
            }
            bytesRead = count;
        } catch (IOException exception) {
            if (ioExceptionIsNoSuchDevice(exception)) {
                throw exception;
            }
            Log.d(TAG, "IOException while reading data bytes", exception);
            return false;
        }
        if (bytesRead != size) {
            Log.d(TAG, "Incorrect number of bytes read while reading data bytes:"
                    + " actual=" + bytesRead + " expected=" + size);
            return false;
        }
        return true;
    }

    boolean write(final FileOutputStream outputStream) throws IOException {
        writeSizeBytes(size);
        try {
            outputStream.write(mSizeBytes);
            outputStream.write(bytes.array(), 0, size);
            outputStream.flush();
            return true;
        } catch (IOException exception) {
            if (ioExceptionIsNoSuchDevice(exception)) {
                throw exception;
            }
            Log.d(TAG, "IOException while writing size+data bytes", exception);
            return false;
        }
    }

    private int readSizeBytes() {
        return ((mSizeBytes[0] & 0xff) << 16 | (mSizeBytes[1] & 0xff) << 8 | (mSizeBytes[2] & 0xff));
    }

    private void writeSizeBytes(final int value) {
        if (BuildConfig.DEBUG && (value <= 0 || value > 0xffff)) {
            throw new AssertionError("Size value out of bounds: " + value);
        }
        mSizeBytes[0] = (byte) ((value & 0xff00) >> 16);
        mSizeBytes[1] = (byte) ((value & 0x00ff) >> 8);
        mSizeBytes[2] = (byte) (value & 0x00ff);
    }

    private boolean ioExceptionIsNoSuchDevice(IOException ioException) {
        final Throwable cause = ioException.getCause();
        if (cause instanceof ErrnoException) {
            final ErrnoException errnoException = (ErrnoException) cause;
            return errnoException.errno == OsConstants.ENODEV;
        }
        return false;
    }
}