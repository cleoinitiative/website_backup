import * as React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme, responsiveFontSizes } from '@mui/material/styles';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Contact';
import News from './pages/News';
import { AnimatePresence } from 'framer-motion';
import emailjs from '@emailjs/browser';
import GetStarted from './pages/GetStarted';
import Testimonials from './pages/Testimonials';
import FAQ from './components/FAQ';
import { Chatbot } from './components/Chatbot';
import { useEffect } from 'react';

declare module '@mui/material/styles' {
  interface Theme {
    status: {
      danger: string;
    };
  }
  interface ThemeOptions {
    status?: {
      danger?: string;
    };
  }
}

let theme = createTheme({
  palette: {
    primary: {
      main: '#0a4b78',
      light: '#3c7ab0',
      dark: '#002546',
    },
    secondary: {
      main: '#ffffff',
    },
    background: {
      default: '#000000',
      paper: 'rgba(255, 255, 255, 0.9)',
    },
    text: {
      primary: '#ffffff',
      secondary: '#000000',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2rem',
      fontWeight: 700,
      color: '#ffffff',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '1.75rem',
      fontWeight: 600,
      color: '#ffffff',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'transparent',
          boxShadow: 'none',
        },
      },
    },
  },
  status: {
    danger: '#e53e3e',
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
});

theme = responsiveFontSizes(theme);

const App: React.FC = () => {
  useEffect(() => {
    emailjs.init("jnT6XaLdydE07qf8-");
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/news" element={<News />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/get-started" element={<GetStarted />} />
          <Route path="/testimonials" element={<Testimonials />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/donate" element={<Home />} />
        </Routes>
      </AnimatePresence>
      <Chatbot />
    </ThemeProvider>
  );
};

export default App; 