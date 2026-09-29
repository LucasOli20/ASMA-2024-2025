from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
from classes.llmresponse import LLMResponse
import google.generativeai as genai
import os
import faiss
import json
from sentence_transformers import SentenceTransformer
import re

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

# Carregar modelo de embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Função de RAG: retorna textos relevantes com base no ciclo
def get_rag_context(question: str, cycle: str, subject: str = "historia", top_k: int = 3):
    cycle_map = {
        "1º ciclo": "1ciclo",
        "2º ciclo": "2ciclo",
        "3º ciclo": "3ciclo"
    }
    ciclo_file = cycle_map.get(cycle, "3ciclo")
    subject = subject.lower().strip().replace(" ", "_")

    index_path = f"docs/faiss/{subject}_{ciclo_file}.faiss"
    texts_path = f"docs/faiss/{subject}_{ciclo_file}_texts.json"

    if not os.path.exists(index_path) or not os.path.exists(texts_path):
        print(f"[LLMAgent] ⚠️ Ficheiros de RAG não encontrados para: {subject}_{ciclo_file}")
        return ""

    index = faiss.read_index(index_path)

    with open(texts_path, "r", encoding="utf-8") as f:
        texts = json.load(f)

    question_embedding = embedding_model.encode([question])
    D, I = index.search(question_embedding, top_k)
    retrieved_texts = [texts[i] for i in I[0] if i < len(texts)]

    return "\n\n".join(retrieved_texts)

def get_all_books_by_subject(subject: str):
    subject = subject.strip().lower().replace(" ", "_")
    json_path = f"docs/books/{subject}_books.json"

    if not os.path.exists(json_path):
        print(f"[LLMAgent] ⚠️ Ficheiro de livros não encontrado para: {subject}")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def filtrar_historico_por_subject(memory_historic: str, subject: str) -> str:
    subject = subject.strip().lower()
    linhas = memory_historic.strip().splitlines()

    padrao_subject = re.compile(r"^\[(.*?)\]\s*$")
    blocos_filtrados = []
    bloco_atual = []
    capturar_bloco = False

    for linha in linhas:
        linha_strip = linha.strip()
        match = padrao_subject.match(linha_strip.lower())

        if match:
            # Encontrou um novo subject
            disciplina = match.group(1).strip().lower()

            # Se estava a capturar e o subject mudou, fecha o bloco
            if bloco_atual:
                if capturar_bloco:
                    blocos_filtrados.append("\n".join(bloco_atual))
                bloco_atual = []

            # Decide se o novo bloco é para capturar ou não
            capturar_bloco = (disciplina == subject)
            bloco_atual = [linha] if capturar_bloco else []

        else:
            if capturar_bloco:
                bloco_atual.append(linha)

    # Último bloco, se for do subject certo
    if capturar_bloco and bloco_atual:
        blocos_filtrados.append("\n".join(bloco_atual))

    return "\n\n".join(blocos_filtrados).strip() or '""'


class CallGeminiBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print("[LLMAgent] Mensagem recebida.")
            performative = msg.get_metadata("performative")
            source = msg.get_metadata("source")

            if performative == "inform" and source == "dialogue_manager":
                try:
                    composed_data = jsonpickle.decode(msg.body)
                    purpose = msg.get_metadata("purpose")

                    if purpose == "final_prompt":  
                        memory_historic = composed_data.get("summary", "")
                        user_message = composed_data.get("user_message", None)
                        cycle = composed_data.get("cycle", None)
                        subject = composed_data.get("subject", None)

                        print(f"[LLMAgent] Dados recebidos: {user_message.text}, Ciclo: {cycle}, Subject: {subject}")

                        rag = True
                        filtered_memory = filtrar_historico_por_subject(memory_historic,subject)
                        print(f"filtered_memory{filtered_memory}")

                        first_interaction = filtered_memory.strip().strip('"') == ""

                        if rag:
                            rag_context = get_rag_context(user_message.text, cycle, subject=subject)
                            books = get_all_books_by_subject(subject)

                            book_context = ""
                            if books:
                                book_context = "**Lista de manuais escolares disponíveis para esta disciplina:**\n"
                                for book in books:
                                    book_context += (
                                        f"- Título: {book['title']}\n"
                                        f"  Autor: {book['author']}\n"
                                        f"  Link: {book['url']}\n"
                                    )
                                book_context += "\nPodes recomendar um destes manuais no campo `book` **apenas se for útil para o tema da pergunta do aluno.**\n"
                                
                            if first_interaction:
                                prompt = (
                                    f"Estás a desempenhar o papel de **MentorAI**, um assistente virtual educativo com personalidade próxima e humana. "
                                    f"És especializado em {subject} e conversas com alunos portugueses de forma descontraída e empática.\n\n"

                                    "**Instruções para esta primeira mensagem:**\n"
                                    "1. Dá uma resposta breve e natural à pergunta do aluno, mesmo que seja apenas um 'olá' ou 'tenho dúvidas'.\n"
                                    "2. Apresenta-te de forma muito curta. Diz apenas o teu nome (MentorAI) e que és especializado em {subject}.\n"
                                    "3. Não faças explicações nem sugerências nesta fase.\n"
                                    "4. Não menciones o ciclo escolar ainda, mesmo que já o saibas.\n"
                                    "5. Usa um tom adequado ao estado emocional do aluno: {user_message.emotion} — deixa que isso influencie o estilo da tua resposta, mas sem o referir diretamente.\n"
                                    "6. Fala sempre em **português de Portugal**, com linguagem simples e acessível.\n\n"

                                    f"📨 Pergunta do aluno:\n{user_message.text}\n\n"

                                    "✏️ Escreve agora a resposta. Sê simpático e breve. Responde ao aluno e apresenta-te de forma natural, sem formalidades."
                                )
                            else:
                                if subject and subject.lower().strip() == "matemática":
                                    prompt = (
                                        f"Estás a desempenhar o papel de **MentorAI**, um tutor dedicado de Matemática para o {cycle} em Portugal, com a missão de apoiar o aluno na compreensão profunda dos conceitos e na resolução de problemas de forma pedagógica e empática.\n"

                                        "**Contexto da conversa:**\n"
                                        f"- Histórico anterior com o aluno:\n{memory_historic}\n"
                                        f"- Estado emocional atual do aluno: {user_message.emotion}\n"
                                        f"- Contexto adicional retirado do manual:\n{rag_context}\n\n"
                                        f"{book_context}"

                                        f"O aluno colocou a seguinte questão:\n\"{user_message.text}\"\n\n"

                                        "Deves responder como um **tutor atento e experiente**, utilizando uma linguagem clara, acessível e adaptada à idade e nível do aluno, ajudando-o a perceber os **conceitos matemáticos**, **raciocínio lógico** e **etapas de resolução**.\n"

                                        "**Importante:**\n"
                                        "  - NÃO DIGAS OLÁ NEM FAÇAS NENHUMA SAUDAÇÃO. Como consegues ver pelo histórico de mensagens, ja fizeste isso anteriormente. Responde apenas a pergunta do Aluno..\n"
                                        "  - Não deves responder a nenhuma questão que não esteja relacionada com a disciplina de Matemática.\n"
                                        "  - Se o aluno fizer uma pergunta de outra disciplina, responde apenas no campo `full_answer` com algo como:\n"
                                        "    - \"Não tenho capacidade para responder a essa pergunta, pois sou professor de Matemática. Para esclarecer dúvidas de [disciplina], deves consultar o Mentor de [disciplina].\"\n\n"
                                        "  - Quero uma resposta rápida, quero o output o mais rápido possível, pois é uma conversa em tempo real.\n"

                                        "Tens acesso ao histórico da conversa e podes referir-te a perguntas anteriores, se for relevante para a explicação.\n\n"

                                        "**Formatação da resposta (`full_answer`):**\n"
                                        "  - Usa **negrito** com `**` para destacar **títulos curtos ou conceitos-chave**.\n"
                                        "  - Usa *itálico* com `*` para **realçar palavras importantes** dentro da explicação.\n"
                                        "  - Para listas com marcadores, começa cada ponto com `- `.\n"
                                        "  - Para listas numeradas, usa `1.`, `2.`, etc.\n"
                                        "  - Mantém a explicação organizada com parágrafos curtos e bem separados.\n\n"

                                        "Devolve a resposta **no seguinte formato JSON**:\n"
                                        "- `full_answer`: Uma explicação para a pergunta do aluno. Explica de forma clara e rigorosa em cerca de 1500 caracteres.\n"
                                        "- `steps`: uma lista de passos, onde cada passo contém:\n"
                                        "  - `title`: título do passo (ex: \"Aplicação da fórmula resolvente\")\n"
                                        "  - `explanation`: explicação em linguagem simples\n"
                                        "  - `formula` (opcional): fórmula relevante usada nesse passo\n"
                                        "  - `values` (opcional): dicionário de variáveis com os seus valores (ex: {\"a\": 2, \"b\": 4})\n"
                                        "- `book` (opcional): um manual escolar ou livro relevante, com título, autor e link público.\n\n"

                                        "**Se incluíres um livro**, deves seguir esta estrutura JSON no campo `book`:\n"
                                        "```json\n"
                                        "\"book\": {\n"
                                        "  \"title\": \"Título do manual ou livro\",\n"
                                        "  \"author\": \"Autor(es)\",\n"
                                        "  \"url\": \"https://www.exemplo.com/livro\"\n"
                                        "}\n"
                                        "```\n\n"

                                        "⚠️ O livro deve ser **real, relevante e acessível publicamente**. Evita links inválidos ou fontes pouco fiáveis. Se não houver um livro adequado, omite o campo `book`.\n\n"

                                        "⚠️ Apenas devolve o JSON com os campos `full_answer`, `steps` e (se aplicável) `book`. Não incluas nada fora do JSON."
                                    )
                                elif subject and subject.lower().strip() == "português":
                                    prompt = (
                                        f"Estás a desempenhar o papel de **MentorAI**, um tutor dedicado de Português para o {cycle} em Portugal. O teu objetivo principal é apoiar os alunos no seu percurso de aprendizagem da língua portuguesa, com explicações claras, correções cuidadosas e sugestões que os ajudem a melhorar gradualmente as suas competências.\n"

                                        "**Contexto da conversa:**\n"
                                        f"- Histórico anterior com o aluno:\n{memory_historic}\n"
                                        f"- Estado emocional atual do aluno: {user_message.emotion}\n"
                                        f"- Contexto adicional retirado do manual:\n{rag_context}\n\n"
                                        f"{book_context}"

                                        f"A mensagem do aluno é a seguinte:\n\"{user_message.text}\"\n\n"

                                        "Deves analisá-la cuidadosamente e devolver a resposta **neste formato JSON**, clara e estruturada, para que possa ser usada numa explicação interativa e visual no frontend.\n\n"

                                        "**Lógica de preenchimento:**\n"
                                        "- Se o aluno indicar explicitamente que quer correção ou análise do texto (por exemplo, usar termos como 'corrige', 'corrija' ou colocar o texto entre aspas), deves preencher **todos** os campos JSON: `full_answer`, `corrections`, `style_improvements`, `figures_of_speech` e `book`.\n"
                                        "- Caso contrário, deves devolver **apenas** o campo `full_answer` em JSON, com uma resposta completa e empática adaptada ao nível do aluno.\n"
                                        "- Nunca deves incluir recomendações de livros ou manuais no campo `full_answer`. Apenas o campo `book` pode conter essa informação.\n"
                                        "- Nunca digas que não podes escrever algo por ser longo demais. Divide a resposta em várias partes se for necessário, mas responde sempre de forma completa.\n\n"

                                        "**O teu objetivo, se e só se o aluno pedir, é:**\n"
                                        "1. Identificar e corrigir **erros ortográficos, gramaticais ou de pontuação**.\n"
                                        "2. Sugerir **melhorias de vocabulário e estilo**, como substituições por sinónimos ou construções mais ricas.\n"
                                        "3. Destacar e explicar eventuais **figuras de estilo ou recursos expressivos** usados (como metáforas, hipérboles, aliterações, etc).\n\n"

                                        "⚠️ Se algum dos blocos não se aplicar (por exemplo, se não houver figuras de estilo), devolve esse campo como uma lista vazia.\n"
                                        "⚠️ O campo `book` deve conter sempre título, autor e link (URL direto para consulta ou compra do livro).\n\n"

                                        "**Importante:**\n"
                                        "  - NÃO DIGAS OLÁ NEM FAÇAS NENHUMA SAUDAÇÃO. Como consegues ver pelo histórico de mensagens, ja fizeste isso anteriormente. Responde apenas a pergunta do Aluno..\n"
                                        "  - Não deves responder a nenhuma questão que não esteja relacionada com a disciplina de Português. Não confundas português com história!\n"
                                        "  - Se o aluno fizer uma pergunta de outra disciplina, responde apenas no campo `full_answer` com algo como:\n"
                                        "    - \"Não tenho capacidade para responder a essa pergunta, pois sou professor de Português. Para esclarecer dúvidas de [disciplina], deves consultar o Mentor de [disciplina].\"\n\n"
                                        "  - Quero uma resposta rápida, quero o output o mais rápido possível, pois é uma conversa em tempo real.\n"

                                        "**Formatação da resposta (`full_answer`):**\n"
                                        "  - Usa **negrito** com `**` para destacar **títulos curtos ou conceitos-chave**.\n"
                                        "  - Usa *itálico* com `*` para **realçar palavras importantes** dentro da explicação.\n"
                                        "  - Para listas com marcadores, começa cada ponto com `- `.\n"
                                        "  - Para listas numeradas, usa `1.`, `2.`, etc.\n"
                                        "  - Mantém a explicação organizada com parágrafos curtos e bem separados.\n\n"

                                        "Tens acesso ao histórico da conversa e podes referir-te a perguntas anteriores, se for relevante para a explicação.\n"

                                        "**Formato de resposta JSON:**\n"
                                        "```json\n"
                                        "{\n"
                                        "  \"full_answer\": \"...\",\n"
                                        "  \"corrections\": [\n"
                                        "    {\n"
                                        "      \"original\": \"Texto com erro\",\n"
                                        "      \"corrected\": \"Texto corrigido\",\n"
                                        "      \"comment\": \"Explicação breve do erro\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"style_improvements\": [\n"
                                        "    {\n"
                                        "      \"original\": \"Texto simples\",\n"
                                        "      \"suggested\": \"Texto mais expressivo\",\n"
                                        "      \"comment\": \"Explicação da melhoria sugerida\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"figures_of_speech\": [\n"
                                        "    {\n"
                                        "      \"fragment\": \"Trecho da figura de estilo\",\n"
                                        "      \"type\": \"Tipo da figura (ex: metáfora)\",\n"
                                        "      \"comment\": \"Explicação em linguagem simples do recurso expressivo\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"book\": {\n"
                                        "    \"title\": \"Título do manual ou livro relevante\",\n"
                                        "    \"author\": \"Autor(es)\",\n"
                                        "    \"url\": \"https://www.exemplo.com/livro\"\n"
                                        "  }\n"
                                        "}\n"
                                        "```\n\n"

                                        "🧠 Relembra: responde apenas com o JSON acima. Todas as explicações devem estar em **português de Portugal** e adaptadas ao nível de um aluno do {cycle}."
                                    )
                                elif subject and subject.lower().strip() == "história":
                                    prompt = (
                                        f"Estás a desempenhar o papel de **MentorAI**, um tutor dedicado de História para o {cycle} em Portugal, cuja missão é orientar e educar os alunos de forma clara, rigorosa e empática. O teu objetivo é explicar os acontecimentos históricos de forma estruturada, estimulando o pensamento crítico e a compreensão profunda dos processos históricos.\n"

                                        
                                        "**Contexto da conversa:**\n"
                                        f"- Histórico anterior com o aluno:\n{memory_historic}\n"
                                        f"- Estado emocional atual do aluno: {user_message.emotion}\n"
                                        f"- Contexto adicional retirado do manual:\n{rag_context}\n\n"
                                        f"{book_context}"

                                        f"O aluno colocou a seguinte questão ou comentário:\n\"{user_message.text}\"\n\n"

                                        "Deves responder com uma explicação clara, empática e rigorosa, estruturada **num formato JSON**, para que possa ser utilizada numa animação interativa no frontend e auxiliar o aluno no seu processo de aprendizagem.\n"


                                        "**Lógica de resposta:**\n"
                                        "- Concentra-te sempre na pergunta ou comentário do aluno.\n"
                                        "- Tens acesso ao histórico da conversa e podes fazer referência a mensagens anteriores, se isso for útil para contextualizar ou esclarecer a resposta atual.\n"
                                        "- Só deves preencher os blocos de `timeline`, `cause_effect`, `figures` e `glossary` se fizerem realmente sentido para esclarecer a resposta.\n"
                                        "- Se não forem úteis ou relevantes para a pergunta do aluno, deves devolver esses campos como listas vazias.\n"
                                        "- O campo `book` também é opcional e só deve ser preenchido se tiveres um manual escolar ou livro relevante, real e publicamente acessível.\n\n"

                                        "**Importante:**\n"
                                        "  - NÃO DIGAS OLÁ NEM FAÇAS NENHUMA SAUDAÇÃO. Como consegues ver pelo histórico de mensagens, ja fizeste isso anteriormente. Responde apenas a pergunta do Aluno..\n"
                                        "  - Não deves responder a nenhuma questão que não esteja relacionada com a disciplina de História. Não confundas história com português!\n"
                                        "  - Se o aluno fizer uma pergunta de outra disciplina, responde apenas no campo `full_answer` com algo como:\n"
                                        "    - \"Não tenho capacidade para responder a essa pergunta, pois sou professor de História. Para esclarecer dúvidas de [disciplina], deves consultar o Mentor de [disciplina].\"\n\n"
                                        "  - Quero uma resposta rápida, quero o output o mais rápido possível, pois é uma conversa em tempo real.\n"

                                        "Tens acesso ao histórico da conversa e podes referir-te a perguntas anteriores, se for relevante para a explicação.\n"

                                        "**Formatação da resposta (`full_answer`):**\n"
                                        "  - Usa **negrito** com `**` para destacar **títulos curtos ou conceitos-chave**.\n"
                                        "  - Usa *itálico* com `*` para **realçar palavras importantes** dentro da explicação.\n"
                                        "  - Para listas com marcadores, começa cada ponto com `- `.\n"
                                        "  - Para listas numeradas, usa `1.`, `2.`, etc.\n"
                                        "  - Mantém a explicação organizada com parágrafos curtos e bem separados.\n\n"

                                        "**Formato de resposta JSON:**\n"
                                        "```json\n"
                                        "{\n"
                                        "  \"full_answer\": \"Uma explicação clara e rigorosa em cerca de 1500 caracteres.\",\n"
                                        "  \"timeline\": [\n"
                                        "    {\n"
                                        "      \"date\": \"DATA\",\n"
                                        "      \"event\": \"Nome do evento histórico\",\n"
                                        "      \"description\": \"Breve explicação acessível\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"cause_effect\": [\n"
                                        "    {\n"
                                        "      \"cause\": \"Fator que levou ao acontecimento\",\n"
                                        "      \"event\": \"Nome do acontecimento\",\n"
                                        "      \"consequence\": \"Impacto direto ou posterior\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"figures\": [\n"
                                        "    {\n"
                                        "      \"name\": \"Nome da figura histórica\",\n"
                                        "      \"biography\": \"Resumo breve da sua vida ou papel\",\n"
                                        "      \"importance\": \"Porque é relevante para este tema\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"glossary\": [\n"
                                        "    {\n"
                                        "      \"term\": \"Palavra ou conceito difícil\",\n"
                                        "      \"definition\": \"Definição simples e adaptada ao ciclo\"\n"
                                        "    }\n"
                                        "  ],\n"
                                        "  \"book\": {\n"
                                        "    \"title\": \"Título do manual ou livro relevante\",\n"
                                        "    \"author\": \"Autor(es)\",\n"
                                        "    \"url\": \"https://www.exemplo.com/livro\"\n"
                                        "  }\n"
                                        "}\n"
                                        "```\n\n"

                                        "🧠 Relembra: responde apenas com o JSON acima. Todas as explicações devem estar em **português de Portugal** e adaptadas ao nível de um aluno do {cycle}."
                                    )
                                else: 
                                    prompt = (
                                        f"Estás a desempenhar o papel de **MentorAI**, um professor especializado em {subject} do {cycle} em Portugal. "
                                        f"Estás a conversar com um aluno de forma empática, clara e próxima.\n\n"

                                        "**Instruções que deves seguir:**\n"
                                        "1. Não te apresentes nem cumprimentes novamente. Nem digas 'Olá' ou algo do género.\n"
                                        "2. Responde diretamente à pergunta do aluno, com base no histórico da conversa.\n"
                                        "3. Dá sempre contexto histórico relevante e adapta o vocabulário ao nível do {cycle}.\n"
                                        "4. Mantém um tom empático e acessível, como um professor atento ao bem-estar do aluno.\n"
                                        "5. Se fizer sentido, recomenda recursos úteis como manuais escolares, livros, filmes, documentários, vídeos educativos ou podcasts — qualquer material que ajude o aluno a compreender melhor o tema.\n"
                                        "6. Não inventes sugestões. Apenas recomenda materiais quando forem realmente úteis e relacionados com o tema da pergunta.\n"
                                        "7. Todas as respostas devem ser em **português de Portugal**.\n\n"

                                        f"📚 Contexto histórico (retirado do manual do {cycle}):\n{rag_context}\n\n"
                                        f"📜 Histórico da conversa até agora:\n{memory_historic}\n"
                                        f"🧠 Estado emocional atual do aluno: {user_message.emotion}\n\n"
                                        
                                        f"📨 Pergunta atual do aluno:\n{user_message.text}\n\n"

                                        "✏️ Responde agora de forma clara, útil e adaptada ao nível do aluno. Dá seguimento natural à conversa e inclui sugestões de materiais (livros, filmes, podcasts, etc.), **apenas se forem relevantes e ajudarem o aluno a aprofundar o tema**."
                                    )
                        response = model.generate_content(prompt)
                        raw_text = response.text.strip()

                        # Remover blocos de markdown (```json ... ```)
                        cleaned_text = re.sub(r"^```json\s*|```$", "", raw_text.strip(), flags=re.IGNORECASE)

                        if subject and (subject.lower().strip() == "matemática" or subject.lower().strip() == "português" or subject.lower().strip() == "história" ) and not first_interaction:
                            if not cleaned_text:
                                print("[LLMAgent] ⚠️ Resposta vazia recebida do modelo.")
                                content = {
                                    "error": "Resposta vazia recebida do modelo.",
                                    "raw": cleaned_text
                                }
                            else:
                                try:
                                    parsed = json.loads(cleaned_text)
                                    content = parsed
                                except Exception as e:
                                    print(f"[LLMAgent] Erro ao interpretar JSON de passos: {e}")
                                    content = {
                                        "error": f"Erro ao interpretar JSON com passo a passo: {str(e)}",
                                        "raw": cleaned_text
                                    }
                        else:
                            content = raw_text
                    elif purpose == "regenerate":
                        # Prompt já montado pelo FeedbackAgent
                        print("[LLMAgent] Regeneração de resposta com prompt refinado.")
                        refined_prompt = composed_data.get("prompt", "")

                        response = model.generate_content(refined_prompt)
                        content = response.text

                except Exception as e:
                    content = f"[ERRO Gemini] {str(e)}"
                    print(f"[LLMAgent] Erro ao gerar resposta: {e}")

                # Empacotar resposta
                llm_response = LLMResponse(content)
                response_msg = Message(to=self.agent.get("dialogue_contact"))
                response_msg.set_metadata("performative", "inform")
                response_msg.set_metadata("source", "llm_agent")
                response_msg.body = jsonpickle.encode(llm_response)

                await self.send(response_msg)
                print("[LLMAgent] Resposta enviada ao DialogueManager.")
