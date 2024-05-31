import speechmatics
from httpx import HTTPStatusError
import asyncio
import pyaudio 
import requests
API_KEY = "frTJ385iXOuR1UY5wjjikJlkUZnXBAN3"
LANGUAGE = "en"
CONNECTION_URL = f"wss://eu2.rt.speechmatics.com/v2/en"
DEVICE_INDEX = 2
CHUNK_SIZE = 1024
lastsentence = ''

class AudioProcessor:
    def __init__(self):
        self.wave_data = bytearray()
        self.read_offset = 0

    async def read(self, chunk_size):
        while self.read_offset + chunk_size > len(self.wave_data):
            await asyncio.sleep(0.1)
        new_offset = self.read_offset + chunk_size
        data = self.wave_data[self.read_offset:new_offset]
        self.read_offset = new_offset
        return data

    def write_audio(self, data):
        self.wave_data.extend(data)
        return


audio_processor = AudioProcessor()
# PyAudio callback
def stream_callback(in_data, frame_count, time_info, status):
    audio_processor.write_audio(in_data)
    return in_data, pyaudio.paContinue

# Set up PyAudio
p = pyaudio.PyAudio()
if DEVICE_INDEX == -1:
    DEVICE_INDEX = p.get_default_input_device_info()['index']
    device_name = p.get_default_input_device_info()['name']
    DEF_SAMPLE_RATE = int(p.get_device_info_by_index(DEVICE_INDEX)['defaultSampleRate'])
    print(f"***\nIf you want to use a different microphone, update DEVICE_INDEX at the start of the code to one of the following:")
    # Filter out duplicates that are reported on some systems
    device_seen = set()
    for i in range(p.get_device_count()):
        if p.get_device_info_by_index(i)['name'] not in device_seen:
            device_seen.add(p.get_device_info_by_index(i)['name'])
            try:
                supports_input = p.is_format_supported(DEF_SAMPLE_RATE, input_device=i, input_channels=1, input_format=pyaudio.paFloat32)
            except Exception:
                supports_input = False
            if supports_input:
                print(f"-- To use << {p.get_device_info_by_index(i)['name']} >>, set DEVICE_INDEX to {i}")
    print("***\n")

SAMPLE_RATE = int(p.get_device_info_by_index(DEVICE_INDEX)['defaultSampleRate'])
device_name = p.get_device_info_by_index(DEVICE_INDEX)['name']

print(f"\nUsing << {device_name} >> which is DEVICE_INDEX {DEVICE_INDEX}")
print("Starting transcription (type Ctrl-C to stop):")

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=DEVICE_INDEX,
                stream_callback=stream_callback
)

# Define connection parameters
conn = speechmatics.models.ConnectionSettings(
    url=CONNECTION_URL,
    auth_token=API_KEY,
    generate_temp_token=True,
)

# Create a transcription client
ws = speechmatics.client.WebsocketClient(conn)

# Define transcription parameters
# Full list of parameters described here: https://speechmatics.github.io/speechmatics-python/models
conf = speechmatics.models.TranscriptionConfig(
    language=LANGUAGE,
    enable_partials=True,
    max_delay=8,
)

# Define an event handler to print the partial transcript
def print_partial_transcript(msg):
    print(f"[partial] {msg['metadata']['transcript']}")
    thisText = {'partial' : msg['metadata']['transcript']}
    url = 'http://localhost:3000/api/postPartial'
    x = requests.post(url, json = thisText)

# Define an event handler to print the full transcript
def print_transcript(msg):
    global lastsentence
    print(f"[  FINAL] {msg['metadata']['transcript']}")
    text = {msg['metadata']['transcript']}
    print(text)
    if (text != {''}) == True:
        lastsentence = {'final': msg['metadata']['transcript']}
    print(lastsentence)
    url = 'http://localhost:3000/api/postFinal'
    urlPartial = 'http://localhost:3000/api/postPartial' 
    x = requests.post(url, json = lastsentence)
    y = requests.post(urlPartial, json = {"partial": ''})
    print(x)

# Register the event handler for partial transcript
ws.add_event_handler(
    event_name=speechmatics.models.ServerMessageType.AddPartialTranscript,
    event_handler=print_partial_transcript,
)

# Register the event handler for full transcript
ws.add_event_handler(
    event_name=speechmatics.models.ServerMessageType.AddTranscript,
    event_handler=print_transcript,
)

settings = speechmatics.models.AudioSettings()
settings.encoding = "pcm_f32le"
settings.sample_rate = SAMPLE_RATE
settings.chunk_size = CHUNK_SIZE

print("Starting transcription (type Ctrl-C to stop):")
try:
    ws.run_synchronously(audio_processor, conf, settings)
except KeyboardInterrupt:
    print("\nTranscription stopped.")
except HTTPStatusError as e:
    if e.response.status_code == 401:
        print('Invalid API key - Check your API_KEY at the top of the code!')
    else:
        raise e