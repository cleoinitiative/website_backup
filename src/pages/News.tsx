import React, { useState, useMemo } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Paper,
  TextField,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  InputAdornment,
  Divider,
} from '@mui/material';
import { motion } from 'framer-motion';
import ParticleBackground from '../components/ParticleBackground';
import SearchIcon from '@mui/icons-material/Search';

// Types
interface NewsItem {
  source: string;
  date: string;
  title: string;
  link: string;
  image?: string;
  recommendedPosition: number;
}

// News Items Data
const newsItems: NewsItem[] = [
  {
    source: "On the Road with Steve Hartman, CBS",
    date: "3/29/2023",
    title: "Teenagers Help Seniors Learn How to Use Technology - and Form Friendships Along the Way",
    link: "https://www.cbsnews.com/news/teenagers-volunteer-help-seniors-learn-how-to-use-technology-form-friendships-along-the-way/",
    image: "/images/news/cbs.png",
    recommendedPosition: 1
  },
  {
    source: "CBS Morning News",
    date: "11/15/2024",
    title: "Kindness 101: Teaching patience through generations",
    link: "https://www.cbsnews.com/video/kindness-101-teaching-patience-through-generations/",
    image: "/images/news/cbsmorning.png",
    recommendedPosition: 2
  },
  {
    source: "Sean Martinelli, NBC-2",
    date: "3/2/2023",
    title: "Teens make weekly retirement community trip to solve tech problems for seniors",
    link: "https://www.youtube.com/watch?v=0zNj4ax-GEM",
    image: "/images/news/nbc2.png",
    recommendedPosition: 3
  },
  {
    source: "7 News Miami",
    date: "12/18/2023",
    title: "South Florida Students Teach Tech to Seniors in Initiative to Bridge Generational 'Digital Divide'",
    link: "https://wsvn.com/news/local/miami-dade/south-florida-students-teach-tech-to-seniors-in-initiative-to-bridge-generational-digital-divide/",
    image: "/images/news/7news.png",
    recommendedPosition: 4
  },
  {
    source: "MIT AgeLab",
    date: "3/19/2024",
    title: "Five High Schoolers Awarded 2024 OMEGA Scholarships for Intergenerational Efforts",
    link: "https://agelab.mit.edu/transportation-and-livable-communities/blog/five-high-schoolers-awarded-2024-omega-scholarships-intergenerational-efforts/",
    image: "/images/news/mit.png",
    recommendedPosition: 5
  },
  {
    source: "NASSP - National Honor Society",
    date: "5/18/2023",
    title: "NHS Students Provide Senior Citizens with Much-Needed Tech Support",
    link: "https://www.nassp.org/nhs-students-provide-senior-citizens-with-much-needed-tech-support/",
    image: "/images/news/nassp.png",
    recommendedPosition: 6
  },
  {
    source: "National Honor Society",
    date: "3/7/2023",
    title: "Three NHS members created CLEO to help seniors in their community with technology",
    link: "https://www.instagram.com/p/CpgjrfZpRNa/",
    image: "/images/news/nhs.png",
    recommendedPosition: 7
  },
  {
    source: "The Christian Heart",
    date: "8/9/2023",
    title: "Helping Seniors with Technology",
    link: "https://thechristianheart.com/helping-seniors-with-technology/",
    image: "/images/news/christianheart.png",
    recommendedPosition: 8
  },
  {
    source: "Canterbury School",
    date: "2/9/2023",
    title: "Club Spotlight: Computer Literacy Education Outreach (CLEO)",
    link: "https://www.canterburyfortmyers.org/news-detail?pk=1270016",
    image: "/images/news/canterbury.png",
    recommendedPosition: 9
  },
];

