import DateFnsUtils from '@date-io/date-fns';
import React from 'react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Link from '@material-ui/core/Link';
import CssBaseline from '@material-ui/core/CssBaseline';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import { makeStyles } from '@material-ui/core/styles';
import {KeyboardDatePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
export {MaterialUIPickers, Album}

var currDate = new Date();
var year = "/" + currDate.getFullYear().toString();
var month =  "/" + (currDate.getMonth() + 1).toString();
var day = "/" + String(currDate.getDate()).padStart(2, '0');

const useStyles = makeStyles(theme => ({
  root: {
    '& > *': {
      margin: theme.spacing(100, 100, 100),
      alignItems: "centre",
    },
    icon: {
      marginRight: theme.spacing(2),
    },
    heroContent: {
      backgroundColor: theme.palette.background.paper,
      padding: theme.spacing(8, 0, 6),
    },
    heroButtons: {
      marginBottom: theme.spacing(50),
    },
    cardGrid: {
      marginTop: theme.spacing(100),
      paddingTop: theme.spacing(8),
      paddingBottom: theme.spacing(8),
    },
    card: {
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    },
    cardMedia: {
      paddingTop: '56.25%', // 16:9
    },
    cardContent: {
      flexGrow: 1,
    },
    footer: {
      backgroundColor: theme.palette.background.paper,
      padding: theme.spacing(6),
    },
  },
}));

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="/">
        20th Legion
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const cards = [1, 2, 3];

function Album() {
  const classes = useStyles();

  return (
    <React.Fragment>
      <CssBaseline />
      <main>
        {/* Hero unit */}
        <div className={classes.heroContent}>
          <Container maxWidth="sm">
            <Typography component="h1" variant="h2" align="center" color="textPrimary" gutterBottom>
              Derivative Trades
            </Typography>
            <Typography variant="subtitle1" align="center" color="textSecondary" paragraph>
              Welcome to the derivatives trades software which helps generate reports and keeps track of all trades that happen on a daily basis. For quickly accessing trades
              or reports on a particular day choose a day in the calender or explore any of the other options.
            </Typography>
              <MaterialUIPickers/>
          </Container>
        </div>
        <Container className={classes.cardGrid} maxWidth="md" >
          <Grid container spacing={4}>
              <Grid item  xs={12} sm={6} md={4}>
                <Card className={classes.card}>
                  <CardMedia
                    className={classes.cardMedia}
                    image="https://source.unsplash.com/random"
                    title="Image title"
                  />
                  <CardContent className={classes.cardContent}>
                    <Typography gutterBottom variant="h5" component="h2">
                      Add
                    </Typography>
                    <Typography>
                      Add a new trade to the Database, by filling in the form.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary" href="/trades/form">
                      Take me here
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
              <Grid item  xs={12} sm={6} md={4}>
                <Card className={classes.card}>
                  <CardContent className={classes.cardContent}>
                    <Typography gutterBottom variant="h5" component="h2">
                      Trades
                    </Typography>
                    <Typography>
                      Have a look through all the trades done and edit them.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary" href="/trades">
                      Take me here
                    </Button>
                  </CardActions>
                </Card>
            </Grid>
            <Grid item  xs={12} sm={6} md={4}>
              <Card className={classes.card}>
                <CardContent className={classes.cardContent}>
                  <Typography gutterBottom variant="h5" component="h2">
                    Reports
                  </Typography>
                  <Typography>
                    Have a look through all reports and print them.
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" color="primary" href="/reports">
                    Take me here
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </main>
      {/* Footer */}
      <footer className={classes.footer}>
        <Typography variant="subtitle1" align="center" color="textSecondary" >
          20th Legion
        </Typography>
        <Typography variant="subtitle1" align="center" color="textSecondary" component="p">
          All rights reserved for our CS261 Coursework
        </Typography>
        <Copyright />
      </footer>
      {/* End footer */}
    </React.Fragment>
  );
}

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

function MaterialUIPickers() { //Handles date changed
  const [selectedDate, setSelectedDate] = React.useState(new Date());
  const classes = useStyles();
  const handleDateChange = date => {
    setSelectedDate(date);
    currDate = date
    year = "/" + currDate.getFullYear().toString();
    month = "/" + (currDate.getMonth() + 1).toString();
    day = "/" + String(currDate.getDate()).padStart(2, '0');
  };

  return (
    <React.Fragment>
      <Grid container justify="space-around">
      <MuiPickersUtilsProvider utils={DateFnsUtils} >
          <KeyboardDatePicker
              margin="normal"
              id="date-picker-dialog"
              label="Quick Select"
              format="dd/MM/yyyy"
              value={selectedDate}
              onChange={handleDateChange}
              KeyboardButtonProps={{
              'aria-label': 'change date',
              }}
          />
      </MuiPickersUtilsProvider>
      </Grid>
      <Grid container spacing={2} justify="center">
        <Grid item>
          <BarButton 
            text="Trades"
            href={"/trades" + year + month + day}  
          />
        </Grid>
        <Grid item>
          <BarButton
            text="Reports"
            href={"/reports" + year + month + day}
          />
        </Grid>
      </Grid>
    </React.Fragment>
  );
}