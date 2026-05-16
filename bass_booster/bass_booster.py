import os
import numpy as np
import soundfile as sf
import sounddevice as sd
from scipy.signal import butter, lfilter

def get_settings():
    cutoff = float(input("Bass cutoff frequency: "))
    bass_mult = float(input("Bass boost multiplier: "))
    dist_mult = float(input("Distortion multiplier: "))
    return cutoff, bass_mult, dist_mult

def apply_bass_boost(audio_data, samplerate, cutoff, bass_mult, dist_mult):
    def butter_lowpass_filter(data_chunk, cutoff_freq, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff_freq / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, data_chunk, axis=0)

    bass = butter_lowpass_filter(audio_data, cutoff, fs=samplerate)
    heavy_bass = audio_data + (bass * bass_mult)
    distorted = heavy_bass * dist_mult
    return np.clip(distorted, -1.0, 1.0)

def real_time_processing():
    cutoff, bass_mult, dist_mult = get_settings()

    fs = 44100
    blocksize = 1024

    print("\nRealtime mode")
    print("Type 'exit' to stop\n")

    stop_flag = {"run": True}
    buffer = np.zeros((blocksize, 2), dtype=np.float32)

    def callback(indata, outdata, frames, time, status):
        if status:
            pass
        processed = apply_bass_boost(indata, fs, cutoff, bass_mult, dist_mult)
        buffer[:] = processed[:, :2]
        outdata[:] = buffer

    stream = sd.Stream(
        samplerate=fs,
        blocksize=blocksize,
        channels=2,
        dtype="float32",
        callback=callback
    )

    stream.start()

    while True:
        cmd = input()
        if cmd.strip().lower() == "exit":
            stop_flag["run"] = False
            break

    stream.stop()
    stream.close()

def bass_boost():
    input_path = input("Enter audio file path: ").strip('"')
    data, samplerate = sf.read(input_path)

    cutoff, bass_mult, dist_mult = get_settings()

    processed_data = apply_bass_boost(data, samplerate, cutoff, bass_mult, dist_mult)

    input_dir = os.path.dirname(input_path)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(input_dir, f"{filename}_bass_boosted.wav")

    if os.path.exists(output_path):
        os.remove(output_path)

    sf.write(output_path, processed_data, samplerate)
    print("Done:", output_path)

def main():
    while True:
        print("\n-----Bass Booster-----\n")
        print("1. Process audio file")
        print("2. Real time processing\n")

        try:
            option = int(input("Choose an option: "))
        except ValueError:
            print("Invalid input\n")
            continue

        if option == 1:
            bass_boost()
        elif option == 2:
            real_time_processing()
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