// Components
const NewsCard: React.FC<{ item: NewsItem; index: number }> = ({ item, index }) => (
  <Grid item xs={12}>
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -5 }}
    >
      <Paper 
        component="a"
        href={item.link}
        target="_blank"
        rel="noopener noreferrer"
        sx={{ 
          p: 4,
          height: '100%',
          bgcolor: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          cursor: 'pointer',
          textDecoration: 'none',
          color: 'inherit',
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          gap: { xs: 3, md: 4 },
          alignItems: { xs: 'center', md: 'center' },
          transition: 'all 0.3s ease',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
          '&:hover': {
            bgcolor: 'rgba(255,255,255,0.15)',
            transform: 'translateY(-5px)',
            boxShadow: '0 12px 40px rgba(0,0,0,0.3)',
          },
        }}
      >
        <Box
          sx={{
            width: { xs: '100%', md: '200px' },
            height: { xs: '200px', md: '150px' },
            flexShrink: 0,
            bgcolor: 'white',
            borderRadius: 2,
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          {item.image ? (
            <img
              src={item.image}
              alt={item.title}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                padding: '8px',
              }}
            />
          ) : (
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255,255,255,0.5)',
                textAlign: 'center',
                px: 2
              }}
            >
              Image Coming Soon
            </Typography>
          )}
        </Box>

        <Box sx={{ 
          flex: 1,
          textAlign: { xs: 'center', md: 'left' }
        }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              mb: 1,
              color: '#64b5f6',
              fontSize: '0.9rem',
              fontWeight: 500
            }}
          >
            {item.source} — {item.date}
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 2,
              fontSize: { xs: '1.25rem', md: '1.5rem' },
              fontWeight: 500,
              lineHeight: 1.3,
              background: 'linear-gradient(45deg, #ffffff 30%, #64b5f6 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {item.title}
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'rgba(255,255,255,0.7)',
              fontSize: '0.9rem',
              fontStyle: 'italic'
            }}
          >
            Click to read full article →
          </Typography>
        </Box>
      </Paper>
    </motion.div>
  </Grid>
);

const SearchAndSort: React.FC<{
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  sortOrder: 'newest' | 'oldest' | 'recommended';
  setSortOrder: (order: 'newest' | 'oldest' | 'recommended') => void;
}> = ({ searchTerm, setSearchTerm, sortOrder, setSortOrder }) => (
  <Box 
    sx={{ 
      display: 'flex', 
      gap: 3, 
      mb: 6,
      flexDirection: { xs: 'column', sm: 'row' },
      alignItems: 'center',
      justifyContent: 'space-between'
    }}
  >
    <TextField
      fullWidth
      variant="outlined"
      placeholder="Search news articles..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      sx={{
        maxWidth: '500px',
        '& .MuiOutlinedInput-root': {
          color: 'white',
          '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
          '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
          '&.Mui-focused fieldset': { borderColor: 'white' },
        }
      }}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
          </InputAdornment>
        ),
      }}
    />

    <FormControl 
      sx={{ 
        minWidth: 200,
        '& .MuiInputLabel-root': {
          color: 'white',
          '&.Mui-focused': {
            color: 'white',
          },
        },
        '& .MuiOutlinedInput-root': {
          color: 'white',
          '& fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.3)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.5)',
          },
          '&.Mui-focused fieldset': {
            borderColor: 'white',
          },
        },
        '& .MuiSelect-icon': {
          color: 'white',
        },
        '& .MuiMenuItem-root': {
          color: 'black',
        },
      }}
    >
      <InputLabel>Sort By</InputLabel>
      <Select
        value={sortOrder}
        onChange={(e) => setSortOrder(e.target.value as 'newest' | 'oldest' | 'recommended')}
        label="Sort By"
      >
        <MenuItem value="recommended" sx={{ color: 'black' }}>Recommended</MenuItem>
        <MenuItem value="newest" sx={{ color: 'black' }}>Newest First</MenuItem>
        <MenuItem value="oldest" sx={{ color: 'black' }}>Oldest First</MenuItem>
      </Select>
    </FormControl>
  </Box>
);

