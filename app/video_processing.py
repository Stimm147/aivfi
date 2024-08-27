import cv2
import os
from moviepy.editor import VideoFileClip


def interpolate_frames(frame1, frame2, alpha):
    """Interpoluje pomiędzy dwiema klatkami."""
    return cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)


def interpolate_video(input_path, output_path, interpolation_factor, progress_callback=None):
    """Interpoluje klatki wideo i zapisuje wynik."""
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    new_fps = fps * (interpolation_factor + 1)
    out = cv2.VideoWriter(output_path, fourcc, new_fps, (width, height))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0

    ret, prev_frame = cap.read()
    if not ret:
        print("Nie udało się wczytać pierwszej klatki wideo.")
        return

    while True:
        ret, next_frame = cap.read()
        if not ret:
            break
        out.write(prev_frame)
        for i in range(1, interpolation_factor + 1):
            alpha = i / (interpolation_factor + 1)
            interpolated_frame = interpolate_frames(prev_frame, next_frame, alpha)
            out.write(interpolated_frame)

        processed_frames += 1
        if progress_callback:
            progress_callback(processed_frames / total_frames * 100)

        prev_frame = next_frame

    out.write(prev_frame)
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def add_audio_to_video(input_video_path, output_video_path, progress_callback=None):
    """Dodaje oryginalne audio do interpolowanego wideo za pomocą moviepy, przycinając audio do długości wideo."""
    video = VideoFileClip(output_video_path)
    original = VideoFileClip(input_video_path)

    # Przycinanie audio do długości wideo
    if original.audio:
        audio = original.audio.subclip(0, video.duration)
        video_with_audio = video.set_audio(audio)
    else:
        video_with_audio = video

    # Używamy liczby klatek, aby obliczyć postęp
    total_frames = video.reader.nframes
    current_frame = 0

    # Funkcja callback, która jest wywoływana po każdej zapisanej klatce
    def audio_progress_callback(get_frame, t):
        nonlocal current_frame
        current_frame += 1
        if progress_callback:
            progress_callback(current_frame, total_frames)
        return get_frame(t)

    video_with_audio = video_with_audio.fl(audio_progress_callback, apply_to=['audio'])

    # Zapisz finalny plik wideo z audio z dopiskiem "_output"
    temp_output_path = output_video_path.replace(".mp4", "_output.mp4")
    video_with_audio.write_videofile(temp_output_path, codec='libx264', audio_codec='aac')

    # Usuń oryginalny plik wyjściowy bez audio
    if os.path.exists(output_video_path):
        os.remove(output_video_path)

    # Zmień nazwę pliku z "_output" na oryginalną nazwę
    os.rename(temp_output_path, output_video_path)
