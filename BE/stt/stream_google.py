from fastapi import WebSocket
from google.cloud import speech
import asyncio
import contextlib

async def stream_google_transcription(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Conectado")

    client = speech.SpeechAsyncClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="pt-PT"
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    queue = asyncio.Queue()
    websocket_closed = False

    async def receive_audio():
        nonlocal websocket_closed
        try:
            while True:
                data = await websocket.receive_bytes()
                await queue.put(data)
        except Exception as e:
            print("[receive_audio] Erro:", e)
            websocket_closed = True

    async def request_generator():
        # Enviar a config como primeira mensagem
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
        while not websocket_closed:
            data = await queue.get()
            yield speech.StreamingRecognizeRequest(audio_content=data)

    try:
        asyncio.create_task(receive_audio())
        responses = await client.streaming_recognize(requests=request_generator())

        async for response in responses:
            for result in response.results:
                if result.alternatives:
                    transcript = result.alternatives[0].transcript
                    await websocket.send_text(transcript)

    except Exception as e:
        print("[stream_transcription] Erro durante transcrição:", e)

    finally:
        print("[WS] Desconectado")
        with contextlib.suppress(Exception):
            await websocket.close()
