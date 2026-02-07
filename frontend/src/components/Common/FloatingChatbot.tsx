'use client';

import { useState, useRef, useEffect } from 'react';
import { FiHeadphones, FiX, FiSend, FiUser } from 'react-icons/fi';
import { FaRobot } from 'react-icons/fa';
import { useAuth } from '@/app/context/auth'; // Import the auth context

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const FloatingChatbot = () => {
  const { token: authToken } = useAuth(); // Get the token from auth context
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');

    // Show typing indicator
    setIsTyping(true);

    try {
      // Use the auth token from the context
      const token = authToken;

      // Check if token exists before including in headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token && token !== 'null' && token !== 'undefined') {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        // If no token, show error message to user
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'Please log in to use the chatbot.',
          sender: 'bot',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        setIsTyping(false);
        return;
      }

      // Send the message to the backend API
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://rimshaarshad-todo-app.hf.space';
      const response = await fetch(`${apiUrl}/chat/message`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: inputValue,
          session_id: localStorage.getItem('chat_session_id') || null, // Use existing session or create new
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle authentication error specifically
          const errorData = await response.json();
          throw new Error(`Authentication error: ${errorData.detail || 'Unauthorized'}`);
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const data = await response.json();

      // Store the session ID for future messages
      if (data.session_id) {
        localStorage.setItem('chat_session_id', data.session_id);
      }

      // Add bot response
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || 'Sorry, I encountered an error processing your request.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botResponse]);

      // Dispatch events to update UI if the response indicates a task operation
      if (data.task_id || data.response.toLowerCase().includes('task')) {
        // Dispatch task-updated event to refresh task lists and stats
        window.dispatchEvent(new CustomEvent('task-updated'));

        // Create and dispatch activity event for recent activity updates
        let activityType = 'task_updated';
        let activityMessage = '';

        const lowerResponse = data.response.toLowerCase();

        if (lowerResponse.includes('completed') || lowerResponse.includes('done')) {
          activityType = 'task_completed';
          activityMessage = `Task was marked as completed`;
        } else if (lowerResponse.includes('incomplete') || lowerResponse.includes('not done')) {
          activityType = 'task_uncompleted';
          activityMessage = `Task was marked as incomplete`;
        } else if (lowerResponse.includes('delete') || data.response_type === 'task_deleted') {
          activityType = 'task_deleted';
          activityMessage = `Task was deleted`;
        } else if (lowerResponse.includes('create') || data.response_type === 'success') {
          activityType = 'task_updated'; // Could be task_created, but using updated as general
          activityMessage = `Task was updated`;
        } else {
          activityMessage = `Task was updated`;
        }

        const activity = {
          id: `act-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: activityType,
          taskId: data.task_id || 'unknown',
          taskTitle: data.task_title || 'Task',
          userId: authToken,
          timestamp: new Date().toISOString(),
          message: activityMessage
        };

        window.dispatchEvent(new CustomEvent('task-activity', { detail: activity }));
      }
    } catch (error) {
      console.error('Error sending message to chatbot:', error);

      // Check if it's an authentication error
      let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';

      if (error instanceof Error) {
        if (error.message.includes('Authentication error') || error.message.includes('Unauthorized')) {
          errorMessageText = 'Authentication required. Please log in and try again.';
        } else if (error.message.includes('fetch')) {
          errorMessageText = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('HTTP error')) {
          errorMessageText = 'Server error. Please try again later.';
        }
      }

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: errorMessageText,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <>
      {/* Floating Chatbot Button */}
      {!isOpen && (
        <div className="fixed bottom-8 right-8 z-50">
          <div className="relative">
            {/* Circular moving animation */}
            <div className="absolute -inset-1 rounded-full bg-white opacity-50"></div>
            <button
              onClick={toggleChat}
              className="relative w-14 h-14 lg:w-16 lg:h-16 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 cursor-pointer border-2 border-white"
              style={{
                background: 'linear-gradient(135deg, #6B46C1 0%, #EC4899 100%)',
                boxShadow: '0 4px 20px rgba(107, 70, 193, 0.4)',
              }}
              aria-label="Open chatbot"
            >
              <FaRobot className="text-white text-[1.5rem] animate-pulse" />
            </button>
          </div>
        </div>
      )}

      {/* Chatbot Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-md h-[500px] flex flex-col bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
          {/* Header */}
          <div
            className="flex items-center justify-between px-4 py-3"
            style={{ background: 'linear-gradient(135deg, #6B46C1 0%, #EC4899 100%)' }}
          >
            <div className="flex items-center space-x-2">
              <FaRobot className="text-white text-lg" />
              <span className="text-white font-semibold">Chatbot</span>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:bg-white/20 rounded-full p-1 transition-colors"
              aria-label="Close chat"
            >
              <FiX className="text-lg" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${
                      message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}
                  >
                    <div
                      className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        message.sender === 'user'
                          ? 'bg-indigo-500 text-white'
                          : 'bg-purple-500 text-white'
                      }`}
                    >
                      {message.sender === 'user' ? (
                        <FiUser className="text-sm" />
                      ) : (
                        <FaRobot className="text-sm" />
                      )}
                    </div>
                    <div
                      className={`px-4 py-2 rounded-2xl ${
                        message.sender === 'user'
                          ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                          : 'bg-white text-gray-800 border border-gray-200'
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-purple-500 text-white">
                      <FaRobot className="text-sm" />
                    </div>
                    <div className="px-4 py-2 rounded-2xl bg-white text-gray-800 border border-gray-200">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-3 bg-white">
            <div className="flex items-center space-x-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type here..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows={1}
                style={{ minHeight: '40px', maxHeight: '80px' }}
              />
              <button
                onClick={handleSendMessage}
                disabled={inputValue.trim() === ''}
                className={`p-2 rounded-lg flex items-center justify-center ${
                  inputValue.trim() === ''
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:opacity-90'
                }`}
                aria-label="Send message"
              >
                <FiSend className="text-lg" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Backdrop when chat is open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40"
          onClick={handleClose}
          aria-hidden="true"
        />
      )}
    </>
  );
};

export default FloatingChatbot;