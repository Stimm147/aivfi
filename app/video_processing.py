import cv2
import numpy as np
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


def add_audio_to_video(input_video_path, output_video_path):
    """Dodaje oryginalne audio do interpolowanego wideo."""
    video = VideoFileClip(output_video_path)
    original = VideoFileClip(input_video_path)

    # Zastąpienie ścieżki audio
    video_with_audio = video.set_audio(original.audio)
    video_with_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
