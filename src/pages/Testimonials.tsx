import React from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import { motion } from 'framer-motion';
import ParticleBackground from '../components/ParticleBackground';
import TestimonialsCarousel from '../components/TestimonialsCarousel';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Link } from 'react-router-dom';

const Testimonials: React.FC = () => {
  return (
    <>
      {/* Dark box behind header */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '100px',
          bgcolor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 1,
        }}
      />

      {/* Main content wrapper */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, #0a4b78 0%, #001529 100%)',
          overflowY: 'auto',
          pt: '100px',
        }}
      >
        <Box
          sx={{
            position: 'relative',
            minHeight: '100%',
            color: 'white',
          }}
        >
          <ParticleBackground />

          <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, pt: 8 }}>
            <Box sx={{ mb: 4 }}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Button
                  component={Link}
                  to="/"
                  startIcon={<ArrowBackIcon />}
                  sx={{
                    color: 'white',
                    fontSize: '1.1rem',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }
                  }}
                >
                  Back to Home
                </Button>
              </motion.div>
            </Box>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Typography 
                variant="h1" 
                sx={{
                  fontSize: { xs: '2.5rem', md: '4rem' },
                  fontWeight: 700,
                  textAlign: 'center',
                  mb: 6,
                  background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Student Testimonials
              </Typography>

              <Box sx={{ mb: 8 }}>
                <TestimonialsCarousel />
              </Box>
            </motion.div>

            <Box sx={{ textAlign: 'center', mt: 12, mb: 6 }}>
              <Typography variant="h6" gutterBottom sx={{ opacity: 0.9 }}>
                The CLEO Initiative
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                contact@cleoinitiative.org
              </Typography>
            </Box>
          </Container>
        </Box>
      </Box>
    </>
  );
};

export default Testimonials; 