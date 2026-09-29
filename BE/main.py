from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import asyncio
import uvicorn
import jsonpickle
from typing import Optional
from db.memory_repository import update_memory
from db.db import database
from db.setup_tables import create_memory_table
from stt.stream_google import stream_google_transcription

from behaviours.send_feedback_to_dialogue_manager import SendFeedbackToDialogueManagerBehaviour

from agents.UserInterface import UserInterfaceAgent
from agents.DialogueManager import DialogueManagerAgent
from agents.LLMAgent import LLMAgent
from agents.EmotionAgent import EmotionAgent
from agents.MemoryAgent import MemoryAgent
from agents.SummarizerAgent import SummarizerAgent
from agents.FeedbackAgent import FeedbackAgent
from agents.CycleClassifierAgent import CycleClassifierAgent

load_dotenv()

# Lifespan para gerir ciclo de vida da app
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[FastAPI] A iniciar agentes SPADE...", flush=True)
    app.state.sse_clients = []  # Inicializar lista de clientes SSE

    # Conectar ao Postgres
    print("[FastAPI] A conectar ao PostgreSQL...", flush=True)
    await database.connect()

    await create_memory_table()

    try:
        await user_agent.start(auto_register=True)
        print("[DEBUG] UserInterfaceAgent iniciado.", flush=True)

        await dialogue_agent.start(auto_register=True)
        print("[DEBUG] DialogueManagerAgent iniciado.", flush=True)

        await llm_agent.start(auto_register=True)
        print("[DEBUG] LLMAgent iniciado.", flush=True)

        await emotion_agent.start(auto_register=True)
        print("[DEBUG] EmotionAgent iniciado.")

        await memory_agent.start(auto_register=True)
        print("[DEBUG] MemoryAgent iniciado.")

        await summarizer_agent.start(auto_register=True)
        print("[DEBUG] SummarizerAgent iniciado.")

        await feedback_agent.start(auto_register=True)
        print("[DEBUG] FeedbackAgent iniciado.")

        await cycleClassifier_agent.start(auto_register=True)
        print("[DEBUG] ClassifyAgent iniciado.")

        print("[FastAPI] Todos os agentes iniciados.", flush=True)
        yield
    except Exception as e:
        print(f"[ERRO] Erro ao iniciar agentes: {e}", flush=True)
        raise
    finally:
        print("[DEBUG] Encerrando agentes...", flush=True)
        await user_agent.stop()
        await dialogue_agent.stop()
        await llm_agent.stop()
        await emotion_agent.stop()
        await memory_agent.stop()
        await summarizer_agent.stop()
        print("[FastAPI] Agentes terminados.", flush=True)

        # Desconectar do Postgres
        print("[FastAPI] A desconectar do PostgreSQL...", flush=True)
        await database.disconnect()

# Criar app com lifespan
app = FastAPI(lifespan=lifespan)

# Ativar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou coloca o URL do teu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis de ambiente
ui_jid = os.getenv("USER_AGENT_JID")
ui_pwd = os.getenv("USER_AGENT_PASSWORD")
dlg_jid = os.getenv("DIALOGUE_AGENT_JID")
dlg_pwd = os.getenv("DIALOGUE_AGENT_PASSWORD")
llm_jid = os.getenv("LLM_AGENT_JID")
llm_pwd = os.getenv("LLM_AGENT_PASSWORD")
emotion_jid = os.getenv("EMOTION_AGENT_JID")
emotion_pwd = os.getenv("EMOTION_AGENT_PASSWORD")
memory_jid = os.getenv("MEMORY_AGENT_JID")
memory_pwd = os.getenv("MEMORY_AGENT_PASSWORD")
summarizer_jid = os.getenv("SUMMARIZER_AGENT_JID")
summarizer_pwd = os.getenv("SUMMARIZER_AGENT_PASSWORD")
feedback_jid = os.getenv("FEEDBACK_AGENT_JID")
feedback_pwd = os.getenv("FEEDBACK_AGENT_PASSWORD")
classify_jid = os.getenv("CLASSIFY_AGENT_JID")
classify_pwd = os.getenv("CLASSIFY_AGENT_PASSWORD")



# Instanciar agentes
user_agent = UserInterfaceAgent(ui_jid, ui_pwd, app)
dialogue_agent = DialogueManagerAgent(dlg_jid, dlg_pwd)
llm_agent = LLMAgent(llm_jid, llm_pwd)
emotion_agent = EmotionAgent(emotion_jid, emotion_pwd)
memory_agent = MemoryAgent(memory_jid, memory_pwd)
summarizer_agent = SummarizerAgent(summarizer_jid, summarizer_pwd)
feedback_agent = FeedbackAgent(feedback_jid, feedback_pwd)
cycleClassifier_agent = CycleClassifierAgent(classify_jid, classify_pwd)


# Definir relações entre agentes
dialogue_agent.set("llm_contact", llm_jid)
dialogue_agent.set("user_interface_contact", ui_jid)
dialogue_agent.set("emotion_contact", emotion_jid)
dialogue_agent.set("memory_contact", memory_jid)
dialogue_agent.set("summarizer_contact", summarizer_jid)
dialogue_agent.set("feedback_contact", feedback_jid)
dialogue_agent.set("cycle_classifier_contact", classify_jid)

