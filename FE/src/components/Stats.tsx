import React, { useEffect, useState } from 'react';
import { getStats } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { MessageSquare, ThumbsUp, ThumbsDown, Lightbulb, Brain, MessageCircle } from 'lucide-react';

interface MemoryMessage {
  id: number;
  text: string;
  response: string;
  emotion: string | null;
  feedback: string | null;
  user_suggestion: string | null;
  cycle: string | null;
  created_at: string;
}

interface StatsData {
  total_messages: number;
  useful_feedback: number;
  not_useful_feedback: number;
  suggestions: number;
  emotions: Record<string, number>;
  messages_by_day: Array<{ date: string; count: number }>;
  top_negative_responses: Array<{ id: number; text: string; response: string }>;
  top_positive_responses: Array<{ id: number; text: string; response: string }>;
  avg_response_length: number;
  conversation_history: MemoryMessage[]; // novo campo
}


const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const Stats: React.FC = () => {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error('Error loading stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center text-red-600 p-4">
        Erro ao carregar estatísticas
      </div>
    );
  }

  const emotionsData = Object.entries(stats.emotions).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard de Estatísticas</h1>
      
      {/* Cards de métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <MessageSquare className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total de Mensagens</p>
              <p className="text-2xl font-semibold text-gray-800">{stats.total_messages}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <ThumbsUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Feedbacks Positivos</p>
              <p className="text-2xl font-semibold text-gray-800">{stats.useful_feedback}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <ThumbsDown className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Feedbacks Negativos</p>
              <p className="text-2xl font-semibold text-gray-800">{stats.not_useful_feedback}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Lightbulb className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Sugestões Recebidas</p>
              <p className="text-2xl font-semibold text-gray-800">{stats.suggestions}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Mensagens por Dia */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Mensagens por Dia</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.messages_by_day}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#4F46E5" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distribuição de Emoções */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Distribuição de Emoções</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={emotionsData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {emotionsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Últimas Interações */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feedbacks Positivos */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Últimos Feedbacks Positivos</h2>
          <div className="space-y-4">
            {stats.top_positive_responses.map((item) => (
              <div key={item.id} className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Pergunta: {item.text}</p>
                <p className="text-sm text-gray-800">Resposta: {item.response}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Feedbacks Negativos */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Últimos Feedbacks Negativos</h2>
          <div className="space-y-4">
            {stats.top_negative_responses.map((item) => (
              <div key={item.id} className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Pergunta: {item.text}</p>
                <p className="text-sm text-gray-800">Resposta: {item.response}</p>
                <p className="text-sm text-gray-800">Resposta: {item.feedback}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Histórico de Conversa */}
        <div className="mt-10 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <MessageCircle className="h-5 w-5 text-blue-600" />
            Histórico da Conversa (últimos 20)
          </h2>
          <div className="divide-y divide-gray-200">
            {stats.conversation_history.map((msg) => (
              <div key={msg.id} className="py-4">
                <p className="text-sm text-gray-600 mb-1">
                  <span className="font-medium">[{new Date(msg.created_at).toLocaleString()}]</span> {msg.cycle && `(${msg.cycle})`}
                </p>
                <p className="text-gray-800"><strong>Pergunta:</strong> {msg.text}</p>
                <p className="text-gray-800"><strong>Resposta:</strong> {msg.response}</p>
                <div className="text-sm text-gray-500 mt-1 flex flex-wrap gap-4">
                  {msg.emotion && <span>Emoção: {msg.emotion}</span>}
                  {msg.feedback && <span>Feedback: {msg.feedback}</span>}
                  {msg.user_suggestion && <span>Sugestão: {msg.user_suggestion}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;