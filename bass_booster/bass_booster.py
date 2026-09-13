import os
import numpy as np
import soundfile as sf
import sounddevice as sd
from scipy.signal import butter, lfilter


def get_settings():
    cutoff = float(input("\nBass cutoff frequency: "))
    bass_mult = float(input("Bass boost multiplier: "))
    dist_mult = float(input("Distortion multiplier: "))

    return cutoff, bass_mult, dist_mult


def create_lowpass(cutoff, samplerate):
    nyq = 0.5 * samplerate

    if cutoff <= 0 or cutoff >= nyq:
        raise ValueError(
            f"Cutoff must be between 0 and {nyq:.0f} Hz."
        )

    b, a = butter(4, cutoff / nyq, btype="low")

    return b, a


def apply_fx(audio, cutoff, bass_mult, dist_mult, samplerate):
    b, a = create_lowpass(cutoff, samplerate)

    bass = lfilter(b, a, audio, axis=0)

    output = audio + bass * bass_mult
    output = output * dist_mult

    return np.clip(output, -1, 1)


def choose_cable():
    devices = []

    for index, device in enumerate(sd.query_devices()):
        name = device["name"]

        if (
            device["max_input_channels"] > 0
            and "CABLE Output" in name
        ):
            devices.append((index, name))

    if not devices:
        print("\nNo CABLE Output devices found.")
        return None

    print("\nAvailable VB-Cable devices:")

    for number, (index, name) in enumerate(devices, 1):
        print(f"{number}. {name}")

    while True:
        try:
            choice = int(input("\nChoose VB-Cable: "))

            if 1 <= choice <= len(devices):
                index, name = devices[choice - 1]

                print(f"Selected: {name}")

                return index

            print("Invalid option.")

        except ValueError:
            print("Invalid input.")


def choose_output():
    devices = []
    used_names = set()

    excluded_names = {
        "CABLE Input",
        "CABLE Input (VB-Audio Virtual Cable)",
    }

    for index, device in enumerate(sd.query_devices()):
        name = device["name"]

        if device["max_output_channels"] <= 0:
            continue

        if "CABLE Input" in name:
            continue

        clean_name = name.strip()

        if clean_name in used_names:
            continue

        used_names.add(clean_name)
        devices.append((index, name))

    if not devices:
        print("\nNo output devices found.")
        return None

    print("\nAvailable output devices:")

    for number, (index, name) in enumerate(devices, 1):
        print(f"{number}. {name}")

    while True:
        try:
            choice = int(input("\nChoose output device: "))

            if 1 <= choice <= len(devices):
                index, name = devices[choice - 1]

                print(f"Selected: {name}")

                return index

            print("Invalid option.")

        except ValueError:
            print("Invalid input.")


def real_time_processing():
    print("\nRealtime mode")

    fs = int(input("Sample rate (ex. 48000): "))
    blocksize = int(input("Block size (ex. 1024): "))

    print("\nAvailable input devices:")

    inputs = []

    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            inputs.append(index)
            print(f"{len(inputs)}. {device['name']}")

    try:
        choice = int(input("\nChoose input device: "))
        mic = inputs[choice - 1]
    except (ValueError, IndexError):
        print("Invalid input device.")
        return

    print("\nAvailable output devices:")

    outputs = []

    for index, device in enumerate(sd.query_devices()):
        if device["max_output_channels"] > 0:
            outputs.append(index)
            print(f"{len(outputs)}. {device['name']}")

    try:
        choice = int(input("\nChoose output device: "))
        output_device = outputs[choice - 1]
    except (ValueError, IndexError):
        print("Invalid output device.")
        return

    cutoff, bass_mult, dist_mult = get_settings()

    try:
        b, a = create_lowpass(cutoff, fs)
    except ValueError as e:
        print(e)
        return

    channels = 1

    zi = np.zeros(
        (max(len(a), len(b)) - 1, channels)
    )

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)

        audio = indata.copy()

        bass, new_zi = lfilter(
            b,
            a,
            audio,
            axis=0,
            zi=zi
        )

        zi[:] = new_zi

        processed = audio + bass * bass_mult
        processed = processed * dist_mult
        processed = np.clip(processed, -1, 1)

        outdata[:] = processed

    try:
        with sd.Stream(
            samplerate=fs,
            blocksize=blocksize,
            dtype="float32",
            channels=channels,
            device=(mic, output_device),
            callback=callback
        ):
            input("\nRUNNING... Press ENTER to stop.\n")

    except Exception as e:
        print("\nAudio stream error:")
        print(e)


