import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Container,
  Box,
  Button,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ParticleBackground from './ParticleBackground';
import { motion } from 'framer-motion';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Link } from 'react-router-dom';

interface FAQItem {
  question: string;
  answer: string | JSX.Element;
}

interface FAQCategory {
  title: string;
  items: FAQItem[];
}

const faqCategories: FAQCategory[] = [
  {
    title: "Getting Started",
    items: [
      {
        question: "What is CLEO?",
        answer:
          "CLEO (Computer Literacy Education Outreach) is a student-led initiative that connects high school students with seniors in retirement homes through technology education volunteering programs.",
      },
      {
        question: "How do I start a CLEO chapter at my school?",
        answer: (
          <>
            Starting a CLEO chapter involves reviewing our setup guide, joining
            our GroupMe, finding local retirement homes, gathering interested
            students, and securing a faculty advisor. Visit our{" "}
            <Link
              to="/get-started"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              Get Started
            </Link>{" "}
            page for a detailed step-by-step guide.
          </>
        ),
      },
      {
        question: "Is there a cost to start or join a CLEO chapter?",
        answer: (
          <>
            There is no cost to start a CLEO chapter for either the school and the seniors. CLEO chapters are free to start and run.
            As an organization, we run on donations and sponsorships. If you are interested in sponsoring CLEO, please
            reach out to us on our{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              contact page
            </Link>{" "}
            to learn more. If you want to donate, please click the button in the top right corner of the page if you are on desktop
            or the button in the dropdown menu if you are on mobile.
          </>
        ),
      },
    ],
  },
  {
    title: "Requirements & Commitments",
    items: [
      {
        question: "Do I need any special skills or experience?",
        answer:
          "No special skills are required beyond what you already know by using your own devices! We provide all the necessary training and resources. The most important qualities are patience, enthusiasm for helping others, and a willingness to learn and teach basic technology skills. Even if you don't know something, you can always look it up together!",
      },
      {
        question: "How much time commitment is required?",
        answer:
          "Most CLEO chapters volunteer once per week or once every other week for 1-2 hours. As a chapter leader, you'll need additional time for planning and coordination, especially in the beginning. Members can participate based on their availability, unless you wish to implement a volunteer schedule.",
      },
      {
        question: "What technology do we need?",
        answer:
          "Because most of the technology seniors use is already owned by them, we don't require any special equipment. However, an internet connection wherever you meet is required to ensure all members can participate. If your facility has public devices like computers or tablets, you can use those too for more specialized activities.",
      },
    ],
  },
  {
    title: "Support & Safety",
    items: [
      {
        question: "What kind of support does CLEO provide?",
        answer: (
          <>
            CLEO provides comprehensive setup guides, training materials,
            ongoing support from our team, connection to our network of
            chapters, and resources for finding members and teaching technology
            to seniors. Check out our{" "}
            <Link
              to="/about#chapters"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              About
            </Link>{" "}
            page to learn more about our organization.
          </>
        ),
      },
      {
        question: "How do you ensure safety and privacy?",
        answer: (
          <>
            All CLEO activities are supervised by faculty advisors and
            retirement home staff. All volunteers must sign and follow our
            safety protocols and code of conduct. If you have any concerns,
            please{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              contact us
            </Link>
            .
          </>
        ),
      },
      {
        question:
          "What if I can't find a faculty advisor, retirement home, or members?",
        answer: (
          <>
            If you're having trouble finding a faculty advisor, retirement home,
            or members, please{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              contact us
            </Link>
            . We're here to help you every step of the way.
          </>
        ),
      },
    ],
  },
  {
    title: "Participation",
    items: [
      {
        question: "Can middle school students participate?",
        answer: (
          <>
            CLEO is primarily designed for high school students, but middle
            school students can participate with additional supervision and
            parental consent.{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              Contact us
            </Link>{" "}
            for any questions relating to starting a chapter.
          </>
        ),
      },
      {
        question: "Can I join an existing chapter?",
        answer: (
          <>
            Usually, CLEO chapters are for students of a single high school.
            However, If there's already a CLEO chapter{" "}
            <Link
              to="/about#chapters"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              in your area
            </Link>{" "}
            and you are a student who doesn't want to start your own chapter,
            you can ask to join as a member.{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              Contact us
            </Link>{" "}
            to help get connected with chapters near you.
          </>
        ),
      },
      {
        question: "How can parents and teachers get involved?",
        answer: (
          <>
            Parents and teachers can serve as advisors, help with coordination,
            or provide support for chapter activities. We welcome adult
            volunteers who want to help make a difference. Visit our{" "}
            <Link
              to="/contact"
              style={{ color: "#64b5f6", textDecoration: "underline" }}
            >
              Contact
            </Link>{" "}
            page to get involved.
          </>
        ),
      },
    ],
  },
];

const FAQ: React.FC = () => {
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
              pb: 8,
            }}
          >
            {/* Move Back Button here, before the hero section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Box sx={{ pt: 4 }}>
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
              </Box>
            </motion.div>

            {/* Hero Section */}
            <Box sx={{ textAlign: 'center', mb: 12, mt: 4 }}>
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
                  Frequently Asked Questions
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
                  Find answers to common questions about starting and running a CLEO chapter
                </Typography>
              </motion.div>
            </Box>

            {/* FAQ Categories */}
            <Box sx={{ maxWidth: '900px', mx: 'auto' }}>
              {faqCategories.map((category, categoryIndex) => (
                <motion.div
                  key={categoryIndex}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: categoryIndex * 0.1 }}
                >
                  <Box sx={{ mb: 8 }}>
                    <Typography 
                      variant="h4" 
                      sx={{ 
                        mb: 4,
                        fontSize: { xs: '1.8rem', md: '2.2rem' },
                        background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                      }}
                    >
                      {category.title}
                    </Typography>
                    
                    {category.items.map((item, itemIndex) => (
                      <Accordion
                        key={itemIndex}
                        sx={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          color: 'white',
                          backdropFilter: 'blur(10px)',
                          WebkitBackdropFilter: 'blur(10px)',
                          mb: 2,
                          borderRadius: '15px !important',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                          '&:before': {
                            display: 'none',
                          },
                          '&.Mui-expanded': {
                            margin: '0 0 16px 0',
                          },
                          overflow: 'hidden',
                        }}
                      >
                        <AccordionSummary
                          expandIcon={<ExpandMoreIcon sx={{ color: 'white' }} />}
                          sx={{
                            '&:hover': {
                              background: 'rgba(255, 255, 255, 0.1)',
                            },
                            transition: 'background 0.3s ease',
                          }}
                        >
                          <Typography
                            sx={{
                              fontSize: '1.2rem',
                              fontWeight: 500,
                              py: 1,
                            }}
                          >
                            {item.question}
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails
                          sx={{
                            background: 'rgba(255, 255, 255, 0.02)',
                            borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                            p: 3,
                          }}
                        >
                          <Typography
                            sx={{
                              color: 'rgba(255, 255, 255, 0.8)',
                              lineHeight: 1.8,
                              fontSize: '1.1rem',
                            }}
                          >
                            {typeof item.answer === 'string' ? item.answer : item.answer}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Box>
                </motion.div>
              ))}
            </Box>

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

export default FAQ;