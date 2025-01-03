import React from 'react';
import { Box, Container, Typography, Paper, Button, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import ParticleBackground from '../components/ParticleBackground';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import GroupsIcon from '@mui/icons-material/Groups';
import SchoolIcon from '@mui/icons-material/School';
import { Link } from 'react-router-dom';

interface StepCard {
  title: string;
  description: string;
  image: string;
  buttonText: string;
  buttonLink: string;
  icon?: React.ReactNode;
}

const stepCards: StepCard[] = [
  {
    title: "1. Review Our Setup Guide",
    description: "Start by reviewing our comprehensive setup guide. This will walk you through everything you need to know about starting and running a successful CLEO chapter.",
    image: "/images/getstarted/guide.png",
    buttonText: "View Setup Guide",
    buttonLink: "https://docs.google.com/presentation/d/1ncAqalbP_F_OKU3bY0g-BCRDHubCecjs/edit?usp=drive_link&ouid=115576920875875729219&rtpof=true&sd=true"
  },
  {
    title: "2. Find Retirement Homes Near You",
    description: "Use our interactive map to locate retirement homes and senior living facilities in your area. These will be potential partners for your CLEO chapter.",
    image: "/images/getstarted/locations.png",
    buttonText: "Open Interactive Map",
    buttonLink: "https://www.google.com/maps/search/retirement+homes+near+me"
  },
  {
    title: "3. Build Your Team",
    description: "Gather interested students and find a faculty advisor who can support your chapter's activities. Having a dedicated team is crucial for success.",
    image: "",
    buttonText: "Learn More",
    buttonLink: "/about"
  },
  {
    title: "4. Join Our Community",
    description: "Become part of our nationwide network of students making a difference. We'll provide ongoing support and resources for your chapter.",
    image: "",
    buttonText: "Get Started",
    buttonLink: "/contact"
  }
];

const GetStarted: React.FC = () => {
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
          
          <Container 
            maxWidth="lg" 
            sx={{ 
              width: '95%',
              mx: 'auto',
            }}
          >
            {/* Hero Section */}
            <Box sx={{ textAlign: 'center', mb: 12, mt: 8 }}>
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
                    mb: 4,
                    background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Start Making a Difference
                </Typography>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    maxWidth: '800px',
                    mx: 'auto',
                    opacity: 0.9,
                    mb: 6,
                    lineHeight: 1.6
                  }}
                >
                  Follow these simple steps to establish your CLEO chapter and start helping seniors in your community.
                </Typography>
              </motion.div>
            </Box>

            {/* Setup Guide Section */}
            <Box sx={{ mb: 12 }}>
              <Paper
                sx={{
                  p: 6,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  WebkitBackdropFilter: 'blur(10px)',
                  borderRadius: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundImage: `url(${stepCards[0].image})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    opacity: 0.15,
                    zIndex: 0,
                  }
                }}
              >
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  <Typography variant="h4" gutterBottom>
                    1. Review Our Setup Guide
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      mb: 6,
                      fontSize: '1.1rem',
                      lineHeight: 1.8,
                      maxWidth: '800px',
                    }}
                  >
                    {stepCards[0].description}
                  </Typography>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="contained"
                      component="a"
                      href={stepCards[0].buttonLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      size="large"
                      endIcon={<ArrowForwardIcon />}
                      sx={{
                        px: 6,
                        py: 2,
                        borderRadius: '50px',
                        fontSize: '1.1rem',
                        background: 'rgba(255,255,255,0.2)',
                        backdropFilter: 'blur(10px)',
                        '&:hover': {
                          background: 'rgba(255,255,255,0.3)',
                        }
                      }}
                    >
                      {stepCards[0].buttonText}
                    </Button>
                  </motion.div>
                </Box>
              </Paper>
            </Box>

            {/* Find Facilities Section */}
            <Box sx={{ mb: 12, mt: 8 }}>
              <Paper
                sx={{
                  p: 6,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  WebkitBackdropFilter: 'blur(10px)',
                  borderRadius: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                }}
              >
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  <Typography variant="h4" gutterBottom>
                    2. Find Retirement Homes Near You
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      mb: 4,
                      fontSize: '1.1rem',
                      lineHeight: 1.8,
                      maxWidth: '800px',
                    }}
                  >
                    {stepCards[1].description}
                  </Typography>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    transition={{ duration: 0.3 }}
                  >
                    <a 
                      href="https://www.google.com/maps/search/retirement+homes+near+me" 
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ textDecoration: 'none' }}
                    >
                      <Box
                        sx={{
                          width: '100%',
                          maxWidth: '800px',
                          mx: 'auto',
                          borderRadius: '20px',
                          overflow: 'hidden',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                          position: 'relative',
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundImage: `url(${stepCards[1].image})`,
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                            opacity: 0.5,
                            filter: 'blur(4px)',
                            backdropFilter: 'blur(4px)',
                            WebkitBackdropFilter: 'blur(4px)',
                            zIndex: 0,
                          },
                          '&::after': {
                            content: '""',
                            display: 'block',
                            paddingBottom: '50%',
                          }
                        }}
                      >
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: `url('https://maps.googleapis.com/maps/api/staticmap?center=39.8283,-98.5795&zoom=3&size=800x400&scale=2&style=feature:all|element:labels|visibility:off&style=feature:water|color:0x4a90e2&style=feature:landscape|color:0x222222')`,
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                            filter: 'blur(3px) brightness(0.8)',
                            transition: 'filter 0.3s ease',
                            '&:hover': {
                              filter: 'blur(2px) brightness(0.9)',
                            }
                          }}
                        />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            color: 'white',
                            textAlign: 'center',
                            zIndex: 1,
                            width: '100%',
                            padding: '20px',
                          }}
                        >
                          <Typography variant="h5" sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.5)', mb: 1 }}>
                            Open Interactive Map
                          </Typography>
                          <Typography variant="body1" sx={{ opacity: 0.9, textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
                            Click to find retirement homes in your area →
                          </Typography>
                        </Box>
                      </Box>
                    </a>
                  </motion.div>
                </Box>
              </Paper>
            </Box>

            {/* Next Steps Section */}
            <Box sx={{ mb: 12 }}>
              <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 6 }}>
                Next Steps
              </Typography>
              <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                  <Paper
                    sx={{
                      p: 4,
                      height: '100%',
                      bgcolor: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      WebkitBackdropFilter: 'blur(10px)',
                      borderRadius: '20px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <GroupsIcon sx={{ fontSize: 40, color: '#64b5f6', mr: 2 }} />
                      <Typography variant="h5">
                        3. Build Your Team
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ opacity: 0.9 }}>
                      Gather interested students and find a faculty advisor who can support your chapter's 
                      activities. Having a dedicated team is crucial for success.
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper
                    sx={{
                      p: 4,
                      height: '100%',
                      bgcolor: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      WebkitBackdropFilter: 'blur(10px)',
                      borderRadius: '20px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SchoolIcon sx={{ fontSize: 40, color: '#64b5f6', mr: 2 }} />
                      <Typography variant="h5">
                        4. Join Our Community
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ opacity: 0.9 }}>
                      Become part of our nationwide network of students making a difference. We'll provide 
                      ongoing support and resources for your chapter.
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>

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

export default GetStarted;