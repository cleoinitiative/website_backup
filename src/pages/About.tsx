import React, { useState, useCallback } from 'react';
import { Box, Container, Typography, Grid, Paper, Button } from '@mui/material';
import { motion } from 'framer-motion';
import ParticleBackground from '../components/ParticleBackground';
import { Link } from 'react-router-dom';
import SchoolIcon from '@mui/icons-material/School';
import GroupsIcon from '@mui/icons-material/Groups';
import PublicIcon from '@mui/icons-material/Public';

interface Founder {
  name: string;
  image: string;
  role: string;
  bio: string;
  linkedin?: string;
}

const founders: Founder[] = [
  { 
    name: 'Derrick Hueniken',
    image: '/images/founders/derrick.png',
    role: 'Co-Founder & President',
    bio: 'Passionate about bridging the technological divide between generations.',
    linkedin: 'https://linkedin.com/in/derrick-hueniken'
  },
  { 
    name: 'Christian Laquis',
    image: '/images/founders/christian.png',
    role: 'Co-Founder & Vice President',
    bio: 'Dedicated to empowering seniors through technology education.',
    linkedin: 'https://linkedin.com/in/christian-laquis'
  },
  { 
    name: 'Aaron Smolyar',
    image: '/images/founders/aaron.png',
    role: 'Co-Founder & Director',
    bio: 'Committed to creating meaningful connections across generations.',
    linkedin: 'https://linkedin.com/in/aaron-smolyar'
  }
];

const stats = [
  { number: '1500+', label: 'Seniors Helped', icon: <GroupsIcon sx={{ fontSize: 40 }} /> },
  { number: '35+', label: 'School Chapters', icon: <SchoolIcon sx={{ fontSize: 40 }} /> },
  { number: '15', label: 'States Reached', icon: <PublicIcon sx={{ fontSize: 40 }} /> },
];

// Timeline data
interface TimelineItem {
  year: string;
  title: string;
  description: string;
  image: string;
}

const timelineItems: TimelineItem[] = [
  {
    year: '2021',
    title: 'A New Idea',
    description: 'The CLEO Initiative was born when Derrick Hueniken, Christian Laquis, and Aaron Smolyar were discussing their shared experience of their grandparents\' daily struggles with technology. They decided that if their grandparents were too far away to help, they could at least help the seniors in their own community.',
    image: '/images/about/about2.jpg'
  },
  {
    year: '2022',
    title: 'Getting Started',
    description: 'The CLEO Initiative started at a Brookdale Senior Living community in Fort Myers. Every week, students from the Canterbury Upper School would visit Brookdale and help the seniors, forging long-lasting connections along the way. Soon, people began to notice that CLEO had a big impact on the seniors it was serving.',
    image: '/images/about/about3.jpg'
  },
  {
    year: '2023',
    title: 'Nationwide Growth',
    description: 'Friends and family of CLEO members began reaching out to start chapters, and thus CLEO became a nationwide effort. Today, CLEO has chapters across multiple states, serving seniors in communities throughout the country.',
    image: '/images/about/about4.jpg'
  }
];

