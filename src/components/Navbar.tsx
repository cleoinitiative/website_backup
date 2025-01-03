import {
  AppBar,
  Toolbar,
  Button,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  useTheme,
  useMediaQuery,
  Modal,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';
import TikTokIcon from '@mui/icons-material/MusicNote';

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [thankYouOpen, setThankYouOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down(1200));
  const location = useLocation();

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

  const menuItems = [
    { text: 'Home', path: '/' },
    { text: 'About', path: '/about' },
    { text: 'CLEO in the News', path: '/news' },
    { text: 'Get Started', path: '/get-started' },
    { text: 'Contact Us', path: '/contact' },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <>
      <Box sx={{ position: 'absolute', left: -9999, top: 'auto', width: 1, height: 1 }}>
        Skip to Content
      </Box>
      <AppBar 
        position="fixed" 
        sx={{ 
          background: 'linear-gradient(to bottom, rgba(10, 75, 120, 0.9) 0%, rgba(10, 75, 120, 0) 100%)',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          height: '100px',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
        }}
      >
        <Toolbar 
          sx={{ 
            height: '100%',
            paddingTop: '20px', 
            paddingBottom: '10px',
          }}
        >
          <Box
            component={Link}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 2
            }}
          >
            <Box
              component="img"
              src="/images/logo.png" 
              alt="CLEO Initiative Logo" 
              sx={{
                height: { xs: '60px', sm: '70px', md: '80px' },
                width: 'auto',
                filter: `
                  drop-shadow(0 0 1px rgba(255, 255, 255, 0.8))
                  drop-shadow(0 0 2px rgba(255, 255, 255, 0.4))
                `,
                transition: 'all 0.4s ease',
                '&:hover': {
                  filter: `
                    drop-shadow(0 0 2px rgba(255, 255, 255, 0.9))
                    drop-shadow(0 0 3px rgba(255, 255, 255, 0.5))
                  `,
                  transform: 'scale(1.03)',
                }
              }}
            />
          </Box>
          
          {isMobile ? (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ transform: 'scale(1.2)' }}
            >
              <MenuIcon />
            </IconButton>
          ) : (
            <Box sx={{ display: 'flex', gap: 1, marginLeft: 'auto' }}>
              {menuItems.map((item) => (
                <Button
                  key={item.text}
                  color="inherit"
                  component={Link}
                  to={item.path}
                  sx={{
                    color: 'white',
                    fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                    padding: { xs: '8px 12px', sm: '8px 16px' },
                    fontWeight: 500,
                    whiteSpace: 'nowrap',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }
                  }}
                >
                  {item.text}
                </Button>
              ))}
              <Box sx={{ display: 'flex', gap: 0.5, mr: { xs: 0.5, sm: 1 } }}>
                <IconButton
                  component="a"
                  href="https://www.instagram.com/cleoinitiative/"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }
                  }}
                >
                  <InstagramIcon />
                </IconButton>
                <IconButton
                  component="a"
                  href="https://www.facebook.com/profile.php?id=100091126731643"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }
                  }}
                >
                  <FacebookIcon />
                </IconButton>
                <IconButton
                  component="a"
                  href="https://www.tiktok.com/@cleoinitiative"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    }
                  }}
                >
                  <TikTokIcon />
                </IconButton>
              </Box>
              <Button
                color="inherit"
                onClick={openDonateWindow}
                sx={{
                  color: 'white',
                  fontSize: { xs: '0.9rem', sm: '1rem', md: '1.1rem' },
                  padding: { xs: '8px 16px', sm: '8px 24px' },
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)'
                  }
                }}
              >
                Donate
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        sx={{
          '& .MuiDrawer-paper': {
            width: { xs: '100%', md: '300px' },
            background: 'linear-gradient(135deg, #0a4b78 0%, #001529 100%)',
            color: 'white',
          }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          p: 2,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <IconButton
            onClick={handleDrawerToggle}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              component={Link}
              to={item.path}
              onClick={handleDrawerToggle}
              sx={{
                color: 'white',
                padding: '12px 24px',
                backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                '& .MuiListItemText-primary': {
                  fontSize: '1.1rem',
                  fontWeight: 500,
                },
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
          
          <ListItem
            button
            onClick={openDonateWindow}
            sx={{
              color: 'white',
              padding: '12px 24px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '& .MuiListItemText-primary': {
                fontSize: '1.1rem',
                fontWeight: 500,
              },
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)'
              },
              mt: 2
            }}
          >
            <ListItemText primary="Donate" />
          </ListItem>
        </List>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <IconButton
            component="a"
            href="https://www.instagram.com/cleoinitiative/"
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <InstagramIcon />
          </IconButton>
          <IconButton
            component="a"
            href="https://www.facebook.com/profile.php?id=100091126731643"
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <FacebookIcon />
          </IconButton>
          <IconButton
            component="a"
            href="https://www.tiktok.com/@cleoinitiative"
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <TikTokIcon />
          </IconButton>
        </Box>
      </Drawer>

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

            <Typography variant="body1" sx={{ mb: 3, color: '#34495e', lineHeight: 1.6 }}>
              Your donation will help us:
              <Box component="ul" sx={{ textAlign: 'left', mt: 1, mb: 2 }}>
                <li>Provide technology education to seniors</li>
                <li>Bridge the generational digital divide</li>
                <li>Create meaningful intergenerational connections</li>
              </Box>
              Together, we're making technology accessible for everyone.
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
                Continue Making a Difference
              </Button>
            </Box>
          </Box>
        </Box>
      </Modal>
    </>
  );
};

export default Navbar;