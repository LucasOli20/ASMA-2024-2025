// Message type for chat messages
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  isFeedbackPrompt?: boolean;
  memoryId?: number;
}

export type Subject = 'história' | 'português' | 'matemática';