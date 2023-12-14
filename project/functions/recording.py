import threading
import queue
import threading
import sounddevice as sd
import soundfile as sf
import time


class Recording:
    def __init__(self):
        self.q = queue.Queue()
        self.recorder = False
        self.recording = False
        self.waiting_time = 5

        self.kor_recording_path = "./기말project/code/data/recorded_voice/voice_record_kor.wav"
        self.eng_recording_path = "./기말project/code/data/recorded_voice/voice_record_eng.wav"

    def complicated_record_kor(self):
        '''
            sampling rate 16kHz로 음성 파일을 녹음하는 함수.
        '''
        with sf.SoundFile(self.kor_recording_path, mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
            with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=self.complicated_save):
                while self.recording:
                    file.write(self.q.get())

    def complicated_record_eng(self):
        '''
            sampling rate 16kHz로 음성 파일을 녹음하는 함수.
        '''
        with sf.SoundFile(self.eng_recording_path, mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
            with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=self.complicated_save):
                while self.recording:
                    file.write(self.q.get())

    def complicated_save(self, indata, frames, time, status):
        self.q.put(indata.copy())

    # 녹음 시간을 변경하는 메서드
    def change_waiting_time(self, seconds):
        if (seconds < 5):
            print("반드시 3초 이상 녹음해야 합니다.")
            return

        self.waiting_time = seconds

    def wait_for_sec(self, seconds):
        print("\n")
        for sec in range(seconds, 0, -1):
            print(f"{sec}초 남았습니다.")
            time.sleep(1)

    def start_recording(self, recording_type):
        self.recording = True

        if (recording_type == "kor"):
            self.recorder = threading.Thread(
                target=self.complicated_record_kor)
        elif (recording_type == "eng"):
            self.recorder = threading.Thread(
                target=self.complicated_record_eng)

        # start recording
        self.recorder.start()

        # 한국어 녹음일 때만 출력하기
        if (recording_type == "kor"):
            print(f'원하는 문장을 말씀해 주세요. ({recording_type})')

        # 정해진 시간 동안 대기
        self.wait_for_sec(self.waiting_time)

        # stop recording
        self.stop()

    def stop(self):
        self.recording = False
        self.recorder.join()
        print('녹음이 종료되었습니다.')
