import DateFnsUtils from '@date-io/date-fns';
import React from 'react';
import Grid from '@material-ui/core/Grid';
import {KeyboardDatePicker, MuiPickersUtilsProvider} from '@material-ui/pickers';
export {MaterialUIPickers}

function MaterialUIPickers() {
  // The first commit of Material-UI
  const [selectedDate, setSelectedDate] = React.useState(new Date('2014-08-18T21:11:54'));

  const handleDateChange = date => {
    setSelectedDate(date);
  };

  return (
    
    
    <Grid container justify="space-around">
    {/* <KeyboardDatePicker
        disableToolbar
        variant="inline"
        format="MM/dd/yyyy"
        margin="normal"
        id="date-picker-inline"
        label="Date picker inline"
        value={selectedDate}
        onChange={handleDateChange}
        KeyboardButtonProps={{
        'aria-label': 'change date',
        }}
    /> */}
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
    {/* <KeyboardTimePicker
        margin="normal"
        id="time-picker"
        label="Time picker"
        value={selectedDate}
        onChange={handleDateChange}
        KeyboardButtonProps={{
        'aria-label': 'change time',
        }}
    /> */}
    </Grid>
  );
}