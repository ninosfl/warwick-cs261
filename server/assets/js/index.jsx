/* jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';
<<<<<<< HEAD
import Button from '@material-ui/core/Button';
import { YearList, MonthList, DayList } from './list-reports';
import { ErrorMessage } from './errors';

function App() {
  return (
    <Button variant="contained" color="primary">
      Hello World
    </Button>
  );
}

// Try different render targets, rendering to the one that appears first
let target = null;
if (target = document.querySelector('#react-app')) {
  ReactDOM.render(<App />, target);
=======
import { YearList, MonthList, DayList } from './list-reports';
import { ErrorMessage } from './errors';
import { SearchBar } from './searchbar';
import { SuperForm } from './forms';


// Try different render targets, rendering to the one that appears first
let target = null;

if (target = document.querySelector('#searchbar')){
  ReactDOM.render(<SearchBar />, target)
>>>>>>> 82d8fc951b744ddce83090cffcae77d51265133d
}

if (target = document.querySelector('#report-list-years')) {
  ReactDOM.render(<YearList />, target);
} else if (target = document.querySelector('#report-list-months')) {
  ReactDOM.render(<MonthList />, target);
} else if (target = document.querySelector('#report-list-days')) {
  ReactDOM.render(<DayList />, target);
}

if (target = document.querySelector('#error-root')) {
  ReactDOM.render(<ErrorMessage />, target);
<<<<<<< HEAD
} 
=======
}

if (target = document.querySelector('#form-root')) {
  ReactDOM.render(<SuperForm />, target);
}
>>>>>>> 82d8fc951b744ddce83090cffcae77d51265133d
