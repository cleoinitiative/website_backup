import React, { useState } from 'react';
import { Box, Typography, Paper, IconButton } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface Testimonial {
  quote: string;
  author: string;
  role: string;
  video: string;
}

const testimonials: Testimonial[] = [
  {
    quote: "A huge amount of fulfillment comes from being able to make such a positive impact on the lives of others.",
    author: "Chase Alley",
    role: "CLEO Student Leader",
    video: "/videos/testimonial1.mp4"
  },
  {
    quote: "The joy on my senior partner's face when she successfully made her first video call to her grandchildren was unforgettable. These moments remind me why CLEO is so important.",
    author: "Sarah Chen",
    role: "Chapter Leader",
    video: "/videos/testimonial2.mp4"
  },
  {
    quote: "Through CLEO, I've not only taught technology skills but also gained a mentor. The stories and wisdom shared during our sessions are just as valuable as the digital literacy we provide.",
    author: "Michael Rodriguez",
    role: "Student Volunteer",
    video: "/videos/testimonial3.mp4"
  },
  {
    quote: "Starting a CLEO chapter has created a bridge between generations. We're not just teaching technology; we're building meaningful connections that last.",
    author: "Emma Thompson",
    role: "Chapter Founder",
    video: "/videos/testimonial4.mp4"
  },
  {
    quote: "What makes CLEO special is how it transforms both students and seniors. We come to teach but end up learning so much about life, resilience, and the power of human connection.",
    author: "David Park",
    role: "Student Leader",
    video: "/videos/testimonial5.mp4"
  },
  {
    quote: "The impact goes beyond technology. We're helping seniors stay connected with their loved ones and maintain their independence in an increasingly digital world.",
    author: "Sophia Martinez",
    role: "Chapter Leader",
    video: "/videos/testimonial6.mp4"
  },
  {
    quote: "Every week, I look forward to our CLEO sessions. Seeing our senior partners grow more confident with technology while sharing their incredible life stories is truly rewarding.",
    author: "James Wilson",
    role: "Student Volunteer",
    video: "/videos/testimonial7.mp4"
  },
  {
    quote: "CLEO has taught me that small actions can have a big impact. Helping a senior connect with family through video calls or navigate online services makes a real difference in their life.",
    author: "Olivia Chang",
    role: "Student Leader",
    video: "/videos/testimonial8.mp4"
  }
];

const TestimonialsCarousel: React.FC = () => {
  const [[page, direction], setPage] = useState([0, 0]);

  const paginate = (newDirection: number) => {
    const nextPage = page + newDirection;
    const totalTestimonials = testimonials.length;
    const wrappedPage = ((nextPage % totalTestimonials) + totalTestimonials) % totalTestimonials;
    setPage([wrappedPage, newDirection]);
  };

  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 500 : -500,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 500 : -500,
      opacity: 0
    })
  };

  const currentIndex = ((page % testimonials.length) + testimonials.length) % testimonials.length;
  const currentTestimonial = testimonials[currentIndex];

  return (
    <Box sx={{ position: 'relative', height: '500px', overflow: 'hidden' }}>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'hidden',
        }}
      >
        <video
          autoPlay
          muted
          loop
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.3,
          }}
          src={currentTestimonial.video}
        />
      </Box>

      <Box
        sx={{
          position: 'relative',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <IconButton
          onClick={() => paginate(-1)}
          sx={{
            position: 'absolute',
            left: 20,
            color: 'white',
            backgroundColor: 'rgba(255,255,255,0.1)',
            zIndex: 10,
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.2)',
            }
          }}
        >
          <ArrowBackIcon />
        </IconButton>

        <AnimatePresence initial={false} custom={direction} mode="wait">
          <motion.div
            key={page}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{
              x: { type: "spring", stiffness: 400, damping: 35 },
              opacity: { duration: 0.15 }
            }}
          >
            <Paper
              sx={{
                p: 6,
                maxWidth: '800px',
                mx: 'auto',
                textAlign: 'center',
                bgcolor: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                borderRadius: '20px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
              }}
            >
              <Typography
                variant="h4"
                component="blockquote"
                sx={{
                  fontStyle: 'italic',
                  mb: 3,
                }}
              >
                "{currentTestimonial.quote}"
              </Typography>
              <Typography variant="h6">
                {currentTestimonial.author}
              </Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.7 }}>
                {currentTestimonial.role}
              </Typography>
            </Paper>
          </motion.div>
        </AnimatePresence>

        <IconButton
          onClick={() => paginate(1)}
          sx={{
            position: 'absolute',
            right: 20,
            color: 'white',
            backgroundColor: 'rgba(255,255,255,0.1)',
            zIndex: 10,
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.2)',
            }
          }}
        >
          <ArrowForwardIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default TestimonialsCarousel; 