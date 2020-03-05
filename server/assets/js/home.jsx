import DateFnsUtils from '@date-io/date-fns';
import React from 'react';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import { makeStyles } from '@material-ui/core/styles';
import {KeyboardDatePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
export {MaterialUIPickers}

const useStyles = makeStyles(theme => ({
  root: {
    '& > *': {
      margin: theme.spacing(3, 1, 2),
      alignItems: "centre",
    },
  },
}));

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

function MaterialUIPickers() {
  // The first commit of Material-UI
  const [selectedDate, setSelectedDate] = React.useState(new Date('2014-08-18T21:11:54'));
  const classes = useStyles();
  const handleDateChange = date => {
    setSelectedDate(date);
  };

  return (
    
    <div className={classes.root}> 
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
    {/* Will need to modifiy these buttons to work with new URLs */}
      <BarButton 
        text="Trades"
        href="/trades" 
      />
      <BarButton
        text="Reports"
        href="/trades"
      />
    </div>

  );
}