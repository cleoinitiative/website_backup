import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Fab,
  Zoom,
  Avatar,
  CircularProgress,
  Collapse,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Send as SendIcon,
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  QuestionAnswer as ChatIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Message type definition
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Suggested questions - tech help and CLEO info
const SUGGESTED_QUESTIONS = [
  "What is CLEO?",
  "How do I start a chapter?",
  "How do I make a video call?",
  "How do I stay safe online?",
];

// API URL - update this when deploying
const API_URL = import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:8000';

const Chatbot: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm here to help you with technology questions. Feel free to ask me anything about using your phone, computer, email, video calling, or staying safe online. What can I help you with today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message to the API
  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment, or ask a CLEO volunteer for help!",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  // Handle keyboard shortcuts (Enter to send, Shift+Enter for new line)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  // Handle suggested question click
  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  return (
    <>
      {/* Floating Action Button */}
      <Zoom in={!isOpen}>
        <Fab
          color="primary"
          aria-label="Open tech help chat"
          onClick={() => setIsOpen(true)}
          sx={{
            position: 'fixed',
            bottom: { xs: 16, sm: 24 },
            right: { xs: 16, sm: 24 },
            width: { xs: 56, sm: 64 },
            height: { xs: 56, sm: 64 },
            background: 'linear-gradient(135deg, #0a4b78 0%, #1976d2 100%)',
            boxShadow: '0 4px 20px rgba(10, 75, 120, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #083d61 0%, #1565c0 100%)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.3s ease',
            zIndex: 1000,
          }}
        >
          <ChatIcon sx={{ fontSize: { xs: 28, sm: 32 } }} />
        </Fab>
      </Zoom>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            style={{
              position: 'fixed',
              bottom: isMobile ? 0 : 24,
              right: isMobile ? 0 : 24,
              zIndex: 1001,
              width: isMobile ? '100%' : 400,
              height: isMobile ? '100%' : 600,
              maxHeight: isMobile ? '100%' : 'calc(100vh - 48px)',
            }}
          >
            <Paper
              elevation={8}
              sx={{
                width: '100%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: isMobile ? 0 : 3,
                overflow: 'hidden',
                background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  background: 'linear-gradient(135deg, #0a4b78 0%, #1976d2 100%)',
                  color: 'white',
                  p: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Avatar
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      width: 40,
                      height: 40,
                    }}
                  >
                    <BotIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                      Tech Help
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Ask me anything about technology
                    </Typography>
                  </Box>
                </Box>
                <IconButton
                  onClick={() => setIsOpen(false)}
                  sx={{ color: 'white' }}
                  aria-label="Close chat"
                >
                  <CloseIcon />
                </IconButton>
              </Box>

              {/* Messages Area */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                }}
              >
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                      gap: 1,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 36,
                        height: 36,
                        bgcolor: message.role === 'user' ? '#0a4b78' : '#e3f2fd',
                        color: message.role === 'user' ? 'white' : '#0a4b78',
                      }}
                    >
                      {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
                    </Avatar>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        maxWidth: '80%',
                        bgcolor: message.role === 'user' ? '#0a4b78' : '#f1f5f9',
                        color: message.role === 'user' ? 'white' : '#1e293b',
                        borderRadius: 2,
                        borderTopRightRadius: message.role === 'user' ? 0 : 16,
                        borderTopLeftRadius: message.role === 'user' ? 16 : 0,
                      }}
                    >
                      <Typography
                        variant="body1"
                        sx={{
                          fontSize: '1rem',
                          lineHeight: 1.6,
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {message.content}
                      </Typography>
                    </Paper>
                  </Box>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 36,
                        height: 36,
                        bgcolor: '#e3f2fd',
                        color: '#0a4b78',
                      }}
                    >
                      <BotIcon />
                    </Avatar>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        bgcolor: '#f1f5f9',
                        borderRadius: 2,
                        borderTopLeftRadius: 0,
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} sx={{ color: '#0a4b78' }} />
                        <Typography variant="body2" color="text.secondary">
                          Thinking...
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                )}

                <div ref={messagesEndRef} />
              </Box>

              {/* Suggested Questions */}
              <Collapse in={messages.length <= 1 && !isLoading}>
                <Box
                  sx={{
                    px: 2,
                    pb: 1,
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 1,
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      width: '100%',
                      color: 'text.secondary',
                      mb: 0.5,
                    }}
                  >
                    Try asking:
                  </Typography>
                  {SUGGESTED_QUESTIONS.map((question, index) => (
                    <Box
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      sx={{
                        px: 2,
                        py: 1,
                        bgcolor: '#e3f2fd',
                        borderRadius: 2,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          bgcolor: '#bbdefb',
                          transform: 'translateY(-1px)',
                        },
                      }}
                    >
                      <Typography variant="body2" sx={{ color: '#0a4b78' }}>
                        {question}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Collapse>

              {/* Input Area */}
              <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{
                  p: 2,
                  borderTop: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <TextField
                  fullWidth
                  placeholder="Type your question here..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isLoading}
                  variant="outlined"
                  size="medium"
                  multiline
                  maxRows={3}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 3,
                      fontSize: '1rem',
                      bgcolor: 'white',
                      '&:hover fieldset': {
                        borderColor: '#0a4b78',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#0a4b78',
                      },
                    },
                    '& .MuiInputBase-input': {
                      color: '#1e293b',
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: '#94a3b8',
                      opacity: 1,
                    },
                  }}
                  inputProps={{
                    'aria-label': 'Type your technology question',
                  }}
                />
                <IconButton
                  type="submit"
                  disabled={!inputValue.trim() || isLoading}
                  sx={{
                    bgcolor: '#0a4b78',
                    color: 'white',
                    width: 48,
                    height: 48,
                    '&:hover': {
                      bgcolor: '#083d61',
                    },
                    '&:disabled': {
                      bgcolor: '#e0e0e0',
                      color: '#9e9e9e',
                    },
                  }}
                  aria-label="Send message"
                >
                  <SendIcon />
                </IconButton>
              </Box>

              {/* Footer */}
              <Box
                sx={{
                  px: 2,
                  py: 1,
                  bgcolor: '#f8fafc',
                  borderTop: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: 'text.secondary',
                    display: 'block',
                    textAlign: 'center',
                  }}
                >
                  Powered by CLEO Initiative • For personalized help, contact a volunteer
                </Typography>
              </Box>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Chatbot;
