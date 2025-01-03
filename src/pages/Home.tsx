import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Paper,
  useTheme,
  useMediaQuery,
  Modal,
  IconButton,
} from '@mui/material';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import ParticleBackground from '../components/ParticleBackground';
import CloseIcon from '@mui/icons-material/Close';

const Home: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down(1200));
  const [thankYouOpen, setThankYouOpen] = useState(false);

  const openDonateWindow = () => {
    // Show thank you modal immediately
    setThankYouOpen(true);
    
    // Open PayPal window
    const width = 450;
    const height = 600;
    const left = (window.innerWidth - width) / 2 + window.screenX;
    const top = (window.innerHeight - height) / 2 + window.screenY;
    
    const popup = window.open(
      'https://www.paypal.com/donate/?hosted_button_id=BTWBAKTQS265S',
      'PayPalDonate',
      `popup=yes,width=${width},height=${height},left=${left},top=${top}`
    );

    if (popup) popup.focus();
  };

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

          {/* Hero Section with Background Image */}
          <Box
            sx={{
              position: 'relative',
              minHeight: { xs: '60vh', md: '80vh' },
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage: 'url(/images/home/home1.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'right center',
                opacity: 0.9,
                maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)',
                WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)',
                zIndex: 0,
              }
            }}
          >
            <Container 
              maxWidth="lg" 
              sx={{ 
                position: 'relative',
                zIndex: 2,
                textAlign: 'center',
                py: { xs: 2, sm: 6, md: 8 },
                px: { xs: 2, sm: 4, md: 6 },
              }}
            >
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.3 }}
                >
                  <Typography 
                    variant="h1" 
                    sx={{
                      fontSize: { 
                        xs: '2rem',
                        sm: '3rem',
                        md: '4.5rem' 
                      },
                      fontWeight: 700,
                      letterSpacing: { xs: '-0.01em', md: '-0.02em' },
                      lineHeight: { xs: 1.2, md: 1.2 },
                      mb: { xs: 2, sm: 3, md: 4 },
                      textAlign: 'center',
                      background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.5))',
                    }}
                  >
                    Empowering Seniors Through Technology
                  </Typography>

                  <Typography 
                    variant="h5" 
                    sx={{ 
                      mb: { xs: 4, sm: 6 },
                      opacity: 0.9,
                      maxWidth: '800px',
                      margin: '0 auto',
                      lineHeight: { xs: 1.4, md: 1.6 },
                      textAlign: 'center',
                      fontSize: { xs: '1.1rem', md: '1.5rem' },
                      color: 'white',
                      textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                      display: { xs: 'none', sm: 'block' }
                    }}
                  >
                    Technology is rapidly changing and it can be overwhelming for seniors who are not familiar with it.
                    Our mission is to establish a community around providing access to technology and improving the quality 
                    of life for seniors who lack digital literacy skills.
                  </Typography>

                  <Typography 
                    variant="h5" 
                    sx={{ 
                      mb: 4,
                      opacity: 0.9,
                      maxWidth: '800px',
                      margin: '0 auto',
                      lineHeight: 1.4,
                      textAlign: 'center',
                      fontSize: '1.1rem',
                      color: 'white',
                      textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                      display: { xs: 'block', sm: 'none' }
                    }}
                  >
                    Helping seniors navigate the digital world through student-led technology education.
                  </Typography>
                </motion.div>

                <Box sx={{ textAlign: 'center' }}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      variant="contained"
                      component={Link}
                      to="/get-started"
                      size="large"
                      sx={{
                        mt: 4,
                        mb: 0,
                        px: 6,
                        py: 2,
                        borderRadius: '50px',
                        fontSize: '1.2rem',
                        background: 'rgba(255,255,255,0.1)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'rgba(255,255,255,0.2)',
                          transform: 'translateY(-2px)',
                        },
                        color: 'white',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                      }}
                    >
                      Join CLEO Today
                    </Button>
                  </motion.div>

                  {/* Show Donate Button below 1200px */}
                  {isMobile && (
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        variant="contained"
                        onClick={openDonateWindow}
                        size="large"
                        sx={{
                          mt: 2,
                          mb: 0,
                          px: 6,
                          py: 2,
                          borderRadius: '50px',
                          fontSize: '1.2rem',
                          background: 'rgba(255,255,255,0.1)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            background: 'rgba(255,255,255,0.2)',
                            transform: 'translateY(-2px)',
                          },
                          color: 'white',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        }}
                      >
                        Donate Now
                      </Button>
                    </motion.div>
                  )}
                </Box>
              </motion.div>
            </Container>
          </Box>

          {/* Content Cards Section */}
          <Container maxWidth="lg" sx={{ 
            py: { xs: 2, sm: 3, md: 4 },
            position: 'relative',
            zIndex: 1,
            width: '95%',
            mt: isMobile ? 0 : { xs: -4, sm: -6, md: -8 },
            mb: isMobile ? 16 : { xs: 8, sm: 10, md: 12 }
          }}>
            <Grid container spacing={{ xs: 2, sm: 3, md: 8 }}>
              {!isMobile && (
                <Grid item xs={12} md={6} sx={{ display: 'flex' }}>
                  <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    style={{ width: '100%' }}
                  >
                    <Paper 
                      elevation={0}
                      sx={{ 
                        p: { xs: 4, sm: 6, md: 8 },
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        background: 'rgba(255,255,255,0.08)',
                        backdropFilter: 'blur(10px)',
                        WebkitBackdropFilter: 'blur(10px)',
                        borderRadius: { xs: '20px', sm: '30px' },
                        transition: 'all 0.4s ease',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                        '&:hover': {
                          transform: 'translateY(-5px)',
                          background: 'rgba(255,255,255,0.12)',
                          boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.45)',
                        }
                      }}
                    >
                      <Box sx={{ mb: { xs: 2, sm: 3, md: 4 } }}>
                        <Typography 
                          variant="h3" 
                          gutterBottom
                          sx={{
                            fontSize: { xs: '2rem', md: '2.5rem' },
                            fontWeight: 700,
                            lineHeight: 1.2,
                            mb: { xs: 2, sm: 3 },
                            background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                          }}
                        >
                          Join the CLEO initiative today!
                        </Typography>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            fontSize: '1.1rem',
                            lineHeight: 1.7,
                            opacity: 0.9,
                            mb: { xs: 3, sm: 4, md: 6 }
                          }}
                        >
                          The CLEO initiative has chapters all over the United States. Join us today and make your 
                          impact on the seniors in your community.
                        </Typography>
                      </Box>
                      <Box sx={{ mt: 'auto' }}>
                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          <Button
                            variant="contained"
                            component={Link}
                            to="/get-started"
                            size="large"
                            sx={{
                              borderRadius: '50px',
                              px: 6,
                              py: 2,
                              fontSize: '1.1rem',
                              fontWeight: 500,
                              background: 'rgba(255,255,255,0.15)',
                              backdropFilter: 'blur(10px)',
                              '&:hover': {
                                background: 'rgba(255,255,255,0.25)',
                              }
                            }}
                          >
                            Get Started
                          </Button>
                        </motion.div>
                      </Box>
                    </Paper>
                  </motion.div>
                </Grid>
              )}

              <Grid item xs={12} md={isMobile ? 12 : 6} sx={{ display: 'flex' }}>
                <motion.div
                  initial={{ opacity: 0, x: isMobile ? 0 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                  style={{ width: '100%' }}
                >
                  <Paper 
                    elevation={0}
                    sx={{ 
                      p: { xs: 4, sm: 6, md: 8 },
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      background: 'rgba(255,255,255,0.08)',
                      backdropFilter: 'blur(10px)',
                      WebkitBackdropFilter: 'blur(10px)',
                      borderRadius: { xs: '20px', sm: '30px' },
                      transition: 'all 0.4s ease',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                      '&:hover': {
                        transform: 'translateY(-5px)',
                        background: 'rgba(255,255,255,0.12)',
                        boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.45)',
                      }
                    }}
                  >
                    <Box sx={{ mb: { xs: 2, sm: 3, md: 4 } }}>
                      <Typography 
                        variant="h3" 
                        gutterBottom
                        sx={{
                          fontSize: { xs: '2rem', md: '2.5rem' },
                          fontWeight: 700,
                          lineHeight: 1.2,
                          mb: { xs: 2, sm: 3 },
                          background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        Want to see our projects?
                      </Typography>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontSize: '1.1rem',
                          lineHeight: 1.7,
                          opacity: 0.9,
                          mb: { xs: 3, sm: 4, md: 6 }
                        }}
                      >
                        Click below to see information about our chapters and learn more about our organization
                      </Typography>
                    </Box>
                    <Box sx={{ mt: 'auto' }}>
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                          variant="contained"
                          component={Link}
                          to="/about"
                          size="large"
                          sx={{
                            borderRadius: '50px',
                            px: 6,
                            py: 2,
                            fontSize: '1.1rem',
                            fontWeight: 500,
                            background: 'rgba(255,255,255,0.15)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                              background: 'rgba(255,255,255,0.25)',
                            }
                          }}
                        >
                          Learn More
                        </Button>
                      </motion.div>
                    </Box>
                  </Paper>
                </motion.div>
              </Grid>
            </Grid>
          </Container>

          {/* Bottom Image Section */}
          <Box
            sx={{
              position: 'relative',
              width: '100%',
              height: '400px',
              mt: -12,
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage: 'url(/images/home/home2.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'top center',
                opacity: 0.3,
                maskImage: 'linear-gradient(to top, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 30%, rgba(0,0,0,0.8) 80%, rgba(0,0,0,0) 100%)',
                WebkitMaskImage: 'linear-gradient(to top, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 30%, rgba(0,0,0,0.8) 80%, rgba(0,0,0,0) 100%)',
                zIndex: 0,
              }
            }}
          >
            <Container 
              maxWidth="lg" 
              sx={{ 
                position: 'relative', 
                zIndex: 1, 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Box
                component={Link}
                to="/testimonials"
                sx={{
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'transform 0.3s ease',
                  display: 'block',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                  }
                }}
              >
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8 }}
                >
                  <Typography 
                    variant="h4" 
                    component="blockquote" 
                    sx={{ 
                      textAlign: 'center',
                      fontStyle: 'italic',
                      maxWidth: '800px',
                      mx: 'auto',
                      px: 4,
                    }}
                  >
                    "A huge amount of fulfillment comes from being able to make such a positive impact on the lives of others."
                  </Typography>
                  <Typography 
                    variant="subtitle1"
                    sx={{
                      textAlign: 'center',
                      mt: 2,
                      opacity: 0.8,
                    }}
                  >
                    — Chase Alley, Senior from Canterbury School
                  </Typography>
                  <Typography 
                    variant="body2"
                    sx={{
                      textAlign: 'center',
                      mt: 2,
                      opacity: 0.6,
                      fontStyle: 'italic',
                    }}
                  >
                    Click to see more testimonials →
                  </Typography>
                </motion.div>
              </Box>
            </Container>
          </Box>

          {/* FAQ Link Section */}
          <Container maxWidth="lg" sx={{ 
            textAlign: 'center', 
            py: { xs: 4, sm: 6, md: 8 },
            position: 'relative', 
            zIndex: 1,
            display: 'flex',
            justifyContent: 'center',
            px: 2
          }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              style={{ display: 'flex', justifyContent: 'center' }}
            >
              <Box
                component={Link}
                to="/faq"
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  textDecoration: 'none',
                  color: 'white',
                  background: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  padding: { xs: '12px 24px', sm: '16px 32px' },
                  borderRadius: { xs: '25px', sm: '50px' },
                  transition: 'all 0.3s ease',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  width: { xs: '280px', sm: '400px' },
                  '&:hover': {
                    background: 'rgba(255,255,255,0.2)',
                    transform: 'translateY(-2px)',
                  }
                }}
              >
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontSize: { xs: '0.9rem', sm: '1.1rem' },
                    whiteSpace: 'nowrap',
                    textAlign: 'center'
                  }}
                >
                  Have questions? Check out our FAQ →
                </Typography>
              </Box>
            </motion.div>
          </Container>

          {/* Footer */}
          <Box sx={{ textAlign: 'center', mt: 4, mb: 6 }}>
            <Typography variant="h6" gutterBottom sx={{ opacity: 0.9 }}>
              The CLEO Initiative
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              contact@cleoinitiative.org
            </Typography>
          </Box>
        </Box>
      </Box>

      <Modal
        open={thankYouOpen}
        onClose={() => setThankYouOpen(false)}
        aria-labelledby="thank-you-modal"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box
          sx={{
            position: 'relative',
            borderRadius: 3,
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            p: 4,
            width: '90%',
            maxWidth: '500px',
            textAlign: 'center',
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.18)',
          }}
        >
          <IconButton
            aria-label="close"
            onClick={() => setThankYouOpen(false)}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: '#0a4b78',
              '&:hover': {
                background: 'rgba(10, 75, 120, 0.1)',
              }
            }}
          >
            <CloseIcon />
          </IconButton>

          <Box sx={{ mt: 1 }}>
            <Typography
              variant="h4"
              component="h2"
              sx={{
                mb: 3,
                color: '#0a4b78',
                fontWeight: 700,
                background: 'linear-gradient(45deg, #0a4b78 30%, #0d6ebd 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Thank You for Your Generosity!
            </Typography>

            <Typography variant="h6" sx={{ mb: 3, color: '#2c3e50', fontWeight: 500 }}>
              Your support means the world to us and the seniors we serve.
            </Typography>

            

            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                variant="contained"
                onClick={() => setThankYouOpen(false)}
                sx={{
                  background: 'linear-gradient(45deg, #0a4b78 30%, #0d6ebd 90%)',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontSize: '1.1rem',
                  boxShadow: '0 3px 5px 2px rgba(10, 75, 120, .3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #083d61 30%, #0b5da1 90%)',
                  }
                }}
              >
                Return to Home
              </Button>
            </Box>
          </Box>
        </Box>
      </Modal>
    </>
  );
};

export default Home;