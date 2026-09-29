let eventSource: EventSource | null = null;

export const sendChatMessage = async (message: string, subject: string): Promise<string> => {
  try {
    const response = await fetch('http://localhost:8000/chat/text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, subject }),
    });

    if (!response.ok) {
      throw new Error(`Erro: ${response.status}`);
    }

    const data = await response.json();
    return data.response || 'Mensagem enviada, aguarde resposta...';
  } catch (error) {
    console.error('Erro em sendChatMessage:', error);
    throw error;
  }
};

export const sendFeedback = async (memoryId: number, feedback: string, suggestion?: string) => {
  const response = await fetch('http://localhost:8000/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      memory_id: memoryId, 
      feedback: feedback, 
      suggestion: suggestion || null,
    }),
  });

  if (!response.ok) {
    throw new Error('Erro ao enviar feedback');
  }
};

export const startSSEConnection = (onMessage: (data: string) => void) => {
  if (eventSource) return;

  eventSource = new EventSource('http://localhost:8000/sse');

  eventSource.onmessage = (event) => {
    onMessage(event.data);
  };

  eventSource.onerror = (error) => {
    console.error('Erro SSE:', error);
    eventSource?.close();
    eventSource = null;
  };
};

export const closeSSEConnection = () => {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
};

export const getStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/stats');
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching stats:', error);
    throw error;
  }
};