def system_wide_processing():
    print("\nSystem-wide processing")
    print("Set CABLE Input as your Windows output device.")
    print("All system audio will go through the Bass Booster.")
    print("Press ENTER to stop.\n")

    cable = choose_cable()

    if cable is None:
        return

    output_device = choose_output()

    if output_device is None:
        return

    cable_info = sd.query_devices(cable)
    output_info = sd.query_devices(output_device)

    samplerate = int(cable_info["default_samplerate"])

    input_channels = cable_info["max_input_channels"]
    output_channels = output_info["max_output_channels"]

    channels = min(input_channels, output_channels, 2)

    if channels < 1:
        print("The selected devices have no compatible channels.")
        return

    print(f"\nUsing sample rate: {samplerate} Hz")
    print(f"Using channels: {channels}")

    cutoff, bass_mult, dist_mult = get_settings()

    try:
        b, a = create_lowpass(cutoff, samplerate)
    except ValueError as e:
        print(e)
        return

    filter_state = np.zeros(
        (max(len(a), len(b)) - 1, channels)
    )

    import queue

    audio_queue = queue.Queue(maxsize=20)

    def input_callback(indata, frames, time, status):
        if status:
            print(status)

        audio = indata[:, :channels].copy()

        try:
            audio_queue.put_nowait(audio)
        except queue.Full:
            pass

    def output_callback(outdata, frames, time, status):
        if status:
            print(status)

        try:
            audio = audio_queue.get_nowait()
        except queue.Empty:
            outdata.fill(0)
            return

        bass, new_state = lfilter(
            b,
            a,
            audio,
            axis=0,
            zi=filter_state
        )

        filter_state[:] = new_state

        processed = audio + bass * bass_mult
        processed = processed * dist_mult
        processed = np.clip(processed, -1, 1)

        outdata[:, :channels] = processed

    try:
        with sd.InputStream(
            samplerate=samplerate,
            blocksize=1024,
            dtype="float32",
            channels=channels,
            device=cable,
            callback=input_callback
        ):

            with sd.OutputStream(
                samplerate=samplerate,
                blocksize=1024,
                dtype="float32",
                channels=channels,
                device=output_device,
                callback=output_callback
            ):

                input("RUNNING... Press ENTER to stop.\n")

    except Exception as e:
        print("\nAudio stream error:")
        print(e)


def bass_boost():
    input_path = input("\nEnter audio file path: ").strip('"')

    if not os.path.isfile(input_path):
        print("File does not exist.")
        return

    try:
        data, samplerate = sf.read(input_path)

        cutoff, bass_mult, dist_mult = get_settings()

        processed = apply_fx(
            data,
            cutoff,
            bass_mult,
            dist_mult,
            samplerate
        )

        input_dir = os.path.dirname(input_path)
        filename = os.path.splitext(
            os.path.basename(input_path)
        )[0]

        output_path = os.path.join(
            input_dir,
            f"{filename}_bass_boosted.wav"
        )

        sf.write(
            output_path,
            processed,
            samplerate
        )

        print("Done:", output_path)

    except Exception as e:
        print("\nError:")
        print(e)


def main():
    while True:
        print("\n-----Bass Booster-----\n")
        print("1. Process audio file")
        print("2. Real time processing")
        print("3. System-wide processing")
        print("4. Exit\n")

        try:
            option = int(input("Choose an option: "))

        except ValueError:
            print("Invalid input.")
            continue

        if option == 1:
            bass_boost()

        elif option == 2:
            real_time_processing()

        elif option == 3:
            system_wide_processing()

        elif option == 4:
            print("Exiting...")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
