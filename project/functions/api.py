import urllib3
import urllib.request
import json
import base64


class Translation():
    def __init__(self):
        self.client_id = ""  # 개발자 센터에서 발급받은 Client ID 값
        self.client_secret = ""  # 개발자 센터에서 발급받은 Client Secret 값
        self.apiUrl = "https://openapi.naver.com/v1/papago/n2mt"
        self.translate_text = ""

    def request_api(self, spoken_text):
        response = None

        try:
            encText = urllib.parse.quote(spoken_text)
            text_data = "source=ko&target=en&text=" + encText

            request = urllib.request.Request(self.apiUrl)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)

            response = urllib.request.urlopen(
                request, data=text_data.encode("utf-8"))
        except Exception as e:
            print(f"번역을 시도하는 과정에서 에러가 발생했습니다. : {e}")

        return response

    def decode_response(self, response):
        rescode = response.getcode()
        result = "failed"

        if (rescode == 200):
            response_body = response.read()
            result = response_body.decode('utf-8')
            decoded = json.loads(result)
            result = decoded["message"]["result"]["translatedText"]

        return result

    def translate_kor_to_eng(self, spoken_text):
        response = self.request_api(spoken_text)

        # response가 None이 아닐 경우, decode 진행
        if (response):
            result = self.decode_response(response)

        # 만약 failed라면 저장하지 않고 종료
        if (result == "failed"):
            return

        # 번역에 성공한 경우라면 저장
        self.translate_text = result


class STT():
    def __init__(self):
        self.apiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
        self.accessKey = ""
        self.audioFilePath = "./기말project/code/data/recorded_voice/voice_record_kor.wav"
        self.languageCode = "korean"  # 언어 선택

        self.http = urllib3.PoolManager()

    def encode_audio_file(self):
        '''
            API 요청으로 전송할 audio file을 open하고
            base64로 encoding하여 file 객체로 저장하는 함수
        '''

        file = open(self.audioFilePath, "rb")
        self.audioContents = base64.b64encode(file.read()).decode("utf8")
        file.close()

    def request_api(self):
        '''
            encoding한 file 객체를 실어
            API 요청으로 전송하는 함수
        '''

        requestJson = {
            "argument": {
                "language_code": self.languageCode,
                "audio": self.audioContents
            }
        }

        response = self.http.request(
            "POST",
            self.apiURL,
            headers={"Content-Type": "application/json; charset=UTF-8",
                     "Authorization": self.accessKey},
            body=json.dumps(requestJson)
        )

        return response

    def decode_response(self, response):
        if response.status != 200:
            print("음성인식에 실패했습니다. 다시 시도해 주세요.")
            return

        spoken_text = json.loads(response.data.decode(
            "utf-8"))["return_object"]["recognized"]

        return spoken_text

    def get_text_from_audio(self):
        '''
            STT API 요청의 전체 과정을 시작하는 함수
        '''

        self.encode_audio_file()
        response = self.request_api()
        return self.decode_response(response)


class PronunciationTest():
    def __init__(self):
        self.languageCode = "english"
        self.accessKey = ""
        self.audioFilePath = "./기말project/code/data/recorded_voice/voice_record_eng.wav"
        self.apiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Pronunciation"

    def test(self, script):
        file = open(self.audioFilePath, "rb")
        audioContents = base64.b64encode(file.read()).decode("utf8")
        file.close()

        requestJson = {
            "argument": {
                "language_code": self.languageCode,
                "script": script,
                "audio": audioContents
            }
        }

        score = -1

        # post 요청에 실패할 경우에 대비하여 try/catch 사용
        try:
            http = urllib3.PoolManager()
            response = http.request(
                "POST",
                self.apiURL,
                headers={"Content-Type": "application/json; charset=UTF-8",
                         "Authorization": self.accessKey},
                body=json.dumps(requestJson)
            )
        except Exception as e:
            print("평가 과정에서 에러가 발생했습니다. 다시 시도해 주세요\n")
            return score

        # print("[responseCode] " + str(response.status))
        # print("[responBody]")

        if (response.status == 200):
            score_object = json.loads(
                response.data.decode("utf-8"))["return_object"]
            score = score_object['score']
            score = int(float(score)*20)
        else:
            print("평가 과정에서 네트워크 에러가 발생했습니다. 다시 시도해 주세요\n")

        return score