const About: React.FC = () => {
  const [isMapVisible, setIsMapVisible] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseLeave = useCallback(() => {
    if (!isHovering) {
      setIsMapVisible(false);
    }
  }, [isHovering]);

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

          {/* Hero Section */}
          <Box
            sx={{
              position: 'relative',
              height: { xs: 'auto', md: '70vh' },
              minHeight: { xs: '50vh', md: '70vh' },
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              py: { xs: 4, md: 0 },
              px: { xs: 2, md: 0 },
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage: 'url(/images/about/hero.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                opacity: 0.4,
                zIndex: 0,
              }
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontSize: { 
                      xs: '2.5rem', 
                      sm: '3.5rem',
                      md: '5rem' 
                    },
                    fontWeight: 700,
                    mb: { xs: 2, md: 3 },
                    background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    px: { xs: 2, md: 0 },
                  }}
                >
                  About CLEO
                </Typography>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    maxWidth: '800px',
                    margin: '0 auto',
                    opacity: 0.9,
                    lineHeight: 1.6,
                    mb: 4,
                  }}
                >
                  Empowering seniors through technology, one connection at a time
                </Typography>
              </Container>
            </motion.div>
          </Box>

          {/* Stats Section */}
          <Container maxWidth="lg" sx={{ mt: { xs: -8, md: -12 }, mb: 8 }}>
            <Grid container spacing={3} justifyContent="center">
              {stats.map((stat, index) => (
                <Grid item xs={12} sm={4} key={stat.label}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.2 }}
                  >
                    <Paper
                      sx={{
                        p: 4,
                        height: '100%',
                        textAlign: 'center',
                        background: 'rgba(255,255,255,0.1)',
                        backdropFilter: 'blur(10px)',
                        WebkitBackdropFilter: 'blur(10px)',
                        borderRadius: '20px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        transition: 'transform 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-5px)',
                          background: 'rgba(255,255,255,0.15)',
                        }
                      }}
                    >
                      <Box sx={{ mb: 2, color: '#64b5f6' }}>
                        {stat.icon}
                      </Box>
                      <Typography 
                        variant="h3" 
                        sx={{ 
                          mb: 1,
                          fontWeight: 700,
                          background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {stat.number}
                      </Typography>
                      <Typography 
                        variant="h6"
                        sx={{ 
                          opacity: 0.9,
                          fontWeight: 500
                        }}
                      >
                        {stat.label}
                      </Typography>
                    </Paper>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Container>

          {/* What is CLEO Section */}
          <Container 
            maxWidth="lg" 
            sx={{ 
              mt: { xs: 4, md: 8 },
              mb: { xs: 4, md: 8 },
              px: { xs: 2, md: 3 },
              '& > *': {
                mx: 'auto',
                width: '100%',
              }
            }}
          >
            <Paper
              sx={{
                position: 'relative',
                overflow: 'hidden',
                bgcolor: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                borderRadius: '30px',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: '-25px',
                  right: '-25px',
                  bottom: 0,
                  backgroundImage: 'url(/images/about/about1.jpg)',
                  backgroundSize: 'cover',
                  backgroundPosition: '55% center',
                  opacity: 0.2,
                  zIndex: 0,
                }
              }}
            >
              <Box sx={{ position: 'relative', zIndex: 1, p: { xs: 4, md: 8 } }}>
                <Grid container spacing={6} alignItems="center">
                  <Grid item xs={12} md={5}>
                    <Typography 
                      variant="h3" 
                      gutterBottom 
                      sx={{ 
                        fontWeight: 700,
                        background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                      }}
                    >
                      What is CLEO?
                    </Typography>
                    <Typography 
                      variant="h5" 
                      sx={{ 
                        mb: 4, 
                        opacity: 0.9,
                        fontWeight: 500,
                        color: '#64b5f6'
                      }}
                    >
                      Computer Literacy Education Outreach
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={7}>
                    <Box>
                      <Typography 
                        variant="body1" 
                        paragraph 
                        sx={{ 
                          fontSize: '1.2rem', 
                          lineHeight: 1.8,
                          textShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          mb: 4
                        }}
                      >
                        CLEO is an initiative that bridges the digital divide between generations, 
                        connecting high school students with seniors to share essential technology skills.
                      </Typography>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <Box>
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              color: '#64b5f6',
                              mb: 1
                            }}
                          >
                            Our Mission
                          </Typography>
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontSize: '1.1rem', 
                              lineHeight: 1.8,
                              opacity: 0.9
                            }}
                          >
                            We empower seniors with the knowledge and confidence to navigate the digital world, 
                            helping them stay connected with loved ones and maintain independence.
                          </Typography>
                        </Box>

                        <Box>
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              color: '#64b5f6',
                              mb: 1
                            }}
                          >
                            How It Works
                          </Typography>
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontSize: '1.1rem', 
                              lineHeight: 1.8,
                              opacity: 0.9
                            }}
                          >
                            Student volunteers meet regularly with seniors in local retirement communities, 
                            providing one-on-one guidance on using smartphones, computers, and other digital tools.
                          </Typography>
                        </Box>

                        <Box>
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              color: '#64b5f6',
                              mb: 1
                            }}
                          >
                            Our Impact
                          </Typography>
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontSize: '1.1rem', 
                              lineHeight: 1.8,
                              opacity: 0.9
                            }}
                          >
                            Beyond technical skills, CLEO creates meaningful intergenerational connections 
                            that enrich both students' and seniors' lives through shared learning experiences.
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </Paper>
          </Container>

          {/* Founders Section */}
          <Container 
            maxWidth="lg" 
            sx={{ 
              mt: { xs: 4, md: 8 },
              mb: { xs: 4, md: 8 },
              px: { xs: 2, md: 3 },
              '& > *': {
                mx: 'auto',
                width: '100%',
              }
            }}
          >
            <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 8 }}>
              Our Founders
            </Typography>
            <Grid container spacing={{ xs: 2, sm: 3, md: 6 }}>
              {founders.map((founder, index) => (
                <Grid 
                  item 
                  xs={4}  // Always take 4 columns (1/3 of width) on all screen sizes
                  key={founder.name}
                >
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.2 }}
                    whileHover={{ y: -10 }}
                  >
                    <Paper
                      sx={{
                        p: { xs: 1, sm: 2, md: 3 },  // Reduced padding for smaller screens
                        bgcolor: 'rgba(255,255,255,0.1)',
                        backdropFilter: 'blur(10px)',
                        WebkitBackdropFilter: 'blur(10px)',
                        borderRadius: '20px',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          bgcolor: 'rgba(255,255,255,0.15)',
                          boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
                        }
                      }}
                    >
                      <Box
                        sx={{
                          position: 'relative',
                          paddingTop: '100%',
                          borderRadius: '15px',
                          overflow: 'hidden',
                          mb: { xs: 1, sm: 2, md: 3 },  // Reduced margin for smaller screens
                        }}
                      >
                        <img
                          src={founder.image}
                          alt={founder.name}
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                      </Box>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          textAlign: 'center',
                          fontSize: { xs: '1rem', sm: '1.25rem', md: '1.5rem' }  // Responsive font size
                        }}
                      >
                        {founder.name}
                      </Typography>
                    </Paper>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Container>

          {/* Journey Section with Timeline */}
          <Container 
            maxWidth="lg" 
            sx={{ 
              mt: { xs: 4, md: 8 },
              mb: { xs: 4, md: 8 },
              px: { xs: 2, md: 3 },
              '& > *': {
                mx: 'auto',
                width: '100%',
              }
            }}
          >
            <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 12 }}>
              Our Journey
            </Typography>

            {/* Timeline Container */}
            <Box
              sx={{
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: 2,
                  height: '100%',
                  background: 'rgba(255,255,255,0.2)',
                  zIndex: 0,
                }
              }}
            >
              {timelineItems.map((item, index) => (
                <Box
                  key={item.year}
                  sx={{
                    position: 'relative',
                    mb: { xs: 12, md: index === timelineItems.length - 1 ? 0 : -20 },
                    mt: { xs: 0, md: index === 0 ? 0 : -20 },
                    display: 'flex',
                    alignItems: 'center',
                    minHeight: { md: '400px' },
                    width: '100%',
                    justifyContent: { xs: 'center', md: 'flex-start' },
                    zIndex: index % 2 === 0 ? 2 : 1,
                  }}
                >
                  {/* Timeline dot */}
                  <Box
                    sx={{
                      position: 'absolute',
                      left: '50%',
                      top: { xs: 0, md: '50%' },
                      transform: { 
                        xs: 'translate(-50%, -50%)', 
                        md: 'translate(-50%, -50%)' 
                      },
                      width: { xs: 16, md: 20 },
                      height: { xs: 16, md: 20 },
                      borderRadius: '50%',
                      bgcolor: 'primary.light',
                      border: '4px solid white',
                      zIndex: 3,  // Ensure dots are always on top
                    }}
                  />

                  {/* Content Card */}
                  <Box
                    sx={{
                      width: { xs: '90%', md: 'calc(50% - 40px)' },
                      ml: { 
                        xs: 0, 
                        md: index % 2 === 0 ? 0 : 'calc(50% + 40px)' 
                      },
                      mr: { 
                        xs: 0, 
                        md: index % 2 === 0 ? 'calc(50% + 40px)' : 0 
                      },
                      position: 'relative',  // For proper z-indexing
                    }}
                  >
                    <Paper
                      sx={{
                        overflow: 'hidden',
                        bgcolor: 'rgba(255,255,255,0.1)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: '20px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                        width: '100%',
                        transition: 'transform 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-5px)',
                          zIndex: 4,  // Ensure hovered item is on top
                        },
                      }}
                    >
                      {/* Image */}
                      <Box
                        sx={{
                          width: '100%',
                          height: { xs: '200px', sm: '250px', md: '300px' },
                          position: 'relative',
                          overflow: 'hidden',
                        }}
                      >
                        <img
                          src={item.image}
                          alt={item.title}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            objectPosition: index === timelineItems.length - 1 ? 'top' : 'center',
                          }}
                        />
                      </Box>

                      {/* Text Content */}
                      <Box sx={{ p: { xs: 3, md: 4 } }}>
                        <Typography 
                          variant="h4" 
                          gutterBottom 
                          color="primary.light"
                          sx={{ fontSize: { xs: '1.75rem', md: '2.125rem' } }}
                        >
                          {item.year}
                        </Typography>
                        <Typography 
                          variant="h5" 
                          gutterBottom
                          sx={{ fontSize: { xs: '1.5rem', md: '1.75rem' } }}
                        >
                          {item.title}
                        </Typography>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            fontSize: { xs: '1rem', md: '1.1rem' },
                            lineHeight: 1.8,
                            opacity: 0.9
                          }}
                        >
                          {item.description}
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                </Box>
              ))}
            </Box>

            {/* Chapters Section */}
            <Container 
              maxWidth="lg" 
              sx={{ 
                mt: { xs: 4, md: 8 },
                mb: { xs: 4, md: 8 },
                px: { xs: 2, md: 3 },
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
              id="chapters"
            >
              <Box sx={{ width: '100%', maxWidth: '800px' }}>
                <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 6 }}>
                  Our Chapters
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    textAlign: 'center', 
                    mb: 8, 
                    opacity: 0.9, 
                    maxWidth: '800px', 
                    mx: 'auto',
                    px: { xs: 2, md: 0 }
                  }}
                >
                  From coast to coast, CLEO chapters are making a difference in their communities. 
                  Each pin represents a school where students are actively helping seniors bridge the digital divide.
                </Typography>

                <Paper
                  sx={{
                    p: { xs: 2, md: 4 },
                    bgcolor: 'rgba(255,255,255,0.1)',
                    backdropFilter: 'blur(10px)',
                    WebkitBackdropFilter: 'blur(10px)',
                    borderRadius: '20px',
                    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    width: '100%',
                  }}
                >
                  <Box sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
                    <Typography variant="h6" gutterBottom>
                      Want to start a chapter at your school?
                    </Typography>
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
                          mt: 2,
                          px: { xs: 4, md: 6 },
                          py: 1.5,
                          borderRadius: '50px',
                          fontSize: { xs: '1rem', md: '1.1rem' },
                          background: 'rgba(255,255,255,0.2)',
                          backdropFilter: 'blur(10px)',
                          '&:hover': {
                            background: 'rgba(255,255,255,0.3)',
                          }
                        }}
                      >
                        Get Started Today
                      </Button>
                    </motion.div>
                  </Box>

                  {/* Map Container */}
                  <motion.div
                    whileHover={{ 
                      y: -5,
                      transition: { duration: 0.3 }
                    }}
                  >
                    <Box 
                      sx={{ 
                        width: '100%',
                        height: { xs: '400px', sm: '500px', md: '600px' },  // Adjusted height for mobile
                        position: 'relative',
                        overflow: 'hidden',
                        borderRadius: '20px',
                        bgcolor: 'rgba(255,255,255,0.1)',
                        transition: 'box-shadow 0.3s ease',
                        aspectRatio: { xs: '1/1', md: '16/9' },  // Square on mobile, widescreen on desktop
                        '&:hover': {
                          boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.45)',
                        }
                      }}
                      onMouseLeave={handleMouseLeave}
                      onMouseEnter={() => setIsHovering(true)}
                      onMouseOver={() => setIsHovering(true)}
                      onMouseOut={() => setIsHovering(false)}
                    >
                      {!isMapVisible && (
                        <Box
                          onClick={() => setIsMapVisible(true)}
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backdropFilter: 'blur(10px)',
                            WebkitBackdropFilter: 'blur(10px)',
                            zIndex: 2,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(0,0,0,0.3)',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              background: 'rgba(0,0,0,0.4)',
                            }
                          }}
                        >
                          <Typography 
                            variant="h4" 
                            sx={{ 
                              color: 'white',
                              textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                              letterSpacing: '1px',
                              fontWeight: 500,
                              opacity: 0.9,
                              transition: 'opacity 0.3s ease',
                              '&:hover': {
                                opacity: 1
                              }
                            }}
                          >
                            Click to View Map
                          </Typography>
                        </Box>
                      )}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          pointerEvents: isMapVisible ? 'auto' : 'none',
                        }}
                      >
                        <iframe 
                          src="https://www.google.com/maps/d/embed?mid=1jslHrYUFFqXpfYP_vJZEojGeMl_CHTo&ehbc=2E312F&hl=en&ui=0"
                          style={{ 
                            border: 0,
                            width: '100%',
                            height: 'calc(100% + 60px)',
                            marginTop: '-60px',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                          }}
                          title="CLEO Chapters Map"
                        />
                      </Box>
                    </Box>
                  </motion.div>
                </Paper>
              </Box>
            </Container>

            {/* FAQ Button */}
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

export default About;