user_agent.set("dialogue_contact", dlg_jid)
llm_agent.set("dialogue_contact", dlg_jid)
emotion_agent.set("dialogue_contact", dlg_jid)
memory_agent.set("dialogue_contact", dlg_jid)
summarizer_agent.set("dialogue_contact", dlg_jid)
feedback_agent.set("dialogue_contact", dlg_jid)
cycleClassifier_agent.set("dialogue_contact", dlg_jid)

class ChatMessage(BaseModel):
    message: str
    subject: str

class FeedbackInput(BaseModel):
    memory_id: int
    feedback: str
    suggestion: Optional[str] = None

@app.post("/feedback")
async def receive_feedback(data: FeedbackInput, request: Request):
    try:
        feedback_behaviour = SendFeedbackToDialogueManagerBehaviour(
            dialogue_jid=dlg_jid,
            memory_id=data.memory_id,
            feedback=data.feedback,
            suggestion=data.suggestion,
        )
        dialogue_agent.add_behaviour(feedback_behaviour)

        return {"status": "ok"}

    except Exception as e:
        print("[/feedback] Erro:", str(e), flush=True)
        return {"status": "erro", "detalhe": str(e)}


@app.post("/chat/text")
async def chat_text(msg: ChatMessage):
    behaviour = user_agent.create_send_behaviour(msg.message,msg.subject)
    user_agent.add_behaviour(behaviour)
    return {"response": "Mensagem enviada para o sistema multiagente."}

# Endpoint SSE
@app.get("/events")
async def sse_endpoint(request: Request):
    queue = asyncio.Queue()
    app.state.sse_clients.append(queue)
    print("[SSE] Novo cliente conectado.")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    print("[SSE] Cliente desconectado.")
                    break

                data = await queue.get()
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.01)  # <--- ajuda a manter a ligação viva
        except asyncio.CancelledError:
            print("[SSE] Ligação cancelada.")
        finally:
            request.app.state.sse_clients.remove(queue)
            print("[SSE] Cliente removido.")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/stats")
async def get_stats():
    try:
        total_messages = await database.fetch_val("SELECT COUNT(*) FROM memory_messages")
        useful_feedback = await database.fetch_val("SELECT COUNT(*) FROM memory_messages WHERE feedback = 'useful'")
        not_useful_feedback = await database.fetch_val("SELECT COUNT(*) FROM memory_messages WHERE feedback = 'not_useful'")
        suggestions = await database.fetch_val("SELECT COUNT(*) FROM memory_messages WHERE user_suggestion IS NOT NULL")
        
        emotion_distribution = await database.fetch_all(
            "SELECT emotion, COUNT(*) as count FROM memory_messages GROUP BY emotion ORDER BY count DESC"
        )
        emotions = {record["emotion"]: record["count"] for record in emotion_distribution}
        
        messages_per_day = await database.fetch_all(
            "SELECT DATE(created_at) AS date, COUNT(*) AS count FROM memory_messages GROUP BY date ORDER BY date"
        )
        messages_by_day = [{"date": record["date"], "count": record["count"]} for record in messages_per_day]

        top_negative_responses = await database.fetch_all(
            "SELECT id, text, response, user_suggestion FROM memory_messages WHERE feedback = 'not_useful' ORDER BY id DESC LIMIT 5"
        )

        top_positive_responses = await database.fetch_all(
            "SELECT id, text, response FROM memory_messages WHERE feedback = 'useful' ORDER BY id DESC LIMIT 5"
        )

        avg_response_length = await database.fetch_val(
            "SELECT AVG(LENGTH(response) - LENGTH(REPLACE(response, ' ', '')) + 1) FROM memory_messages WHERE response IS NOT NULL"
        )

        # Novo: histórico das últimas 20 mensagens
        conversation_history = await database.fetch_all(
            "SELECT id, text, response, emotion, feedback, user_suggestion, cycle, created_at FROM memory_messages ORDER BY created_at DESC LIMIT 20"
        )
        conversation = [
            {
                "id": record["id"],
                "text": record["text"],
                "response": record["response"],
                "emotion": record["emotion"],
                "feedback": record["feedback"],
                "user_suggestion": record["user_suggestion"],
                "cycle": record["cycle"],
                "created_at": record["created_at"].isoformat()
            }
            for record in conversation_history
        ]

        return {
            "total_messages": total_messages,
            "useful_feedback": useful_feedback,
            "not_useful_feedback": not_useful_feedback,
            "suggestions": suggestions,
            "emotions": emotions,
            "messages_by_day": messages_by_day,
            "top_negative_responses": top_negative_responses,
            "top_positive_responses": top_positive_responses,
            "avg_response_length": avg_response_length,
            "conversation_history": conversation  # novo campo
        }
    except Exception as e:
        return JSONResponse(content={"status": "erro", "detalhe": str(e)}, status_code=500)

@app.websocket("/ws/speech")
async def websocket_speech(ws: WebSocket):
    await stream_google_transcription(ws)

# Lançar app
if __name__ == "__main__":
    print("[DEBUG] Lançando FastAPI com uvicorn...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
