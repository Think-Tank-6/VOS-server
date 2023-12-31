
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

from ai_models.text_generation.preprocessing import get_user_name,extract_messages
from ai_models.text_generation.token_limit import load_text_from_bottom
from ai_models.text_generation.characteristic_generation import merge_prompt_text,get_characteristics
from ai_models.text_generation.chat_generation import insert_persona_to_prompt,merge_prompt_input,get_response,prepare_chat
from ai_models.speaker_identification.clova_speech import ClovaSpeechClient
from ai_models.speaker_identification.postprocessing import speaker_diarization

import json
from io import BytesIO
from pydub import AudioSegment

### Load GPT ###
class PromptGeneration:
    API_KEY = os.getenv("GPT_API_KEY")
    client = OpenAI(api_key=API_KEY)

    def __init__(self, request,original_text_file) -> None:

        self.original_text_file = original_text_file
        self.star_gender = request["gender"]
        self.star_name = request["star_name"]
        self.persona = request["persona"]
        self.relationship = request["relationship"]

        self.API_KEY = os.getenv("GPT_API_KEY")
        self.client = OpenAI(api_key=self.API_KEY)

        # 추후 수정
        self.prompt_file_path = 'prompt_data/extract_characteristic.txt'
        self.system_input_path = "prompt_data/system_input.txt"

    def create_prompt_input(self,original_text_file) -> str:
 
        text = original_text_file.read()
        decoded_text = text.decode("utf-8")
               
        user_name = get_user_name(decoded_text)
        if user_name:
            star_text = extract_messages(decoded_text, user_name)
      
        star_text_12k = load_text_from_bottom(star_text, 12000,'gpt3.5')
        star_text_4k = load_text_from_bottom(star_text, 4000,'gpt4')
               
        # process for extracting characteristics
        prompt = merge_prompt_text(star_text_12k,self.prompt_file_path)
        characteristics = get_characteristics(prompt,self.client)
        
        # process for preparing system prompt
        system_input = insert_persona_to_prompt(self.star_name,self.relationship,self.system_input_path)
        chat_prompt_input_data = merge_prompt_input(characteristics,system_input,star_text_4k)
        
        return chat_prompt_input_data





    
class SpeakerIdentification:

    def __init__(self,original_voice_file):
        self.original_voice_file = original_voice_file
        self.speech_list = []

    def get_speaker_samples(self):
        audio_byte = BytesIO(self.original_voice_file.file.read())
        audio_seg = AudioSegment.from_file(audio_byte)
        audio_binary = audio_seg.export(format="wav").read()
        res = ClovaSpeechClient().req_upload(file=audio_binary, completion='sync')
        timestamp = json.loads(res.text)

        speaker_num, speech_list, speaker_sample_list = speaker_diarization(timestamp)
        self.speech_list = speech_list

        # speaker_num: speaker 수, speaker_sample_list: speaker 각자의 목소리 담긴 리스트
        # 이것들을 프론트에 넘겨줄 수 있도록 작업


        return None

    def get_star_voice(self):
        # speech_list 가져와서 고인 목소리 이어붙이는 작업

        pass

    


class ChatGeneration:
    API_KEY = os.getenv("GPT_API_KEY")
    client = OpenAI(api_key=API_KEY)

    def __init__(self,user_input,p_data, messages):
        self.user_input = user_input
        self.p_data = p_data
        self.messages = messages

    def get_gpt_answer(self) -> str:
        
        # GPT에 대화 히스토리 넣고 답변 받기
        messages = prepare_chat(self.p_data)
        gpt_answer, messages = get_response(self.client,self.user_input, self.messages)

        return gpt_answer, messages