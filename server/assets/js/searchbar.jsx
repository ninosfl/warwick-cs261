import React from 'react';
import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import InputBase from '@material-ui/core/InputBase';
import { fade, makeStyles } from '@material-ui/core/styles';
import useScrollTrigger from '@material-ui/core/useScrollTrigger';
import Fab from '@material-ui/core/Fab';
import SearchIcon from '@material-ui/icons/Search';
import HomeIcon from '@material-ui/icons/Home';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import Zoom from '@material-ui/core/Zoom';

export{SearchBar};

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,

  },

  top: {
    position: 'fixed',
    bottom: theme.spacing(2),
    right: theme.spacing(2),
    'z-index': 12,  //Keep this high or the top button will be moved to the background and inaccessible
  },

  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
    display: 'none',
    [theme.breakpoints.up('sm')]: {
      display: 'block',
    },
  },
  search: {
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: fade(theme.palette.common.white, 0.15),
    '&:hover': {
      backgroundColor: fade(theme.palette.common.white, 0.25),
    },
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(1),
      width: 'auto',
    },
  },
  searchIcon: {
    width: theme.spacing(7),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputRoot: {
    color: 'inherit',
  },
  inputInput: {
    padding: theme.spacing(1, 1, 1, 7),
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      width: 120,
      '&:focus': {
        width: 200,
      },
    },
  },
}));

// This is the beginning of the scroll button, This is there incase the user wants to go back to the top
function ScrollTop(props) {
  const { children, window } = props;
  const classes = useStyles();
  // Note that you normally won't need to set the window ref as useScrollTrigger
  // will default to window.
  // This is only being set here because the demo is in an iframe.
  const trigger = useScrollTrigger({
    target: window ? window() : undefined,
    disableHysteresis: true,
    threshold: 100,
  });

  const handleClick = event => {
    const anchor = (event.target.ownerDocument || document).querySelector('#back-to-top-anchor');

    if (anchor) {
      anchor.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    event.stopPropagation()
  };

  return (
    <Zoom in={trigger}>
      <div onClickCapture={handleClick} className={classes.top}>
        {children}
      </div>
    </Zoom>
  );
}

//End of the scroll button

// General React Component to add buttons to our bar
function BarButton(props){
  return (<Button
  variant="contained"
  color="primary"
  disableElevation={true}
  href={props.href}
>
  {props.text}
</Button>);
}

function SearchBar() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
            {/* This part does the scroll button with the arrow mark */}
      <ScrollTop > 
        <Fab color="primary" size="small" aria-label="scroll back to top">
          <KeyboardArrowUpIcon />  
        </Fab>
      </ScrollTop>
      <AppBar position="static">
        <Toolbar  id="back-to-top-anchor"> 
          {/* <IconButton
            edge="start"
            className={classes.menuButton}
            color="inherit"
            aria-label="open drawer"
          >
            <MenuIcon />
          </IconButton> */}
          <Typography className={classes.title} variant="h6" noWrap>
            20th Legion
          </Typography>
          <IconButton
            color="inherit"
            aria-label="Home"
            href="/"        //Home also added in manually
          >
            <HomeIcon />
          </IconButton>
          <BarButton 
            text="Add"
            href="/trades/" //Ways to add links to our buttons and formatting willk be done automatically TODO! make it accessable through dynamic URL?
          />
          <BarButton 
            text="Trades"
            href="/trades/" //Ways to add links to our buttons and formatting willk be done automatically
          />
          <BarButton 
            text="Reports"
            href="/reports/" //Ways to add links to our buttons and formatting willk be done automatically
          />
          <BarButton 
            text="Admin"
            href="/admin/" //Ways to add links to our buttons and formatting willk be done automatically
          />
          <div className={classes.search}>
            <div className={classes.searchIcon}>
              <SearchIcon />
            </div>
            <InputBase
              placeholder="Search…" // will need to implement some kind of api call from here
              classes={{
                root: classes.inputRoot,
                input: classes.inputInput,
              }}
              inputProps={{ 'aria-label': 'search' }}
            />
          </div>
        </Toolbar>
      </AppBar>
    </div>
  );
}