// Remove the old getArticlePriority function and replace it with:
const getArticlePriority = (item: NewsItem): number => {
  return newsItems.findIndex(newsItem => 
    newsItem.source === item.source && newsItem.title === item.title
  );
};

// Main Component
const News: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest' | 'recommended'>('recommended');

  const { matchingNews, otherNews } = useMemo(() => {
    const allNews = [...newsItems];
    
    if (!searchTerm) {
      return { matchingNews: allNews, otherNews: [] };
    }

    const matching = allNews.filter(item => 
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.source.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const others = allNews
      .filter(item => !matching.includes(item))
      .sort((a, b) => {
        if (a.recommendedPosition !== b.recommendedPosition) {
          return a.recommendedPosition - b.recommendedPosition;
        }
        
        const [monthA, dayA, yearA] = a.date.split('/');
        const [monthB, dayB, yearB] = b.date.split('/');
        
        const dateA = new Date(parseInt(yearA), parseInt(monthA) - 1, parseInt(dayA));
        const dateB = new Date(parseInt(yearB), parseInt(monthB) - 1, parseInt(dayB));
        
        return dateB.getTime() - dateA.getTime();
      });

    return { matchingNews: matching, otherNews: others };
  }, [searchTerm]);

  const sortedMatchingNews = useMemo(() => {
    return [...matchingNews].sort((a, b) => {
      if (sortOrder === 'recommended') {
        return getArticlePriority(a) - getArticlePriority(b);
      }
      
      const [monthA, dayA, yearA] = a.date.split('/');
      const [monthB, dayB, yearB] = b.date.split('/');
      
      const dateA = new Date(parseInt(yearA), parseInt(monthA) - 1, parseInt(dayA));
      const dateB = new Date(parseInt(yearB), parseInt(monthB) - 1, parseInt(dayB));
      
      return sortOrder === 'newest' 
        ? dateB.getTime() - dateA.getTime()
        : dateA.getTime() - dateB.getTime();
    });
  }, [matchingNews, sortOrder]);

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
            px: { xs: 2, sm: 4, md: 6 },
          }}
        >
          <ParticleBackground />

          <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, width: '95%', pt: 8 }}>
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
                CLEO in the News
              </Typography>

              <SearchAndSort 
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                sortOrder={sortOrder}
                setSortOrder={setSortOrder}
              />

              <Grid container spacing={4}>
                {sortedMatchingNews.length > 0 ? (
                  sortedMatchingNews.map((item, index) => (
                    <NewsCard key={index} item={item} index={index} />
                  ))
                ) : searchTerm && (
                  <Grid item xs={12}>
                    <Typography 
                      variant="h6" 
                      sx={{ textAlign: 'center', opacity: 0.7, mt: 4 }}
                    >
                      No news articles found matching "{searchTerm}"
                    </Typography>
                  </Grid>
                )}

                {searchTerm && otherNews.length > 0 && (
                  <>
                    <Grid item xs={12}>
                      <Divider 
                        sx={{ 
                          my: 6, 
                          borderColor: 'rgba(255, 255, 255, 0.1)',
                          '&::before, &::after': {
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                          }
                        }}
                      >
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            color: 'rgba(255, 255, 255, 0.7)',
                            px: 2
                          }}
                        >
                          Other Articles
                        </Typography>
                      </Divider>
                    </Grid>
                    {otherNews.map((item, index) => (
                      <NewsCard key={`other-${index}`} item={item} index={index} />
                    ))}
                  </>
                )}
              </Grid>

              <Box sx={{ textAlign: 'center', mt: 12, mb: 6 }}>
                <Typography variant="h6" gutterBottom sx={{ opacity: 0.9 }}>
                  The CLEO Initiative
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.7 }}>
                  contact@cleoinitiative.org
                </Typography>
              </Box>
            </motion.div>
          </Container>
        </Box>
      </Box>
    </>
  );
};

export default News;