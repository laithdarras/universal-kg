import React, { useState } from "react";
import { api, QAResponse } from "../lib/api";

interface QAPanelProps {
  onAnswerReceived: (citedNodes: string[], citedEdges: string[]) => void;
}

export const QAPanel: React.FC<QAPanelProps> = ({ onAnswerReceived }) => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<QAResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.qa(question);
      setAnswer(response);
      onAnswerReceived(response.cited_nodes, response.cited_edges);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get answer");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h2 className="text-xl font-bold text-white mb-4">Ask Questions</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Question
          </label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What is artificial intelligence?"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
            onKeyPress={(e) => e.key === "Enter" && handleAskQuestion()}
          />
        </div>

        <button
          onClick={handleAskQuestion}
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Asking...
            </>
          ) : (
            "Ask"
          )}
        </button>

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-2 rounded">
            {error}
          </div>
        )}

        {answer && (
          <div className="bg-gray-700 p-3 rounded-md">
            <h3 className="text-sm font-medium text-gray-300 mb-2">Answer:</h3>
            <p className="text-white text-sm">{answer.answer}</p>

            {answer.cited_nodes.length > 0 && (
              <div className="mt-2">
                <span className="text-xs text-gray-400">Cited nodes: </span>
                <span className="text-xs text-blue-400">
                  {answer.cited_nodes.length}
                </span>
              </div>
            )}

            {answer.cited_edges.length > 0 && (
              <div>
                <span className="text-xs text-gray-400">Cited edges: </span>
                <span className="text-xs text-red-400">
                  {answer.cited_edges.length}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
