from pydub import AudioSegment
import os


def split_audio(input_path, output_dir, chunk_duration):
    audio = AudioSegment.from_wav(input_path)
    total_duration = len(audio)
    chunk_size = chunk_duration

    for start in range(0, total_duration, chunk_size):
        end = start + chunk_size
        if end > total_duration:
            # skip last chunk if it's too small
            break
        chunk = audio[start:end]
        chunk.export(
            os.path.join(output_dir, f"chunk_{format(start, '05d')}.wav"),
            format="wav",
        )


if __name__ == "__main__":
    source_directory = "data"

    chunk_duration = 100  # ms
    files = [f for f in os.listdir(source_directory) if f.endswith(".wav")]
    for file in files:
        print(f"Processing file: {file}")

        file_path = os.path.join(source_directory, file)
        file_name = os.path.splitext(file)[0]
        output_directory = f"data/chunks_{file_name}"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        split_audio(file_path, output_directory, chunk_duration)
        print(f"Splitted file: {file}")
